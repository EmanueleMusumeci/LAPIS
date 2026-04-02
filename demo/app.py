"""
app.py — LAPIS Streamlit demo dashboard.

Launch:
    cd /DATA/context-matters-demo
    streamlit run demo/app.py

Set LAPIS_DEMO_MOCK=1 to run without API keys (UI testing).
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Optional

import streamlit as st

# ── path setup ────────────────────────────────────────────────────────────────
_DEMO_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _DEMO_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from demo.runner import LAPISRunner, RunResult, StageResult, MOCK_MODE

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LAPIS — AI Planning Demo",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── inject CSS ────────────────────────────────────────────────────────────────
_css_path = _DEMO_DIR / "style.css"
if _css_path.exists():
    st.markdown(f"<style>{_css_path.read_text()}</style>", unsafe_allow_html=True)

# ── constants ─────────────────────────────────────────────────────────────────
DOMAINS = ["blocksworld", "barman", "floortile", "grippers", "storage", "tyreworld"]
MODELS = {
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
    "claude-3-haiku-20240307": "Claude 3 Haiku",
    "gpt-4o": "GPT-4o",
    "gpt-4o-mini": "GPT-4o mini",
    "gpt-3.5-turbo": "GPT-3.5 Turbo",
}
PLANNER_OPTIONS = ["pyperplan", "up_fd", "fd"]

_NL_DATA_ROOT = _REPO_ROOT / "data" / "llmpp"
_LLMPP_ROOT   = _REPO_ROOT / "third-party" / "llm-pddl" / "domains"


# ── preset loading ────────────────────────────────────────────────────────────

def _load_domain_nl(domain: str) -> str:
    """Load the domain-level NL description (action descriptions) for a domain."""
    # Try llm-pddl first (cleaner single-domain description)
    llmpp_path = _LLMPP_ROOT / domain / "domain.nl"
    if llmpp_path.exists():
        return llmpp_path.read_text().strip()
    # Fall back: first paragraph of p01/nl
    nl_path = _NL_DATA_ROOT / domain / "p01" / "nl"
    if nl_path.exists():
        text = nl_path.read_text().strip()
        parts = _split_nl(text)
        return parts[0]
    return ""


def _load_problem_nl(domain: str, problem_id: str) -> str:
    """Load the problem-instance NL (world state + goal)."""
    nl_path = _NL_DATA_ROOT / domain / problem_id / "nl"
    if nl_path.exists():
        text = nl_path.read_text().strip()
        parts = _split_nl(text)
        return parts[1] if len(parts) > 1 else parts[0]
    return ""


def _split_nl(text: str) -> list[str]:
    """
    Split a combined nl file into [domain_part, problem_part].

    The convention is: domain NL describes actions (multi-paragraph intro),
    then a blank line, then the instance description (objects, state, goal).
    We find the first blank line that appears after at least one paragraph.
    """
    lines = text.splitlines()
    # Find the first blank line after the first non-blank content
    seen_content = False
    split_idx = None
    for i, line in enumerate(lines):
        if line.strip():
            seen_content = True
        elif seen_content:
            split_idx = i
            break

    if split_idx is None:
        return [text, ""]

    domain_part = "\n".join(lines[:split_idx]).strip()
    problem_part = "\n".join(lines[split_idx:]).strip()
    return [domain_part, problem_part]


def _available_presets() -> dict[str, dict]:
    """
    Return {label: {domain, problem_id, domain_nl, problem_nl}}.
    Includes blocksworld p01-p05, barman p01-p03, and "Custom".
    """
    presets: dict[str, dict] = {}
    for domain, pids in [("blocksworld", [f"p{i:02d}" for i in range(1, 6)]),
                         ("barman",      [f"p{i:02d}" for i in range(1, 4)])]:
        for pid in pids:
            nl_path = _NL_DATA_ROOT / domain / pid / "nl"
            if nl_path.exists():
                label = f"{domain} {pid}"
                presets[label] = {
                    "domain": domain,
                    "problem_id": pid,
                    "domain_nl": _load_domain_nl(domain),
                    "problem_nl": _load_problem_nl(domain, pid),
                }
    presets["Custom"] = {"domain": "blocksworld", "problem_id": "", "domain_nl": "", "problem_nl": ""}
    return presets


# ── agent factory ─────────────────────────────────────────────────────────────

def _make_agent(model_id: str):
    if MOCK_MODE:
        return None
    if model_id.startswith("claude"):
        from src.lapis.agents.claude import ClaudeAgent
        return ClaudeAgent(model=model_id)
    else:
        from src.lapis.agents.gpt import GPTAgent
        return GPTAgent(model=model_id)


# ── session state init ────────────────────────────────────────────────────────

def _init_state():
    defaults = {
        "lapis_result": None,
        "llmpp_result": None,
        "stages_lapis": [],
        "stages_llmpp": [],
        "running_lapis": False,
        "running_llmpp": False,
        "domain_nl_widget": "",
        "problem_nl_widget": "",
        "selected_preset": "blocksworld p01",
        "selected_domain": "blocksworld",
        "model_id": "claude-3-5-sonnet-20241022",
        "planner": "pyperplan",
        "max_refinements": 3,
        # Blocksworld visualization state
        "vis_frame_idx": 0,
        "vis_autoplay": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Populate default preset on first load
    if not st.session_state.domain_nl_widget and st.session_state.selected_preset != "Custom":
        presets = _available_presets()
        if st.session_state.selected_preset in presets:
            preset = presets[st.session_state.selected_preset]
            st.session_state.domain_nl_widget = preset["domain_nl"]
            st.session_state.problem_nl_widget = preset["problem_nl"]

_init_state()


# ── stage card rendering ──────────────────────────────────────────────────────

_STAGE_ICONS = {
    "Domain Generation": "🔧",
    "Domain Adequacy Check": "🔍",
    "Problem Generation": "📋",
    "Planning + Refinement": "⚙️",
}

_STATUS_ICON = {
    "pending": "⏳",
    "running": "🔄",
    "done": "✅",
    "error": "❌",
    "skipped": "⏭️",
}


def _render_stage_card(sr: StageResult) -> str:
    icon = _STAGE_ICONS.get(sr.name, "▶")
    status_icon = _STATUS_ICON.get(sr.status, "")
    badge_class = f"badge-{sr.status}"
    card_class = f"stage-card {sr.status}"

    dur_html = (f'<span class="stage-duration">{sr.duration:.1f}s</span>'
                if sr.status in ("done", "error", "skipped") and sr.duration > 0
                else "")

    preview = ""
    if sr.status == "done" or sr.status == "skipped":
        if sr.name == "Domain Generation" or sr.name == "Domain Adequacy Check":
            snippet = (sr.domain_pddl or "")[:200].replace("<", "&lt;").replace(">", "&gt;")
            if snippet:
                preview = f'<div class="stage-preview">{snippet}…</div>'
        elif sr.name == "Problem Generation":
            snippet = (sr.problem_pddl or "")[:200].replace("<", "&lt;").replace(">", "&gt;")
            if snippet:
                preview = f'<div class="stage-preview">{snippet}…</div>'
        elif sr.name == "Planning + Refinement" and sr.plan_actions:
            actions_str = "\n".join(sr.plan_actions[:4])
            preview = f'<div class="stage-preview">{actions_str}</div>'
    elif sr.status == "running":
        hint = sr.adequacy_analysis or "…"
        preview = f'<div class="stage-preview">{hint[:120]}</div>'
    elif sr.status == "error":
        msg = (sr.error_msg or "Unknown error")[:180]
        preview = f'<div class="stage-preview" style="color:#f87171;">{msg}</div>'

    amended_tag = ""
    if sr.domain_amended:
        amended_tag = ' <span style="color:#f59e0b;font-size:0.7rem;">amended</span>'
    if sr.problem_amended:
        amended_tag += ' <span style="color:#f59e0b;font-size:0.7rem;">amended</span>'

    return f"""
