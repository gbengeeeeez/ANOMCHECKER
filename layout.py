# =============================================================
# ANOMCHECKER — layout.py
# All UI components and page structure.
# Imports COLORS from visualizations to keep styles consistent.
# =============================================================

from dash import dcc, html
import dash_bootstrap_components as dbc
from visualizations import COLORS


# ── Reusable style helpers ────────────────────────────────────

def _card(children, border_color=None, extra_style=None):
    """Consistent dark card wrapper."""
    style = {
        "background": COLORS["card_bg"],
        "borderRadius": "12px",
        "padding": "20px",
        "border": f'1px solid {border_color or "rgba(0,212,255,0.12)"}',
        **(extra_style or {}),
    }
    return html.Div(style=style, children=children)


def _section_divider(label: str):
    """Horizontal rule with a floating label — used between result sections."""
    return html.Div(style={"position": "relative", "margin": "8px 0 20px"}, children=[
        html.Hr(style={"borderColor": "rgba(0,212,255,0.15)", "margin": "0"}),
        html.Span(label, style={
            "position": "absolute", "top": "-11px", "left": "16px",
            "background": COLORS["bg"], "padding": "0 12px",
            "color": COLORS["cyan"], "fontWeight": "700", "fontSize": "13px",
        }),
    ])


# ── Page Sections ─────────────────────────────────────────────

def navbar() -> html.Div:
    return html.Div(className="navbar-custom", children=[
        dbc.Row([
            dbc.Col([
                html.Span("🛡️ ", style={"fontSize": "24px"}),
                html.Span("ANOMCHECKER", style={
                    "fontSize": "22px", "fontWeight": "800",
                    "color": COLORS["cyan"], "letterSpacing": "2px",
                }),
                html.Span("  Network Threat Detection System", style={
                    "fontSize": "13px", "color": COLORS["subtext"], "marginLeft": "10px",
                }),
            ], width="auto"),
            dbc.Col(html.Div([
                html.Span(className="pulse-dot"),
                html.Span("System Active", style={"color": COLORS["green"], "fontSize": "13px"}),
                html.Span("  |  v1.0.0", style={"color": COLORS["subtext"], "fontSize": "12px"}),
            ], style={"textAlign": "right", "lineHeight": "40px"})),
        ], justify="between", align="center"),
    ])


def hero_section() -> html.Div:
    stats = [
        ("2",         "Algorithms"),
        ("10K",       "Max Rows"),
        ("5+",        "Metrics"),
        ("Real-time", "Analysis"),
    ]
    return html.Div(style={
        "background": f'linear-gradient(135deg, {COLORS["bg"]} 0%, #0d1445 100%)',
        "padding": "48px 40px 32px",
        "borderBottom": "1px solid rgba(0,212,255,0.15)",
    }, children=[
        html.H1(
            "Detect Threats with Intelligent Clustering",
            style={
                "color": "white", "fontWeight": "800",
                "fontSize": "32px", "marginBottom": "10px",
            },
        ),
        html.P(
            "Upload your network log CSV, define your row range, and let ANOMCHECKER "
            "automatically run K-Means and DBSCAN, evaluate both, and surface the threats.",
            style={
                "color": COLORS["subtext"], "fontSize": "15px",
                "maxWidth": "700px", "marginBottom": "28px",
            },
        ),
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Div(s[0], style={"color": COLORS["cyan"], "fontSize": "24px", "fontWeight": "800"}),
                    html.Div(s[1], style={"color": COLORS["subtext"], "fontSize": "12px"}),
                ], style={"textAlign": "center"}),
                width="auto",
            )
            for s in stats
        ], className="g-4"),
    ])


