# UI_PLAN.md — DEPRECATED

> **⚠️ DEPRECATED**: This document refers to the legacy Streamlit demo which has been archived to `IGNORE_THIS_FOLDER/`. The current frontend is the React+FastAPI web app in `lapis-web/`. See `lapis-web/README.md` for current documentation.

---

## Historical Reference (Legacy Streamlit Demo)

This document outlined fixes and improvements for the original Streamlit demo dashboard.

**Legacy Files (archived in `IGNORE_THIS_FOLDER/`):**
- `app.py.old` — Main Streamlit application
- `runner.py.old` — Pipeline runner with mock mode
- `style.css.old` — Dark theme CSS
- `requirements_demo.txt` — Demo-specific dependencies

---

## Priority 1: Critical Fixes

### 1.1 Missing `termes` Domain in Dropdown

**Issue:** `DOMAINS` list in `app.py:43` is missing `termes`.

**Current:**
```python
DOMAINS = ["blocksworld", "barman", "floortile", "grippers", "storage", "tyreworld"]
```

**Fix:**
```python
DOMAINS = ["blocksworld", "barman", "floortile", "grippers", "storage", "termes", "tyreworld"]
```

### 1.2 Outdated Model List

**Issue:** `MODELS` dict uses old model IDs (Claude 3.5 Sonnet, etc.)

**Current:**
```python
MODELS = {
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
    "claude-3-haiku-20240307": "Claude 3 Haiku",
    ...
}
```

**Fix:**
```python
MODELS = {
    "claude-sonnet-4-6": "Claude Sonnet 4.6",
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
    "gpt-4o": "GPT-4o",
    "gpt-4o-mini": "GPT-4o mini",
}
```

### 1.3 Hardcoded Planner Timeout

**Issue:** `runner.py:582-583` uses hardcoded 60s timeout, should be configurable.

**Current:**
```python
plan, pddlenv_err, planner_err, _ = plan_with_output(
    domain_path, problem_dir, plan_path, planner_name=planner_name, timeout=60
)
```

**Fix:** Add `planner_timeout` parameter to `LAPISRunner.run()` and propagate it.

### 1.4 Broken Path in Launch Comment

**Issue:** `app.py:6` references wrong directory.

**Current:**
```python
# cd /DATA/context-matters-demo
```

**Fix:**
```python
# cd /DATA/lapis
```

---

## Priority 2: UX Improvements

### 2.1 Add Planner Timeout Slider

**Location:** Sidebar configuration (`app.py:327-377`)

**Add:**
```python
st.session_state.planner_timeout = st.slider(
    "Planner timeout (seconds)", 30, 300, 180,
    help="Maximum time for the symbolic planner per problem"
)
```

### 2.2 Add Adequacy Check Toggle

**Location:** Sidebar

**Add:**
```python
st.session_state.enable_adequacy = st.checkbox(
    "Enable adequacy checks (LAPIS mode)",
    value=True,
    help="CoT checks verify domain can represent observed facts"
)
```

### 2.3 Better Error Display

**Issue:** Errors show truncated in stage cards (max 180 chars).

**Improvement:** Add expandable error details.

**File:** `app.py:219-220`

```python
# Add full error in expander after stage cards
if sr.status == "error" and sr.error_msg:
    with st.expander("Full error message"):
        st.code(sr.error_msg, language="text")
```

### 2.4 Loading Indicator During Pipeline Run

**Issue:** No visual feedback while waiting for LLM responses.

**Add spinner to `_execute_run()`:**
```python
with st.spinner(f"Running {method.upper()} pipeline..."):
    result = runner.run(...)
```

### 2.5 Export Results Button

**Add to Plan tab:**
```python
if result.plan_actions:
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download Plan",
            "\n".join(result.plan_actions),
            file_name="plan.txt",
            mime="text/plain"
        )
    with col2:
        st.download_button(
            "Download PDDL",
            f"{result.final_domain_pddl}\n\n{result.final_problem_pddl}",
            file_name="pddl_files.pddl",
            mime="text/plain"
        )
```

---

## Priority 3: Feature Additions

### 3.1 Batch Mode Support

Add ability to run multiple problems from a domain:

```python
# In sidebar
batch_mode = st.checkbox("Batch mode")
if batch_mode:
    problems = _discover_problems(domain)
    selected_problems = st.multiselect("Select problems", problems, default=problems[:3])
```

### 3.2 Results History

Store and display history of runs in the session:

