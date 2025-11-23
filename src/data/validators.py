"""Data validation utilities for market data quality checks."""

import pandas as pd
import numpy as np


class DataValidationError(Exception):
    """Custom exception for data validation failures."""
    pass


def validate_ohlcv_data(df: pd.DataFrame) -> bool:
    """
    Validate OHLCV data for integrity and consistency.
    
    Performs the following checks:
    1. Required columns exist
    2. No null values in critical columns (open, high, low, close)
    3. High >= Low for all rows
    4. Volume is non-negative
    5. Timestamps are in ascending order
    6. Prices are positive
    
    Args:
        df: DataFrame containing OHLCV data with columns:
            timestamp, open, high, low, close, volume
    
    Returns:
        True if all validations pass
        
    Raises:
        DataValidationError: If any validation check fails
    """
    # Check 1: Required columns exist
    required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise DataValidationError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    if df.empty:
        raise DataValidationError("DataFrame is empty")
    
    # Check 2: No null values in critical columns
    critical_columns = ['open', 'high', 'low', 'close']
    null_counts = df[critical_columns].isnull().sum()
    
    if null_counts.any():
        null_info = null_counts[null_counts > 0].to_dict()
        raise DataValidationError(
            f"Null values found in critical columns: {null_info}"
        )
    
    # Check 3: High >= Low for all rows
    invalid_hl = df[df['high'] < df['low']]
    if not invalid_hl.empty:
        raise DataValidationError(
            f"Found {len(invalid_hl)} rows where High < Low. "
            f"First occurrence at index {invalid_hl.index[0]}"
        )
    
    # Check 4: Volume is non-negative
    negative_volume = df[df['volume'] < 0]
    if not negative_volume.empty:
        raise DataValidationError(
            f"Found {len(negative_volume)} rows with negative volume. "
            f"First occurrence at index {negative_volume.index[0]}"
        )
    
    # Check 5: Timestamps are in ascending order
    if not df['timestamp'].is_monotonic_increasing:
        raise DataValidationError(
            "Timestamps are not in ascending order"
        )
    
    # Check 6: Prices are positive
    price_columns = ['open', 'high', 'low', 'close']
    for col in price_columns:
        non_positive = df[df[col] <= 0]
        if not non_positive.empty:
            raise DataValidationError(
                f"Found {len(non_positive)} rows with non-positive {col} prices. "
                f"First occurrence at index {non_positive.index[0]}"
            )
    
    # Check 7: Additional consistency checks
    # Open and Close should be between Low and High
    invalid_open = df[(df['open'] < df['low']) | (df['open'] > df['high'])]
    if not invalid_open.empty:
        raise DataValidationError(
            f"Found {len(invalid_open)} rows where Open is outside [Low, High] range. "
            f"First occurrence at index {invalid_open.index[0]}"
        )
    
    invalid_close = df[(df['close'] < df['low']) | (df['close'] > df['high'])]
    if not invalid_close.empty:
        raise DataValidationError(
            f"Found {len(invalid_close)} rows where Close is outside [Low, High] range. "
            f"First occurrence at index {invalid_close.index[0]}"
        )
    
    return True


def validate_price_continuity(df: pd.DataFrame, max_gap_pct: float = 0.5) -> bool:
    """
    Check for unrealistic price gaps between consecutive periods.
    
    Args:
        df: DataFrame with OHLCV data
        max_gap_pct: Maximum allowed percentage gap (default 50%)
        
    Returns:
        True if no excessive gaps found
        
    Raises:
        DataValidationError: If price gaps exceed threshold
    """
    if len(df) < 2:
        return True
    
    # Calculate percentage change in close prices
    df_sorted = df.sort_values('timestamp')
    pct_change = df_sorted['close'].pct_change().abs()
    
    # Find gaps exceeding threshold
    excessive_gaps = pct_change[pct_change > max_gap_pct]
    
    if not excessive_gaps.empty:
        max_gap = excessive_gaps.max()
        gap_index = excessive_gaps.idxmax()
        raise DataValidationError(
            f"Found excessive price gap of {max_gap*100:.1f}% at index {gap_index}. "
            f"This may indicate data quality issues or stock splits."
        )
    
    return True


def sanitize_ohlcv_data(df: pd.DataFrame, drop_nulls: bool = True) -> pd.DataFrame:
    """
    Clean and sanitize OHLCV data.
    
    Args:
        df: DataFrame with potentially dirty OHLCV data
        drop_nulls: Whether to drop rows with null values
        
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Remove duplicates based on timestamp
    df_clean = df_clean.drop_duplicates(subset=['timestamp'], keep='first')
    
    # Sort by timestamp
    df_clean = df_clean.sort_values('timestamp').reset_index(drop=True)
    
    # Handle null values
    if drop_nulls:
        df_clean = df_clean.dropna(subset=['open', 'high', 'low', 'close'])
    else:
        # Forward fill for missing values
        df_clean[['open', 'high', 'low', 'close']] = df_clean[['open', 'high', 'low', 'close']].fillna(method='ffill')
    
    # Ensure volume is non-negative (replace negative with 0)
    df_clean['volume'] = df_clean['volume'].clip(lower=0)
    
    return df_clean
