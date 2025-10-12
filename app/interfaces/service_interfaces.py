"""
Service interfaces - Interfaces for service layer components
"""

from .service_interfaces import (
    ITelegramService,
    ITransactionRepository
)

__all__ = [
    'ITelegramService',
    'ITransactionRepository'
]