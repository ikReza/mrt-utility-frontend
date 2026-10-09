import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Palette aligned with the dark sci-fi route map
INK = "#e9f6ff"
INK_MUTED = "#7b86b8"
GRID = "rgba(0,240,255,0.10)"
AXIS = "rgba(0,240,255,0.25)"
BASELINE = "rgba(233,246,255,0.06)"
FONT_FAMILY = "'JetBrains Mono', 'Segoe UI', Arial, sans-serif"
TITLE_FONT = "Orbitron, " + FONT_FAMILY
HOVER_BG = "#0b1126"
HOVER_BORDER = "#00f0ff"

# Trend line: near-white dashed — deliberately NOT in the package palette,
# so it can never be mistaken for a CP line.
TREND_COLOR = "#ff6a00"
TREND_DASH = "dash"
TREND_WIDTH = 1.8

# Neon categorical palette matching the route map (no white/near-white entries,
# so the trend line always stays visually distinct)
PACKAGE_COLORS = [
    "#00f0ff",  # cyan
    "#ff2e9a",  # magenta
    "#ffcc33",  # amber
    "#2bff88",  # green
    "#8f7bff",  # violet
    "#38bdf8",  # sky
    "#ff6b9e",  # rose
    "#a3ff6b",  # lime
]


def generate_plotly_chart(df):
    df = df.copy()
    df["Work Progress"] = df["Work Progress"].apply(lambda x: x*100)
    df["Work Status (%)"] = df["Work Progress"].apply(lambda x: f"{x:.1f}%")
    df["Baseline Progress"] = df["Baseline Progress"].apply(lambda x: x*100)

    contract_packages = df["Contract Package"].unique()
    color_map = {cp: PACKAGE_COLORS[i % len(PACKAGE_COLORS)] for i, cp in enumerate(contract_packages)}

    fig = go.Figure()

    # 1) baseline track (behind everything)
    fig.add_trace(go.Bar(
        y=df["Station Name"], x=df["Baseline Progress"], orientation='h',
        name='Baseline', marker_color=BASELINE, marker_line_width=0,
        width=0.7, hoverinfo='skip'
    ))

    # 2) trend line — drawn BEFORE the package bars so bars and their
    #    percentage labels always sit on top of it (it can never hide the text).
    #    Thin white dashed, no markers → distinct from every CP color.
    fig.add_trace(go.Scatter(
        x=df["Work Progress"], y=df["Station Name"], mode='lines',
        name='Progress Trend',
        line=dict(color=TREND_COLOR, width=TREND_WIDTH, dash=TREND_DASH),
        hoverinfo='skip'
    ))

    # 3) package bars (drawn last → on top of the trend line)
    for cp in contract_packages:
        subset = df[df["Contract Package"] == cp]
        fig.add_trace(go.Bar(
            y=subset["Station Name"], x=subset["Work Progress"], orientation='h', name=cp,
            marker_color=color_map[cp], marker_line_width=0, width=0.5,
            text=subset["Work Status (%)"], textposition='outside',
            cliponaxis=False,
            textfont=dict(size=12, color=INK, family=FONT_FAMILY),
            hovertemplate='<b>%{y}</b><br>Progress: %{x:.1f}%<br>Package: ' + cp + '<extra></extra>'
        ))

    fig.update_layout(
        title=dict(text="Utility Relocation Progress by Station", x=0, xanchor='left',
                    font=dict(size=15, color=INK, family=TITLE_FONT)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY, size=12, color=INK_MUTED),
        dragmode=False,                       # ← disables drag zoom/pan
        xaxis=dict(
            title=dict(text="Work Progress (%)", font=dict(size=12, color=INK_MUTED, family=FONT_FAMILY)),
            range=[0, 115], showgrid=True, gridcolor=GRID, griddash='dot', zeroline=False,
            tickfont=dict(size=11, color=INK_MUTED, family=FONT_FAMILY),
            linecolor=AXIS, showline=True,
            fixedrange=True,                  # ← no zoom/pan on this axis
        ),
        yaxis=dict(
            title=None, showgrid=False,
            tickfont=dict(size=12, color=INK, family=FONT_FAMILY),
            linecolor=AXIS, showline=True,
            fixedrange=True,                  # ← no zoom/pan on this axis
        ),
        barmode='overlay',
        legend=dict(
            orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,
            font=dict(size=11, color=INK_MUTED, family=FONT_FAMILY),
            bgcolor='rgba(0,0,0,0)', borderwidth=0,
        ),
        height=750,
        margin=dict(l=20, r=170, t=70, b=50),
        hoverlabel=dict(bgcolor=HOVER_BG, bordercolor=HOVER_BORDER,
                        font=dict(family=FONT_FAMILY, color=INK)),
    )
    return fig


