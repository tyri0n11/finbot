from typing import Dict, Any, Optional
from core.telegram_bot import TelegramBot
from core.settings import settings
from core.logger import get_logger
from interfaces.service import ITelegramService
from services.parser import parser_manager_service
from utils.validation import clean_and_validate_text
from repo.transaction import TransactionRepository
from datetime import datetime
TAG = "Telegram_Service"

class TelegramService(ITelegramService):
    """
    Service layer for handling Telegram-specific business logic
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
        self.parser_manager = parser_manager_service
        self.transaction_repo = TransactionRepository()
    
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
                # Extract user data from message
                user_data = {
                    'username': message.get("from", {}).get("username"),
                    'first_name': message.get("from", {}).get("first_name"),
                    'last_name': message.get("from", {}).get("last_name"),
                    'language_code': message.get("from", {}).get("language_code", 'vi')
                }
                
                # Validate and clean input text
                try:
                    clean_text = clean_and_validate_text(text)
                except ValueError as e:
                    self.logger.warning(f"[{TAG}] Invalid text input: {e}")
                    return False
                
                # Parse message using the new parser manager system
                start_time = datetime.now()
                parse_result = self.parser_manager.parse_message(clean_text)
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                parsed_json = parse_result.to_dict()
                
                # Enhanced transaction data for database
                if parse_result.message_type.value == 'transaction' and parsed_json.get('data'):
                    transaction_data = {
                        **parsed_json['data'],
                        'chat_id': chat_id,
                        'user_data': user_data,
                        'original_message': text,
                        'parser_name': parse_result.parser_name,
                        'confidence_score': getattr(parse_result, 'confidence_score', None)
                    }
                    
                    # Save transaction to database
                    await self.transaction_repo.save_transaction(transaction_data)
                
                # Save parser log
                parser_log_data = {
                    'original_message': text,
                    'parser_name': parse_result.parser_name,
                    'message_type': parse_result.message_type.value,
                    'parsed_data': parsed_json,
                    'extracted_verb': parsed_json.get('data', {}).get('verb'),
                    'extracted_item': parsed_json.get('data', {}).get('item') or parsed_json.get('data', {}).get('description'),
                    'extracted_amount': parsed_json.get('data', {}).get('amount'),
                    'extracted_currency': parsed_json.get('data', {}).get('currency'),
                    'extracted_category': parsed_json.get('data', {}).get('category'),
                    'extracted_time_info': parsed_json.get('data', {}).get('time'),
                    'success': len(parse_result.errors) == 0,
                    'error_message': ', '.join(parse_result.errors) if parse_result.errors else None,
                    'processing_time_ms': int(processing_time),
                    'confidence_score': getattr(parse_result, 'confidence_score', None)
                }
                
                await self.transaction_repo.save_parser_log(chat_id, parser_log_data)
                
                self.logger.info(f"[{TAG}] Parsed message to JSON: {parsed_json}")
                
                # Process the parsed JSON content
                response = await self._generate_response(parsed_json, chat_id)
                
                # Send response back to user with markdown formatting
                await self.bot.send_message(chat_id, response, mode_html=False)
                
                return True
                
        except Exception as e:
            self.logger.error(f"[{TAG}] Error processing message: {e}")
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
        
        try:
            msg_type = parsed_data.get("type", "unknown")
            data = parsed_data.get("data", {})
            original = parsed_data.get("original_message", "")
            timestamp = parsed_data.get("timestamp", "")
            
            # Build response with clear visual sections
            response_parts = []
            
            # Header with message type
            type_emoji = {
                "transaction": "💳",
                "key_value": "🔑",
                "text": "📝",
                "json": "📋",
                "unknown": "❓"
            }
            emoji = type_emoji.get(msg_type, "📄")
            response_parts.append(f"{emoji} *{msg_type.upper().replace('_', ' ')} MESSAGE*")
            response_parts.append("━━━━━━━━━━━━━━━━━━━━")
            
            # Original message section (if present)
            if original:
                response_parts.append("")
                response_parts.append("💬 *Message*")
                if len(original) <= 150:
                    response_parts.append(f"_{original}_")
                else:
                    response_parts.append(f"_{original[:150]}..._")
            
            # Main data section
            if data:
                response_parts.append("")
                response_parts.append("📊 *Parsed Information*")
                response_parts.append("")
                
                if msg_type == "transaction":
                    response_parts.extend(self._format_transaction(data))
                elif msg_type == "key_value":
                    response_parts.extend(self._format_key_value(data))
                elif msg_type == "text":
                    response_parts.extend(self._format_text(data))
                elif msg_type == "json":
                    response_parts.extend(self._format_json(data))
                else:
                    response_parts.extend(self._format_generic(data))
            
            # Timestamp footer
            if timestamp:
                response_parts.append("")
                response_parts.append("━━━━━━━━━━━━━━━━━━━━")
                formatted_time = self._format_timestamp(timestamp)
                response_parts.append(f"⏰ {formatted_time}")
            
            # Error handling
            if "error" in parsed_data:
                response_parts.append("")
                response_parts.append("━━━━━━━━━━━━━━━━━━━━")
                response_parts.append(f"❌ *Error:* {parsed_data['error']}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error formatting response: {e}")
            return self._format_fallback(parsed_data)

    def _format_transaction(self, data: dict) -> list:
        """Format transaction data with visual hierarchy"""
        lines = []
        
        # Amount (most important - show first and larger)
        if "amount" in data:
            amount = data["amount"]
            currency = data.get("currency", "")
            if isinstance(amount, (int, float)):
                lines.append(f"💰 *Amount:* `{amount:,.0f} {currency}`")
            else:
                lines.append(f"💰 *Amount:* `{amount} {currency}`")
            lines.append("")
        
        # Other transaction details
        field_icons = {
            "description": "📝",
            "category": "🏷️",
            "date": "📅",
            "merchant": "🏪",
            "account": "🏦",
            "status": "✅"
        }
        
        for key, value in data.items():
            if key not in ["amount", "currency", "raw_text"]:
                icon = field_icons.get(key, "▪️")
                lines.append(f"{icon} *{key.title()}:* {value}")
        
        return lines

    def _format_key_value(self, data: dict) -> list:
        """Format key-value data with smart grouping"""
        lines = []
        
        # Monetary values first
        monetary_keys = ["amount", "cost", "price", "paid", "total", "subtotal"]
        currency = data.get("currency", "")
        
        for key in monetary_keys:
            if key in data:
                value = data[key]
                if isinstance(value, (int, float)):
                    lines.append(f"💵 *{key.title()}:* `{value:,.0f} {currency}`")
                else:
                    lines.append(f"💵 *{key.title()}:* `{value} {currency}`")
        
        if lines:
            lines.append("")
        
        # Other fields
        for key, value in data.items():
            if key not in monetary_keys and key not in ["currency", "raw_text"]:
                # Smart icon selection
                if "date" in key.lower() or "time" in key.lower():
                    icon = "📅"
                elif "name" in key.lower():
                    icon = "👤"
                elif "email" in key.lower():
                    icon = "📧"
                elif "phone" in key.lower():
                    icon = "📱"
                elif "address" in key.lower():
                    icon = "📍"
                else:
                    icon = "▪️"
                
                lines.append(f"{icon} *{key.title()}:* {value}")
        
        return lines

    def _format_text(self, data: dict) -> list:
        """Format text data with statistics"""
        lines = []
        
        content = data.get("content", "")
        if content:
            # Show preview
            lines.append("📄 *Content Preview*")
            if len(content) <= 200:
                lines.append(f"_{content}_")
            else:
                lines.append(f"_{content[:200]}..._")
            lines.append("")
        
        # Statistics in a compact format
        word_count = data.get("word_count", 0)
        char_count = data.get("char_count", 0)
        
        lines.append("📊 *Statistics*")
        lines.append(f"▪️ Words: `{word_count}`")
        lines.append(f"▪️ Characters: `{char_count}`")
        
        return lines

    def _format_json(self, data: dict) -> list:
        """Format JSON data in a code block"""
        import json
        lines = []
        
        lines.append("```json")
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        lines.append(json_str)
        lines.append("```")
        
        return lines

    def _format_generic(self, data: dict) -> list:
        """Generic formatter for unknown data types"""
        lines = []
        
        for key, value in data.items():
            if key != "raw_text":
                # Format value based on type
                if isinstance(value, (int, float)):
                    lines.append(f"▪️ *{key.title()}:* `{value}`")
                elif isinstance(value, dict):
                    lines.append(f"▪️ *{key.title()}:*")
                    import json
                    lines.append(f"```json\n{json.dumps(value, indent=2, ensure_ascii=False)}\n```")
                else:
                    lines.append(f"▪️ *{key.title()}:* {value}")
        
        return lines

    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp in a readable way"""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%d %b %Y, %H:%M:%S")
        except:
            return timestamp

    def _format_fallback(self, parsed_data: dict) -> str:
        """Fallback formatter if main formatting fails"""
        import json
        return f"📋 *Response Data*\n━━━━━━━━━━━━━━━━━━━━\n```json\n{json.dumps(parsed_data, indent=2, ensure_ascii=False)}\n```"
    
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