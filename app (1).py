import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="U Learns App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700&family=Barlow+Condensed:wght@500;700&display=swap');
html, body, [class*=css] {
    font-family: Barlow, sans-serif;
    background-color: #0d1b2a !important;
    color: #e0e8f0 !important;
}
.stApp { background-color: #0d1b2a !important; }
section[data-testid=stSidebar] {
    background-color: #0a1520 !important;
    border-right: 1px solid #1e3a5f;
}
section[data-testid=stSidebar] * { color: #a0c4e0 !important; }
.dash-header {
    background: linear-gradient(90deg, #0f2d4a 0%, #1a4a7a 50%, #0f2d4a 100%);
    border-bottom: 2px solid #1e6eb5;
    padding: 1rem 2rem;
    border-radius: 8px;
    margin-bottom: 1.2rem;
}
.dash-header h1 {
    font-family: Barlow Condensed, sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 0 !important;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.dash-header .sub {
    font-size: 12px;
    color: #7ab3d4;
    text-transform: uppercase;
    letter-spacing: .1em;
    margin-top: 3px;
}
.kpi-card {
    background: #0f2d4a;
    border: 1px solid #1e5080;
    border-left: 4px solid #1e90ff;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: .8rem;
}
.kpi-card.green  { border-left-color: #00c896; }
.kpi-card.orange { border-left-color: #ff8c00; }
.kpi-card.red    { border-left-color: #ff4560; }
.kpi-card.purple { border-left-color: #b44bff; }
.kpi-card.cyan   { border-left-color: #00d4ff; }
.kpi-card-label {
    font-size: 10px; color: #7ab3d4; font-weight: 600;
    text-transform: uppercase; letter-spacing: .1em; margin-bottom: 4px;
}
.kpi-card-value {
    font-family: Barlow Condensed, sans-serif;
    font-size: 2.2rem; font-weight: 700; color: #ffffff; line-height: 1;
}
.kpi-card-sub { font-size: 11px; color: #7ab3d4; margin-top: 4px; }
.kpi-up   { color: #00c896 !important; }
.kpi-down { color: #ff4560 !important; }
.chart-title {
    font-family: Barlow Condensed, sans-serif;
    font-size: 13px; font-weight: 600; color: #7ab3d4;
    text-transform: uppercase; letter-spacing: .08em;
    margin-bottom: .5rem;
    border-bottom: 1px solid #1e4070;
    padding-bottom: .4rem;
}
.info-box {
    background: #0a2540; border: 1px solid #1e6eb5;
    border-radius: 6px; padding: .6rem 1rem;
    font-size: 12px; color: #7ab3d4; margin-bottom: 1rem;
}
.stTabs [data-baseweb=tab-list] {
    background: #0a1e35; border-radius: 6px; padding: 4px; gap: 4px;
}
.stTabs [data-baseweb=tab] {
    font-family: Barlow Condensed, sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important;
    text-transform: uppercase !important; color: #7ab3d4 !important;
    border-radius: 4px !important; padding: 6px 16px !important;
}
.stTabs [aria-selected=true] {
    background: #1a5080 !important; color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────
DARK_BG  = "#0f2440"
GRID_COL = "#1e4070"
TEXT_COL = "#a0c4e0"
ACCENT   = ["#1e90ff","#00c896","#ff8c00","#ff4560","#b44bff",
            "#00d4ff","#ffd700","#ff6ec7","#7fff00","#ff6347"]
COLORS   = ["green","cyan","orange","red","purple","green","cyan"]

# ── Helpers ───────────────────────────────────────────────────
def fmt(v):
    try:
        v = float(v)
        if abs(v) >= 1e6: return f"{v/1e6:.1f}M"
        if abs(v) >= 1e3: return f"{v/1e3:.1f}K"
        return f"{v:,.1f}" if v != int(v) else f"{int(v):,}"
    except:
        return str(v)

def pct_change(s):
    s = s.dropna()
    if len(s) < 2: return 0
    a, b = float(s.iloc[0]), float(s.iloc[-1])
    return round((b - a) / abs(a) * 100, 1) if a != 0 else 0

def dark_layout(fig, h=320):
    fig.update_layout(
        plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG,
        font=dict(family="Barlow, sans-serif", color=TEXT_COL, size=11),
        margin=dict(t=20, b=15, l=10, r=10), height=h,
        legend=dict(font=dict(size=10, color=TEXT_COL), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, tickfont=dict(color=TEXT_COL)),
        yaxis=dict(gridcolor=GRID_COL, linecolor=GRID_COL, tickfont=dict(color=TEXT_COL)),
    )
    return fig

@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <h1>📊 U Learns App</h1>
  <div class="sub">Excel &amp; CSV Dashboard Analyzer</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📁 Upload File")
    uploaded = st.file_uploader(
        "Drop Excel or CSV here",
        type=["xlsx", "xls", "csv"]
    )
    st.markdown("---")
    st.markdown("**How to use**")
    st.markdown("1. Upload any Excel or CSV file\n2. Dashboard builds instantly\n3. Explore tabs for charts & data")
    st.markdown("---")
    st.markdown("**U Learns App**")
    st.caption("Powered by Streamlit + Plotly")

# ── No file state ─────────────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem;background:#0f2440;
                border:2px dashed #1e4070;border-radius:10px;margin-top:1rem;">
        <div style="font-size:5rem;">📂</div>
        <h2 style="font-family:Barlow Condensed,sans-serif;color:#fff;
                   font-size:1.8rem;margin:.8rem 0 .4rem;">
            Upload your spreadsheet from the sidebar</h2>
        <p style="color:#7ab3d4;font-size:14px;">
            Supports Excel (.xlsx, .xls) and CSV files<br>
            Dashboard builds automatically from your data</p>
        <div style="display:flex;justify-content:center;gap:10px;margin-top:1.2rem;">
            <span style="background:#0a2540;border:1px solid #1e4070;
                         padding:5px 14px;border-radius:20px;font-size:12px;color:#1e90ff">.xlsx</span>
            <span style="background:#0a2540;border:1px solid #1e4070;
                         padding:5px 14px;border-radius:20px;font-size:12px;color:#00c896">.xls</span>
            <span style="background:#0a2540;border:1px solid #1e4070;
                         padding:5px 14px;border-radius:20px;font-size:12px;color:#ff8c00">.csv</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load ──────────────────────────────────────────────────────
df       = load_data(uploaded)
num_cols = df.select_dtypes(include="number").columns.tolist()
txt_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

st.markdown(
    f'<div class="info-box">'
    f'✅ &nbsp;<strong style="color:#fff">{uploaded.name}</strong>&nbsp; loaded — '
    f'<strong style="color:#1e90ff">{len(df):,}</strong> rows · '
    f'<strong style="color:#1e90ff">{len(df.columns)}</strong> columns · '
    f'<span style="color:#00c896">{len(num_cols)} numeric</span> · '
    f'<span style="color:#ff8c00">{len(txt_cols)} text</span>'
    f'</div>',
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠  OVERVIEW", "📈  CHARTS", "🔍  DATA TABLE", "📊  CORRELATIONS"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab1:

    # KPI Cards
    kpi_cols = num_cols[:6]
    if kpi_cols:
        kcols = st.columns(len(kpi_cols))
        for i, col in enumerate(kpi_cols):
            s     = df[col].dropna()
            chg   = pct_change(s)
            arrow = "▲" if chg >= 0 else "▼"
            cls   = "kpi-up" if chg >= 0 else "kpi-down"
            color = COLORS[i % len(COLORS)]
            with kcols[i]:
                st.markdown(
                    f'<div class="kpi-card {color}">'
                    f'<div class="kpi-card-label">{col}</div>'
                    f'<div class="kpi-card-value">{fmt(s.sum())}</div>'
                    f'<div class="kpi-card-sub">avg {fmt(s.mean())}'
                    f'&nbsp;<span class="{cls}">{arrow} {abs(chg)}%</span></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    # Gauges
    if num_cols:
        st.markdown(
            '<div class="chart-title" style="margin-top:.8rem">KEY METRICS — GAUGE VIEW</div>',
            unsafe_allow_html=True
        )
        gauge_colors = ["#1e90ff", "#00c896", "#ff8c00", "#ff4560"]
        gcols = st.columns(min(4, len(num_cols)))
        for i, col in enumerate(num_cols[:4]):
            s  = df[col].dropna()
            mn, mx = float(s.min()), float(s.max())
            val    = float(s.mean())
            with gcols[i]:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=round(val, 1),
                    delta={
                        "reference": round(float(s.median()), 1),
                        "increasing": {"color": "#00c896"},
                        "decreasing": {"color": "#ff4560"},
                        "font": {"size": 11}
                    },
                    title={"text": col[:16], "font": {"size": 11, "color": "#7ab3d4"}},
                    number={"font": {"size": 20, "color": "#ffffff",
                                     "family": "Barlow Condensed"}},
                    gauge={
                        "axis": {
                            "range": [mn, mx], "tickwidth": 1,
                            "tickcolor": "#1e4070",
                            "tickfont": {"size": 9, "color": "#a0c4e0"}
                        },
                        "bar": {"color": gauge_colors[i], "thickness": 0.25},
                        "bgcolor": "#0a1e35",
                        "borderwidth": 1, "bordercolor": "#1e4070",
                        "steps": [
                            {"range": [mn, mn+(mx-mn)*0.33], "color": "#0a2540"},
                            {"range": [mn+(mx-mn)*0.33, mn+(mx-mn)*0.66], "color": "#0d2e50"},
                            {"range": [mn+(mx-mn)*0.66, mx], "color": "#0f3660"},
                        ],
                        "threshold": {
                            "line": {"color": "#ffffff", "width": 2},
                            "thickness": 0.8,
                            "value": round(float(s.quantile(0.75)), 1)
                        }
                    }
                ))
                fig.update_layout(
                    paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
                    margin=dict(t=30, b=10, l=20, r=20),
                    height=200, font=dict(color=TEXT_COL)
                )
                st.plotly_chart(fig, use_container_width=True)

    # Bar + Pie + Area
    c1, c2, c3 = st.columns([2, 1, 2])

    with c1:
        st.markdown('<div class="chart-title">COLUMN AVERAGES</div>', unsafe_allow_html=True)
        if num_cols:
            avgs = df[num_cols[:8]].mean().reset_index()
            avgs.columns = ["Column", "Value"]
            fig = px.bar(avgs, x="Column", y="Value", color="Column",
                         color_discrete_sequence=ACCENT)
            fig.update_traces(marker_line_width=0)
            fig = dark_layout(fig, 260)
            fig.update_layout(showlegend=False, xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns.")

    with c2:
        st.markdown('<div class="chart-title">DISTRIBUTION</div>', unsafe_allow_html=True)
        if txt_cols:
            vc  = df[txt_cols[0]].value_counts().head(6)
            fig = px.pie(values=vc.values, names=vc.index,
                         color_discrete_sequence=ACCENT, hole=0.55)
            fig.update_traces(
                textposition="inside", textinfo="percent",
                textfont_size=10,
                marker=dict(line=dict(color=DARK_BG, width=2))
            )
            fig.update_layout(
                paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
                margin=dict(t=10, b=10, l=0, r=0), height=260,
                legend=dict(font=dict(size=9, color=TEXT_COL), bgcolor="rgba(0,0,0,0)"),
                font=dict(color=TEXT_COL)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No text columns.")

    with c3:
        st.markdown('<div class="chart-title">TREND OVER TIME</div>', unsafe_allow_html=True)
        if num_cols:
            step  = max(1, len(df) // 60)
            col0  = num_cols[0]
            trend = df[col0].iloc[::step].reset_index()
            trend.columns = ["Index", col0]
            fig = px.area(trend, x="Index", y=col0,
                          color_discrete_sequence=["#1e90ff"])
            fig.update_traces(
                fill="tozeroy",
                fillcolor="rgba(30,144,255,0.15)",
                line=dict(color="#1e90ff", width=2)
            )
            fig = dark_layout(fig, 260)
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — CHARTS
# ══════════════════════════════════════════════════════════════
with tab2:
    all_cols = num_cols + txt_cols
    if all_cols:
        c1, c2 = st.columns([2, 1])
        with c1:
            sel_col = st.selectbox("Select column to explore", all_cols)
        is_num = sel_col in num_cols
        with c2:
            if is_num:
                ctype = st.radio("Chart type",
                                 ["Histogram", "Box", "Bar", "Violin"],
                                 horizontal=True)
            else:
                ctype = st.radio("Chart type",
                                 ["Bar (freq)", "Pie", "Treemap"],
                                 horizontal=True)

        fig = None
        if is_num:
            if ctype == "Histogram":
                fig = px.histogram(df, x=sel_col, nbins=30,
                                   color_discrete_sequence=["#1e90ff"])
                fig = dark_layout(fig, 400)
            elif ctype == "Box":
                fig = px.box(df, y=sel_col,
                             color_discrete_sequence=["#00c896"])
                fig = dark_layout(fig, 400)
            elif ctype == "Bar":
                step = max(1, len(df) // 60)
                fig = px.bar(df.iloc[::step].head(60), y=sel_col,
                             color_discrete_sequence=["#1e90ff"])
                fig.update_traces(marker_line_width=0)
                fig = dark_layout(fig, 400)
            elif ctype == "Violin":
                fig = px.violin(df, y=sel_col, box=True,
                                color_discrete_sequence=["#b44bff"])
                fig = dark_layout(fig, 400)
        else:
            vc = df[sel_col].value_counts().head(20).reset_index()
            vc.columns = [sel_col, "Count"]
            if ctype == "Bar (freq)":
                fig = px.bar(vc, x="Count", y=sel_col, orientation="h",
                             color=sel_col, color_discrete_sequence=ACCENT)
                fig.update_layout(showlegend=False)
                fig = dark_layout(fig, max(300, len(vc) * 35))
            elif ctype == "Pie":
                fig = px.pie(vc, values="Count", names=sel_col,
                             color_discrete_sequence=ACCENT, hole=0.45)
                fig.update_traces(
                    marker=dict(line=dict(color=DARK_BG, width=2)))
                fig.update_layout(
                    paper_bgcolor=DARK_BG, height=400,
                    font=dict(color=TEXT_COL),
                    margin=dict(t=20, b=20, l=20, r=20)
                )
            elif ctype == "Treemap":
                fig = px.treemap(vc, path=[sel_col], values="Count",
                                 color_discrete_sequence=ACCENT)
                fig.update_layout(
                    paper_bgcolor=DARK_BG, height=400,
                    font=dict(color=TEXT_COL),
                    margin=dict(t=20, b=20, l=20, r=20)
                )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No columns available.")

    # Scatter
    if len(num_cols) >= 2:
        st.markdown("---")
        st.markdown('<div class="chart-title">SCATTER ANALYSIS</div>',
                    unsafe_allow_html=True)
        cx, cy, cz = st.columns(3)
        with cx: xcol     = st.selectbox("X axis", num_cols, key="sx")
        with cy: ycol     = st.selectbox("Y axis", num_cols,
                                          index=min(1, len(num_cols)-1), key="sy")
        with cz: color_by = st.selectbox("Color by", ["None"] + txt_cols, key="sc")
        fig = px.scatter(
            df, x=xcol, y=ycol,
            color=None if color_by == "None" else color_by,
            color_discrete_sequence=ACCENT, opacity=0.75
        )
        fig = dark_layout(fig, 400)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — DATA TABLE
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="chart-title">SEARCH &amp; FILTER</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        search = st.text_input("Search", placeholder="Filter any column…")
    with c2:
        page_size = st.selectbox("Rows/page", [10, 25, 50, 100], index=1)
    with c3:
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        st.download_button(
            "⬇ Export CSV", data=buf.getvalue(),
            file_name="ulearns_export.csv", mime="text/csv"
        )

    active_filters = {}
    if txt_cols:
        fcols = st.columns(min(3, len(txt_cols)))
        for i, col in enumerate(txt_cols[:3]):
            with fcols[i]:
                opts = ["All"] + sorted(
                    df[col].dropna().astype(str).unique())[:60]
                sel = st.selectbox(col, opts, key=f"f_{col}")
                if sel != "All":
                    active_filters[col] = sel

    filtered = df.copy()
    if search:
        mask = filtered.apply(
            lambda r: r.astype(str).str.contains(
                search, case=False, na=False).any(), axis=1)
        filtered = filtered[mask]
    for col, val in active_filters.items():
        filtered = filtered[filtered[col].astype(str) == val]

    total_pages = max(1, -(-len(filtered) // page_size))
    page = st.number_input("Page", min_value=1,
                            max_value=total_pages, value=1)
    st.markdown(
        f'<div class="info-box">'
        f'<strong style="color:#fff">{len(filtered):,}</strong> rows · '
        f'page {page} / {total_pages}'
        f'</div>',
        unsafe_allow_html=True
    )
    st.dataframe(
        filtered.iloc[(page-1)*page_size : page*page_size],
        use_container_width=True, height=440
    )

# ══════════════════════════════════════════════════════════════
# TAB 4 — CORRELATIONS
# ══════════════════════════════════════════════════════════════
with tab4:
    if len(num_cols) >= 2:
        st.markdown('<div class="chart-title">CORRELATION HEATMAP</div>',
                    unsafe_allow_html=True)
        corr = df[num_cols].corr()
        fig  = px.imshow(corr, text_auto=".2f", aspect="auto",
                          color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        fig.update_layout(
            paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
            font=dict(color=TEXT_COL, size=11),
            margin=dict(t=20, b=20, l=20, r=20), height=480,
            coloraxis_colorbar=dict(tickfont=dict(color=TEXT_COL))
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="chart-title">TOP CORRELATIONS</div>',
                    unsafe_allow_html=True)
        pairs = [
            {"Column A": corr.columns[i],
             "Column B": corr.columns[j],
             "Correlation": round(corr.iloc[i, j], 4)}
            for i in range(len(corr.columns))
            for j in range(i+1, len(corr.columns))
        ]
        st.dataframe(
            pd.DataFrame(pairs)
            .sort_values("Correlation", key=abs, ascending=False)
            .head(15),
            use_container_width=True
        )

        st.markdown('<div class="chart-title">MULTI-COLUMN COMPARISON</div>',
                    unsafe_allow_html=True)
        compare_cols = st.multiselect(
            "Select columns to compare", num_cols,
            default=num_cols[:min(4, len(num_cols))]
        )
        if compare_cols:
            step    = max(1, len(df) // 50)
            comp_df = df[compare_cols].iloc[::step].reset_index(drop=True)
            fig     = px.line(comp_df, color_discrete_sequence=ACCENT)
            fig     = dark_layout(fig, 340)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 2 numeric columns for correlation analysis.")
