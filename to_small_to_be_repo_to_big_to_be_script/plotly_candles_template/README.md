# Plotly Candles Interactive Chart Template

A clean, feature-rich template for building interactive candlestick charts with Plotly and Dash. This template includes quality-of-life keyboard shortcuts and interactions that make chart navigation more efficient.

## 🎯 Purpose

This template provides a **starting point** for AI assistants and developers to build candlestick chart applications without starting from scratch. It includes essential interactive features that enhance the user experience when analyzing financial data.

## ✨ Features

### Interactive Controls

1. **Shift + Scroll**: Y-axis zoom
   - Scroll up/down while holding Shift to zoom in/out on the Y-axis
   - Works on both charts independently
   - Zooms around the center of the current view

2. **Shift + Alt + Scroll**: Fast Y-axis zoom
   - Same as Shift+Scroll but with larger zoom steps
   - Useful for quickly adjusting the view range

3. **Alt + Click**: Auto-fit Y-axis to visible data
   - Alt+Click anywhere on the chart to automatically fit the Y-axis to the currently visible X-range
   - Particularly useful after zooming in on the X-axis
   - Ensures you see all the data in the visible time range
   - Works on both charts

4. **Resize charts**: Drag the bottom-right corner
   - Each chart container is resizable by dragging the bottom-right corner
   - Similar to resizing a textarea in modern UIs
   - **The chart automatically resizes to fill the container** - no scrollbars!
   - Uses ResizeObserver API to detect container changes and update Plotly graph heights
   - Allows making charts bigger or smaller than the default size
   - Great for focusing on specific charts or adjusting to your screen size

5. **Double-click**: Reset zoom
   - Standard Plotly double-click to reset to default view

6. **View State Persistence**: 
   - Zoom and pan state is preserved when you update the data

### Visual Features

- **Modern Dark Theme**: Eye-friendly dark color scheme
- **Professional Candlestick Colors**: Teal for bullish, red for bearish
- **Responsive Layout**: Works on different screen sizes
- **Unified Hover**: See values across all subplots simultaneously

## 📁 File Structure

```
plotly_candles_template/
├── app.py              # Main Dash application with all interactive features
├── config.py           # Configuration (colors, settings, etc.)
├── sample_data.py      # Sample data generator (replace with your data source)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser to: `http://127.0.0.1:8050`

### Customization

**To use your own data:**

1. Open `sample_data.py`
2. Modify the `load_data()` function to load your data source
3. Ensure your data is a pandas DataFrame with these columns:
   - `open`: Opening price
   - `high`: Highest price
   - `low`: Lowest price
   - `close`: Closing price
   - `volume`: Trading volume (optional, not displayed by default)
   - Index: pandas DatetimeIndex with timestamps

**Example:**
```python
def load_data():
    # Replace this with your data loading logic
    df = pd.read_csv('your_ohlcv_data.csv', index_col='timestamp', parse_dates=True)
    return df
```

**To customize colors and appearance:**

Edit `config.py` to change:
- Chart height
- Color scheme (background, candles, grid, etc.)
- App title
- Host and port

## 🎨 Adding More Features

### Adding Overlays (e.g., Moving Averages)

Add traces to the figure in the `update_chart` callback:

```python
# After creating the candlestick
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['sma_20'],  # Your calculated indicator
    name='SMA 20',
    line=dict(color='#2196F3', width=2)
))
```

### Adding Subplots (e.g., Volume, RSI)

Use `plotly.subplots.make_subplots` instead of `go.Figure`:

```python
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.7, 0.3]
)

# Add candlestick to row 1
fig.add_trace(
    go.Candlestick(...),
    row=1, col=1
)

# Add volume to row 2
fig.add_trace(
    go.Bar(x=df.index, y=df['volume'], name='Volume'),
    row=2, col=1
)
```

**Note:** All the interactive features (Shift+Scroll, Alt+Click, draggable borders) automatically work with subplots!

## 🛠️ Technical Details

### How the Interactive Features Work

The interactive features are implemented using custom JavaScript injected into the Dash app via `app.index_string`. This JavaScript:

1. **Finds the Plotly graph element** on the page
2. **Attaches event listeners** for wheel events (Shift+Scroll) and click events (Alt+Click)
3. **Detects which subplot** the user is interacting with based on mouse position
4. **Calculates new axis ranges** based on the user's action
5. **Calls `Plotly.relayout()`** to update the chart without re-rendering

The view state persistence uses Dash's `dcc.Store` component to save axis ranges and restore them when the figure updates.

### Architecture

- **Dash**: Web framework for building the interactive application
- **Plotly**: Charting library for rendering the candlestick chart
- **Dash Bootstrap Components**: Provides modern UI components
- **Pandas**: Data manipulation and handling time series data
- **NumPy**: Numerical operations for data generation

## 📝 For AI Assistants

When using this template:

1. **Don't modify the JavaScript sections** in `app.index_string` unless specifically asked
2. **The interactive features are self-contained** and require no additional setup
3. **To add indicators**: Modify the `update_chart` callback to add more traces
4. **To add subplots**: Use `make_subplots` and all features still work
5. **Data format is critical**: Must have OHLC columns and datetime index
6. **View state persistence** is handled automatically via callbacks

### Common Modifications

- **Change data source**: Edit `sample_data.py`
- **Add indicators**: Add traces in `update_chart()`
- **Change appearance**: Edit `config.py`
- **Add controls**: Add components to the sidebar in `app.layout`
- **Add callbacks**: Follow the existing callback pattern

## 🐛 Troubleshooting

**Problem**: Interactive features don't work
- **Solution**: Make sure the graph element has `id="main-chart"`
- Check browser console for JavaScript errors

**Problem**: Data doesn't display
- **Solution**: Verify your DataFrame has the correct OHLC columns and datetime index
- Check for NaN values in the data

**Problem**: Chart is too small/large
- **Solution**: Adjust `CHART_HEIGHT` in `config.py`

## 📚 Resources

- [Plotly Documentation](https://plotly.com/python/)
- [Dash Documentation](https://dash.plotly.com/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

## 📄 License

This is a template - use it however you want! No attribution required.

## 🤝 Contributing

This is a minimal template. If you add useful features, consider creating your own enhanced version!

---

**Happy Charting! 📈**

