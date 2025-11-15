"""
Plotly Candles Interactive Chart Template
==========================================

This is a minimal template for creating interactive candlestick charts with Plotly and Dash.
It includes several quality-of-life features for better chart interaction.

QUALITY OF LIFE FEATURES:
- Shift+Scroll: Y-axis zoom on any chart independently
- Shift+Alt+Scroll: Fast Y-axis zoom
- Alt+Click: Auto-fit Y-axis to visible data
- Resizable charts: Drag bottom-right corner to resize (like textarea)
- Double-click: Reset zoom
- View state persistence: Zoom/pan preserved on updates

LAYOUT:
- Two separate chart containers (main chart + secondary chart)
- Each chart can be resized independently by dragging the corner
- Charts can expand beyond initial window size

CUSTOMIZATION:
Replace the sample_data.load_data() function with your own data source.
The data must be a pandas DataFrame with columns: open, high, low, close, volume
"""
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

import config
from sample_data import load_data


# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
)
app.title = config.APP_TITLE


# Custom CSS and JavaScript for enhanced functionality
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Modern dark theme styling */
            body {
                margin: 0;
                padding: 0;
                background-color: #0e1117;
            }
            
            /* Resizable graph containers */
            .resizable-graph-container {
                resize: vertical;
                overflow: hidden;  /* No scrollbars */
                border: 2px solid #495057;
                border-radius: 4px;
                padding: 0;
                background-color: #1a1d24;
                margin-bottom: 15px;
                min-height: 100px;
                max-height: none;
                position: relative;
            }
            
            .resizable-graph-container:hover {
                border-color: #6c757d;
            }
            
            /* Make sure loading and graph containers fill the resizable container */
            .resizable-graph-container > div,
            .resizable-graph-container .dash-graph {
                height: 100%;
                width: 100%;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // ============================================================
            // SHIFT + SCROLL FOR Y-AXIS ZOOM (works on both charts)
            // ============================================================
            if (typeof window.addShiftScrollZoom === 'undefined') {
                window.addShiftScrollZoom = function() {
                    console.log('🔧 Setting up Shift+Scroll Y-axis zoom...');
                    
                    // Apply to all graph containers
                    const chartIds = ['main-chart', 'secondary-chart'];
                    
                    chartIds.forEach(chartId => {
                        const graphContainer = document.getElementById(chartId);
                        if (!graphContainer) {
                            console.warn(`⚠️ Graph container #${chartId} not found`);
                            return;
                        }
                        
                        const plotlyDiv = graphContainer.querySelector('.js-plotly-plot') || graphContainer;
                        
                        if (!plotlyDiv) {
                            console.error(`❌ Plotly div not found inside ${chartId}`);
                            return;
                        }
                        
                        // Add wheel event listener for Shift+Scroll
                        plotlyDiv.addEventListener('wheel', function(e) {
                        if (e.shiftKey) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            const gd = plotlyDiv;
                            
                            if (!gd.layout || !gd._fullLayout) {
                                console.warn('⚠️ Layout not ready yet');
                                return;
                            }
                            
                            const fullLayout = gd._fullLayout;
                            const rect = gd.getBoundingClientRect();
                            const y = e.clientY - rect.top;
                            
                            // Find which subplot (yaxis) we're hovering over
                            let targetYaxis = 'yaxis';
                            
                            for (let i = 1; i <= 10; i++) {
                                const yaxisKey = i === 1 ? 'yaxis' : 'yaxis' + i;
                                const yaxis = fullLayout[yaxisKey];
                                
                                if (yaxis && yaxis.domain) {
                                    const plotHeight = rect.height;
                                    const yaxisTop = plotHeight * (1 - yaxis.domain[1]);
                                    const yaxisBottom = plotHeight * (1 - yaxis.domain[0]);
                                    
                                    if (y >= yaxisTop && y <= yaxisBottom) {
                                        targetYaxis = yaxisKey;
                                        break;
                                    }
                                }
                            }
                            
                            // Get current Y range
                            const yaxis = fullLayout[targetYaxis];
                            if (!yaxis || !yaxis.range) {
                                return;
                            }
                            
                            const currentRange = [...yaxis.range];
                            
                            // Calculate zoom factor
                            // Shift+Alt = fast zoom, Shift only = normal zoom
                            let zoomFactor;
                            if (e.altKey) {
                                zoomFactor = e.deltaY < 0 ? 0.7 : 1.3;
                            } else {
                                zoomFactor = e.deltaY < 0 ? 0.9 : 1.1;
                            }
                            
                            // Calculate new range centered on current center
                            const center = (currentRange[0] + currentRange[1]) / 2;
                            const halfSpan = (currentRange[1] - currentRange[0]) / 2;
                            const newHalfSpan = halfSpan * zoomFactor;
                            
                            const newRange = [
                                center - newHalfSpan,
                                center + newHalfSpan
                            ];
                            
                            // Update the layout
                            const update = {};
                            update[targetYaxis + '.range'] = newRange;
                            
                            Plotly.relayout(gd, update).catch(function(err) {
                                console.error('❌ Relayout error:', err);
                            });
                        }
                        }, { passive: false });
                        
                        console.log(`✅ Shift+Scroll Y-axis zoom ENABLED on ${chartId}`);
                    }); // End forEach
                };
                
                // Attach after page loads
                if (document.readyState === 'complete') {
                    setTimeout(window.addShiftScrollZoom, 500);
                } else {
                    window.addEventListener('load', function() {
                        setTimeout(window.addShiftScrollZoom, 500);
                    });
                }
                
                setTimeout(function() {
                    if (document.querySelector('.js-plotly-plot')) {
                        window.addShiftScrollZoom();
                    }
                }, 2000);
            }
            
            // ============================================================
            // ALT + CLICK TO AUTO-FIT Y-AXIS (works on both charts)
            // ============================================================
            if (typeof window.addAltClickAutoFit === 'undefined') {
                window.addAltClickAutoFit = function() {
                    console.log('🔧 Setting up Alt+Click auto-fit...');
                    
                    // Apply to all graph containers
                    const chartIds = ['main-chart', 'secondary-chart'];
                    
                    chartIds.forEach(chartId => {
                        const graphContainer = document.getElementById(chartId);
                        if (!graphContainer) {
                            console.warn(`⚠️ Graph container #${chartId} not found`);
                            return;
                        }
                        
                        const plotlyDiv = graphContainer.querySelector('.js-plotly-plot') || graphContainer;
                    
                    // Use Plotly's plotly_click event which captures modifier keys
                    plotlyDiv.on('plotly_click', function(data) {
                        const e = data.event;
                        
                        if (e.altKey) {
                            e.stopPropagation();
                            e.preventDefault();
                            
                            const gd = plotlyDiv;
                            if (!gd.layout || !gd._fullLayout || !gd.data) {
                                return;
                            }
                            
                            const fullLayout = gd._fullLayout;
                            const rect = gd.getBoundingClientRect();
                            const y = e.clientY - rect.top;
                            
                            // Find which subplot we clicked on
                            let targetYaxis = 'yaxis';
                            let yaxisNum = 1;
                            
                            for (let i = 1; i <= 10; i++) {
                                const yaxisKey = i === 1 ? 'yaxis' : 'yaxis' + i;
                                const yaxis = fullLayout[yaxisKey];
                                
                                if (yaxis && yaxis.domain) {
                                    const plotHeight = rect.height;
                                    const yaxisTop = plotHeight * (1 - yaxis.domain[1]);
                                    const yaxisBottom = plotHeight * (1 - yaxis.domain[0]);
                                    
                                    if (y >= yaxisTop && y <= yaxisBottom) {
                                        targetYaxis = yaxisKey;
                                        yaxisNum = i;
                                        break;
                                    }
                                }
                            }
                            
                            // Get current X-axis range (to only fit visible data)
                            const xaxis = fullLayout.xaxis;
                            const xRange = xaxis.range || [gd.data[0].x[0], gd.data[0].x[gd.data[0].x.length - 1]];
                            
                            // Convert to timestamps
                            let xMin, xMax;
                            if (typeof xRange[0] === 'string') {
                                xMin = new Date(xRange[0]).getTime();
                                xMax = new Date(xRange[1]).getTime();
                            } else {
                                xMin = xRange[0];
                                xMax = xRange[1];
                            }
                            
                            // Find min/max Y values in visible range
                            let minY = Infinity;
                            let maxY = -Infinity;
                            let foundData = false;
                            
                            const traces = gd._fullData || gd.data;
                            
                            for (let trace of traces) {
                                const traceYaxis = trace.yaxis || 'y';
                                const traceYaxisNum = traceYaxis === 'y' ? 1 : parseInt(traceYaxis.replace('y', ''));
                                
                                if (traceYaxisNum === yaxisNum) {
                                    // Handle candlestick charts
                                    if (trace.type === 'candlestick' && trace.x && trace.high && trace.low) {
                                        for (let i = 0; i < trace.x.length; i++) {
                                            let xVal;
                                            if (typeof trace.x[i] === 'string') {
                                                xVal = new Date(trace.x[i]).getTime();
                                            } else if (typeof trace.x[i] === 'number') {
                                                xVal = trace.x[i];
                                            } else {
                                                xVal = trace.x[i].getTime();
                                            }
                                            
                                            if (xVal >= xMin && xVal <= xMax) {
                                                const highVal = trace.high[i];
                                                const lowVal = trace.low[i];
                                                
                                                if (highVal !== null && highVal !== undefined && !isNaN(highVal)) {
                                                    maxY = Math.max(maxY, highVal);
                                                    foundData = true;
                                                }
                                                if (lowVal !== null && lowVal !== undefined && !isNaN(lowVal)) {
                                                    minY = Math.min(minY, lowVal);
                                                    foundData = true;
                                                }
                                            }
                                        }
                                    }
                                    // Handle regular line/scatter traces
                                    else if (trace.x && trace.y) {
                                        for (let i = 0; i < trace.x.length; i++) {
                                            let xVal;
                                            if (typeof trace.x[i] === 'string') {
                                                xVal = new Date(trace.x[i]).getTime();
                                            } else if (typeof trace.x[i] === 'number') {
                                                xVal = trace.x[i];
                                            } else {
                                                xVal = trace.x[i].getTime();
                                            }
                                            
                                            if (xVal >= xMin && xVal <= xMax) {
                                                const yVal = trace.y[i];
                                                if (yVal !== null && yVal !== undefined && !isNaN(yVal)) {
                                                    minY = Math.min(minY, yVal);
                                                    maxY = Math.max(maxY, yVal);
                                                    foundData = true;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            
                            if (foundData && minY !== Infinity && maxY !== -Infinity) {
                                // Update the Y-axis range
                                const update = {};
                                update[targetYaxis + '.range'] = [minY, maxY];
                                update[targetYaxis + '.autorange'] = false;
                                
                                Plotly.relayout(gd, update).catch(function(err) {
                                    console.error('❌ Auto-fit error:', err);
                                });
                            }
                        }
                        });
                        
                        console.log(`✅ Alt+Click auto-fit ENABLED on ${chartId}`);
                    }); // End forEach
                };
                
                // Attach Alt+Click handler
                if (document.readyState === 'complete') {
                    setTimeout(window.addAltClickAutoFit, 500);
                } else {
                    window.addEventListener('load', function() {
                        setTimeout(window.addAltClickAutoFit, 500);
                    });
                }
                
                setTimeout(function() {
                    if (document.querySelector('.js-plotly-plot')) {
                        window.addAltClickAutoFit();
                    }
                }, 2000);
            }
            
            // ============================================================
            // DRAGGABLE SUBPLOT BORDERS (for multiple subplots)
            // ============================================================
            if (typeof window.addDraggableSubplotBorders === 'undefined') {
                window.addDraggableSubplotBorders = function() {
                    console.log('🔧 Setting up draggable subplot borders...');
                    
                    const graphContainer = document.getElementById('main-chart');
                    if (!graphContainer) {
                        return;
                    }
                    
                    const plotlyDiv = graphContainer.querySelector('.js-plotly-plot') || graphContainer;
                    
                    let isDragging = false;
                    let dragBorderIndex = -1;
                    
                    // Mousemove to detect borders and drag
                    plotlyDiv.addEventListener('mousemove', function(e) {
                        if (isDragging) {
                            const gd = plotlyDiv;
                            if (!gd._fullLayout) return;
                            
                            const rect = gd.getBoundingClientRect();
                            const mouseY = e.clientY - rect.top;
                            const relativeY = mouseY / rect.height;
                            const normalizedY = 1 - relativeY;
                            
                            const update = {};
                            const lowerAxisKey = dragBorderIndex === 0 ? 'yaxis' : 'yaxis' + (dragBorderIndex + 1);
                            const upperAxisKey = 'yaxis' + (dragBorderIndex + 2);
                            
                            const lowerAxis = gd._fullLayout[lowerAxisKey];
                            const upperAxis = gd._fullLayout[upperAxisKey];
                            
                            if (lowerAxis && upperAxis && lowerAxis.domain && upperAxis.domain) {
                                const minY = lowerAxis.domain[0] + 0.05;
                                const maxY = upperAxis.domain[1] - 0.05;
                                const clampedY = Math.max(minY, Math.min(maxY, normalizedY));
                                
                                update[lowerAxisKey + '.domain'] = [lowerAxis.domain[0], clampedY];
                                update[upperAxisKey + '.domain'] = [clampedY, upperAxis.domain[1]];
                                
                                Plotly.relayout(gd, update).catch(err => {
                                    console.error('❌ Relayout error:', err);
                                });
                            }
                        } else {
                            const gd = plotlyDiv;
                            if (!gd._fullLayout) return;
                            
                            const fullLayout = gd._fullLayout;
                            const rect = gd.getBoundingClientRect();
                            const mouseY = e.clientY - rect.top;
                            
                            let nearBorder = false;
                            
                            for (let i = 1; i <= 10; i++) {
                                const lowerAxisKey = i === 1 ? 'yaxis' : 'yaxis' + i;
                                const upperAxisKey = 'yaxis' + (i + 1);
                                
                                const lowerAxis = fullLayout[lowerAxisKey];
                                const upperAxis = fullLayout[upperAxisKey];
                                
                                if (lowerAxis && upperAxis && lowerAxis.domain && upperAxis.domain) {
                                    const borderY = rect.height * (1 - lowerAxis.domain[1]);
                                    
                                    if (Math.abs(mouseY - borderY) < 5) {
                                        nearBorder = true;
                                        plotlyDiv.style.cursor = 'ns-resize';
                                        break;
                                    }
                                }
                            }
                            
                            if (!nearBorder) {
                                plotlyDiv.style.cursor = '';
                            }
                        }
                    });
                    
                    // Mousedown to start dragging
                    plotlyDiv.addEventListener('mousedown', function(e) {
                        const gd = plotlyDiv;
                        if (!gd._fullLayout) return;
                        
                        const fullLayout = gd._fullLayout;
                        const rect = gd.getBoundingClientRect();
                        const mouseY = e.clientY - rect.top;
                        
                        for (let i = 1; i <= 10; i++) {
                            const lowerAxisKey = i === 1 ? 'yaxis' : 'yaxis' + i;
                            const upperAxisKey = 'yaxis' + (i + 1);
                            
                            const lowerAxis = fullLayout[lowerAxisKey];
                            const upperAxis = fullLayout[upperAxisKey];
                            
                            if (lowerAxis && upperAxis && lowerAxis.domain && upperAxis.domain) {
                                const borderY = rect.height * (1 - lowerAxis.domain[1]);
                                
                                if (Math.abs(mouseY - borderY) < 5) {
                                    isDragging = true;
                                    dragBorderIndex = i - 1;
                                    e.preventDefault();
                                    e.stopPropagation();
                                    break;
                                }
                            }
                        }
                    });
                    
                    // Mouseup to stop dragging
                    document.addEventListener('mouseup', function(e) {
                        if (isDragging) {
                            isDragging = false;
                            dragBorderIndex = -1;
                            plotlyDiv.style.cursor = '';
                        }
                    });
                    
                    console.log('✅ Draggable subplot borders ENABLED');
                };
                
                if (document.readyState === 'complete') {
                    setTimeout(window.addDraggableSubplotBorders, 500);
                } else {
                    window.addEventListener('load', function() {
                        setTimeout(window.addDraggableSubplotBorders, 500);
                    });
                }
                
                setTimeout(function() {
                    if (document.querySelector('.js-plotly-plot')) {
                        window.addDraggableSubplotBorders();
                    }
                }, 2000);
            }
            
            // ============================================================
            // AUTO-RESIZE PLOTLY GRAPHS WHEN CONTAINER IS RESIZED
            // ============================================================
            if (typeof window.setupGraphResizing === 'undefined') {
                window.setupGraphResizing = function() {
                    console.log('🔧 Setting up graph auto-resizing...');
                    
                    // Map of container IDs to their graph IDs
                    const containers = document.querySelectorAll('.resizable-graph-container');
                    
                    containers.forEach(container => {
                        // Find the graph element inside this container
                        const graphDiv = container.querySelector('.js-plotly-plot');
                        
                        if (!graphDiv) {
                            console.warn('⚠️ No graph found in resizable container');
                            return;
                        }
                        
                        // Use ResizeObserver to watch for container size changes
                        const resizeObserver = new ResizeObserver(entries => {
                            for (let entry of entries) {
                                // Get the new height of the container
                                const newHeight = entry.contentRect.height;
                                
                                if (newHeight > 0 && graphDiv.layout) {
                                    console.log(`📏 Container resized to ${newHeight}px, updating graph...`);
                                    
                                    // Update the Plotly graph to match the container height
                                    Plotly.relayout(graphDiv, {
                                        height: newHeight
                                    }).catch(err => {
                                        console.error('❌ Error resizing graph:', err);
                                    });
                                }
                            }
                        });
                        
                        // Start observing the container
                        resizeObserver.observe(container);
                        console.log('✅ Resize observer attached to container');
                    });
                };
                
                // Attach resize observers after graphs load
                if (document.readyState === 'complete') {
                    setTimeout(window.setupGraphResizing, 1000);
                } else {
                    window.addEventListener('load', function() {
                        setTimeout(window.setupGraphResizing, 1000);
                    });
                }
                
                setTimeout(function() {
                    if (document.querySelectorAll('.resizable-graph-container').length > 0) {
                        window.setupGraphResizing();
                    }
                }, 2500);
            }
        </script>
    </body>
</html>
'''


def create_figure(df, view_state=None):
    """Create the candlestick figure."""
    # Create candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
            increasing_line_color=config.COLORS["candle_up"],
            decreasing_line_color=config.COLORS["candle_down"],
        )
    ])
    
    # Update layout with theme and settings
    fig.update_layout(
        title={
            "text": f"{config.APP_TITLE} | Shift+Scroll: Y-Zoom | Alt+Click: Fit | DblClick: Reset",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16, "color": config.COLORS["text"]}
        },
        height=config.CHART_HEIGHT,
        template="plotly_dark",
        paper_bgcolor=config.COLORS["paper"],
        plot_bgcolor=config.COLORS["background"],
        font={"color": config.COLORS["text"]},
        hovermode="x unified",
        showlegend=True,
        xaxis={
            "rangeslider": {"visible": False},
            "gridcolor": config.COLORS["grid"],
            "showgrid": True,
        },
        yaxis={
            "gridcolor": config.COLORS["grid"],
            "showgrid": True,
            "fixedrange": False,  # Allow Y-axis zooming
        },
        margin={"l": 60, "r": 60, "t": 80, "b": 60},
    )
    
    # Restore view state if available
    if view_state:
        layout_updates = {}
        
        # Restore X-axis range
        if 'xaxis.range' in view_state:
            layout_updates['xaxis'] = {'range': view_state['xaxis.range'], 'autorange': False}
        elif 'xaxis.range[0]' in view_state and 'xaxis.range[1]' in view_state:
            x_range = [view_state['xaxis.range[0]'], view_state['xaxis.range[1]']]
            layout_updates['xaxis'] = {'range': x_range, 'autorange': False}
        
        # Restore Y-axis range
        if 'yaxis.range' in view_state:
            layout_updates['yaxis'] = {'range': view_state['yaxis.range'], 'autorange': False}
        elif 'yaxis.range[0]' in view_state and 'yaxis.range[1]' in view_state:
            y_range = [view_state['yaxis.range[0]'], view_state['yaxis.range[1]']]
            layout_updates['yaxis'] = {'range': y_range, 'autorange': False}
        
        if layout_updates:
            fig.update_layout(**layout_updates)
    
    return fig


# Generate initial figures for the layout
_initial_df = load_data()
_initial_figure = create_figure(_initial_df)

# Create second figure (you can customize this with different data/indicators)
_initial_figure_2 = create_figure(_initial_df)
_initial_figure_2.update_layout(
    height=config.CHART_HEIGHT_SECONDARY,
    title={
        "text": "Secondary Chart | Shift+Scroll: Y-Zoom | Alt+Click: Fit",
        "x": 0.5,
        "xanchor": "center",
        "font": {"size": 14, "color": config.COLORS["text"]}
    }
)


# App Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1(config.APP_TITLE, className="text-center mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            # Main chart - resizable
            html.Div([
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=[
                        dcc.Graph(
                            id="main-chart",
                            figure=_initial_figure,
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                                "scrollZoom": False,  # Disabled - using Shift+Scroll instead
                            },
                            style={"height": "100%", "width": "100%"}
                        )
                    ]
                ),
            ], className="resizable-graph-container", style={"height": f"{config.CHART_HEIGHT}px"}),
            
            # Secondary chart - resizable
            html.Div([
                dcc.Loading(
                    id="loading-2",
                    type="default",
                    children=[
                        dcc.Graph(
                            id="secondary-chart",
                            figure=_initial_figure_2,
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                                "scrollZoom": False,
                            },
                            style={"height": "100%", "width": "100%"}
                        )
                    ]
                ),
            ], className="resizable-graph-container", style={"height": f"{config.CHART_HEIGHT_SECONDARY}px"}),
        ], width=10),
        
        # Right sidebar - Controls
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.Strong("Controls"), style={"padding": "8px"}),
                dbc.CardBody([
                    html.P("Interactive Features:", className="fw-bold mb-2"),
                    html.Ul([
                        html.Li("Shift+Scroll: Y-zoom"),
                        html.Li("Shift+Alt+Scroll: Fast Y-zoom"),
                        html.Li("Alt+Click: Auto-fit Y"),
                        html.Li("Drag corner: Resize chart"),
                        html.Li("Double-click: Reset"),
                        html.Li("Drag: Pan"),
                    ], style={"fontSize": "0.85rem"}),
                    
                    html.Hr(),
                    
                    dbc.Button(
                        "Refresh Data",
                        id="refresh-button",
                        color="primary",
                        className="w-100",
                        size="sm"
                    ),
                ], style={"padding": "10px"})
            ], style={"position": "sticky", "top": "20px"}),
        ], width=2),
    ]),
    
    # Store for view state persistence
    dcc.Store(id="chart-view-state", data={}, storage_type='session'),
    
], fluid=True, style={
    "backgroundColor": config.COLORS["background"],
    "minHeight": "100vh",
    "padding": "20px"
})


@app.callback(
    Output("chart-view-state", "data"),
    Input("main-chart", "relayoutData"),
    State("chart-view-state", "data"),
    prevent_initial_call=True
)
def store_view_state(relayout_data, current_state):
    """Store zoom/pan state for persistence across updates."""
    if not relayout_data or relayout_data.keys() == {'autosize'}:
        return dash.no_update
    
    new_state = current_state.copy() if current_state else {}
    
    for key, value in relayout_data.items():
        if 'xaxis.range' in key or 'yaxis' in key:
            new_state[key] = value
    
    return new_state


@app.callback(
    [Output("main-chart", "figure"),
     Output("secondary-chart", "figure")],
    Input("refresh-button", "n_clicks"),
    State("chart-view-state", "data"),
)
def update_charts(n_clicks, view_state):
    """Create and update both candlestick charts."""
    df = load_data()
    
    # Main chart
    fig_main = create_figure(df, view_state)
    
    # Secondary chart (smaller)
    fig_secondary = create_figure(df, view_state)
    fig_secondary.update_layout(
        height=config.CHART_HEIGHT_SECONDARY,
        title={
            "text": "Secondary Chart | Shift+Scroll: Y-Zoom | Alt+Click: Fit",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 14, "color": config.COLORS["text"]}
        }
    )
    
    return fig_main, fig_secondary


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"🚀 Starting {config.APP_TITLE}")
    print(f"{'='*60}")
    print(f"🌐 Open browser to: http://{config.APP_HOST}:{config.APP_PORT}")
    print(f"{'='*60}\n")
    
    app.run(
        debug=config.APP_DEBUG,
        host=config.APP_HOST,
        port=config.APP_PORT
    )

