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
        'thu nhập': [
            'lương', 'thưởng', 'bán', 'nhận', 'thu', 'salary', 'bonus', 'income',
            'tiền lương', 'tiền thưởng', 'tiền bán', 'được trả', 'được nhận',
            'freelance', 'làm thêm', 'kiếm được', 'thu nhập', 'doanh thu',
            'commission', 'hoa hồng', 'tiền công', 'gig', 'part-time', 'overtime'
        ],
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
            'laptop', 'máy tính', 'tai nghe', 'charger', 'sạc', 'case',
            'clothes', 'shoes', 'bag', 'cosmetics', 'watch', 'jewelry', 'phone'
        ],
        'gia dụng': [
            'rau', 'thịt', 'cá', 'trứng', 'sữa', 'gạo', 'dầu ăn', 'nước mắm',
            'đường', 'muối', 'gia vị', 'grocery', 'siêu thị', 'market'
        ],
        'giải trí': [
            'phim', 'karaoke', 'game', 'sách', 'magazine', 'concert', 'show',
            'vé', 'ticket', 'entertainment', 'party', 'bar', 'club', 'movie', 'cá cảnh'
        ],
        'sức khỏe': [
            'thuốc', 'bác sĩ', 'khám bệnh', 'nha khoa', 'massage', 'gym',
            'vitamin', 'medicine', 'hospital', 'clinic', 'dental', 'doctor'
        ],
        'tiện ích': [
            'điện', 'nước', 'internet', 'điện thoại', 'gas', 'wifi', 'bill',
            'hóa đơn', 'utilities', 'electric', 'water', 'phone bill', 'khác'
        ]
    }
    
    for category, keywords in categories.items():
        # Sort keywords by length (descending) to match longer phrases first
        sorted_keywords = sorted(keywords, key=len, reverse=True)
        for keyword in sorted_keywords:
            # Split keyword into words and create pattern for whole word matching
            words = keyword.lower().split()
            if len(words) == 1:
                # Single word - use simple word boundary
                pattern = r'\b' + re.escape(words[0]) + r'\b'
            else:
                # Multi-word - create pattern that matches each word with word boundaries
                word_patterns = [r'\b' + re.escape(word) + r'\b' for word in words]
                pattern = r'\s+'.join(word_patterns)
            
            if re.search(pattern, text_lower):
                return category
    
    return None


def extract_vietnamese_time_reference(text: str) -> Dict[str, str]:
    """
    Extract time references from Vietnamese text
    
    Args:
        text: Text containing time references
        
    Returns:
        dict: Extracted time information with 'type' and 'value' keys
    """
    import datetime
    from datetime import timedelta
    
    text_lower = text.lower().strip()
    today = datetime.date.today()
    
    # Direct date patterns (DD/MM, DD/MM/YYYY, etc.)
    date_patterns = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
        r'(\d{1,2})/(\d{1,2})',          # DD/MM
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
        r'(\d{1,2})-(\d{1,2})',          # DD-MM
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # Full date
                day, month, year = groups
                return {
                    'type': 'specific_date',
                    'value': f"{year}-{month.zfill(2)}-{day.zfill(2)}",
                    'original': match.group(0)
                }
            elif len(groups) == 2:  # Day/Month only
                day, month = groups
                current_year = today.year
                return {
                    'type': 'specific_date',
                    'value': f"{current_year}-{month.zfill(2)}-{day.zfill(2)}",
                    'original': match.group(0)
                }
    
    # Relative time references
    relative_patterns = {
        'hôm nay': {'type': 'relative', 'days': 0},
        'today': {'type': 'relative', 'days': 0},
        'hôm qua': {'type': 'relative', 'days': -1},
        'yesterday': {'type': 'relative', 'days': -1},
        'hôm kia': {'type': 'relative', 'days': -2},
        'ngày mai': {'type': 'relative', 'days': 1},
        'tomorrow': {'type': 'relative', 'days': 1},
        'tuần này': {'type': 'week', 'weeks': 0},
        'this week': {'type': 'week', 'weeks': 0},
        'tuần trước': {'type': 'week', 'weeks': -1},
        'last week': {'type': 'week', 'weeks': -1},
        'tuần sau': {'type': 'week', 'weeks': 1},
        'next week': {'type': 'week', 'weeks': 1},
        'tháng này': {'type': 'month', 'months': 0},
        'this month': {'type': 'month', 'months': 0},
        'tháng trước': {'type': 'month', 'months': -1},
        'last month': {'type': 'month', 'months': -1},
        'tháng sau': {'type': 'month', 'months': 1},
        'next month': {'type': 'month', 'months': 1},
    }
    
    for phrase, info in relative_patterns.items():
        if phrase in text_lower:
            if info['type'] == 'relative':
                target_date = today + timedelta(days=info['days'])
                return {
                    'type': 'relative_date',
                    'value': target_date.strftime('%Y-%m-%d'),
                    'original': phrase,
                    'relative_days': info['days']
                }
            elif info['type'] == 'week':
                # Calculate start of week (Monday)
                days_since_monday = today.weekday()
                week_start = today - timedelta(days=days_since_monday)
                target_week = week_start + timedelta(weeks=info['weeks'])
                return {
                    'type': 'relative_week',
                    'value': target_week.strftime('%Y-%m-%d'),
                    'original': phrase,
                    'relative_weeks': info['weeks']
                }
            elif info['type'] == 'month':
                return {
                    'type': 'relative_month',
                    'value': today.strftime('%Y-%m'),
                    'original': phrase,
                    'relative_months': info['months']
                }
    
    # Number of days ago/later patterns
    days_ago_patterns = [
        r'(\d+)\s*(?:ngày|days?)\s*(?:trước|ago)',
        r'(\d+)\s*(?:ngày|days?)\s*(?:sau|later)',
    ]
    
    for pattern in days_ago_patterns:
        match = re.search(pattern, text_lower)
        if match:
            days = int(match.group(1))
            if 'trước' in match.group(0) or 'ago' in match.group(0):
                days = -days
            target_date = today + timedelta(days=days)
            return {
                'type': 'relative_days',
                'value': target_date.strftime('%Y-%m-%d'),
                'original': match.group(0),
                'relative_days': days
            }
    
    return None


