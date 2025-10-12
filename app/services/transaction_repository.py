"""
Transaction Repository Service - Handles transaction data persistence
"""

from typing import List, Dict, Any
from interfaces.service import ITransactionRepository
from model import Transaction
from core.logger import get_logger

TAG = "Transaction_Repository"

class TransactionRepositoryService(ITransactionRepository):
    """
    Repository service for handling transaction data persistence
    """
    
    def __init__(self):
        self.logger = get_logger()
        # In a real application, this would connect to a database
        # For now, we'll use in-memory storage
        self._transactions: Dict[int, List[Dict[str, Any]]] = {}
    
    async def save_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Save transaction to database
        
        Args:
            transaction_data: Transaction data dictionary
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Validate transaction data
            if not transaction_data.get('amount') or not transaction_data.get('chat_id'):
                self.logger.warning(f"[{TAG}] Invalid transaction data: {transaction_data}")
                return False
            
            chat_id = transaction_data['chat_id']
            
            # Initialize chat transactions if not exists
            if chat_id not in self._transactions:
                self._transactions[chat_id] = []
            
            # Add transaction
            self._transactions[chat_id].append(transaction_data)
            
            self.logger.info(f"[{TAG}] Saved transaction for chat {chat_id}: {transaction_data}")
            return True
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error saving transaction: {e}")
            return False
    
    async def get_transactions(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent transactions for a chat
        
        Args:
            chat_id: Chat ID to get transactions for
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        try:
            if chat_id not in self._transactions:
                return []
            
            # Get latest transactions (most recent first)
            transactions = self._transactions[chat_id]
            return transactions[-limit:] if len(transactions) > limit else transactions
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error getting transactions: {e}")
            return []
    
    async def get_transaction_summary(self, chat_id: int) -> Dict[str, Any]:
        """
        Get transaction summary for a chat
        
        Args:
            chat_id: Chat ID to get summary for
            
        Returns:
            Dictionary with transaction summary
        """
        try:
            transactions = await self.get_transactions(chat_id, limit=1000)  # Get all
            
            if not transactions:
                return {"total_transactions": 0, "total_amount": 0, "currency": "VND"}
            
            total_amount = sum(t.get('amount', 0) for t in transactions)
            currency = transactions[-1].get('currency', 'VND')  # Use latest currency
            
            categories = {}
            for t in transactions:
                category = t.get('category', 'Other')
                if category not in categories:
                    categories[category] = 0
                categories[category] += t.get('amount', 0)
            
            return {
                "total_transactions": len(transactions),
                "total_amount": total_amount,
                "currency": currency,
                "categories": categories
            }
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error getting transaction summary: {e}")
            return {"total_transactions": 0, "total_amount": 0, "currency": "VND"}


# Create global transaction repository instance
transaction_repository_service = TransactionRepositoryService()