<div class="{card_class}">
  <div class="stage-title">
    {icon} {sr.name}{amended_tag}
    <span class="stage-badge {badge_class}">{status_icon} {sr.status}</span>
    {dur_html}
  </div>
  {preview}
</div>
"""


def _render_all_stage_cards(stages: list[StageResult], placeholder=None) -> None:
    html = "".join(_render_stage_card(s) for s in stages)
    if placeholder:
        placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ── refinement terminal ───────────────────────────────────────────────────────

def _render_refinement_terminal(history: list[dict]) -> str:
    if not history:
        return '<div class="refine-terminal"><span class="refine-info">No refinements needed.</span></div>'

    lines = []
    for entry in history:
        i = entry.get("iteration", "?")
        ok = entry.get("success", False)
        err = entry.get("error", "")
        fix = entry.get("fix", "")
        icon = "✅" if ok else "❌"
        lines.append(f'<span class="refine-info">─── Iteration {i}/{len(history)} {icon}</span>')
        if err:
            lines.append(f'  <span class="refine-err">Error: {err[:200]}</span>')
        if fix:
            lines.append(f'  <span class="refine-ok">Fix:   {fix[:200]}</span>')
        lines.append("")

    inner = "\n".join(lines)
    return f'<div class="refine-terminal">{inner}</div>'


# ── plan display ──────────────────────────────────────────────────────────────

def _render_plan_steps(actions: list[str]) -> str:
    rows = []
    for i, a in enumerate(actions, 1):
        rows.append(
            f'<div class="plan-step">'
            f'<span class="plan-step-num">{i}.</span>'
            f'<span class="plan-step-action">{a}</span>'
            f'</div>'
        )
    return "\n".join(rows)


# ── PDDL diff ─────────────────────────────────────────────────────────────────

def _side_by_side_pddl(label_a: str, pddl_a: str, label_b: str, pddl_b: str):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{label_a}**")
        st.code(pddl_a, language="lisp")
    with c2:
        st.markdown(f"**{label_b}**")
        st.code(pddl_b, language="lisp")


# ── blocksworld GIF rendering ─────────────────────────────────────────────────

def _try_render_blocksworld(result: RunResult, container):
    """Attempt to render blocksworld frames; silently skip if not available."""
    if not result.plan_actions:
        return False
    if not result.domain_file_path or not result.problem_file_path:
        return False

    try:
        from src.lapis.plan_renderer import render_blocksworld_gif
        gif_path = str(Path(result.domain_file_path).parent / "plan.gif")
        ok = render_blocksworld_gif(
            domain_file=result.domain_file_path,
            problem_file=result.problem_file_path,
            action_strs=result.plan_actions,
            output_path=gif_path,
            fps=2,
        )
        if ok and Path(gif_path).exists():
            container.image(gif_path, caption="Plan animation", use_container_width=True)
            return True
    except Exception:
        pass
    return False


# ── sidebar ───────────────────────────────────────────────────────────────────

def _sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")

        # Presets
        presets = _available_presets()
        preset_labels = list(presets.keys())
        selected_label = st.selectbox(
            "Preset problem",
            preset_labels,
            index=preset_labels.index(st.session_state.selected_preset)
                  if st.session_state.selected_preset in preset_labels else 0,
            key="_preset_select",
        )

        if selected_label != st.session_state.selected_preset:
            st.session_state.selected_preset = selected_label
            preset = presets[selected_label]
            if selected_label != "Custom":
                st.session_state.domain_nl_widget = preset["domain_nl"]
                st.session_state.problem_nl_widget = preset["problem_nl"]
                st.session_state.selected_domain = preset["domain"]
            st.rerun()

        st.divider()

        # Domain (editable when Custom)
        if selected_label == "Custom":
            st.session_state.selected_domain = st.selectbox(
                "Domain", DOMAINS,
                index=DOMAINS.index(st.session_state.selected_domain)
                      if st.session_state.selected_domain in DOMAINS else 0,
            )

        st.divider()

        # Model
        model_labels = list(MODELS.values())
        model_ids    = list(MODELS.keys())
        cur_model_idx = model_ids.index(st.session_state.model_id) if st.session_state.model_id in model_ids else 0
        chosen_label  = st.selectbox("LLM model", model_labels, index=cur_model_idx)
        st.session_state.model_id = model_ids[model_labels.index(chosen_label)]

        st.divider()

        # Planner
        planner_idx = PLANNER_OPTIONS.index(st.session_state.planner) if st.session_state.planner in PLANNER_OPTIONS else 0
        st.session_state.planner = st.selectbox("Planner backend", PLANNER_OPTIONS, index=planner_idx)
        st.session_state.max_refinements = st.slider("Max refinements", 0, 5, st.session_state.max_refinements)

        st.divider()

        if MOCK_MODE:
            st.info("🔔 **MOCK MODE** active\n`LAPIS_DEMO_MOCK=1`\nNo real LLM calls.")

        # API key status
        if not MOCK_MODE:
            for var, label in [("ANTHROPIC_API_KEY", "Anthropic"), ("OPENAI_API_KEY", "OpenAI")]:
                val = os.environ.get(var, "")
                if val:
                    st.markdown(f"✅ {label} key set")
                else:
                    st.markdown(f"⚠️ {label} key **not set**")


# ── main panel ────────────────────────────────────────────────────────────────

def _header():
    st.markdown(
        '<div class="lapis-header">'
        '<span class="lapis-logo">LAPIS</span>'
        '<span class="lapis-subtitle">Language-to-Action Planning via Iterative Schema injection</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def _nl_input_panel():
    st.markdown("#### Natural Language Input")
    col1, col2 = st.columns(2)
    with col1:
        domain_nl = st.text_area(
            "Domain description (actions, preconditions, effects)",
            height=140,
            key="domain_nl_widget",
            placeholder="Describe the planning domain: actions the agent can perform, "
                         "preconditions and effects...",
        )
    with col2:
        problem_nl = st.text_area(
            "Problem instance (objects, initial state, goal)",
            height=140,
            key="problem_nl_widget",
            placeholder="Describe the specific problem: objects present, initial world state, "
                         "and the goal to achieve...",
        )
    return domain_nl, problem_nl


def _run_buttons(domain_nl: str, problem_nl: str):
    col_a, col_b, col_c, col_d = st.columns([1.6, 1.6, 1.6, 4])
    run_lapis = col_a.button("▶ Run LAPIS",  disabled=st.session_state.running_lapis or st.session_state.running_llmpp, use_container_width=True, type="primary")
    run_llmpp = col_b.button("▶ Run LLM+P",  disabled=st.session_state.running_lapis or st.session_state.running_llmpp, use_container_width=True)
    run_both  = col_c.button("⚡ Run Both",   disabled=st.session_state.running_lapis or st.session_state.running_llmpp, use_container_width=True)
    return run_lapis, run_llmpp, run_both


def _execute_run(method: str, domain_nl: str, problem_nl: str,
                 stages_placeholder, results_placeholder):
    """Run the pipeline and update placeholders in real-time."""
    agent = _make_agent(st.session_state.model_id)
    runner = LAPISRunner(
        agent=agent,
        domain_name=st.session_state.selected_domain,
        tmp_dir=str(_DEMO_DIR / "tmp"),
    )

    if method == "lapis":
        st.session_state.stages_lapis = []
        st.session_state.running_lapis = True
    else:
        st.session_state.stages_llmpp = []
        st.session_state.running_llmpp = True

    def _on_update(sr: StageResult):
        if method == "lapis":
            # Update or append
            existing = [s.name for s in st.session_state.stages_lapis]
            if sr.name in existing:
                idx = existing.index(sr.name)
                st.session_state.stages_lapis[idx] = sr
            else:
                st.session_state.stages_lapis.append(sr)
            _render_all_stage_cards(st.session_state.stages_lapis, stages_placeholder)
        else:
            existing = [s.name for s in st.session_state.stages_llmpp]
            if sr.name in existing:
                idx = existing.index(sr.name)
                st.session_state.stages_llmpp[idx] = sr
            else:
                st.session_state.stages_llmpp.append(sr)
            _render_all_stage_cards(st.session_state.stages_llmpp, stages_placeholder)

    result = runner.run(
        domain_nl=domain_nl,
        problem_nl=problem_nl,
        method=method,
        max_refinements=st.session_state.max_refinements,
        planner_name=st.session_state.planner,
        on_stage_update=_on_update,
    )

    if method == "lapis":
        st.session_state.lapis_result  = result
        st.session_state.running_lapis = False
    else:
        st.session_state.llmpp_result  = result
        st.session_state.running_llmpp = False

    return result


# ── results tabs ──────────────────────────────────────────────────────────────

def _result_tabs(lapis_result: Optional[RunResult], llmpp_result: Optional[RunResult]):
    if lapis_result is None and llmpp_result is None:
        return

    show_compare = lapis_result is not None and llmpp_result is not None
    tab_labels = ["Plan", "PDDL", "Adequacy Detail"]
    if show_compare:
        tab_labels.append("Compare")

    tabs = st.tabs(tab_labels)

    # Prefer lapis_result for display; fall back to llmpp_result
    primary = lapis_result or llmpp_result

    # ── Plan tab ──────────────────────────────────────────────────
    with tabs[0]:
        _plan_tab(primary, lapis_result, llmpp_result)

    # ── PDDL tab ──────────────────────────────────────────────────
    with tabs[1]:
        _pddl_tab(primary)

    # ── Adequacy Detail tab ───────────────────────────────────────
    with tabs[2]:
        _adequacy_tab(lapis_result)

    # ── Compare tab ───────────────────────────────────────────────
    if show_compare:
        with tabs[3]:
            _compare_tab(lapis_result, llmpp_result)


def _plan_tab(result: RunResult, lapis_result, llmpp_result):
    if result is None:
        st.info("No result yet.")
        return

    # Status row
    c1, c2, c3, c4 = st.columns(4)
    badge = '<span class="result-success">SUCCESS</span>' if result.success else '<span class="result-fail">FAILED</span>'
    c1.markdown(badge, unsafe_allow_html=True)
    c2.metric("Plan length", len(result.plan_actions))
    c3.metric("Refinements", result.refinements)
    c4.metric("Total time", f"{result.total_time:.1f}s")

    st.markdown("---")

    if not result.plan_actions:
        st.warning("No plan found.")
        # Show refinement terminal if available
        plan_stage = next((s for s in result.stages if s.name == "Planning + Refinement"), None)
        if plan_stage and plan_stage.refinement_history:
            st.markdown("**Refinement log**")
            st.markdown(_render_refinement_terminal(plan_stage.refinement_history), unsafe_allow_html=True)
        return

    # For blocksworld: try GIF, fallback to action list
    is_blocksworld = "blocksworld" in (result.method + st.session_state.selected_domain).lower() or \
                     _is_blocksworld_plan(result.plan_actions)

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown("**Plan actions**")
        # VAL validity badge
        plan_stage = next((s for s in result.stages if s.name == "Planning + Refinement"), None)
        if plan_stage and "Errors: 0" in (plan_stage.val_log or ""):
            st.markdown('<span class="result-success" style="font-size:0.75rem;">VAL valid</span>', unsafe_allow_html=True)

        st.markdown(_render_plan_steps(result.plan_actions), unsafe_allow_html=True)

    with right_col:
        if is_blocksworld and result.domain_file_path:
            st.markdown("**Visualization**")
            gif_container = st.empty()
            gif_ok = _try_render_blocksworld(result, gif_container)
            if not gif_ok:
                st.caption("(GIF rendering unavailable — Pillow or simulator not installed)")
        else:
            # Colored action table for non-blocksworld
            st.markdown("**Action breakdown**")
            import plotly.express as px
            import pandas as pd
            action_names = [a.strip("()").split()[0] if a.strip() else "" for a in result.plan_actions]
            df = pd.DataFrame({"Step": list(range(1, len(action_names)+1)), "Action": action_names})
            if not df.empty:
                fig = px.bar(df, x="Step", y=[1]*len(df), color="Action",
                             labels={"y": ""}, height=200,
                             title="")
                fig.update_layout(
                    paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                    font_color="#e0e0e0", showlegend=True,
                    yaxis_visible=False, margin=dict(l=0, r=0, t=20, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)

    # Refinement log
    if plan_stage and plan_stage.refinement_history:
        st.markdown("---")
        st.markdown("**Refinement log**")
        st.markdown(_render_refinement_terminal(plan_stage.refinement_history), unsafe_allow_html=True)


def _is_blocksworld_plan(actions: list[str]) -> bool:
    bw_actions = {"pickup", "putdown", "stack", "unstack"}
    for a in actions[:3]:
        clean = a.strip("()").split()
        if clean and clean[0].lower() in bw_actions:
            return True
    return False


def _pddl_tab(result: RunResult):
    if result is None:
        st.info("No result yet.")
        return

    sub_domain, sub_problem = st.tabs(["Domain", "Problem"])

    # Find original (pre-adequacy) vs final domain
    domain_stage = next((s for s in result.stages if s.name == "Domain Generation"), None)
    adequacy_stage = next((s for s in result.stages if s.name == "Domain Adequacy Check"), None)
    problem_stage = next((s for s in result.stages if s.name == "Problem Generation"), None)

    with sub_domain:
        if adequacy_stage and adequacy_stage.domain_amended and domain_stage:
            st.markdown("Domain was **amended** by adequacy check.")
            _side_by_side_pddl(
                "Before adequacy check", domain_stage.domain_pddl or "",
                "After adequacy check",  result.final_domain_pddl,
            )
        else:
            st.code(result.final_domain_pddl or "(no domain generated)", language="lisp")

    with sub_problem:
        if problem_stage and problem_stage.problem_amended:
            # Show original (before adequacy fix) vs final
            _side_by_side_pddl(
                "Generated problem", problem_stage.problem_pddl or "",
                "After adequacy fix", result.final_problem_pddl,
            )
        else:
            st.code(result.final_problem_pddl or "(no problem generated)", language="lisp")


def _adequacy_tab(lapis_result: Optional[RunResult]):
    if lapis_result is None:
        st.info("Run LAPIS to see adequacy analysis.")
        return

    adequacy_stage = next((s for s in lapis_result.stages
                           if s.name == "Domain Adequacy Check"), None)
    if adequacy_stage is None:
        st.info("No adequacy check performed (LLM+P mode skips this).")
        return

    st.markdown("### Domain Adequacy CoT Steps")

    if adequacy_stage.cot_steps:
        for step in adequacy_stage.cot_steps:
            with st.expander(f"Step {step['step']}: {step['label']}", expanded=(step['step'] == 2)):
                st.code(step["content"], language="text")
    else:
        st.code(adequacy_stage.adequacy_analysis or "(no analysis)", language="text")

    if adequacy_stage.domain_amended:
        st.warning("Domain was amended after adequacy check.")
    else:
        st.success("Domain was adequate — no amendment needed.")

    st.markdown("### Problem Adequacy")
    problem_stage = next((s for s in lapis_result.stages if s.name == "Problem Generation"), None)
    if problem_stage:
        if problem_stage.problem_amended:
            st.warning("Problem was amended by adequacy check.")
        else:
            st.success("Problem was adequate — no amendment needed.")

        if problem_stage.schema_block:
            with st.expander("Schema block injected into problem prompt"):
                st.code(problem_stage.schema_block, language="text")


def _compare_tab(lapis_result: RunResult, llmpp_result: RunResult):
    st.markdown("### LAPIS vs LLM+P")

    c1, c2 = st.columns(2)

    def _result_card(col, res: RunResult, label: str):
        with col:
            st.markdown(f'<div class="compare-label">{label}</div>', unsafe_allow_html=True)
            badge = "result-success" if res.success else "result-fail"
            st.markdown(f'<span class="{badge}">'
                        f'{"SUCCESS" if res.success else "FAILED"}</span>',
                        unsafe_allow_html=True)
            st.metric("Plan length", len(res.plan_actions))
            st.metric("Refinements", res.refinements)
            st.metric("Time", f"{res.total_time:.1f}s")

    _result_card(c1, lapis_result, "LAPIS")
    _result_card(c2, llmpp_result, "LLM+P")

    st.markdown("---")
    st.markdown("**Domain PDDL comparison**")
    _side_by_side_pddl(
        "LAPIS domain", lapis_result.final_domain_pddl,
        "LLM+P domain (GT)", llmpp_result.final_domain_pddl,
    )

    if lapis_result.plan_actions and llmpp_result.plan_actions:
        st.markdown("---")
        st.markdown("**Plan comparison**")
        p1, p2 = st.columns(2)
        with p1:
            st.markdown("*LAPIS plan*")
            st.markdown(_render_plan_steps(lapis_result.plan_actions), unsafe_allow_html=True)
        with p2:
            st.markdown("*LLM+P plan*")
            st.markdown(_render_plan_steps(llmpp_result.plan_actions), unsafe_allow_html=True)


# ── pipeline stages display ───────────────────────────────────────────────────

def _pipeline_section():
    st.markdown("### Pipeline Stages")
    lapis_placeholder = st.empty()
    llmpp_placeholder = st.empty()

    # Static render of existing stages
    if st.session_state.stages_lapis:
        with lapis_placeholder.container():
            st.caption("LAPIS pipeline")
            _render_all_stage_cards(st.session_state.stages_lapis)
    if st.session_state.stages_llmpp:
        with llmpp_placeholder.container():
            st.caption("LLM+P pipeline")
            _render_all_stage_cards(st.session_state.stages_llmpp)

    return lapis_placeholder, llmpp_placeholder


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    _sidebar()
    _header()

    domain_nl, problem_nl = _nl_input_panel()

    st.markdown("---")

    run_lapis, run_llmpp, run_both = _run_buttons(domain_nl, problem_nl)

    st.markdown("---")

    stages_container = st.container()
    results_container = st.container()

    with stages_container:
        lapis_ph, llmpp_ph = _pipeline_section()

    with results_container:
        st.markdown("---")
        _result_tabs(st.session_state.lapis_result, st.session_state.llmpp_result)

    # ── handle button presses ──────────────────────────────────────
    if run_lapis or run_both:
        if not domain_nl.strip() or not problem_nl.strip():
            st.error("Please provide both domain and problem descriptions.")
        else:
            with stages_container:
                lapis_stages_ph = st.empty()
            _execute_run("lapis", domain_nl, problem_nl,
                         lapis_stages_ph, results_container)
            st.rerun()

    if run_llmpp or run_both:
        if not problem_nl.strip():
            st.error("Please provide a problem description.")
        else:
            with stages_container:
                llmpp_stages_ph = st.empty()
            _execute_run("llmpp", domain_nl, problem_nl,
                         llmpp_stages_ph, results_container)
            st.rerun()


if __name__ == "__main__":
    main()
