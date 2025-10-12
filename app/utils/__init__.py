"""
Utility functions for the application
"""

from .currency import (
    convert_vnd_amount,
    format_vnd_amount,
    is_vnd_amount,
    detect_language,
    normalize_text,
    extract_amount_from_text
)

from .text_processing import (
    extract_key_value_pairs,
    clean_description,
    categorize_vietnamese_item,
    extract_vietnamese_transaction_parts
)

from .validation import (
    is_valid_json,
    is_command,
    is_transaction_message,
    validate_amount,
    validate_currency,
    clean_and_validate_text
)

__all__ = [
    # Currency utils
    'convert_vnd_amount',
    'format_vnd_amount',
    'is_vnd_amount',
    'detect_language',
    'normalize_text',
    'extract_amount_from_text',
    
    # Text processing
    'extract_key_value_pairs',
    'clean_description',
    'categorize_vietnamese_item',
    'extract_vietnamese_transaction_parts',
    
    # Validation
    'is_valid_json',
    'is_command',
    'is_transaction_message',
    'validate_amount',
    'validate_currency',
    'clean_and_validate_text'
]