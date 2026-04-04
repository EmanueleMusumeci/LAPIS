# Task: Frontend Improvements for Demo Track

**Priority**: HIGH (video = 50% of demo track evaluation)
**Estimated Time**: 4-8 hours
**Dependencies**: None (can run in parallel with experiments)

---

## Objective

Polish the Streamlit dashboard to create a compelling 10-minute demo video. The frontend should clearly visualize the LAPIS pipeline, making the refinement loop and ablation conditions tangible to viewers.

---

## Current State

Existing files:
- `demo/app.py` - Basic Streamlit app
- `demo/app_premium.py` - Enhanced version
- `demo/style_premium.css` - Custom styling
- `demo/runner.py` - Pipeline execution

---

## Required Improvements

### 1. Pipeline Visualization Panel

Show the current pipeline stage with clear visual indicators:

```
┌─────────────────────────────────────────────────────────┐
│  ○ NL Input  →  ● Domain Gen  →  ○ Problem Gen  →  ... │
│                     ▲                                   │
│              [Currently Here]                           │
└─────────────────────────────────────────────────────────┘
```

Implementation:
```python
def render_pipeline_progress(current_stage: str):
    stages = ["NL Input", "Domain Gen", "Adequacy Check",
              "Problem Gen", "Planning", "Validation", "Complete"]

    cols = st.columns(len(stages))
    for i, (col, stage) in enumerate(zip(cols, stages)):
        with col:
            if stage == current_stage:
                st.markdown(f"**● {stage}**")
            elif stages.index(stage) < stages.index(current_stage):
                st.markdown(f"~~{stage}~~")  # completed
            else:
                st.markdown(f"○ {stage}")  # pending
```

### 2. PDDL Side-by-Side Comparison

When in Synthesis mode, show generated vs GT domain:

```
┌─────────────────────┐  ┌─────────────────────┐
│ Generated Domain    │  │ Ground Truth Domain │
│ ─────────────────── │  │ ─────────────────── │
│ (define (domain ..  │  │ (define (domain ..  │
│   (:predicates      │  │   (:predicates      │
│     (on ?x ?y)      │  │     (on ?x ?y)      │
│     (holding ?x) ←──┼──┼→   (holding ?x)     │
│     (clear ?x)      │  │     (arm-empty) ←── │ MISMATCH
│   ...               │  │   ...               │
└─────────────────────┘  └─────────────────────┘
```

Implementation:
```python
def render_pddl_comparison(generated: str, ground_truth: str):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Generated Domain")
        st.code(generated, language="lisp")

    with col2:
        st.subheader("Ground Truth (Oracle)")
        st.code(ground_truth, language="lisp")

    # Highlight differences
    diff = compute_pddl_diff(generated, ground_truth)
    if diff["mismatches"]:
        st.warning(f"Predicate mismatches: {diff['mismatches']}")
```

### 3. Refinement Loop Visualization

Show iteration history with expandable details:

```
┌─────────────────────────────────────────────────────────┐
│ Refinement History                                      │
├─────────────────────────────────────────────────────────┤
│ ▼ Iteration 1 (FAILED)                                  │
│   Error: Predicate 'arm-empty' not declared             │
│   Fix Applied: Added (arm-empty) to predicates          │
├─────────────────────────────────────────────────────────┤
│ ▼ Iteration 2 (FAILED)                                  │
│   Error: Type mismatch in action 'pick-up'              │
│   Fix Applied: Changed parameter type to 'block'        │
├─────────────────────────────────────────────────────────┤
│ ▼ Iteration 3 (SUCCESS)                                 │
│   Plan found: 12 steps                                  │
│   VAL: Valid                                            │
└─────────────────────────────────────────────────────────┘
```

Implementation:
```python
def render_refinement_history(iterations: list[dict]):
    st.subheader("Refinement History")

    for i, iteration in enumerate(iterations):
        status = "✓" if iteration["success"] else "✗"
        color = "green" if iteration["success"] else "red"

        with st.expander(f"Iteration {i+1} ({status})", expanded=(i == len(iterations)-1)):
            if iteration.get("error"):
                st.error(f"Error: {iteration['error']}")
            if iteration.get("fix"):
                st.info(f"Fix: {iteration['fix']}")
            if iteration.get("plan_length"):
                st.success(f"Plan found: {iteration['plan_length']} steps")
```

### 4. Plan Trace Visualization

Animated or step-through plan execution:

```
┌─────────────────────────────────────────────────────────┐
│ Plan Execution (Step 5/12)                    [▶ Play]  │
├─────────────────────────────────────────────────────────┤
│ Current Action: (pick-up block-a)                       │
│                                                         │
│ State Before:          State After:                     │
│ ┌─────────────┐        ┌─────────────┐                  │
│ │ [A]         │   →    │             │                  │
│ │ [B][C]      │        │ [B][C]      │  Hand: [A]       │
│ └─────────────┘        └─────────────┘                  │
│                                                         │
│ [◀ Prev] [Step 5 ▼] [Next ▶]                           │
└─────────────────────────────────────────────────────────┘
```