```python
if "run_history" not in st.session_state:
    st.session_state.run_history = []

# After each run
st.session_state.run_history.append({
    "timestamp": time.time(),
    "domain": domain,
    "method": method,
    "success": result.success,
    "plan_length": len(result.plan_actions),
})

# In sidebar
with st.expander("Run History"):
    for entry in st.session_state.run_history[-5:]:
        st.write(f"{entry['domain']} - {'OK' if entry['success'] else 'FAIL'}")
```

### 3.3 Side-by-Side Domain Comparison

Enhance the Compare tab to show domain diff:

```python
import difflib

def _show_diff(text1, text2, label1, label2):
    diff = difflib.unified_diff(
        text1.splitlines(),
        text2.splitlines(),
        fromfile=label1,
        tofile=label2,
        lineterm=""
    )
    st.code("\n".join(diff), language="diff")
```

### 3.4 Live Token Counter

Show estimated token usage during run:

```python
# In runner.py, add token tracking
class LAPISRunner:
    def __init__(self, ...):
        self.total_tokens = 0

    # Wrap agent.llm_call to track tokens
```

### 3.5 Plan Visualization for More Domains

Currently only blocksworld has GIF rendering. Add basic visualizations for:
- **barman**: ASCII art showing cocktail preparation steps
- **grippers**: Robot arm picking/placing objects

---

## Priority 4: Code Quality

### 4.1 Split `app.py` into Modules

Current 784-line file should be split:

```
demo/
├── app.py              # Main entry, layout
├── runner.py           # Pipeline execution (keep)
├── components/
│   ├── sidebar.py      # Configuration sidebar
│   ├── stage_cards.py  # Stage card rendering
│   ├── plan_display.py # Plan tab content
│   ├── pddl_display.py # PDDL tab content
│   └── compare.py      # Compare tab content
├── utils/
│   ├── presets.py      # NL preset loading
│   └── visualization.py # Plan animation
└── style.css
```

### 4.2 Add Type Hints

Add proper type hints throughout:

```python
def _render_stage_card(sr: StageResult) -> str:
    ...

def _execute_run(
    method: str,
    domain_nl: str,
    problem_nl: str,
    stages_placeholder: st.delta_generator.DeltaGenerator,
    results_placeholder: st.delta_generator.DeltaGenerator,
) -> RunResult:
    ...
```

### 4.3 Error Handling Improvements

Add try-except blocks around external calls:

```python
try:
    from src.lapis.plan_renderer import render_blocksworld_gif
except ImportError:
    render_blocksworld_gif = None  # Graceful degradation
```

### 4.4 Configuration File

Move hardcoded values to `demo/config.yaml`:

```yaml
domains:
  - blocksworld
  - barman
  - floortile
  - grippers
  - storage
  - termes
  - tyreworld

models:
  claude-sonnet-4-6: "Claude Sonnet 4.6"
  gpt-4o: "GPT-4o"

defaults:
  max_refinements: 3
  planner_timeout: 180
  planner: "pyperplan"
```

---

## CSS Improvements

### 5.1 Add Responsive Breakpoints

```css
@media (max-width: 768px) {
    .stage-card {
        padding: 0.5rem;
    }
    .plan-step {
        font-size: 0.75rem;
    }
}
```

### 5.2 Add Animation for Running State

```css
.stage-card.running {
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { border-left-color: #f59e0b; }
    50% { border-left-color: #fbbf24; }
}
```

### 5.3 Better Code Block Styling

```css
.stCodeBlock {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
}

.stCodeBlock code {
    font-family: "JetBrains Mono", "Fira Code", monospace !important;
    font-size: 0.8rem !important;
}
```

---

## Implementation Checklist

### Phase 1: Critical Fixes (1 hour)
- [ ] Add `termes` to DOMAINS list
- [ ] Update model IDs
- [ ] Fix hardcoded timeout
- [ ] Fix path in comment

### Phase 2: UX Improvements (2-3 hours)
- [ ] Add planner timeout slider
- [ ] Add adequacy check toggle
- [ ] Improve error display
- [ ] Add loading spinner
- [ ] Add export buttons

### Phase 3: Features (4-6 hours)
- [ ] Implement batch mode
- [ ] Add run history
- [ ] Implement diff view
- [ ] Add token counter

### Phase 4: Code Quality (4-6 hours)
- [ ] Split into modules
- [ ] Add type hints
- [ ] Improve error handling
- [ ] Create config file

---

## Testing Plan

### Manual Testing
1. Run in mock mode: `LAPIS_DEMO_MOCK=1 streamlit run demo/app.py`
2. Test each domain preset
3. Test LAPIS vs LLM+P comparison
4. Test error states (invalid NL input)
5. Test all tabs

### Integration Testing
1. Run with real API keys
2. Test blocksworld end-to-end
3. Test barman end-to-end
4. Verify VAL validation display
5. Test GIF rendering
