"""
Utility functions for currency conversion and formatting
"""

import re
from typing import Union


def convert_vnd_amount(amount_str: str) -> float:
    """
    Convert Vietnamese Dong shorthand notation to actual number.
    Examples: 400k -> 400000, 1tr -> 1000000, 2.5m -> 2500000
    
    Args:
        amount_str: String representation of VND amount
        
    Returns:
        float: Converted amount
    """
    amount_str = amount_str.lower().strip()
    
    # Remove currency symbols and spaces
    amount_str = re.sub(r'[đvnd\s]', '', amount_str)
    
    multiplier = 1
    number_part = amount_str
    
    # Check for Vietnamese suffixes
    if amount_str.endswith('tr'):  # triệu = 1,000,000
        multiplier = 1_000_000
        number_part = amount_str[:-2]
    elif amount_str.endswith('m'):  # million = 1,000,000
        multiplier = 1_000_000
        number_part = amount_str[:-1]
    elif amount_str.endswith('k'):  # thousand = 1,000
        multiplier = 1_000
        number_part = amount_str[:-1]
    
    try:
        base_amount = float(number_part)
        return base_amount * multiplier
    except ValueError:
        return 0.0


def format_vnd_amount(amount: Union[int, float]) -> str:
    """
    Format VND amount with proper thousand separators
    
    Args:
        amount: Numeric amount
        
    Returns:
        str: Formatted amount string
    """
    return f"{amount:,.0f} VND"


def is_vnd_amount(value: str) -> bool:
    """
    Check if value is a VND amount string
    
    Args:
        value: String to check
        
    Returns:
        bool: True if it's a VND amount
    """
    return bool(re.match(r'\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)$', value.lower()))


def detect_language(text: str) -> str:
    """
    Detect if text is Vietnamese or English
    
    Args:
        text: Text to analyze
        
    Returns:
        str: 'vietnamese' or 'english'
    """
    vietnamese_chars = bool(re.search(
        r'[àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹ]', 
        text
    ))
    return 'vietnamese' if vietnamese_chars else 'english'


def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra spaces and trimming
    
    Args:
        text: Text to normalize
        
    Returns:
        str: Normalized text
    """
    return re.sub(r'\s+', ' ', text.strip())


def extract_amount_from_text(text: str) -> tuple:
    """
    Extract amount and currency from text
    
    Args:
        text: Text containing amount
        
    Returns:
        tuple: (amount, currency) or (None, None) if not found
    """
    # VND patterns
    vnd_patterns = [
        r'(\d+(?:\.\d+)?)\s*(tr|m|k)(?:\s|$|[^\w])',
        r'(\d+(?:\.\d+)?)\s*(đ|vnd)(?:\s|$|[^\w])',
    ]
    
    for pattern in vnd_patterns:
        match = re.search(pattern, text.lower())
        if match:
            amount_str = match.group(1) + match.group(2)
            return convert_vnd_amount(amount_str), 'VND'
    
    # USD patterns
    usd_patterns = [
        r'\$(\d+(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)\s*(?:dollars?|usd)',
    ]
    
    for pattern in usd_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1)), 'USD'
    
    # EUR patterns
    eur_patterns = [
        r'€(\d+(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)\s*(?:euros?|eur)',
    ]
    
    for pattern in eur_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1)), 'EUR'
    
    # GBP patterns
    gbp_patterns = [
        r'£(\d+(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)\s*(?:pounds?|gbp)',
    ]
    
    for pattern in gbp_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1)), 'GBP'
    
    return None, None