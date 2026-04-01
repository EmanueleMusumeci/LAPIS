# Implementation Choices for CoSTL PDDL Generation

This document outlines the key technical decisions and implementation strategies adopted to improve the robustness and accuracy of the CoSTL planning pipeline.

## 1. PDDL Type Hierarchies vs. Union Types

### The Challenge
LLMs often generate PDDL and ADL "union types" using the `(either type1 type2 ...)` syntax. This occurs when a property (like `in-front-of`) applies to multiple distinct categories of objects (like `door` and `item`) that lack a common ancestor in the provided natural language descriptions.

While valid in some PDDL versions, the **Unified Planning (UP)** parser used in our pipeline does not support union types, leading to persistent syntax errors.

### Implementation Choice: Forced Parent-Type Hierarchy
Instead of attempting a complex runtime rewrite of the PDDL, we implemented a **Prompt Engineering constraint** that forces the LLM to maintain a strict single-type hierarchy. 
- **Requirement**: The LLM is instructed to explicitly define a common parent type (e.g., `entity`) in the `(:types)` block whenever an object must satisfy multiple roles.
- **Result**: This ensures high compatibility with a wider range of PDDL parsers and planners (including `up-fast-downward`) while maintaining clear semantic relationships.

## 2. LLM-Based Entity Mapping (Name Grounding)

### The Challenge
Natural language subgoals often use descriptive names (e.g., "green block number 2") that do not match the internal PDDL instance names (e.g., `green_block_1`).

### Implementation Choice: Explicit Grounding Step
We introduced a dedicated LLM-based preprocessing step that maps NL descriptions to exact PDDL objects *before* generation begins. This decouples the "understanding" of the world state from the "generation" of the plan logic, preventing a common source of planning failure where the goal is unreachable simply because the object name is hallucinated.

## 3. Granular NL Context Segmentation

### The Challenge
Traditional PDDL generation prompts often feed the entire environment description to the LLM. This violates the principle of least privilege and often leads to the LLM "cheating" by including goal-specific predicates or future state information in the domain definition.

### Implementation Choice: Content-Specific Filtering
We implemented a strict segmentation policy:
- **Domain Generation**: Receives only descriptions of Actions, Preconditions, and Effects. It is explicitly "blind" to the current goal and object list to ensure a generic, reusable domain model.
- **Problem Generation**: Receives only the Object list and Initial State.
- **Benefit**: This forces the generated PDDL to be grounded in the structural logic of the world rather than the specific details of the current task.

## 4. RAG-Enhanced Refinement Loop

### The Challenge
Iterative refinement often repeatably makes the same mistakes across different subgoals or problem instances.

### Implementation Choice: Issue-Based Knowledge Retrieval
We integrated a **Vector DB** into the refinement loop. When a PDDL file fails validation:
1. The error is converted into a concise "Issue" description.
2. The system searches the DB for similar past issues.
3. Successful historical solutions are injected into the LLM's prompt as "REFERENCE SOLUTIONS."
4. Verified fixes are automatically committed back to the DB to enable learning across the session.

## 5. Lexicon Environment Reproduction (BabyAI)

### The Challenge
Original BabyAI environments used by Lexicon rely on procedural generation that is hard to reproduce identically from seeds alone.

### Implementation Choice: State-Injection via Monkey Patching
We adopted a strategy of **State-Injection** to guarantee consistency:
1.  **Monkey Patching**: Bypassing procedural generation by patching `RoomGrid._gen_grid` and `MiniGridEnv.reset` to load specific states.
2.  **State Representation**: Using `Sample` objects to define initial object positions directly from the original datasets.
3.  **Observation Wrapping**: Converting raw MiniGrid observations into PDDL-ready data via a custom wrapper.
4.  **UP Mapping**: Translating these observations to `unified_planning.Problem` objects to ensure the generated PDDL matches the simulator's internal state.

## 6. Structural Logic Shadowing Detection in Multi-Level Planning

### The Challenge
In multi-level planning, merging contiguous high-level steps into a single subgoal can "shadow" (hide) intermediate states required by global LTL constraints. For example, a `pickup(block)` followed by a `putdown(block)` sequence might be merged into a single PDDL problem where the planner only sees the starting and ending state (both not holding the block). If the LTL constraint requires `F(holding(block))`, this sequence is valid but the intermediate state must be preserved as a "milestone."

Previous attempts to detect this using local LTL verification of partial traces suffered from **"Global Backfire"**: the verifier would reject a valid merge simply because the *rest* of the global formula (unrelated to the current steps) wasn't yet satisfied.

### Implementation Choice: Domain-Agnostic Structural Analysis
We implemented a robust "Structural Logic" conflict detection mechanism that operates *before* planning begins:
1.  **Automated Domain Analysis**: The pipeline uses `unified_planning.PDDLReader` to parse the domain file at runtime and automatically map which actions "set" or "unset" specific predicates.
2.  **LTL-Sensitive Fluent Extraction**: The global LTL formula is analyzed to identify "sensitive" fluents whose transitions are critical to the temporal logic.
3.  **Heuristic Toggle Check**: During the merge phase, a proposed group of actions is analyzed against the next step. If the sequence would "toggle" a sensitive fluent (e.g., Action A sets `holding(X)` and Action B unsets it), the merge is **REJECTED**.
4.  **Benefit**: This provides a domain-agnostic, reliable way to preserve critical intermediate states without the computational overhead or logical pitfalls of partial trace verification. It ensures that every "temporal anchor" in the LTL formula remains visible as a distinct subgoal boundary.
