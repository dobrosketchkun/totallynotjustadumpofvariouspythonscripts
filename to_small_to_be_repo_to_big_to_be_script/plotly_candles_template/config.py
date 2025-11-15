"""
Configuration settings for Plotly Candles Template.
"""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent

# Chart settings
CHART_HEIGHT = 800

# Color scheme (modern dark theme)
COLORS = {
    "background": "#0e1117",
    "paper": "#1a1d24",
    "text": "#ffffff",
    "grid": "#2d3139",
    "candle_up": "#26a69a",    # Teal for bullish
    "candle_down": "#ef5350",  # Red for bearish
}

# App settings
APP_TITLE = "Plotly Candles Interactive Chart Template"
APP_DEBUG = True
APP_HOST = "127.0.0.1"
APP_PORT = 8050

