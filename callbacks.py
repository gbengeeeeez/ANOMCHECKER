# =============================================================
# ANOMCHECKER — callbacks.py
# All Dash callbacks. K-Means is the sole system algorithm.
# DBSCAN and Isolation Forest were evaluated separately in
# Google Colab for comparative study documentation.
# =============================================================

import io
import numpy as np
import pandas as pd
import dash
from dash import Input, Output, State, dcc

from preprocessing  import decode_uploaded_file, get_file_stats, slice_dataframe, preprocess
from models         import run_kmeans, compute_metrics
from visualizations import compute_pca, cluster_scatter, confusion_heatmap, metrics_bar
from layout         import results_panel, welcome_screen, COLORS


def register_callbacks(app):

    # ── 1. Store uploaded file + show file stats ──────────────
    @app.callback(
        Output("uploaded-data-store", "data"),
        Output("file-info",           "children"),
        Output("end-row-input",       "value", allow_duplicate=True),
        Input("upload-data",          "contents"),
        State("upload-data",          "filename"),
        prevent_initial_call=True,
    )
    def store_file(contents, filename):
        if contents is None:
            return dash.no_update, dash.no_update, dash.no_update
        try:
            stats = get_file_stats(contents, filename)
        except ValueError as e:
            return None, _error(str(e)), dash.no_update

        suggested_end = min(stats["total_rows"], 10000)
        label_status  = ("✅ Label column detected" if stats["has_label"]
                         else "⚠️ No 'Label' column found")
        label_color   = COLORS["green"] if stats["has_label"] else COLORS["yellow"]
        return contents, _file_info_block(stats, label_status, label_color), suggested_end


    # ── 2. Quick preset buttons ────────────────────────────────
    @app.callback(
        Output("start-row-input", "value"),
        Output("end-row-input",   "value"),
        Input("preset-1k",  "n_clicks"),
        Input("preset-5k",  "n_clicks"),
        Input("preset-10k", "n_clicks"),
        prevent_initial_call=True,
    )
    def apply_preset(n1k, n5k, n10k):
        triggered = dash.callback_context.triggered_id
        presets   = {"preset-1k": 1000, "preset-5k": 5000, "preset-10k": 10000}
        return 1, presets.get(triggered, 10000)


    # ── 3. Live row-range validation ──────────────────────────
    @app.callback(
        Output("row-range-feedback", "children"),
        Input("start-row-input", "value"),
        Input("end-row-input",   "value"),
        State("uploaded-data-store", "data"),
        State("upload-data",    "filename"),
        prevent_initial_call=True,
    )
    def validate_range(start, end, contents, filename):
        if start is None or end is None:
            return ""
        if start < 1:
            return _warn("Start row must be ≥ 1.")
        if end <= start:
            return _warn("End row must be greater than start row.")
        span = end - start
        if span > 10000:
            return _warn(f"Range is {span:,} rows — exceeds 10K max. "
                         f"System will cap at {start:,}–{start + 10000:,}.")
        if span < 100:
            return _warn(f"Only {span} rows selected — results may be unreliable.")
        return _ok(f"✅  {span:,} rows selected  ({start:,} → {end:,})")


    # ── 4. Main analysis — K-Means only ───────────────────────
    @app.callback(
        Output("results-area",  "children"),
        Output("error-message", "children"),
        Input("run-btn",        "n_clicks"),
        State("uploaded-data-store", "data"),
        State("upload-data",    "filename"),
        State("start-row-input","value"),
        State("end-row-input",  "value"),
        prevent_initial_call=True,
    )
    def run_analysis(n_clicks, contents, filename, start_row, end_row):
        if not contents:
            return welcome_screen(), _warn("⚠️ Please upload a CSV file first.")
        if start_row is None or end_row is None:
            return welcome_screen(), _warn("⚠️ Please set a valid row range.")

        try:
            # Step 1 — Decode CSV
            df_raw = decode_uploaded_file(contents, filename)

            # Step 2 — Slice (10K max enforced)
            actual_end = min(end_row, start_row + 10000 - 1)
            df_sliced  = slice_dataframe(df_raw, start_row, actual_end)

            # Step 3 — Preprocess
            X_scaled, y, df_clean = preprocess(df_sliced)

            # Step 4 — Run K-Means (8-seed optimisation)
            km_preds = run_kmeans(X_scaled, y)

            # Step 5 — Evaluate
            km_metrics = compute_metrics(y, km_preds)

            # Step 6 — Flag anomaly rows
            anomaly_idx  = np.where(km_preds == 1)[0]
            df_flagged   = df_clean.iloc[anomaly_idx].copy()
            df_flagged["ANOMCHECKER_FLAG"] = "THREAT"
            flagged_json = df_flagged.to_json(date_format="iso", orient="split")

            # Step 7 — Build figures
            X_2d      = compute_pca(X_scaled)
            scatter   = cluster_scatter(X_2d, km_preds)
            cm_fig    = confusion_heatmap(km_metrics["cm"])
            bar_fig   = metrics_bar(km_metrics)

            # Step 8 — Summary counts
            total   = len(y)
            normal  = int((km_preds == 0).sum())
            attacks = int((km_preds == 1).sum())

            return results_panel(
                km_metrics, scatter, cm_fig, bar_fig,
                total, normal, attacks,
                flagged_json, start_row, actual_end,
            ), ""

        except ValueError as ve:
            return welcome_screen(), _error(f"Validation Error: {str(ve)}")
        except Exception as e:
            return welcome_screen(), _error(f"Unexpected Error: {str(e)}")


    # ── 5. Download flagged anomalies ─────────────────────────
    @app.callback(
        Output("download-csv", "data"),
        Input("download-btn",  "n_clicks"),
        State("flagged-store", "data"),
        prevent_initial_call=True,
    )
    def download_flagged(n_clicks, flagged_json):
        if not flagged_json:
            return dash.no_update
        df = pd.read_json(io.StringIO(flagged_json), orient="split")
        return dcc.send_data_frame(df.to_csv,
                                   "anomchecker_flagged_threats.csv",
                                   index=False)


# ── Private helpers ───────────────────────────────────────────

def _error(msg):
    return dash.html.Div(f"❌ {msg}",
        style={"color": COLORS["red"], "fontSize": "13px", "marginTop": "8px"})

def _warn(msg):
    return dash.html.Div(msg,
        style={"color": COLORS["yellow"], "fontSize": "13px", "marginTop": "6px"})

def _ok(msg):
    return dash.html.Div(msg,
        style={"color": COLORS["green"], "fontSize": "12px", "marginTop": "6px"})

def _file_info_block(stats, label_status, label_color):
    from dash import html
    return html.Div([
        html.Div(f"📄 {stats['filename']}",
            style={"color": COLORS["cyan"], "fontWeight": "700", "fontSize": "13px"}),
        html.Div(f"Size: {stats['size_mb']} MB  |  Total Rows: {stats['total_rows']:,}",
            style={"color": COLORS["subtext"], "fontSize": "12px"}),
        html.Div(f"Columns: {stats['total_cols']}  |  Numeric Features: {stats['numeric_features']}",
            style={"color": COLORS["subtext"], "fontSize": "12px"}),
        html.Div(label_status,
            style={"color": label_color, "fontSize": "12px", "marginTop": "4px"}),
    ])