def sidebar() -> html.Div:
    return html.Div(style={
        "width": "340px", "minWidth": "340px",
        "padding": "24px 16px",
        "background": COLORS["card_bg"],
        "borderRight": "1px solid rgba(0,212,255,0.1)",
        "minHeight": "80vh",
    }, children=[

        # ── Upload Card ──────────────────────────────
        _card([
            html.H6(
                "📂 Upload Dataset",
                style={"color": COLORS["cyan"], "fontWeight": "700", "marginBottom": "14px"},
            ),
            dcc.Upload(
                id="upload-data",
                children=html.Div([
                    html.Div("📤", style={"fontSize": "32px", "marginBottom": "8px"}),
                    html.Div("Drag & Drop CSV here", style={
                        "color": COLORS["text"], "fontWeight": "600",
                    }),
                    html.Div("or click to browse", style={
                        "color": COLORS["subtext"], "fontSize": "12px",
                    }),
                    html.Div(
                        "Supports: CICIDS2017 | UNSW-NB15",
                        style={"color": COLORS["purple"], "fontSize": "11px", "marginTop": "6px"},
                    ),
                ], style={
                    "textAlign": "center",
                    "padding": "28px 0",
                    "pointerEvents": "none",
                    "userSelect": "none",
                }),
                className="upload-zone",
                multiple=False,
                max_size=200 * 1024 * 1024,
                disable_click=False,
                style={
                    "width": "100%",
                    "display": "block",
                    "cursor": "pointer",
                    "pointerEvents": "all",
                },
            ),
            html.Div(id="file-info", style={"marginTop": "12px"}),
        ], extra_style={"marginBottom": "16px"}),

        # ── Row Range Card ───────────────────────────
        _card([
            html.H6(
                "📏 Row Range",
                style={"color": COLORS["cyan"], "fontWeight": "700", "marginBottom": "6px"},
            ),
            html.P(
                "After uploading, enter which rows to analyze. Max range is 10,000 rows.",
                style={"color": COLORS["subtext"], "fontSize": "12px", "marginBottom": "14px"},
            ),
            dbc.Row([
                dbc.Col([
                    html.Label("Start Row", style={"color": COLORS["subtext"], "fontSize": "12px"}),
                    dbc.Input(
                        id="start-row-input",
                        type="number",
                        min=1,
                        step=1,
                        placeholder="e.g. 1",
                        value=1,
                        debounce=True,
                        style={
                            "background": COLORS["bg"],
                            "color": "white",
                            "border": "1px solid rgba(0,212,255,0.3)",
                            "borderRadius": "8px",
                        },
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("End Row", style={"color": COLORS["subtext"], "fontSize": "12px"}),
                    dbc.Input(
                        id="end-row-input",
                        type="number",
                        min=1,
                        step=1,
                        placeholder="e.g. 10000",
                        value=10000,
                        debounce=True,
                        style={
                            "background": COLORS["bg"],
                            "color": "white",
                            "border": "1px solid rgba(0,212,255,0.3)",
                            "borderRadius": "8px",
                        },
                    ),
                ], width=6),
            ], className="g-2"),

            html.Div(id="row-range-feedback", style={"marginTop": "8px"}),

            html.Div(style={"marginTop": "12px"}, children=[
                html.P(
                    "Quick presets:",
                    style={"color": COLORS["subtext"], "fontSize": "11px", "marginBottom": "6px"},
                ),
                html.Div(style={"display": "flex", "gap": "6px", "flexWrap": "wrap"}, children=[
                    dbc.Button("1K",  id="preset-1k",  size="sm", outline=True, color="info",    n_clicks=0),
                    dbc.Button("5K",  id="preset-5k",  size="sm", outline=True, color="info",    n_clicks=0),
                    dbc.Button("10K", id="preset-10k", size="sm", outline=True, color="success", n_clicks=0),
                ]),
                html.P(
                    "10K = recommended for best accuracy",
                    style={"color": COLORS["green"], "fontSize": "11px", "marginTop": "6px"},
                ),
            ]),
        ], extra_style={"marginBottom": "16px"}),

        # ── Run Button ───────────────────────────────
        dbc.Button(
            [dbc.Spinner(size="sm", spinner_style={"display": "none"}), " 🚀 RUN ANOMCHECKER"],
            id="run-btn",
            className="run-btn",
            color="primary",
            style={"width": "100%", "padding": "14px"},
            n_clicks=0,
        ),

        html.Div(id="error-message", style={"marginTop": "12px"}),
    ])


def welcome_screen() -> html.Div:
    steps = [
        ("1", "Upload CSV",    "Drag & drop your CICIDS2017 or UNSW-NB15 network log file."),
        ("2", "Set Row Range", "Choose which rows to analyze — up to 10,000 rows max."),
        ("3", "View Results",  "Explore both algorithm visualizations, metrics, and download flagged threats."),
    ]
    return html.Div(style={"textAlign": "center", "padding": "60px 40px"}, children=[
        html.Div("🛡️", style={"fontSize": "72px", "marginBottom": "20px"}),
        html.H3("Welcome to ANOMCHECKER", style={"color": "white", "fontWeight": "800"}),
        html.P(
            "An intelligent clustering-based system for cyber security threat detection in network logs.",
            style={"color": COLORS["subtext"], "marginBottom": "40px"},
        ),
        dbc.Row([
            dbc.Col(
                _card([
                    html.Div(s[0], style={
                        "width": "40px", "height": "40px", "borderRadius": "50%",
                        "background": f'linear-gradient(135deg, {COLORS["purple"]}, {COLORS["cyan"]})',
                        "color": "white", "fontWeight": "800", "fontSize": "18px",
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                        "margin": "0 auto 14px",
                    }),
                    html.H6(s[1], style={"color": COLORS["cyan"], "fontWeight": "700"}),
                    html.P(s[2], style={"color": COLORS["subtext"], "fontSize": "13px"}),
                ]),
                md=4,
            )
            for s in steps
        ], className="g-3"),
    ])


def metric_card(label: str, value: float, color: str, icon: str) -> html.Div:
    return html.Div(className="metric-card", style={"borderTop": f"3px solid {color}"}, children=[
        html.Div(icon, style={"fontSize": "24px", "marginBottom": "6px"}),
        html.Div(f"{value}%", style={"color": color, "fontSize": "28px", "fontWeight": "800"}),
        html.Div(label, style={"color": COLORS["subtext"], "fontSize": "12px", "marginTop": "4px"}),
    ])


def algo_stats_strip(metrics: dict) -> html.Div:
    """Mini metric strip shown below each cluster scatter plot."""
    items = [
        ("Accuracy",  f'{metrics["accuracy"]}%',  COLORS["green"]),
        ("F1-Score",  f'{metrics["f1"]}%',         COLORS["yellow"]),
        ("Recall",    f'{metrics["recall"]}%',     COLORS["purple"]),
        ("Precision", f'{metrics["precision"]}%',  COLORS["cyan"]),
    ]
    return html.Div(style={
        "display": "flex", "justifyContent": "space-around",
        "padding": "10px 16px",
        "borderTop": "1px solid rgba(255,255,255,0.05)",
    }, children=[
        html.Div([
            html.Div(label, style={"color": COLORS["subtext"], "fontSize": "11px"}),
            html.Div(val,   style={"color": color, "fontWeight": "700"}),
        ])
        for label, val, color in items
    ])


def results_panel(
    best_metrics: dict,
    km_metrics:   dict,
    db_metrics:   dict,
    km_fig,
    db_fig,
    km_cm_fig,              # ← K-Means confusion matrix (was: cm_fig)
    db_cm_fig,              # ← DBSCAN confusion matrix  (new)
    comp_fig,
    best_algo:    str,
    total:        int,
    normal:       int,
    attacks:      int,
    flagged_json: str,
    start_row:    int,
    end_row:      int,
) -> html.Div:
    tp, tn, fp, fn = (
        best_metrics["tp"], best_metrics["tn"],
        best_metrics["fp"], best_metrics["fn"],
    )

    return html.Div(style={"padding": "24px"}, children=[

        # ── Header ───────────────────────────────────
        html.Div(style={"marginBottom": "20px"}, children=[
            html.H5(
                "📊 Analysis Results",
                style={"color": "white", "fontWeight": "800", "marginBottom": "4px"},
            ),
            html.P(
                f"Rows analyzed: {start_row:,} → {end_row:,}  •  "
                f"Best Algorithm: {best_algo}  •  "
                f"Samples: {total:,}  •  Threats: {attacks:,}",
                style={"color": COLORS["subtext"], "fontSize": "13px"},
            ),
        ]),

        # ── Metric Cards (best algorithm) ─────────────
        dbc.Row([
            dbc.Col(metric_card("Accuracy",            best_metrics["accuracy"],  COLORS["green"],  "✅"), md=True),
            dbc.Col(metric_card("Precision",           best_metrics["precision"], COLORS["cyan"],   "🎯"), md=True),
            dbc.Col(metric_card("Recall",              best_metrics["recall"],    COLORS["purple"], "📡"), md=True),
            dbc.Col(metric_card("F1-Score",            best_metrics["f1"],        COLORS["yellow"], "⚡"), md=True),
            dbc.Col(metric_card("False Positive Rate", best_metrics["fpr"],       COLORS["red"],    "⚠️"), md=True),
        ], className="g-3 mb-3"),

        # ── Cluster Scatter Plots ─────────────────────
        _section_divider("🔵  Cluster Visualizations — K-Means vs DBSCAN"),
        dbc.Row([
            dbc.Col(
                html.Div(style={
                    "background": COLORS["card_bg"],
                    "borderRadius": "12px",
                    "border": f'1px solid {"rgba(255,214,0,0.4)" if best_algo == "K-Means" else "rgba(0,212,255,0.12)"}',
                    "overflow": "hidden",
                    "padding": "4px",
                }, children=[
                    dcc.Graph(figure=km_fig, config={"displayModeBar": False}),
                    algo_stats_strip(km_metrics),
                ]),
                md=6,
            ),
            dbc.Col(
                html.Div(style={
                    "background": COLORS["card_bg"],
                    "borderRadius": "12px",
                    "border": f'1px solid {"rgba(255,214,0,0.4)" if best_algo == "DBSCAN" else "rgba(0,212,255,0.12)"}',
                    "overflow": "hidden",
                    "padding": "4px",
                }, children=[
                    dcc.Graph(figure=db_fig, config={"displayModeBar": False}),
                    algo_stats_strip(db_metrics),
                ]),
                md=6,
            ),
        ], className="g-3 mb-3"),

        # ── Confusion Matrices — one per algorithm ────
        _section_divider("🟩  Confusion Matrices — K-Means vs DBSCAN"),
        dbc.Row([
            dbc.Col(
                html.Div(style={
                    "background": COLORS["card_bg"],
                    "borderRadius": "12px",
                    "border": "1px solid rgba(0,212,255,0.2)",
                    "padding": "4px",
                }, children=[
                    dcc.Graph(figure=km_cm_fig, config={"displayModeBar": False}),
                ]),
                md=6,
            ),
            dbc.Col(
                html.Div(style={
                    "background": COLORS["card_bg"],
                    "borderRadius": "12px",
                    "border": "1px solid rgba(123,47,255,0.2)",
                    "padding": "4px",
                }, children=[
                    dcc.Graph(figure=db_cm_fig, config={"displayModeBar": False}),
                ]),
                md=6,
            ),
        ], className="g-3 mb-3"),

        # ── Comparison Bar Chart ──────────────────────
        _section_divider("📈  Algorithm Comparison"),
        dbc.Row([
            dbc.Col(
                html.Div(style={
                    "background": COLORS["card_bg"],
                    "borderRadius": "12px",
                    "border": "1px solid rgba(0,212,255,0.12)",
                    "padding": "4px",
                }, children=[
                    dcc.Graph(figure=comp_fig, config={"displayModeBar": False}),
                ]),
                md=12,
            ),
        ], className="g-3 mb-3"),

        # ── Detection Report ──────────────────────────
        _section_divider("📋  Detection Report"),
        _card([
            dbc.Row([
                # Column 1 — Traffic summary
                dbc.Col([
                    *[html.Div(style={
                        "display": "flex", "justifyContent": "space-between",
                        "padding": "9px 0", "borderBottom": "1px solid rgba(255,255,255,0.05)",
                    }, children=[
                        html.Span(k, style={"color": COLORS["subtext"], "fontSize": "13px"}),
                        html.Span(v, style={"color": c, "fontWeight": "700", "fontSize": "13px"}),
                    ]) for k, v, c in [
                        ("Total Samples",    f"{total:,}",                              "white"),
                        ("Normal Traffic",   f"{normal:,} ({normal/total*100:.1f}%)",   COLORS["green"]),
                        ("Threats Detected", f"{attacks:,} ({attacks/total*100:.1f}%)", COLORS["red"]),
                        ("Row Range",        f"{start_row:,} → {end_row:,}",            COLORS["subtext"]),
                    ]],
                ], md=4),

                # Column 2 — Confusion breakdown
                dbc.Col([
                    *[html.Div(style={
                        "display": "flex", "justifyContent": "space-between",
                        "padding": "9px 0", "borderBottom": "1px solid rgba(255,255,255,0.05)",
                    }, children=[
                        html.Span(k, style={"color": COLORS["subtext"], "fontSize": "13px"}),
                        html.Span(v, style={"color": c, "fontWeight": "700", "fontSize": "13px"}),
                    ]) for k, v, c in [
                        ("True Positives (Caught)",  f"{tp:,}", COLORS["green"]),
                        ("True Negatives",           f"{tn:,}", COLORS["cyan"]),
                        ("False Negatives (Missed)", f"{fn:,}", COLORS["yellow"]),
                        ("False Positives (Alarms)", f"{fp:,}", COLORS["red"]),
                    ]],
                ], md=4),

                # Column 3 — Winner + download
                dbc.Col([
                    html.Div(style={
                        "display": "flex", "justifyContent": "space-between",
                        "padding": "9px 0", "borderBottom": "1px solid rgba(255,255,255,0.05)",
                    }, children=[
                        html.Span("Best Algorithm", style={"color": COLORS["subtext"], "fontSize": "13px"}),
                        html.Span(f"👑 {best_algo}", style={
                            "color": COLORS["yellow"], "fontWeight": "700", "fontSize": "13px",
                        }),
                    ]),
                    html.Div(style={"marginTop": "24px"}),
                    dbc.Button(
                        "📥 Download Flagged Anomalies (CSV)",
                        id="download-btn",
                        color="success",
                        outline=True,
                        style={"width": "100%", "borderRadius": "8px", "fontWeight": "700"},
                        n_clicks=0,
                    ),
                    dcc.Download(id="download-csv"),
                    dcc.Store(id="flagged-store", data=flagged_json),
                ], md=4),
            ]),
        ]),
    ])


def create_layout() -> html.Div:
    """Root layout function called by app.py."""
    return html.Div(style={"background": COLORS["bg"], "minHeight": "100vh"}, children=[
        navbar(),
        hero_section(),
        html.Div(style={"display": "flex"}, children=[
            sidebar(),
            html.Div(style={"flex": "1", "minWidth": "0"}, children=[
                html.Div(id="results-area", children=[welcome_screen()]),
            ]),
        ]),
        _footer(),
        dcc.Store(id="uploaded-data-store"),
    ])


def _footer() -> html.Div:
    return html.Div(style={
        "background": COLORS["card_bg"],
        "borderTop": "1px solid rgba(0,212,255,0.15)",
        "padding": "20px 40px",
        "textAlign": "center",
    }, children=[
        html.Span("🛡️ ANOMCHECKER  ", style={"color": COLORS["cyan"], "fontWeight": "700"}),
        html.Span(
            "| Built with Python, Plotly Dash & Scikit-learn | ",
            style={"color": COLORS["subtext"], "fontSize": "13px"},
        ),
        html.Span("Undergraduate Thesis Project", style={"color": COLORS["subtext"], "fontSize": "13px"}),
    ])