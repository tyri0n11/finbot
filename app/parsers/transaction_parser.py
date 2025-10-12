"""
Transaction Parser - Specialized parser for financial transactions with Vietnamese support
"""

import re
from datetime import datetime
from interfaces import IMessageParser, ParseResult, MessageType
from utils.currency import convert_vnd_amount, extract_amount_from_text
from utils.text_processing import (
    categorize_vietnamese_item, 
    extract_vietnamese_transaction_parts,
    extract_vietnamese_time_reference
)
from utils.validation import is_transaction_message


class TransactionParser(IMessageParser):
    """Parser for financial transaction messages with Vietnamese language support"""
    
    def __init__(self):
        # Vietnamese transaction verbs
        self.vietnamese_verbs = [
            'mua', 'chi', 'trả', 'mất', 'tốn', 'đi', 'ăn', 'uống', 
            'thuê', 'đóng', 'nạp', 'rút', 'chuyển', 'gửi'
        ]
    
    def can_parse(self, message: str) -> bool:
        """Check if message is a transaction"""
        return is_transaction_message(message)
    
    def parse(self, message: str) -> ParseResult:
        """Parse transaction message"""
        if not self.can_parse(message):
            return ParseResult(
                message_type=MessageType.UNKNOWN,
                data={},
                original_message=message,
                errors=["Not a transaction message"],
                parser_name="TransactionParser"
            )
        
        # Try Vietnamese parsing first
        vietnamese_result = self._parse_vietnamese_transaction(message)
        if vietnamese_result:
            return ParseResult(
                message_type=MessageType.TRANSACTION,
                data=vietnamese_result,
                original_message=message,
                confidence=0.9,
                parser_name="TransactionParser"
            )
        
        # Try English parsing
        english_result = self._parse_english_transaction(message)
        if english_result:
            return ParseResult(
                message_type=MessageType.TRANSACTION,
                data=english_result,
                original_message=message,
                confidence=0.8,
                parser_name="TransactionParser"
            )
        
        return ParseResult(
            message_type=MessageType.UNKNOWN,
            data={},
            original_message=message,
            errors=["Could not parse transaction"],
            parser_name="TransactionParser"
        )
    
    def _parse_vietnamese_transaction(self, message: str) -> dict:
        """Parse Vietnamese transaction messages with enhanced features"""
        result = {}
        
        # Use the enhanced transaction parts extraction
        transaction_parts = extract_vietnamese_transaction_parts(message)
        
        # Extract transaction type (income/expense)
        if 'type' in transaction_parts:
            result['transaction_type'] = transaction_parts['type']
        
        # Extract verb
        if 'verb' in transaction_parts:
            result['verb'] = transaction_parts['verb']
        
        # Extract amount and currency
        if 'amount' in transaction_parts and 'unit' in transaction_parts:
            amount = transaction_parts['amount']
            unit = transaction_parts['unit']
            
            # Convert VND amounts
            if unit in ['tr', 'm']:
                amount = amount * 1_000_000
            elif unit in ['k']:
                amount = amount * 1_000
            
            result['amount'] = amount
            result['currency'] = 'VND' if unit in ['tr', 'm', 'k', 'đ', 'vnd'] else unit.upper()
        else:
            # Fallback to old method
            amount, currency = extract_amount_from_text(message)
            if amount is not None:
                result['amount'] = amount
                result['currency'] = currency
        
        # Extract description/item
        if 'item' in transaction_parts:
            result['description'] = transaction_parts['item']
        
        # Extract category
        if 'category' in transaction_parts:
            result['category'] = transaction_parts['category']
        elif 'item' in transaction_parts:
            # Auto-categorize based on item
            category = categorize_vietnamese_item(transaction_parts['item'])
            if category:
                result['category'] = category
        
        # Extract time information
        if 'time' in transaction_parts:
            time_info = transaction_parts['time']
            result['time_reference'] = time_info
            if 'value' in time_info:
                result['date'] = time_info['value']
        
        # Add metadata
        if result:
            if 'date' not in result:
                result['date'] = datetime.now().strftime('%Y-%m-%d')
            result['raw_text'] = message
        
        return result
    
    def _parse_english_transaction(self, message: str) -> dict:
        """Parse English transaction messages"""
        result = {}
        
        # Extract amount and currency
        amount, currency = extract_amount_from_text(message)
        if amount is not None:
            result['amount'] = amount
            result['currency'] = currency
        
        # Extract description
        desc_patterns = [
            r'(?:for|bought|purchased)\s+([^.!?]+?)(?:\s+(?:at|from)\s+|\s*$)',
            r'(?:spent|paid).*?(?:for|on)\s+([^.!?]+?)(?:\s+(?:at|from)\s+|\s*$)',
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, message.lower())
            if match:
                desc = match.group(1).strip()
                # Clean description
                desc = re.sub(r'\d+(?:\.\d+)?\s*(?:dollars?|euros?|pounds?|usd|eur|gbp|\$|€|£)', '', desc).strip()
                if desc:
                    result['description'] = desc
                break
        
        # Add metadata
        if result:
            result['date'] = datetime.now().strftime('%Y-%m-%d')
            result['time'] = datetime.now().strftime('%H:%M')
            result['raw_text'] = message
            result['language'] = 'english'
        
        return result
    
    def get_priority(self) -> int:
        """Transaction parsing has medium priority"""
        return 2
    
    def get_name(self) -> str:
        """Get parser name"""
        return "TransactionParser"
