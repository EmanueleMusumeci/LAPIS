# LAPIS Premium Dashboard: Task Resumption & Status

## 🎯 Objective
Create a high-performance, visually premium version of the LAPIS planning dashboard for the ICAPS 2026 system demonstration. The new application (`demo/app_premium.py`) must feature a "Cyber-Glass" design and a "Model Race" dashboard for real-time parallel execution of planning methods.

## 📍 Current State
- [x] **Premium UI**: Implemented `demo/style_premium.css` with glassmorphism, backdrop-blur, and mesh gradients.
- [x] **Architecture**: Created `demo/app_premium.py` as a standalone premium version (Plan B `demo/app.py` is untouched).
- [x] **Parallel Engine**: Implemented `_execute_run_parallel` in `app_premium.py` using Python `threading`.
- [x] **Streamlit Threading**: Integrated `add_script_run_ctx` from `streamlit.runtime.scriptrunner` to allow background threads to update UI placeholders.
- [x] **Model Race UI**: Added dual-track layout with real-time progress bars and stage card updates.
- [x] **API Integration**: Updated `ClaudeAgent` to handle `ANTHROPIC_API_KEY` and fallback to `OPENROUTER_API_KEY`.

## 📂 Key Files
- `demo/app_premium.py`: Main entry point for the premium dashboard.
- `demo/style_premium.css`: Premium CSS tokens and layout overrides.
- `demo/runner.py`: The planning orchestration logic (shared with the original app).
- `key.sh`: Contains the `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` used for experiments.

## 🚀 How to Run
To run the dashboard with full functionality (real LLM calls):
```bash
# From the repository root
source key.sh
streamlit run demo/app_premium.py --server.port 8503
```

## 🛠 Missing Steps & Blockers
1. **Server Stability**: The Streamlit server on port 8503 has been intermittently unreachable or "Stopping" immediately. Ensure it is started from the repository root to avoid `demo/app_premium.py not found` errors.
2. **Functional Verification**: Capture a full browser recording of the **"Model Race"** from start to finish using `blocksworld p01` or another preset.
3. **OpenAI Key Validation**: The LLM+P racer requires `OPENAI_API_KEY`. Ensure the key in `key.sh` is correctly mapped in `app_premium.py` or the environment.
4. **Race Track Polish**: Verify that the `lapis_ph` and `llmpp_ph` placeholders update correctly in the `while` loop inside `_execute_run_parallel`.
5. **Backend Check**: Ensure the local planning binaries (`fast-downward`, `pyperplan`) are available or the UP (Unified Planning) environment is properly initialized.

## 🏁 Verification Goals
- [ ] Successfully load `http://localhost:8503`.
- [ ] Select a preset and click "🏁 MODEL RACE".
- [ ] Observe both tracks (LAPIS 🌀 and LLM+P 🚀) updating stages in real-time.
- [ ] See the "Race Complete!" status and a "Winner" indicator (optional polish).
- [ ] View the resulting plans and PDDL diffs in the premium tabs.

---
*Last update: 2026-04-02*
