"""
Parser Manager Service - Central orchestrator for all message parsers
"""

from typing import List, Dict, Optional
from interfaces.parser import IMessageParser, IParserManager
from model import ParseResult, MessageType
from parsers import CommandParser, TransactionParser, JSONParser, KeyValueParser, TextParser


class ParserManagerService(IParserManager):
    """
    Central manager for all message parsers with priority-based selection
    """
    
    def __init__(self):
        self.parsers = []
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize all available parsers in priority order"""
        self.parsers = [
            CommandParser(),      # Priority 1 - highest
            JSONParser(),         # Priority 2 - high  
            TransactionParser(),  # Priority 2 - high
            KeyValueParser(),     # Priority 3 - medium
            TextParser()          # Priority 10 - lowest (fallback)
        ]
        
        # Sort by priority (lower number = higher priority)
        self.parsers.sort(key=lambda p: p.get_priority())
    
    def register_parser(self, parser: IMessageParser):
        """Register a new parser and maintain priority order"""
        self.parsers.append(parser)
        self.parsers.sort(key=lambda p: p.get_priority())
    
    def parse_message(self, message: str) -> ParseResult:
        """
        Parse message using the highest priority parser that can handle it
        
        Args:
            message: The input message to parse
            
        Returns:
            ParseResult: Result from the selected parser
        """
        if not message or not message.strip():
            return ParseResult(
                message_type=MessageType.UNKNOWN,
                data={},
                original_message=message,
                errors=["Empty message"],
                parser_name="ParserManagerService"
            )
        
        # Try each parser in priority order
        for parser in self.parsers:
            if parser.can_parse(message):
                try:
                    result = parser.parse(message)
                    # Ensure parser_name is set
                    if not result.parser_name:
                        result.parser_name = parser.get_name()
                    return result
                except Exception as e:
                    # Log error and continue to next parser
                    continue
        
        # Fallback if no parser can handle the message
        return ParseResult(
            message_type=MessageType.UNKNOWN,
            data={"raw_message": message},
            original_message=message,
            errors=["No suitable parser found"],
            parser_name="ParserManagerService"
        )
    
    def parse_with_specific_parser(self, message: str, parser_name: str) -> ParseResult:
        """
        Parse message with a specific parser
        
        Args:
            message: The input message to parse
            parser_name: Name of the parser to use
            
        Returns:
            ParseResult or None if parser not found or can't parse
        """
        for parser in self.parsers:
            if parser.get_name() == parser_name:
                if parser.can_parse(message):
                    try:
                        result = parser.parse(message)
                        if not result.parser_name:
                            result.parser_name = parser.get_name()
                        return result
                    except Exception:
                        return ParseResult(
                            message_type=MessageType.UNKNOWN,
                            data={},
                            original_message=message,
                            errors=[f"Error parsing with {parser_name}"],
                            parser_name=parser_name
                        )
                else:
                    return ParseResult(
                        message_type=MessageType.UNKNOWN,
                        data={},
                        original_message=message,
                        errors=[f"{parser_name} cannot parse this message"],
                        parser_name=parser_name
                    )
        
        return ParseResult(
            message_type=MessageType.UNKNOWN,
            data={},
            original_message=message,
            errors=[f"Parser {parser_name} not found"],
            parser_name="ParserManagerService"
        )
    
    def get_available_parsers(self) -> List[str]:
        """Get list of available parser names"""
        return [parser.get_name() for parser in self.parsers]
    
    def get_parser_priorities(self) -> Dict[str, int]:
        """Get parser priorities for debugging"""
        return {parser.get_name(): parser.get_priority() for parser in self.parsers}


# Create global parser manager instance
parser_manager_service = ParserManagerService()