Implementation:
```python
def render_plan_trace(plan: list[str], current_step: int = 0):
    st.subheader("Plan Execution")

    # Step selector
    step = st.slider("Step", 0, len(plan)-1, current_step)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Prev") and step > 0:
            step -= 1
    with col3:
        if st.button("Next ▶") and step < len(plan)-1:
            step += 1

    # Current action
    st.code(plan[step], language="lisp")

    # State visualization (domain-specific)
    if "blocksworld" in st.session_state.get("domain", ""):
        render_blocksworld_state(step)
```

### 5. Ablation Condition Selector

Allow users to switch between experimental conditions:

```
┌─────────────────────────────────────────────────────────┐
│ Experimental Condition                                  │
├─────────────────────────────────────────────────────────┤
│ ○ LLM+P (GT domain, no refinement)                     │
│ ○ LAPIS/GT (GT domain, with refinement)                │
│ ● LAPIS/Synthesis (generate domain)                    │
│ ○ LAPIS/Adequacy (generate + CoT check)                │
└─────────────────────────────────────────────────────────┘
```

Implementation:
```python
def render_condition_selector():
    condition = st.radio(
        "Experimental Condition",
        options=[
            ("llmpp", "LLM+P (GT domain, no refinement)"),
            ("lapis_gt", "LAPIS/GT (GT domain, with refinement)"),
            ("lapis_synth", "LAPIS/Synthesis (generate domain)"),
            ("lapis_adequacy", "LAPIS/Adequacy (generate + CoT check)")
        ],
        format_func=lambda x: x[1]
    )
    return condition[0]
```

### 6. Results Dashboard

Show aggregated success rates across domains:

```
┌─────────────────────────────────────────────────────────┐
│ Results Summary                                         │
├─────────────────────────────────────────────────────────┤
│ Domain      │ LLM+P │ LAPIS/GT │ Synth │ Adequacy │    │
│ ──────────────────────────────────────────────────────  │
│ Blocksworld │ 100%  │   60%    │  --   │    --    │    │
│ Storage     │ 100%  │   --     │  90%  │   85%    │    │
│ Termes      │ 100%  │   --     │ 100%  │  100%    │    │
│ Floortile   │  --   │   45%    │  94%  │   88%    │ ★  │
│ ...         │       │          │       │          │    │
└─────────────────────────────────────────────────────────┘
                                          ★ = Synth > GT
```

---

## Styling Guidelines

Use consistent color scheme:
- **Green**: Success, valid, passed
- **Red**: Failure, invalid, error
- **Orange**: Warning, refinement needed
- **Blue**: Information, current step
- **Purple**: Symbolic/planner components

Update `demo/style_premium.css` with:
```css
.success { color: #28a745; }
.failure { color: #dc3545; }
.warning { color: #ffc107; }
.info { color: #17a2b8; }
.symbolic { color: #6f42c1; }

.pddl-code {
    font-family: 'Fira Code', monospace;
    font-size: 12px;
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 1rem;
    border-radius: 4px;
}

.pipeline-stage {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    margin: 0 0.25rem;
}

.pipeline-stage.active {
    background: #17a2b8;
    color: white;
}

.pipeline-stage.complete {
    background: #28a745;
    color: white;
}
```

---

## Video Recording Checklist

The demo video should showcase:

1. **[0:00-1:00] Introduction**
   - What is LAPIS?
   - The NL-to-plan problem

2. **[1:00-3:00] Basic Demo**
   - Input NL task description
   - Watch domain generation
   - See problem synthesis
   - View generated plan

3. **[3:00-5:00] Refinement in Action**
   - Show a failing case
   - Watch refinement iterations
   - See error diagnosis and fixes
   - Successful recovery

4. **[5:00-7:00] Ablation Comparison**
   - Switch between conditions
   - Show GT vs Synthesis side-by-side
   - Highlight the coupling insight (Synthesis > GT)

5. **[7:00-9:00] Results Dashboard**
   - Aggregated success rates
   - Domain-by-domain breakdown

6. **[9:00-10:00] Conclusion**
   - Key takeaways
   - Future directions

---

## Files to Modify

1. `demo/app_premium.py` - Main dashboard (or create new `demo/app_icaps.py`)
2. `demo/style_premium.css` - Styling
3. `demo/components/` - Reusable visualization components (create if needed):
   - `pipeline_progress.py`
   - `pddl_viewer.py`
   - `refinement_history.py`
   - `plan_trace.py`
   - `results_dashboard.py`

---

## Success Criteria

1. Clear visual pipeline showing current stage
2. Side-by-side PDDL comparison working
3. Refinement history with expandable iterations
4. Plan trace with step-through navigation
5. Results dashboard with all experimental data
6. 10-minute video script executable from start to finish
7. No crashes or visual glitches during recording

---

## What NOT To Do

- Don't add features that aren't stable enough for video recording
- Don't over-engineer animations (simple is better)
- Don't spend time on mobile responsiveness (demo is desktop-only)
- Don't add authentication or user management
