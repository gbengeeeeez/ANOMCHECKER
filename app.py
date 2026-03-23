# =============================================================
# ANOMCHECKER — app.py
# Entry point. Initializes Dash app and registers callbacks.
# =============================================================

import dash
import dash_bootstrap_components as dbc
from layout import create_layout
import callbacks  # noqa: F401 — importing registers all callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
)
app.title = "ANOMCHECKER - Network Threat Detection"
server = app.server  # Expose for deployment (Gunicorn etc.)

# Register layout
app.layout = create_layout()

# Register callbacks (imported above, they reference 'app' via callbacks.py)
callbacks.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8050)

    