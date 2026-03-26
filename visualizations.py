# =============================================================
# ANOMCHECKER — visualizations.py
# All Plotly figure builders. K-Means only.
# =============================================================

import numpy as np
import plotly.graph_objects as go
from sklearn.decomposition import PCA

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

# Base layout shared by all figures — no xaxis/yaxis here
# so individual functions can set them without conflict
_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,21,53,0.8)",
    font=dict(color="#e0e0e0", family="Segoe UI"),
)

_GRID = dict(gridcolor="rgba(255,255,255,0.06)",
             zerolinecolor="rgba(255,255,255,0.1)")


def compute_pca(X_scaled: np.ndarray) -> np.ndarray:
    n_components = min(2, X_scaled.shape[1])
    pca = PCA(n_components=n_components, random_state=42)
    X_2d = pca.fit_transform(X_scaled)
    if X_2d.shape[1] == 1:
        X_2d = np.hstack([X_2d, np.zeros((X_2d.shape[0], 1))])
    return X_2d


def cluster_scatter(X_2d: np.ndarray, predictions: np.ndarray,
                    title: str = "K-Means Clustering — PCA 2D") -> go.Figure:
    fig = go.Figure()
    for label, color, name in [(0, COLORS["green"], "Normal"),
                                (1, COLORS["red"],   "Threat")]:
        mask = predictions == label
        if not mask.any():
            continue
        fig.add_trace(go.Scatter(
            x=X_2d[mask, 0], y=X_2d[mask, 1],
            mode="markers", name=name,
            marker=dict(color=color, size=4, opacity=0.7),
        ))

    fig.add_annotation(
        text="👑 K-Means — System Algorithm",
        xref="paper", yref="paper", x=1.0, y=1.08, showarrow=False,
        font=dict(color=COLORS["yellow"], size=12),
        bgcolor="rgba(255,214,0,0.15)",
        bordercolor=COLORS["yellow"], borderwidth=1, borderpad=4,
    )

    fig.update_layout(
        **_BASE,
        title=dict(text=title, font=dict(color=COLORS["yellow"], size=14)),
        xaxis=dict(title="PC1", **_GRID),
        yaxis=dict(title="PC2", **_GRID),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e0e0e0"),
                    orientation="h", y=-0.22),
        margin=dict(l=40, r=20, t=55, b=55),
        height=380,
    )
    return fig


def confusion_heatmap(cm_data: list) -> go.Figure:
    cm = np.array(cm_data)
    tn, fp = int(cm[0, 0]), int(cm[0, 1])
    fn, tp = int(cm[1, 0]), int(cm[1, 1])
    axis_labels = ["Normal", "Threat"]
    text = [[f"TN\n{tn:,}", f"FP\n{fp:,}"], [f"FN\n{fn:,}", f"TP\n{tp:,}"]]

    fig = go.Figure(go.Heatmap(
        z=cm, x=axis_labels, y=axis_labels,
        colorscale=[[0, COLORS["card_bg"]], [1, COLORS["cyan"]]],
        showscale=False, text=text,
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=18, color="white"),
    ))

    for row, col in [(0, 0), (1, 1)]:
        fig.add_shape(type="rect",
            x0=col-.5, x1=col+.5, y0=row-.5, y1=row+.5,
            line=dict(color=COLORS["green"], width=2),
            fillcolor="rgba(0,245,160,0.08)")
    for row, col in [(0, 1), (1, 0)]:
        fig.add_shape(type="rect",
            x0=col-.5, x1=col+.5, y0=row-.5, y1=row+.5,
            line=dict(color=COLORS["red"], width=2),
            fillcolor="rgba(255,77,109,0.08)")

    fig.update_layout(
        **_BASE,
        title=dict(text="K-Means — Confusion Matrix",
                   font=dict(color=COLORS["cyan"], size=14)),
        xaxis=dict(title="Predicted", **_GRID),
        yaxis=dict(title="Actual",    **_GRID),
        margin=dict(l=60, r=20, t=55, b=60),
        height=380,
    )
    return fig


def metrics_bar(metrics: dict) -> go.Figure:
    labels = ["Accuracy", "Precision", "Recall", "F1-Score", "FPR"]
    keys   = ["accuracy", "precision", "recall", "f1", "fpr"]
    colors = [COLORS["green"], COLORS["cyan"], COLORS["purple"],
              COLORS["yellow"], COLORS["red"]]
    values = [metrics[k] for k in keys]

    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors,
        text=[f"{v}%" for v in values],
        textposition="outside", opacity=0.9,
    ))
    fig.update_layout(
        **_BASE,
        title=dict(text="K-Means — Performance Metrics Overview",
                   font=dict(color=COLORS["cyan"], size=14)),
        xaxis=dict(**_GRID),
        yaxis=dict(title="Score (%)", range=[0, 115], **_GRID),
        margin=dict(l=40, r=20, t=55, b=40),
        height=380,
    )
    return fig