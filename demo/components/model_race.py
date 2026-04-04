"""
model_race.py — Premium Model Race dashboard for the LAPIS Streamlit demo.

Renders three views:
1. Command Center     — aggregate metric cards + Plotly success-rate chart
2. Problem Inspector  — side-by-side comparison per problem
3. Cost & Time Panel  — wall-clock time comparison
"""

from __future__ import annotations

import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path


# ── Color / Label Mapping ─────────────────────────────────────────────────────

SYSTEM_COLORS = {
    "direct_llm": "#ef4444",   # red — floor
    "llmpp":      "#f59e0b",   # amber — baseline with GT domain
    "nl2plan":    "#8b5cf6",   # purple — competitor
    "lapis_c":    "#3b82f6",   # blue — LAPIS VAL only
    "lapis_d":    "#06b6d4",   # cyan — LAPIS VAL + adequacy
    "lapis_e":    "#10b981",   # green — LAPIS full semantic
}

SYSTEM_LABELS = {
    "direct_llm": "Direct LLM",
    "llmpp":      "LLM+P (GT)",
    "nl2plan":    "NL2Plan",
    "lapis_c":    "LAPIS (VAL)",
    "lapis_d":    "LAPIS (VAL+Adq)",
    "lapis_e":    "LAPIS (Full)",
}

# Premium HSL-based palette for the chart
CHART_PALETTE = [
    "#ef4444", "#f59e0b", "#8b5cf6",
    "#3b82f6", "#06b6d4", "#10b981",
]


# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data
def load_results(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        return {"results": data}
    return data


def get_systems(data: dict) -> list[str]:
    systems = set()
    for entry in data.get("results", []):
        if "system" in entry:
            systems.add(entry["system"])
    return sorted(systems)


def get_domains(data: dict) -> list[str]:
    return sorted(set(e["domain"] for e in data.get("results", []) if "domain" in e))


# ── Aggregation ───────────────────────────────────────────────────────────────

def compute_success_table(data: dict) -> pd.DataFrame:
    results = data.get("results", [])
    domains = get_domains(data)
    systems = get_systems(data)

    rows = []
    for domain in domains:
        row: dict = {"Domain": domain}
        for system in systems:
            sys_entries = [r for r in results
                           if r.get("domain") == domain and r.get("system") == system]
            if sys_entries:
                successes = sum(1 for r in sys_entries if r.get("success_oracle"))
                row[system] = round(successes / len(sys_entries) * 100, 1)
            else:
                row[system] = None
        rows.append(row)

    df = pd.DataFrame(rows)
    avg_row: dict = {"Domain": "Average"}
    for system in systems:
        vals = [r[system] for r in rows if r.get(system) is not None]
        avg_row[system] = round(sum(vals) / len(vals), 1) if vals else None
    df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
    return df


def compute_time_table(data: dict) -> pd.DataFrame:
    results = data.get("results", [])
    domains = get_domains(data)
    systems = get_systems(data)

    rows = []
    for domain in domains:
        row: dict = {"Domain": domain}
        for system in systems:
            sys_entries = [r for r in results
                           if r.get("domain") == domain and r.get("system") == system]
            times = [r.get("time_seconds", 0) for r in sys_entries if r.get("time_seconds")]
            row[system] = round(sum(times) / len(times), 1) if times else None
        rows.append(row)
    return pd.DataFrame(rows)


def _overall_success_rate(data: dict, system: str) -> float:
    results = data.get("results", [])
    sys_entries = [r for r in results if r.get("system") == system]
    if not sys_entries:
        return 0.0
    return round(sum(1 for r in sys_entries if r.get("success_oracle")) / len(sys_entries) * 100, 1)


def _avg_time(data: dict, system: str) -> float:
    results = data.get("results", [])
    sys_entries = [r for r in results if r.get("system") == system and r.get("time_seconds")]
    if not sys_entries:
        return 0.0
    return round(sum(r["time_seconds"] for r in sys_entries) / len(sys_entries), 1)


# ── Metric Cards ──────────────────────────────────────────────────────────────

_CARD_CSS = """
<style>
.mr-card-row { display:flex; gap:16px; margin-bottom:24px; flex-wrap:wrap; }
.mr-card {
    flex:1; min-width:160px;
    background: linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 18px 20px;
    backdrop-filter: blur(10px);
}
.mr-card-label { font-size:0.72rem; color:#94a3b8; letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px; }
.mr-card-value { font-size:1.9rem; font-weight:700; line-height:1; }
.mr-card-sub   { font-size:0.75rem; color:#64748b; margin-top:4px; }

/* Success rate heatmap table */
.mr-table { width:100%; border-collapse:collapse; font-size:0.82rem; margin-top:8px; }
.mr-table th {
    background:rgba(255,255,255,0.06); color:#94a3b8;
    padding:8px 12px; text-align:center; border-bottom:1px solid rgba(255,255,255,0.1);
    font-weight:600; letter-spacing:.05em; font-size:0.75rem; text-transform:uppercase;
}
.mr-table td { padding:7px 12px; text-align:center; border-bottom:1px solid rgba(255,255,255,0.05); }
.mr-table tr:last-child td { border-bottom:none; font-weight:700; background:rgba(255,255,255,0.04); }
.mr-table td:first-child { text-align:left; color:#cbd5e1; }
.mr-badge-ok  { background:#10b98122; color:#6ee7b7; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:600; }
.mr-badge-mid { background:#f59e0b22; color:#fcd34d; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:600; }
.mr-badge-bad { background:#ef444422; color:#fca5a5; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:600; }
.mr-badge-nil { color:#475569; font-size:0.78rem; }
</style>
"""


def _rate_badge(val) -> str:
    if val is None:
        return '<span class="mr-badge-nil">—</span>'
    if val >= 80:
        return f'<span class="mr-badge-ok">{val:.0f}%</span>'
    if val >= 50:
        return f'<span class="mr-badge-mid">{val:.0f}%</span>'
    return f'<span class="mr-badge-bad">{val:.0f}%</span>'


def render_command_center(data: dict):
    """Top-level dashboard: metric cards + success-rate chart + styled table."""
    st.markdown(_CARD_CSS, unsafe_allow_html=True)

    systems = get_systems(data)
    domains = get_domains(data)
    n_entries = len(data.get("results", []))

    # ── Row 1: Aggregate metric cards ─────────────────────────────────────────
    # Find best system by overall success rate
    rates = {s: _overall_success_rate(data, s) for s in systems}
    best_sys = max(rates, key=rates.get) if rates else None
    best_rate = rates.get(best_sys, 0) if best_sys else 0
    best_label = SYSTEM_LABELS.get(best_sys, best_sys) if best_sys else "—"
    n_sys = len(systems)
    n_dom = len(domains)

    cards_html = '<div class="mr-card-row">'
    cards_html += f'''
    <div class="mr-card">
      <div class="mr-card-label">Best System</div>
      <div class="mr-card-value" style="color:#10b981;font-size:1.2rem;">{best_label}</div>
      <div class="mr-card-sub">{best_rate:.0f}% oracle success</div>
    </div>
    <div class="mr-card">
      <div class="mr-card-label">Systems Compared</div>
      <div class="mr-card-value" style="color:#3b82f6;">{n_sys}</div>
      <div class="mr-card-sub">across {n_dom} domains</div>
    </div>
    <div class="mr-card">
      <div class="mr-card-label">Total Evaluations</div>
      <div class="mr-card-value" style="color:#8b5cf6;">{n_entries}</div>
      <div class="mr-card-sub">problem–system pairs</div>
    </div>'''

    # Per-system best-rate cards (up to 3)
    for sys in list(systems)[:3]:
        r = rates.get(sys, 0)
        col = SYSTEM_COLORS.get(sys, "#64748b")
        lbl = SYSTEM_LABELS.get(sys, sys)
        t = _avg_time(data, sys)
        cards_html += f'''
    <div class="mr-card">
      <div class="mr-card-label">{lbl}</div>
      <div class="mr-card-value" style="color:{col};">{r:.0f}%</div>
      <div class="mr-card-sub">avg {t:.0f}s / problem</div>
    </div>'''

    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Row 2: Plotly grouped bar chart ───────────────────────────────────────
    df = compute_success_table(data)
    chart_df = df[df["Domain"] != "Average"].set_index("Domain")

    fig = go.Figure()
    for i, sys in enumerate(systems):
        label = SYSTEM_LABELS.get(sys, sys)
        color = SYSTEM_COLORS.get(sys, CHART_PALETTE[i % len(CHART_PALETTE)])
        if sys in chart_df.columns:
            fig.add_trace(go.Bar(
                name=label,
                x=chart_df.index.tolist(),
                y=chart_df[sys].tolist(),
                marker_color=color,
                marker_line_color="rgba(0,0,0,0.3)",
                marker_line_width=1,
                opacity=0.9,
                text=[f"{v:.0f}%" if v is not None else "" for v in chart_df[sys].tolist()],
                textposition="outside",
            ))

    fig.update_layout(
        barmode="group",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="#e2e8f0", size=12),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)",
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(
            title="Oracle Success Rate (%)",
            range=[0, 110],
            gridcolor="rgba(255,255,255,0.06)",
            ticksuffix="%",
        ),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        bargap=0.18,
        bargroupgap=0.06,
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Premium success-rate table ────────────────────────────────────
    st.markdown("**Oracle Success Rates**")
    _header_parts = []
    for s in systems:
        _col = SYSTEM_COLORS.get(s, "#94a3b8")
        _lbl = SYSTEM_LABELS.get(s, s)
        _header_parts.append(f'<th style="color:{_col}">{_lbl}</th>')
    header_cells = "<th>Domain</th>" + "".join(_header_parts)
    rows_html = ""
    for _, row in df.iterrows():
        row_cells = f'<td>{row["Domain"]}</td>'
        for sys in systems:
            row_cells += f"<td>{_rate_badge(row.get(sys))}</td>"
        rows_html += f"<tr>{row_cells}</tr>"

    table_html = f"""
    <table class="mr-table">
      <thead><tr>{header_cells}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# ── Problem Inspector ─────────────────────────────────────────────────────────

def render_problem_inspector(data: dict):
    st.subheader("Problem Inspector")
    results = data.get("results", [])
    domains = get_domains(data)
    systems = get_systems(data)

    if not domains:
        st.info("No results available yet.")
        return

    col1, col2 = st.columns(2)
    with col1:
        domain = st.selectbox("Domain", domains, key="inspector_domain")
    with col2:
        domain_entries = [r for r in results if r.get("domain") == domain]
        pids = sorted(set(r["problem_id"] for r in domain_entries if "problem_id" in r))
        pid = st.selectbox("Problem ID", pids, key="inspector_pid") if pids else None

    if pid is None:
        st.info("No problems found for this domain.")
        return

    problem_entries = [r for r in results
                       if r.get("domain") == domain and r.get("problem_id") == pid]
    present_systems = [r["system"] for r in problem_entries if r.get("system") in systems]
    if not present_systems:
        st.info("No results for this problem yet.")
        return

    cols = st.columns(len(present_systems))
    for col, system in zip(cols, present_systems):
        entry = next(r for r in problem_entries if r.get("system") == system)
        with col:
            success = entry.get("success_oracle", False)
            badge = "✅" if success else "❌"
            label = SYSTEM_LABELS.get(system, system)
            color = SYSTEM_COLORS.get(system, "#666")
            st.markdown(f"<h4 style='color:{color}'>{label} {badge}</h4>", unsafe_allow_html=True)

            t = entry.get("time_seconds") or 0
            tokens = entry.get("token_usage") or 0
            iters = entry.get("refinement_iterations") or 0

            st.metric("Time", f"{t:.1f}s")
            if tokens:
                st.metric("Tokens", f"{tokens:,}")
            if iters:
                st.metric("Refinement Iters", iters)
            if entry.get("semantic_score") is not None:
                st.metric("Semantic Score", f"{entry['semantic_score']:.1f}/5")

            if entry.get("generated_domain_pddl"):
                with st.expander("Domain PDDL"):
                    st.code(entry["generated_domain_pddl"], language="lisp")
            if entry.get("generated_problem_pddl"):
                with st.expander("Problem PDDL"):
                    st.code(entry["generated_problem_pddl"], language="lisp")
            plan = entry.get("plan", [])
            if plan:
                with st.expander(f"Plan ({len(plan)} steps)"):
                    st.code("\n".join(plan), language="lisp")
            error = entry.get("error") or entry.get("oracle_error")
            if error:
                with st.expander("Error Details"):
                    st.error(str(error)[:500])


# ── Cost & Time Panel ─────────────────────────────────────────────────────────

def render_cost_panel(data: dict):
    st.subheader("Cost & Time Comparison")
    systems = get_systems(data)
    time_df = compute_time_table(data)

    # Plotly heatmap-style bar chart for time
    fig = go.Figure()
    for sys in systems:
        label = SYSTEM_LABELS.get(sys, sys)
        color = SYSTEM_COLORS.get(sys, "#64748b")
        if sys in time_df.columns:
            fig.add_trace(go.Bar(
                name=label,
                x=time_df["Domain"].tolist(),
                y=time_df[sys].tolist(),
                marker_color=color,
                opacity=0.85,
            ))

    fig.update_layout(
        barmode="group",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#e2e8f0", size=12),
        yaxis=dict(title="Avg time (s)", gridcolor="rgba(255,255,255,0.06)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

    rename = {s: SYSTEM_LABELS.get(s, s) for s in systems}
    st.dataframe(time_df.rename(columns=rename), use_container_width=True, hide_index=True)


# ── Top-level Entry Point ─────────────────────────────────────────────────────

def render_model_race_page(results_path: str):
    st.title("⚡ Model Race — Benchmark Dashboard")

    if not Path(results_path).exists():
        st.warning(f"Results file not found: `{results_path}`")
        st.info(
            "Run the benchmark first:\n"
            "```bash\n"
            "python scripts/run_full_comparison.py \\\n"
            "    --systems direct_llm llmpp lapis_c lapis_d\n"
            "```"
        )
        if st.button("Create mock data for development"):
            _create_mock_results(results_path)
            st.success(f"Mock data created at `{results_path}`")
            st.rerun()
        return

    data = load_results(results_path)
    n_results = len(data.get("results", []))
    n_systems = len(get_systems(data))
    n_domains = len(get_domains(data))
    st.caption(f"📊 {n_results} evaluations · {n_systems} systems · {n_domains} domains")

    tab1, tab2, tab3 = st.tabs([
        "🏆 Dashboard",
        "🔍 Problem Inspector",
        "⏱ Cost & Time",
    ])

    with tab1:
        render_command_center(data)
    with tab2:
        render_problem_inspector(data)
    with tab3:
        render_cost_panel(data)


# ── Mock Data Helper ──────────────────────────────────────────────────────────

def _create_mock_results(path: str):
    import random
    random.seed(42)
    domains = ["blocksworld", "barman", "storage", "termes", "grippers", "floortile", "tyreworld"]
    systems = ["direct_llm", "llmpp", "lapis_c", "lapis_d"]
    base_rates = {"direct_llm": 0.30, "llmpp": 0.75, "lapis_c": 0.82, "lapis_d": 0.93}
    results = []
    for domain in domains:
        for system in systems:
            for pid in range(1, 6):
                rate = base_rates[system]
                success = random.random() < rate
                results.append({
                    "system": system, "domain": domain, "problem_id": pid,
                    "llm_model": "claude-sonnet-4-6",
                    "success_oracle": success, "success_internal": success,
                    "time_seconds": round(random.uniform(2, 60), 1),
                    "token_usage": random.randint(1000, 15000),
                    "refinement_iterations": random.randint(0, 3),
                    "plan": ["(action-1 a b)", "(action-2 c)"] if success else [],
                    "error": None if success else "Planning failed",
                })
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump({"meta": {"mock": True}, "results": results}, f, indent=2)