def generate_station_corridor_plotly(df, station_name):
    df = df.copy()

    df['Completed'] = pd.to_numeric(df['Completed'], errors='coerce')
    df['Length'] = pd.to_numeric(df['Length'], errors='coerce')
    df['Overall Progress'] = pd.to_numeric(df['Overall Progress'], errors='coerce')

    df['Progress'] = df.apply(lambda row: (row['Completed'] / row['Length']) if row['Length'] > 0 else 0, axis=1)

    west_df = df[df['Corridor'] == 'West'].reset_index(drop=True)
    east_df = df[df['Corridor'] == 'East'].reset_index(drop=True)

    try:
        west_overall = west_df['Overall Progress'].dropna().values[0]
    except IndexError:
        west_overall = 0

    try:
        east_overall = east_df['Overall Progress'].dropna().values[0]
    except IndexError:
        east_overall = 0

    total_completed = df['Completed'].sum()
    total_length = df['Length'].sum()
    whole_progress = (total_completed / total_length) if total_length > 0 else 0

    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
        subplot_titles=("<b>WEST CORRIDOR</b>", "<b>EAST CORRIDOR</b>")
    )

    # West Corridor Bars (cyan gradient)
    if not west_df.empty:
        fig.add_trace(go.Bar(
            x=west_df['Item'],
            y=west_df['Progress'] * 100,
            marker=dict(color=west_df['Progress'] * 100,
                        colorscale=[[0, '#0e2a3a'], [1, '#00f0ff']], showscale=False),
            marker_line_width=0,
            width=0.62,
            text=[f"{v*100:.1f}%" for v in west_df['Progress']],
            textposition='outside',
            cliponaxis=False,
            textfont=dict(family=FONT_FAMILY, size=11, color=INK),
            hovertemplate='<b>%{x}</b><br>Progress: %{y:.1f}%<extra></extra>',
            name='West'
        ), row=1, col=1)

    # East Corridor Bars (magenta gradient)
    if not east_df.empty:
        fig.add_trace(go.Bar(
            x=east_df['Item'],
            y=east_df['Progress'] * 100,
            marker=dict(color=east_df['Progress'] * 100,
                        colorscale=[[0, '#3a0e28'], [1, '#ff2e9a']], showscale=False),
            marker_line_width=0,
            width=0.62,
            text=[f"{v*100:.1f}%" for v in east_df['Progress']],
            textposition='outside',
            cliponaxis=False,
            textfont=dict(family=FONT_FAMILY, size=11, color=INK),
            hovertemplate='<b>%{x}</b><br>Progress: %{y:.1f}%<extra></extra>',
            name='East'
        ), row=1, col=2)

    fig.add_hline(
        y=west_overall * 100,
        line_dash="dash", line_color="#ffcc33", line_width=2,
        row=1, col=1,
        annotation_text=f"Overall {west_overall*100:.1f}%",
        annotation_position="top right",
        annotation_font_color="#ffcc33",
        annotation_font_size=12,
        annotation_font_family="JetBrains Mono, sans-serif",
        annotation=dict(yshift=10)
    )

    fig.add_hline(
        y=east_overall * 100,
        line_dash="dash", line_color="#ffcc33", line_width=2,
        row=1, col=2,
        annotation_text=f"Overall {east_overall*100:.1f}%",
        annotation_position="top right",
        annotation_font_color="#ffcc33",
        annotation_font_size=12,
        annotation_font_family="JetBrains Mono, sans-serif",
        annotation=dict(yshift=10)
    )

    fig.update_layout(
        title=dict(text=f"{station_name} &nbsp;·&nbsp; Overall Progress {whole_progress*100:.1f}%",
                    x=0.4, xanchor='left',
                    font=dict(size=18, color=INK, family=TITLE_FONT)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY, size=12, color=INK_MUTED),
        showlegend=False,
        height=600,
        margin=dict(t=90, b=120),
        hoverlabel=dict(bgcolor=HOVER_BG, bordercolor=HOVER_BORDER,
                        font=dict(family=FONT_FAMILY, color=INK)),
    )

    fig.update_annotations(font=dict(family=TITLE_FONT, size=13, color=INK))
    fig.update_yaxes(
        title=dict(text="Progress (%)", font=dict(size=12, color=INK_MUTED, family=FONT_FAMILY)),
        range=[0, 115], gridcolor=GRID, tickfont=dict(size=11, color=INK_MUTED, family=FONT_FAMILY),
        linecolor=AXIS, showline=True, row=1, col=1,
    )
    fig.update_yaxes(
        range=[0, 115], gridcolor=GRID, tickfont=dict(size=11, color=INK_MUTED, family=FONT_FAMILY),
        linecolor=AXIS, showline=True, row=1, col=2,
    )
    fig.update_xaxes(
        tickangle=-40, tickfont=dict(size=12, color=INK_MUTED, family=FONT_FAMILY),
        linecolor=AXIS, showline=True,
    )

    return fig