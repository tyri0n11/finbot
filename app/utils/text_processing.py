"""
Text processing utilities
"""

import re
from typing import List, Dict


def extract_key_value_pairs(text: str) -> Dict[str, str]:
    """
    Extract key-value pairs from text in format "key: value"
    
    Args:
        text: Text containing key-value pairs
        
    Returns:
        dict: Extracted key-value pairs
    """
    result = {}
    lines = text.strip().splitlines()
    
    for line in lines:
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key and value:
                result[key] = value
    
    return result


def clean_description(text: str, remove_patterns: List[str] = None) -> str:
    """
    Clean description text by removing unwanted patterns
    
    Args:
        text: Text to clean
        remove_patterns: List of regex patterns to remove
        
    Returns:
        str: Cleaned text
    """
    if remove_patterns is None:
        remove_patterns = [
            r'\d+(?:\.\d+)?\s*(?:tr|m|k|vnd|đ|dollars?|euros?|pounds?|usd|eur|gbp|\$|€|£)',
            r'^\s*(?:mua|chi|trả|tốn|đi|ăn|uống|spent|paid|bought|purchased)\s*',
        ]
    
    cleaned = text
    for pattern in remove_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    return re.sub(r'\s+', ' ', cleaned).strip()


def categorize_vietnamese_item(text: str) -> str:
    """
    Auto-categorize Vietnamese items based on keywords
    
    Args:
        text: Text to categorize
        
    Returns:
        str: Category name or None
    """
    text_lower = text.lower()
    
    categories = {
        'ăn uống': [
            'bánh mì', 'phở', 'bún', 'cơm', 'mì', 'bánh', 'cháo', 'xôi', 'nem', 'chả',
            'gỏi', 'canh', 'thịt', 'gà', 'cá', 'tôm', 'cua', 'cà phê', 'trà', 'nước',
            'bia', 'rượu', 'sinh tố', 'nước ngọt', 'coca', 'pepsi', 'juice', 'milk tea',
            'trà sữa', 'bánh ngọt', 'kẹo', 'snack', 'chocolate', 'kem', 'cafe'
        ],
        'di chuyển': [
            'xe buýt', 'taxi', 'grab', 'uber', 'xăng', 'gửi xe', 'đậu xe', 'vé xe',
            'tàu', 'máy bay', 'xe ôm', 'bus', 'train', 'petrol', 'gas', 'parking'
        ],
        'mua sắm': [
            'quần áo', 'giày', 'túi', 'mỹ phẩm', 'nước hoa', 'đồng hồ', 'trang sức',
            'điện thoại', 'laptop', 'máy tính', 'tai nghe', 'charger', 'sạc', 'case',
            'clothes', 'shoes', 'bag', 'cosmetics', 'watch', 'jewelry', 'phone'
        ],
        'gia dụng': [
            'rau', 'thịt', 'cá', 'trứng', 'sữa', 'gạo', 'dầu ăn', 'nước mắm',
            'đường', 'muối', 'gia vị', 'grocery', 'siêu thị', 'market'
        ],
        'giải trí': [
            'phim', 'karaoke', 'game', 'sách', 'magazine', 'concert', 'show',
            'vé', 'ticket', 'entertainment', 'party', 'bar', 'club', 'movie'
        ],
        'sức khỏe': [
            'thuốc', 'bác sĩ', 'khám bệnh', 'nha khoa', 'massage', 'gym',
            'vitamin', 'medicine', 'hospital', 'clinic', 'dental', 'doctor'
        ],
        'tiện ích': [
            'điện', 'nước', 'internet', 'điện thoại', 'gas', 'wifi', 'bill',
            'hóa đơn', 'utilities', 'electric', 'water', 'phone bill'
        ]
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return category
    
    return None


def extract_vietnamese_transaction_parts(message: str) -> Dict[str, str]:
    """
    Extract parts from Vietnamese transaction messages
    
    Args:
        message: Vietnamese transaction message
        
    Returns:
        dict: Extracted parts (verb, item, amount, etc.)
    """
    result = {}
    message_lower = message.lower().strip()
    
    # Extract verb
    vietnamese_verbs = [
        'mua', 'chi', 'trả', 'mất', 'tốn', 'đi', 'ăn', 'uống', 
        'thuê', 'đóng', 'nạp', 'rút', 'chuyển', 'gửi'
    ]
    
    for verb in vietnamese_verbs:
        if message_lower.startswith(verb):
            result['verb'] = verb
            break
    
    # Extract item/description using patterns
    desc_patterns = [
        r'(?:mua|chi|trả|tốn|đi)\s+([^0-9]+?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
        r'^([^0-9]+?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
        r'(?:ăn|uống)\s+([^0-9]+?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
    ]
    
    for pattern in desc_patterns:
        match = re.search(pattern, message_lower)
        if match:
            item = match.group(1).strip()
            result['item'] = re.sub(r'\s+', ' ', item)
            break
    
    return result