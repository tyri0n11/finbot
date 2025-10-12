"""
Basic Parsers - JSON, Key-Value, and Text parsers
"""

import json
from interfaces.parser import IMessageParser
from model import ParseResult, MessageType
from utils.validation import is_valid_json, is_command
from utils.text_processing import extract_key_value_pairs
from utils.currency import is_vnd_amount, convert_vnd_amount, detect_language


class JSONParser(IMessageParser):
    """Parser for JSON messages"""
    
    def can_parse(self, message: str) -> bool:
        """Check if message is valid JSON"""
        return is_valid_json(message)
    
    def parse(self, message: str) -> ParseResult:
        """Parse JSON message"""
        try:
            data = json.loads(message.strip())
            return ParseResult(
                message_type=MessageType.JSON,
                data=data,
                original_message=message,
                confidence=1.0,
                parser_name="JSONParser"
            )
        except json.JSONDecodeError as e:
            return ParseResult(
                message_type=MessageType.UNKNOWN,
                data={},
                original_message=message,
                errors=[f"Invalid JSON: {str(e)}"],
                parser_name="JSONParser"
            )
    
    def get_priority(self) -> int:
        """JSON has high priority due to strict format"""
        return 2
    
    def get_name(self) -> str:
        return "JSONParser"


class KeyValueParser(IMessageParser):
    """Parser for key-value pair messages with VND support"""
    
    def can_parse(self, message: str) -> bool:
        """Check if message contains key-value pairs"""
        pairs = extract_key_value_pairs(message)
        return len(pairs) >= 1
    
    def parse(self, message: str) -> ParseResult:
        """Parse key-value message"""
        result = extract_key_value_pairs(message)
        
        # Process VND amounts
        for key, value in result.items():
            if key in ['amount', 'cost', 'price', 'paid', 'spent'] and is_vnd_amount(value):
                result[key] = convert_vnd_amount(value)
                result['currency'] = 'VND'
        
        if result:
            return ParseResult(
                message_type=MessageType.KEY_VALUE,
                data=result,
                original_message=message,
                confidence=0.8,
                parser_name="KeyValueParser"
            )
        else:
            return ParseResult(
                message_type=MessageType.UNKNOWN,
                data={},
                original_message=message,
                errors=["No valid key-value pairs found"],
                parser_name="KeyValueParser"
            )
    
    def get_priority(self) -> int:
        """Key-value parsing has medium priority"""
        return 3
    
    def get_name(self) -> str:
        return "KeyValueParser"


class TextParser(IMessageParser):
    """Fallback parser for plain text messages"""
    
    def can_parse(self, message: str) -> bool:
        """Can always parse text (fallback parser)"""
        return bool(message.strip())
    
    def parse(self, message: str) -> ParseResult:
        """Parse text message"""
        text = message.strip()
        
        if not text:
            return ParseResult(
                message_type=MessageType.UNKNOWN,
                data={},
                original_message=message,
                errors=["Empty message"],
                parser_name="TextParser"
            )
        
        # Detect language
        language = detect_language(text)
        
        data = {
            'content': text,
            'word_count': len(text.split()),
            'char_count': len(text),
            'language': language
        }
        
        return ParseResult(
            message_type=MessageType.TEXT,
            data=data,
            original_message=message,
            confidence=0.5,
            parser_name="TextParser"
        )
    
    def get_priority(self) -> int:
        """Text parsing has lowest priority (fallback)"""
        return 10
    
    def get_name(self) -> str:
        return "TextParser"