def extract_vietnamese_transaction_parts(message: str) -> Dict[str, str]:
    """
    Extract parts from Vietnamese transaction messages
    
    Args:
        message: Vietnamese transaction message
        
    Returns:
        dict: Extracted parts (verb, item, amount, time, type, etc.)
    """
    result = {}
    message_lower = message.lower().strip()
    
    # Extract time reference first
    time_info = extract_vietnamese_time_reference(message)
    if time_info:
        result['time'] = time_info
    
    # Extract verb - including income verbs
    vietnamese_verbs = [
        # Expense verbs
        'mua', 'chi', 'trả', 'mất', 'tốn', 'đi', 'ăn', 'uống', 
        'thuê', 'đóng', 'nạp', 'rút', 'chuyển', 'gửi',
        # Income verbs
        'nhận', 'được', 'thu', 'kiếm', 'bán', 'lương', 'thưởng',
        'earn', 'receive', 'get', 'salary', 'bonus', 'income'
    ]
    
    # Income indicators
    income_verbs = [
        'nhận', 'được', 'thu', 'kiếm', 'bán', 'lương', 'thưởng',
        'earn', 'receive', 'get', 'salary', 'bonus', 'income'
    ]
    
    for verb in vietnamese_verbs:
        if message_lower.startswith(verb) or f' {verb} ' in message_lower:
            result['verb'] = verb
            # Determine transaction type
            if verb in income_verbs:
                result['type'] = 'income'
            else:
                result['type'] = 'expense'
            break
    
    # If no explicit verb found, try to detect based on context
    if 'type' not in result:
        income_keywords = [
            'lương', 'thưởng', 'thu nhập', 'kiếm được', 'bán được',
            'salary', 'bonus', 'income', 'earned', 'received'
        ]
        for keyword in income_keywords:
            if keyword in message_lower:
                result['type'] = 'income'
                break
        else:
            result['type'] = 'expense'  # Default to expense
    
    # Extract item/description using enhanced patterns
    desc_patterns = [
        # Expense patterns
        r'(?:mua|chi|trả|tốn|đi)\s+([^0-9]+?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
        r'(?:ăn|uống)\s+([^0-9]+?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
        # Income patterns
        r'(?:nhận|được|thu|kiếm|bán)\s+([^0-9]+?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
        r'(?:lương|thưởng)\s+([^0-9]*?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
        # General patterns
        r'^([^0-9]+?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
        r'([^0-9]+?)\s+\d+(?:\.\d+)?(?:tr|m|k|đ|vnd)',
    ]
    
    for pattern in desc_patterns:
        match = re.search(pattern, message_lower)
        if match:
            item = match.group(1).strip()
            if item:  # Only set if not empty
                result['item'] = re.sub(r'\s+', ' ', item)
                break
    
    # Extract amount patterns
    amount_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:tr|triệu)',  # millions
        r'(\d+(?:\.\d+)?)\s*(?:m|tr)',      # millions  
        r'(\d+(?:\.\d+)?)\s*(?:k|nghìn)',   # thousands
        r'(\d+(?:\.\d+)?)\s*(?:đ|vnd)',     # dong
        r'(\d+(?:\.\d+)?)\s*(?:usd|\$)',    # dollars
        r'(\d+(?:\.\d+)?)\s*(?:eur|€)',     # euros
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, message_lower)
        if match:
            amount = float(match.group(1))
            unit = match.group(0).replace(match.group(1), '').strip()
            result['amount'] = amount
            result['unit'] = unit
            break
    
    # Auto-categorize if no explicit category
    if 'item' in result:
        category = categorize_vietnamese_item(result['item'])
        if category:
            result['category'] = category
    
    return result