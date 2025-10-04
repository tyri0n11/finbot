from typing import Dict, Any
from services.telegram_service import TelegramService
from core.logger import get_logger
TAG = "Webhook_Service"

class WebhookService:
    """
    Service layer for handling webhook business logic
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.telegram_service = TelegramService()
    
    async def process_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming webhook update from Telegram
        
        Args:
            update_data: The update data received from Telegram webhook
            
        Returns:
            Dict: Response data indicating processing status
        """
        try:
            self.logger.info(f"[{TAG}] Processing update: {update_data.get('update_id', 'unknown')}")            
            # Handle different types of updates
            processed = False
            
            # Process regular message
            if "message" in update_data:
                processed = await self.telegram_service.process_message(update_data["message"])
            
            # Process edited message
            elif "edited_message" in update_data:
                processed = await self.telegram_service.handle_edited_message(update_data["edited_message"])
            
            # Process callback query (inline keyboard responses)
            elif "callback_query" in update_data:
                processed = await self.telegram_service.handle_callback_query(update_data["callback_query"])
            
            # Handle other update types as needed
            # elif "inline_query" in update_data:
            #     processed = await self._handle_inline_query(update_data["inline_query"])
            
            else:
                self.logger.info(f"[{TAG}] Unhandled update type: {list(update_data.keys())}")
                processed = True  # Return success for unhandled but valid updates
            
            return {
                "status": "ok",
                "processed": processed,
                "update_id": update_data.get("update_id")
            }
            
        except Exception as e:
            self.logger.info(f"[{TAG}] Error processing update: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processed": False
            }
    
    async def validate_update(self, update_data: Dict[str, Any]) -> bool:
        """
        Validate the incoming update data
        
        Args:
            update_data: The update data to validate
            
        Returns:
            bool: True if update is valid, False otherwise
        """
        try:
            # Basic validation - check if update has required fields
            if not isinstance(update_data, dict):
                return False
            
            # Check if update has at least one of the expected fields
            expected_fields = ["message", "edited_message", "callback_query", "inline_query"]
            has_expected_field = any(field in update_data for field in expected_fields)
            
            return has_expected_field
            
        except Exception as e:
            self.logger.info(f"[{TAG}] Error validating update: {e}")
            return False
    
    def get_update_type(self, update_data: Dict[str, Any]) -> str:
        """
        Determine the type of the update
        
        Args:
            update_data: The update data to analyze
            
        Returns:
            str: The type of update (message, edited_message, callback_query, etc.)
        """
        if "message" in update_data:
            return "message"
        elif "edited_message" in update_data:
            return "edited_message"
        elif "callback_query" in update_data:
            return "callback_query"
        elif "inline_query" in update_data:
            return "inline_query"
        else:
            return "unknown"