"""
Command Parser - Specialized parser for bot commands with Vietnamese support
"""

import re
from interfaces.parser import IMessageParser
from model import ParseResult, MessageType


class CommandParser(IMessageParser):
    """Parser for bot commands like /help, /start, /balance with Vietnamese aliases"""
    
    def __init__(self):
        # Vietnamese command mappings
        self.vietnamese_commands = {
            '/giup': '/help',
            '/sodu': '/balance', 
            '/batdau': '/start',
            '/dung': '/stop',
            '/thongke': '/stats',
            '/lichsu': '/history',
            '/caidat': '/settings'
        }
        
        # Command definitions with their actions
        self.commands = {
            '/help': {
                'action': 'show_help',
                'description': 'Show available commands',
                'response_type': 'help_menu'
            },
            '/start': {
                'action': 'start_bot',
                'description': 'Start the bot',
                'response_type': 'welcome_message'
            },
            '/balance': {
                'action': 'show_balance',
                'description': 'Show current balance',
                'response_type': 'balance_info'
            },
            '/stop': {
                'action': 'stop_bot',
                'description': 'Stop the bot',
                'response_type': 'goodbye_message'
            },
            '/stats': {
                'action': 'show_stats',
                'description': 'Show transaction statistics',
                'response_type': 'stats_info'
            },
            '/history': {
                'action': 'show_history',
                'description': 'Show transaction history',
                'response_type': 'history_list'
            },
            '/settings': {
                'action': 'show_settings',
                'description': 'Show bot settings',
                'response_type': 'settings_menu'
            }
        }
    
    def can_parse(self, message: str) -> bool:
        """Check if message is a bot command"""
        message = message.strip()
        
        # Check for standard commands
        if message.startswith('/'):
            command = message.split()[0].lower()
            return command in self.commands or command in self.vietnamese_commands
        
        return False
    
    def parse(self, message: str) -> ParseResult:
        """Parse command message"""
        message = message.strip()
        
        if not self.can_parse(message):
            return ParseResult(
                message_type=MessageType.UNKNOWN,
                data={},
                original_message=message,
                errors=["Not a valid command"],
                parser_name="CommandParser"
            )
        
        parts = message.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Convert Vietnamese command to English
        if command in self.vietnamese_commands:
            command = self.vietnamese_commands[command]
        
        # Get command info
        command_info = self.commands.get(command, {})
        
        command_data = {
            'command': command.lstrip('/'),  # Remove leading slash
            'original_command': parts[0],
            'args': args,
            'action': command_info.get('action', 'unknown'),
            'description': command_info.get('description', ''),
            'response_type': command_info.get('response_type', 'text')
        }
        
        return ParseResult(
            message_type=MessageType.COMMAND,
            data=command_data,
            original_message=message,
            confidence=1.0,
            parser_name="CommandParser"
        )
    
    def get_priority(self) -> int:
        """Commands have highest priority"""
        return 1
    
    def get_name(self) -> str:
        """Get parser name"""
        return "CommandParser"
