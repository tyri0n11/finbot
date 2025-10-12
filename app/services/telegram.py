from typing import Dict, Any, Optional
from core.telegram_bot import TelegramBot
from core.settings import settings
from core.logger import get_logger
from interfaces.service import ITelegramService
from services.parser_manager import parser_manager_service
from utils.validation import clean_and_validate_text

TAG = "Telegram_Service"

class TelegramService(ITelegramService):
    """
    Service layer for handling Telegram-specific business logic
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
        self.parser_manager = parser_manager_service
    
    async def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process an incoming Telegram message
        
        Args:
            message: The message object from Telegram update
            
        Returns:
            bool: True if message was processed successfully, False otherwise
        """
        try:
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            self.logger.info(f"[{TAG}] Processing message from chat {chat_id}: {text}")

            if text:
                # Validate and clean input text
                try:
                    clean_text = clean_and_validate_text(text)
                except ValueError as e:
                    self.logger.warning(f"[{TAG}] Invalid text input: {e}")
                    return False
                
                # Parse message using the new parser manager system
                parse_result = self.parser_manager.parse_message(clean_text)
                parsed_json = parse_result.to_dict()
                self.logger.info(f"[{TAG}] Parsed message to JSON: {parsed_json}")
                
                # Process the parsed JSON content
                response = await self._generate_response(parsed_json, chat_id)
                
                # Send response back to user with markdown formatting
                await self.bot.send_message(chat_id, response, mode_html=False)
                
                return True
                
        except Exception as e:
            self.logger.info(f"[{TAG}] Error processing message: {e}")
            return False
            
        return False
    
    async def _generate_response(self, parsed_data: dict, chat_id: int) -> str:
        """
        Generate response based on parsed message data
        
        Args:
            parsed_data: The parsed JSON data from the message
            chat_id: The chat ID where message came from
            
        Returns:
            str: The response message to send back
        """
        import json
        
        # Format the JSON response for better readability in Telegram
        try:
            # Create a nicely formatted response
            response_parts = ["🤖 *Parsed Message:*"]
            
            # Add message type
            msg_type = parsed_data.get("type", "unknown")
            response_parts.append(f"📝 *Type:* {msg_type}")
            
            # Add original message
            original = parsed_data.get("original_message", "")
            if original and len(original) <= 100:  # Limit length for display
                response_parts.append(f"💬 *Original:* {original}")
            elif original:
                response_parts.append(f"💬 *Original:* {original[:100]}...")
            
            # Add parsed data
            data = parsed_data.get("data", {})
            if data:
                response_parts.append("📊 *Parsed Data:*")
                
                # Format the data nicely
                if msg_type == "transaction":
                    for key, value in data.items():
                        if key != "raw_text":  # Skip raw_text as it's redundant
                            if key == "amount" and "currency" in data:
                                # Format amount with currency
                                currency = data.get("currency", "")
                                response_parts.append(f"   • *{key.title()}:* {value:,.0f} {currency}")
                            elif key != "currency":  # Don't show currency separately
                                response_parts.append(f"   • *{key.title()}:* {value}")
                elif msg_type == "key_value":
                    for key, value in data.items():
                        if key in ["amount", "cost", "paid", "price"] and "currency" in data:
                            # Format monetary values with currency
                            currency = data.get("currency", "")
                            if isinstance(value, (int, float)):
                                response_parts.append(f"   • *{key.title()}:* {value:,.0f} {currency}")
                            else:
                                response_parts.append(f"   • *{key.title()}:* {value}")
                        elif key != "currency":  # Don't show currency separately
                            response_parts.append(f"   • *{key.title()}:* {value}")
                elif msg_type == "text":
                    response_parts.append(f"   • *Content:* {data.get('content', '')}")
                    response_parts.append(f"   • *Words:* {data.get('word_count', 0)}")
                    response_parts.append(f"   • *Characters:* {data.get('char_count', 0)}")
                elif msg_type == "json":
                    # Pretty print the JSON data
                    json_str = json.dumps(data, indent=2, ensure_ascii=False)
                    response_parts.append(f"```\n{json_str}\n```")
                else:
                    # Fallback: just show the data as JSON
                    json_str = json.dumps(data, indent=2, ensure_ascii=False)
                    response_parts.append(f"```\n{json_str}\n```")
            
            # Add timestamp (formatted nicely)
            timestamp = parsed_data.get("timestamp", "")
            if timestamp:
                # Parse and format timestamp
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    response_parts.append(f"⏰ *Processed:* {formatted_time}")
                except:
                    response_parts.append(f"⏰ *Processed:* {timestamp}")
            
            # Handle errors
            if "error" in parsed_data:
                response_parts.append(f"❌ *Error:* {parsed_data['error']}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            # Fallback to simple JSON dump if formatting fails
            self.logger.error(f"[{TAG}] Error formatting response: {e}")
            return f"📋 *JSON Response:*\n```\n{json.dumps(parsed_data, indent=2, ensure_ascii=False)}\n```"
    
    async def send_message(self, chat_id: int, text: str, mode_html: bool = False) -> Dict[str, Any]:
        """
        Send a message to a specific chat
        
        Args:
            chat_id: The chat ID to send message to
            text: The message text to send
            mode_html: Whether to parse message as HTML
            
        Returns:
            Dict: The response from Telegram API
        """
        return await self.bot.send_message(chat_id, text, mode_html)
    
    async def handle_callback_query(self, callback_query: Dict[str, Any]) -> bool:
        """
        Handle callback queries from inline keyboards
        
        Args:
            callback_query: The callback query object from Telegram update
            
        Returns:
            bool: True if callback was processed successfully, False otherwise
        """
        # Placeholder for callback query handling
        # Implement based on your bot's functionality
        try:
            query_id = callback_query["id"]
            data = callback_query.get("data", "")
            chat_id = callback_query["message"]["chat"]["id"]

            self.logger.info(f"[{TAG}] Processing callback query: {data} from chat {chat_id}")

            return True
            
        except Exception as e:
            self.logger.info(f"[{TAG}] Error processing callback query: {e}")
            return False
    
    async def handle_edited_message(self, edited_message: Dict[str, Any]) -> bool:
        """
        Handle edited messages
        
        Args:
            edited_message: The edited message object from Telegram update
            
        Returns:
            bool: True if edited message was processed successfully, False otherwise
        """
        # Placeholder for edited message handling
        try:
            chat_id = edited_message["chat"]["id"]
            text = edited_message.get("text", "")

            self.logger.info(f"[{TAG}] Processing edited message from chat {chat_id}: {text}")

            # Add logic to handle edited messages
            # For example, you might want to update previous responses
            
            return True
            
        except Exception as e:
            self.logger.info(f"[{TAG}] Error processing edited message: {e}")
            return False
    
    async def send_message(self, chat_id: int, text: str) -> bool:
        """
        Send message to Telegram chat
        
        Args:
            chat_id: Target chat ID
            text: Message text to send
            
        Returns:
            bool: True if message sent successfully
        """
        try:
            await self.bot.send_message(chat_id, text, mode_html=False)
            return True
        except Exception as e:
            self.logger.error(f"[{TAG}] Error sending message: {e}")
            return False