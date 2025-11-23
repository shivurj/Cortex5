"""Stock universe definitions for Cortex5.

Contains lists of stocks available for analysis and backtesting.
"""

from typing import Dict, Optional

# Top 30 S&P 500 stocks by market cap (as of 2024)
SP500_TOP_30 = [
    'AAPL',   # Apple Inc.
    'MSFT',   # Microsoft Corporation
    'GOOGL',  # Alphabet Inc. Class A
    'AMZN',   # Amazon.com Inc.
    'NVDA',   # NVIDIA Corporation
    'META',   # Meta Platforms Inc.
    'TSLA',   # Tesla Inc.
    'BRK.B',  # Berkshire Hathaway Inc. Class B
    'UNH',    # UnitedHealth Group Inc.
    'JNJ',    # Johnson & Johnson
    'V',      # Visa Inc.
    'XOM',    # Exxon Mobil Corporation
    'WMT',    # Walmart Inc.
    'JPM',    # JPMorgan Chase & Co.
    'PG',     # Procter & Gamble Co.
    'MA',     # Mastercard Inc.
    'HD',     # The Home Depot Inc.
    'CVX',    # Chevron Corporation
    'MRK',    # Merck & Co. Inc.
    'ABBV',   # AbbVie Inc.
    'KO',     # The Coca-Cola Company
    'PEP',    # PepsiCo Inc.
    'AVGO',   # Broadcom Inc.
    'COST',   # Costco Wholesale Corporation
    'LLY',    # Eli Lilly and Company
    'TMO',    # Thermo Fisher Scientific Inc.
    'MCD',    # McDonald's Corporation
    'CSCO',   # Cisco Systems Inc.
    'ACN',    # Accenture plc
    'ADBE',   # Adobe Inc.
]

# Stock metadata: company name and sector
STOCK_INFO: Dict[str, Dict[str, str]] = {
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology'},
    'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology'},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology'},
    'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical'},
    'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology'},
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Cyclical'},
    'BRK.B': {'name': 'Berkshire Hathaway Inc.', 'sector': 'Financial Services'},
    'UNH': {'name': 'UnitedHealth Group Inc.', 'sector': 'Healthcare'},
    'JNJ': {'name': 'Johnson & Johnson', 'sector': 'Healthcare'},
    'V': {'name': 'Visa Inc.', 'sector': 'Financial Services'},
    'XOM': {'name': 'Exxon Mobil Corporation', 'sector': 'Energy'},
    'WMT': {'name': 'Walmart Inc.', 'sector': 'Consumer Defensive'},
    'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
    'PG': {'name': 'Procter & Gamble Co.', 'sector': 'Consumer Defensive'},
    'MA': {'name': 'Mastercard Inc.', 'sector': 'Financial Services'},
    'HD': {'name': 'The Home Depot Inc.', 'sector': 'Consumer Cyclical'},
    'CVX': {'name': 'Chevron Corporation', 'sector': 'Energy'},
    'MRK': {'name': 'Merck & Co. Inc.', 'sector': 'Healthcare'},
    'ABBV': {'name': 'AbbVie Inc.', 'sector': 'Healthcare'},
    'KO': {'name': 'The Coca-Cola Company', 'sector': 'Consumer Defensive'},
    'PEP': {'name': 'PepsiCo Inc.', 'sector': 'Consumer Defensive'},
    'AVGO': {'name': 'Broadcom Inc.', 'sector': 'Technology'},
    'COST': {'name': 'Costco Wholesale Corporation', 'sector': 'Consumer Defensive'},
    'LLY': {'name': 'Eli Lilly and Company', 'sector': 'Healthcare'},
    'TMO': {'name': 'Thermo Fisher Scientific Inc.', 'sector': 'Healthcare'},
    'MCD': {'name': "McDonald's Corporation", 'sector': 'Consumer Cyclical'},
    'CSCO': {'name': 'Cisco Systems Inc.', 'sector': 'Technology'},
    'ACN': {'name': 'Accenture plc', 'sector': 'Technology'},
    'ADBE': {'name': 'Adobe Inc.', 'sector': 'Technology'},
}


def get_stock_info(ticker: str) -> Optional[Dict[str, str]]:
    """
    Get company name and sector for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        Dictionary with 'name' and 'sector' keys, or None if ticker not found
    """
    return STOCK_INFO.get(ticker.upper())


def get_all_stocks() -> list:
    """
    Get list of all available stocks with their metadata.
    
    Returns:
        List of dictionaries with ticker, name, and sector
    """
    return [
        {
            'ticker': ticker,
            'name': info['name'],
            'sector': info['sector']
        }
        for ticker, info in STOCK_INFO.items()
    ]
