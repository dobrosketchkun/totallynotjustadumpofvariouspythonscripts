"""
Generate sample candlestick data for demonstration purposes.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_candles(num_candles=500, start_price=100.0, volatility=0.02):
    """
    Generate realistic sample OHLCV candlestick data.
    
    Args:
        num_candles: Number of candles to generate
        start_price: Starting price
        volatility: Price volatility (standard deviation as fraction of price)
    
    Returns:
        pd.DataFrame with columns: open, high, low, close, volume
    """
    np.random.seed(42)  # For reproducible data
    
    # Generate timestamps (1-hour intervals)
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=num_candles)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=num_candles)
    
    # Generate price data with realistic movements
    data = []
    current_price = start_price
    
    for i in range(num_candles):
        # Random walk with slight upward bias
        price_change = np.random.normal(0.0002, volatility)  # Slight upward drift
        current_price *= (1 + price_change)
        
        # Generate OHLC for this candle
        open_price = current_price
        close_price = current_price * (1 + np.random.normal(0, volatility * 0.5))
        
        # High and low based on open/close
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, volatility * 0.3)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, volatility * 0.3)))
        
        # Volume (random but somewhat realistic)
        volume = np.random.lognormal(10, 1)
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
        
        current_price = close_price
    
    df = pd.DataFrame(data, index=timestamps)
    return df


def load_data():
    """
    Load or generate sample data.
    Replace this function with your own data loading logic.
    
    Returns:
        pd.DataFrame with OHLCV data
    """
    return generate_sample_candles(num_candles=1000)

