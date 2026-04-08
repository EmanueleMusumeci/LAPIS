"""
websocket.py — WebSocket handler for real-time pipeline updates.

Provides:
- WebSocket endpoint /ws/pipeline
- Real-time stage updates during pipeline execution
- Connection lifecycle management
"""
from __future__ import annotations

import asyncio
import json
import uuid
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from .models import (
    PipelineConfig, StageResult, RunResult, StageStatus,
    WSMessage, WSMessageType
)
from .runner import LAPISRunner, make_agent, sanitize_error_message
from .editor_orchestrator import EditorOrchestrator


class ConnectionManager:
    """Manages WebSocket connections and their associated runs."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.running_tasks: dict[str, asyncio.Task] = {}
        self.orchestrators: dict[str, EditorOrchestrator] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """Accept connection and return connection ID."""
        await websocket.accept()
        conn_id = str(uuid.uuid4())
        self.active_connections[conn_id] = websocket
        self.orchestrators[conn_id] = EditorOrchestrator()
        return conn_id

    def disconnect(self, conn_id: str):
        """Remove connection and cancel any running task."""
        if conn_id in self.active_connections:
            del self.active_connections[conn_id]

        if conn_id in self.running_tasks:
            self.running_tasks[conn_id].cancel()
            del self.running_tasks[conn_id]

        if conn_id in self.orchestrators:
            del self.orchestrators[conn_id]

    async def send_message(self, conn_id: str, message: WSMessage):
        """Send a message to a specific connection."""
        if conn_id in self.active_connections:
            websocket = self.active_connections[conn_id]
            try:
                await websocket.send_json(message.model_dump())
            except Exception:
                self.disconnect(conn_id)

    async def broadcast(self, message: WSMessage):
        """Send a message to all connections."""
        disconnected = []
        for conn_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message.model_dump())
            except Exception:
                disconnected.append(conn_id)

        for conn_id in disconnected:
            self.disconnect(conn_id)

    def is_running(self, conn_id: str) -> bool:
        """Check if a connection has a running task."""
        if conn_id not in self.running_tasks:
            return False
        return not self.running_tasks[conn_id].done()


manager = ConnectionManager()


async def run_pipeline_ws(
    conn_id: str,
    config: PipelineConfig,
):
    """Execute pipeline and send updates via WebSocket."""
    run_id = str(uuid.uuid4())

    try:
        # Send run started message
        await manager.send_message(conn_id, WSMessage(
            type=WSMessageType.RUN_STARTED,
            run_id=run_id,
            message="Pipeline execution started",
        ))

        agent = make_agent(config.model_id, api_key=config.api_key)
        runner = LAPISRunner(
            agent=agent,
            domain_name=config.domain_name,
        )

        async def on_stage_update(stage: StageResult):
            """Send stage update via WebSocket."""
            await manager.send_message(conn_id, WSMessage(
                type=WSMessageType.STAGE_UPDATE,
                run_id=run_id,
                data=stage.model_dump(),
            ))

        result = await runner.run(config, on_stage_update=on_stage_update)

        # Send completion message
        await manager.send_message(conn_id, WSMessage(
            type=WSMessageType.COMPLETE,
            run_id=run_id,
            data=result.model_dump(),
        ))

    except asyncio.CancelledError:
        await manager.send_message(conn_id, WSMessage(
            type=WSMessageType.ERROR,
            run_id=run_id,
            message="Pipeline cancelled",
        ))
    except Exception as e:
        err_msg = sanitize_error_message(e)
        await manager.send_message(conn_id, WSMessage(
            type=WSMessageType.ERROR,
            run_id=run_id,
            message=err_msg,
        ))


async def handle_websocket(websocket: WebSocket):
    """
    Main WebSocket handler for pipeline connections.

    Protocol:
    1. Client connects -> receives {type: "connected", run_id: <conn_id>}
    2. Client sends {type: "run", config: {...PipelineConfig}}
    3. Server sends {type: "stage_update", data: {...StageResult}} for each stage
    4. Server sends {type: "complete", data: {...RunResult}} when done
    5. On error: {type: "error", message: "..."}
    """
    conn_id = await manager.connect(websocket)

    try:
        # Send connected message
        await manager.send_message(conn_id, WSMessage(
            type=WSMessageType.CONNECTED,
            run_id=conn_id,
            message="Connected to LAPIS pipeline WebSocket",
        ))

        while True:
            # Wait for messages from client
            data = await websocket.receive_json()

            msg_type = data.get("type", "")

            if msg_type == "run":
                # Start pipeline run
                if manager.is_running(conn_id):
                    await manager.send_message(conn_id, WSMessage(
                        type=WSMessageType.ERROR,
                        message="A pipeline is already running. Wait for completion or reconnect.",
                    ))
                    continue

                try:
                    config = PipelineConfig(**data.get("config", {}))
                except Exception as e:
                    await manager.send_message(conn_id, WSMessage(
                        type=WSMessageType.ERROR,
                        message=f"Invalid configuration: {e}",
                    ))
                    continue

                # Create and store the task
                task = asyncio.create_task(run_pipeline_ws(conn_id, config))
                manager.running_tasks[conn_id] = task

            elif msg_type == "cancel":
                # Cancel running pipeline
                if conn_id in manager.running_tasks:
                    manager.running_tasks[conn_id].cancel()
                    await manager.send_message(conn_id, WSMessage(
                        type=WSMessageType.ERROR,
                        message="Pipeline cancelled by user",
                    ))

            elif msg_type == "ping":
                # Health check
                await websocket.send_json({"type": "pong"})

            elif msg_type == WSMessageType.USER_MESSAGE.value:
                text = (data.get("text") or "").strip()
                api_key = (data.get("api_key") or "").strip() or None
                orchestrator = manager.orchestrators[conn_id]
                state_payload = await orchestrator.process_user_message(text, api_key=api_key)

                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.AGENT_MESSAGE,
                    data={
                        "response": state_payload["response"],
                        "domain": state_payload["domain"],
                        "problem": state_payload["problem"],
                        "verification": state_payload["verification"],
                    },
                ))

                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.UPDATE,
                    data={
                        "domain": state_payload["domain"],
                        "problem": state_payload["problem"],
                        "source": "agent",
                        "verification": state_payload["verification"],
                    },
                ))

                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.VERIFY_RESULTS,
                    data=state_payload["verification"],
                ))

            elif msg_type == WSMessageType.INIT_SESSION.value:
                domain_name = data.get("domain_name")
                domain_pddl = data.get("domain_pddl") or None
                problem_pddl = data.get("problem_pddl") or None
                orchestrator = manager.orchestrators[conn_id]
                init_payload = await orchestrator.init_session(
                    domain_name=domain_name,
                    domain_pddl=domain_pddl,
                    problem_pddl=problem_pddl,
                )

                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.UPDATE,
                    data={
                        "domain": init_payload["domain"],
                        "problem": init_payload["problem"],
                        "source": "agent",
                        "verification": init_payload["verification"],
                    },
                ))

                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.VERIFY_RESULTS,
                    data=init_payload["verification"],
                ))

            elif msg_type == WSMessageType.PDDL_UPDATE.value:
                domain = data.get("domain", "")
                problem = data.get("problem", "")

                if not domain or not problem:
                    await manager.send_message(conn_id, WSMessage(
                        type=WSMessageType.ERROR,
                        message="PDDL_UPDATE requires both domain and problem content",
                    ))
                    continue

                orchestrator = manager.orchestrators[conn_id]
                sync_payload = await orchestrator.sync_pddl(
                    domain=domain,
                    problem=problem,
                    source=data.get("source", "text"),
                )

                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.UPDATE,
                    data={
                        "domain": sync_payload["domain"],
                        "problem": sync_payload["problem"],
                        "source": sync_payload["source"],
                        "verification": sync_payload["verification"],
                    },
                ))

                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.VERIFY_RESULTS,
                    data=sync_payload["verification"],
                ))

            elif msg_type == WSMessageType.VERIFY_REQUEST.value:
                orchestrator = manager.orchestrators[conn_id]
                verification = await orchestrator.run_verification()
                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.VERIFY_RESULTS,
                    data=verification,
                ))

            elif msg_type == WSMessageType.UPDATE.value:
                domain = data.get("domain", "")
                problem = data.get("problem", "")
                source = data.get("source", "text")

                if not domain or not problem:
                    await manager.send_message(conn_id, WSMessage(
                        type=WSMessageType.ERROR,
                        message="UPDATE requires both domain and problem content",
                    ))
                    continue

                orchestrator = manager.orchestrators[conn_id]
                sync_payload = await orchestrator.sync_pddl(domain=domain, problem=problem, source=source)
                await manager.send_message(conn_id, WSMessage(
                    type=WSMessageType.UPDATE,
                    data={
                        "domain": sync_payload["domain"],
                        "problem": sync_payload["problem"],
                        "source": sync_payload["source"],
                        "verification": sync_payload["verification"],
                    },
                ))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            err_msg = sanitize_error_message(e)
            await manager.send_message(conn_id, WSMessage(
                type=WSMessageType.ERROR,
                message=f"WebSocket error: {err_msg}",
            ))
        except Exception:
            pass
    finally:
        manager.disconnect(conn_id)
