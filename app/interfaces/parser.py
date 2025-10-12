"""
Parser interfaces for clean architecture
"""

from abc import ABC, abstractmethod
from interfaces import ParseResult


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