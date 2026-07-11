import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Palette aligned with utils/ui.py design tokens
INK = "#12142b"
INK_MUTED = "#5c6079"
GRID = "#e7e9f3"
BASELINE = "rgba(18, 20, 43, 0.12)"
TREND_LINE = "rgba(91, 91, 246, 0.55)"
FONT_FAMILY = "Inter, 'Segoe UI', Arial, sans-serif"

# Modern, cohesive categorical palette (replaces harsh ColorBrewer Set1)
PACKAGE_COLORS = [
    "#5b5bf6",  # indigo
    "#12c2a9",  # teal
    "#f5a623",  # amber
    "#ef4a5f",  # coral
    "#8a5bf6",  # violet
    "#2fb6d9",  # sky
    "#e0509a",  # pink
    "#6bbf59",  # green
]

def generate_plotly_chart(df):
    df = df.copy()
    df["Work Progress"] = df["Work Progress"].apply(lambda x: x*100)
    df["Work Status (%)"] = df["Work Progress"].apply(lambda x: f"{x:.1f}%")
    df["Baseline Progress"] = df["Baseline Progress"].apply(lambda x: x*100)

    contract_packages = df["Contract Package"].unique()
    color_map = {cp: PACKAGE_COLORS[i % len(PACKAGE_COLORS)] for i, cp in enumerate(contract_packages)}

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Station Name"], x=df["Baseline Progress"], orientation='h',
        name='Baseline', marker_color=BASELINE, marker_line_width=0,
        width=0.7, hoverinfo='skip'
    ))

    for cp in contract_packages:
        subset = df[df["Contract Package"] == cp]
        fig.add_trace(go.Bar(
            y=subset["Station Name"], x=subset["Work Progress"], orientation='h', name=cp,
            marker_color=color_map[cp], marker_line_width=0, width=0.5,
            text=subset["Work Status (%)"], textposition='outside',
            textfont=dict(size=12, color=INK, family=FONT_FAMILY),
            hovertemplate='<b>%{y}</b><br>Progress: %{x:.1f}%<br>Package: ' + cp + '<extra></extra>'
        ))

    fig.add_trace(go.Scatter(
        x=df["Work Progress"], y=df["Station Name"], mode='lines+markers', name='Progress Trend',
        line=dict(color=TREND_LINE, width=2),
        marker=dict(size=7, color=TREND_LINE, symbol='circle'),
        hoverinfo='skip'
    ))

    fig.update_layout(
        title=dict(text="Utility Relocation Progress by Station", x=0.25, xanchor='left',
                    font=dict(size=17, color=INK, family="Space Grotesk, " + FONT_FAMILY)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY, size=12, color=INK_MUTED),
        xaxis=dict(
            title=dict(text="Work Progress (%)", font=dict(size=12, color=INK_MUTED, family=FONT_FAMILY)),
            range=[0, 115], showgrid=True, gridcolor=GRID, griddash='dot', zeroline=False,
            tickfont=dict(size=11, color=INK_MUTED, family=FONT_FAMILY),
            linecolor=GRID, showline=True,
        ),
        yaxis=dict(
            title=None, showgrid=False,
            tickfont=dict(size=12, color=INK, family=FONT_FAMILY),
            linecolor=GRID, showline=True,
        ),
        barmode='overlay',
        legend=dict(
            orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,
            font=dict(size=11, color=INK, family=FONT_FAMILY),
            bgcolor='rgba(0,0,0,0)', borderwidth=0,
        ),
        height=750,
        margin=dict(l=20, r=170, t=70, b=50),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT_FAMILY, color=INK)),
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
    
    # Calculate Whole Progress for the Title
    total_completed = df['Completed'].sum()
    total_length = df['Length'].sum()
    whole_progress = (total_completed / total_length) if total_length > 0 else 0
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
        subplot_titles=("<b>WEST CORRIDOR</b>", "<b>EAST CORRIDOR</b>")
    )
    
    # West Corridor Bars (Blue Gradient)
    if not west_df.empty:
        fig.add_trace(go.Bar(
            x=west_df['Item'],
            y=west_df['Progress'] * 100,
            marker=dict(color=west_df['Progress'] * 100,
                        colorscale=[[0, '#c7d2ff'], [1, '#5b5bf6']], showscale=False),
            marker_line_width=0,
            width=0.62,
            text=[f"{v*100:.1f}%" for v in west_df['Progress']],
            textposition='outside',
            textfont=dict(family=FONT_FAMILY, size=11, color=INK),
            hovertemplate='<b>%{x}</b><br>Progress: %{y:.1f}%<extra></extra>',
            name='West'
        ), row=1, col=1)
        
    # East Corridor Bars (Orange/Red Gradient)
    if not east_df.empty:
        fig.add_trace(go.Bar(
            x=east_df['Item'],
            y=east_df['Progress'] * 100,
            marker=dict(color=east_df['Progress'] * 100,
                        colorscale=[[0, '#aeeee3'], [1, '#12c2a9']], showscale=False),
            marker_line_width=0,
            width=0.62,
            text=[f"{v*100:.1f}%" for v in east_df['Progress']],
            textposition='outside',
            textfont=dict(family=FONT_FAMILY, size=11, color=INK),
            hovertemplate='<b>%{x}</b><br>Progress: %{y:.1f}%<extra></extra>',
            name='East'
        ), row=1, col=2)

    # Add Individual Overall Progress Line & Text for West (Col 1)
    fig.add_hline(
        y=west_overall * 100,
        line_dash="dash", line_color="#f5a623", line_width=2,
        row=1, col=1,
        annotation_text=f"Overall {west_overall*100:.1f}%",
        annotation_position="top right",
        annotation_font_color="#c9821a",
        annotation_font_size=12,
        annotation_font_family="Inter, sans-serif",
        annotation=dict(yshift=10)
    )

    # Add Individual Overall Progress Line & Text for East (Col 2)
    fig.add_hline(
        y=east_overall * 100,
        line_dash="dash", line_color="#f5a623", line_width=2,
        row=1, col=2,
        annotation_text=f"Overall {east_overall*100:.1f}%",
        annotation_position="top right",
        annotation_font_color="#c9821a",
        annotation_font_size=12,
        annotation_font_family="Inter, sans-serif",
        annotation=dict(yshift=10)
    )

    fig.update_layout(
        title=dict(text=f"{station_name} &nbsp;·&nbsp; Overall Progress {whole_progress*100:.1f}%",
                    x=0.4, xanchor='left',
                    font=dict(size=20, color='#e3342f', family="Space Grotesk, " + FONT_FAMILY)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT_FAMILY, size=12, color=INK_MUTED),
        showlegend=False,
        height=600,
        margin=dict(t=90, b=120),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT_FAMILY, color=INK)),
    )
    
    
    fig.update_annotations(font=dict(family="Space Grotesk, " + FONT_FAMILY, size=13, color=INK))
    fig.update_yaxes(
        title=dict(text="Progress (%)", font=dict(size=12, color=INK_MUTED, family=FONT_FAMILY)),
        range=[0, 115], gridcolor=GRID, tickfont=dict(size=11, color=INK_MUTED, family=FONT_FAMILY),
        linecolor=GRID, showline=True, row=1, col=1,
    )
    fig.update_yaxes(
        range=[0, 115], gridcolor=GRID, tickfont=dict(size=11, color=INK_MUTED, family=FONT_FAMILY),
        linecolor=GRID, showline=True, row=1, col=2,
    )
    fig.update_xaxes(
        tickangle=-40, tickfont=dict(size=12, color=INK_MUTED, family=FONT_FAMILY),
        linecolor=GRID, showline=True,
    )

    return fig