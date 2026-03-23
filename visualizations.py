# =============================================================
# ANOMCHECKER — visualizations.py
# All Plotly figure builders.
# =============================================================

import numpy as np
import plotly.graph_objects as go
from sklearn.decomposition import PCA

# ── Shared style constants ────────────────────────────────────
COLORS = {
    "bg":      "#0a0e27",
    "card_bg": "#0f1535",
    "cyan":    "#00d4ff",
    "purple":  "#7b2fff",
    "green":   "#00f5a0",
    "yellow":  "#ffd600",
    "red":     "#ff4d6d",
    "text":    "#e0e0e0",
    "subtext": "#8892b0",
}

PLOT_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,21,53,0.8)",
    font=dict(color="#e0e0e0", family="Segoe UI"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.1)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.1)",
    ),
)


def compute_pca(X_scaled: np.ndarray) -> np.ndarray:
    """
    Reduce feature matrix to 2D using PCA for scatter plotting.
    Pads with zeros if only 1 component is possible.
    """
    n_components = min(2, X_scaled.shape[1])
    pca = PCA(n_components=n_components, random_state=42)
    X_2d = pca.fit_transform(X_scaled)
    if X_2d.shape[1] == 1:
        X_2d = np.hstack([X_2d, np.zeros((X_2d.shape[0], 1))])
    return X_2d


def cluster_scatter(
    X_2d: np.ndarray,
    predictions: np.ndarray,
    title: str,
    is_best: bool = False,
) -> go.Figure:
    """
    2D PCA scatter plot with Normal/Threat coloring.
    Adds a gold crown badge if this algorithm is the winner.
    """
    fig = go.Figure()

    for label, color, name in [
        (0, COLORS["green"], "Normal"),
        (1, COLORS["red"],   "Threat"),
    ]:
        mask = predictions == label
        if not mask.any():
            continue
        fig.add_trace(go.Scatter(
            x=X_2d[mask, 0],
            y=X_2d[mask, 1],
            mode="markers",
            name=name,
            marker=dict(color=color, size=4, opacity=0.7),
        ))

    if is_best:
        fig.add_annotation(
            text="👑 BEST",
            xref="paper", yref="paper",
            x=1.0, y=1.08,
            showarrow=False,
            font=dict(color=COLORS["yellow"], size=13),
            bgcolor="rgba(255,214,0,0.15)",
            bordercolor=COLORS["yellow"],
            borderwidth=1,
            borderpad=4,
        )

    fig.update_layout(
        **PLOT_TEMPLATE,
        title=dict(
            text=title,
            font=dict(
                color=COLORS["yellow"] if is_best else COLORS["cyan"],
                size=14,
            ),
        ),
        xaxis_title="PC1",
        yaxis_title="PC2",
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e0e0"),
            orientation="h",
            y=-0.22,
        ),
        margin=dict(l=40, r=20, t=55, b=55),
        height=360,
    )
    return fig


def confusion_heatmap(cm_data: list, algorithm_name: str = "Algorithm") -> go.Figure:
    """
    Heatmap visualisation of a confusion matrix.

    Parameters
    ----------
    cm_data        : 2×2 list/array  [[TN, FP], [FN, TP]]
    algorithm_name : str  — shown in the chart title so screenshots are
                            unambiguous.  Pass "K-Means" or "DBSCAN".

    Returns
    -------
    go.Figure
    """
    cm = np.array(cm_data)
    tn, fp = int(cm[0, 0]), int(cm[0, 1])
    fn, tp = int(cm[1, 0]), int(cm[1, 1])

    axis_labels = ["Normal", "Threat"]

    # Build rich cell labels: abbreviation + count
    text = [
        [f"TN\n{tn:,}", f"FP\n{fp:,}"],
        [f"FN\n{fn:,}", f"TP\n{tp:,}"],
    ]

    # Colour scale: dark card → algorithm colour
    algo_colour = COLORS["cyan"] if algorithm_name == "K-Means" else COLORS["purple"]

    fig = go.Figure(go.Heatmap(
        z=cm,
        x=axis_labels,
        y=axis_labels,
        colorscale=[[0, COLORS["card_bg"]], [1, algo_colour]],
        showscale=False,
        text=text,
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=18, color="white"),
    ))

    # Green border overlay on correct cells (TN, TP)
    for row, col in [(0, 0), (1, 1)]:          # TN, TP
        fig.add_shape(
            type="rect",
            x0=col - 0.5, x1=col + 0.5,
            y0=row - 0.5, y1=row + 0.5,
            line=dict(color=COLORS["green"], width=2),
            fillcolor="rgba(0,245,160,0.08)",
        )
    for row, col in [(0, 1), (1, 0)]:          # FP, FN
        fig.add_shape(
            type="rect",
            x0=col - 0.5, x1=col + 0.5,
            y0=row - 0.5, y1=row + 0.5,
            line=dict(color=COLORS["red"], width=2),
            fillcolor="rgba(255,77,109,0.08)",
        )

    fig.update_layout(
        **PLOT_TEMPLATE,
        title=dict(
            text=f"{algorithm_name} — Confusion Matrix",
            font=dict(color=algo_colour, size=14),
        ),
        xaxis_title="Predicted",
        yaxis_title="Actual",
        margin=dict(l=60, r=20, t=55, b=60),
        height=360,
    )
    return fig


def comparison_bar(km_metrics: dict, db_metrics: dict) -> go.Figure:
    """Grouped bar chart comparing K-Means vs DBSCAN across all metrics."""
    metric_names = ["Accuracy", "Precision", "Recall", "F1-Score", "FPR"]
    km_vals = [
        km_metrics["accuracy"], km_metrics["precision"],
        km_metrics["recall"],   km_metrics["f1"],
        km_metrics["fpr"],
    ]
    db_vals = [
        db_metrics["accuracy"], db_metrics["precision"],
        db_metrics["recall"],   db_metrics["f1"],
        db_metrics["fpr"],
    ]

    fig = go.Figure(data=[
        go.Bar(
            name="K-Means", x=metric_names, y=km_vals,
            marker_color=COLORS["cyan"], opacity=0.85,
        ),
        go.Bar(
            name="DBSCAN", x=metric_names, y=db_vals,
            marker_color=COLORS["purple"], opacity=0.85,
        ),
    ])
    fig.update_layout(
        **PLOT_TEMPLATE,
        title=dict(
            text="Algorithm Comparison — All Metrics",
            font=dict(color=COLORS["cyan"]),
        ),
        barmode="group",
        yaxis_title="Score (%)",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e0e0e0")),
        margin=dict(l=40, r=20, t=50, b=40),
        height=360,
    )
    return fig