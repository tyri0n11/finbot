"""
Core interfaces for the parser system using clean architecture principles
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List
from datetime import datetime


class MessageType(Enum):
    """Enumeration of message types that can be parsed"""
    COMMAND = "command"
    TRANSACTION = "transaction"
    JSON = "json"
    KEY_VALUE = "key_value"
    TEXT = "text"
    UNKNOWN = "unknown"


class ParseResult:
    """
    Standard result object returned by all parsers
    """
    def __init__(self, 
                 message_type: MessageType, 
                 data: Dict[str, Any], 
                 original_message: str,
                 confidence: float = 1.0,
                 errors: List[str] = None,
                 parser_name: str = ""):
        self.message_type = message_type
        self.data = data
        self.original_message = original_message
        self.confidence = confidence
        self.errors = errors or []
        self.parser_name = parser_name
        self.timestamp = self._get_timestamp()
    
    def _get_timestamp(self) -> str:
        return datetime.now().isoformat()
    
    def is_successful(self) -> bool:
        """Check if parsing was successful"""
        return self.message_type != MessageType.UNKNOWN and not self.errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "type": self.message_type.value,
            "data": self.data,
            "original_message": self.original_message,
            "confidence": self.confidence,
            "errors": self.errors,
            "timestamp": self.timestamp,
            "parser_name": self.parser_name
        }


class IMessageParser(ABC):
    """Interface for message parsers"""
    
    @abstractmethod
    def can_parse(self, message: str) -> bool:
        """Check if this parser can handle the message"""
        pass
    
    @abstractmethod
    def parse(self, message: str) -> ParseResult:
        """Parse the message and return result"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """Get parser priority (lower number = higher priority)"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get parser name for identification"""
        pass


class IParserManager(ABC):
    """Interface for parser manager"""
    
    @abstractmethod
    def register_parser(self, parser: IMessageParser):
        """Register a new parser"""
        pass
    
    @abstractmethod
    def parse_message(self, message: str) -> ParseResult:
        """Parse message using available parsers"""
        pass
    
    @abstractmethod
    def parse_with_specific_parser(self, message: str, parser_name: str) -> ParseResult:
        """Parse with a specific parser"""
        pass


class ITelegramService(ABC):
    """Interface for Telegram service"""
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> bool:
        """Process incoming Telegram message"""
        pass
    
    @abstractmethod
    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send message to Telegram chat"""
        pass


class ITransactionRepository(ABC):
    """Interface for transaction repository"""
    
    @abstractmethod
    async def save_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """Save transaction to database"""
        pass
    
    @abstractmethod
    async def get_transactions(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions for a chat"""
        pass