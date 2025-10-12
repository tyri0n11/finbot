"""
Service interfaces for clean architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


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