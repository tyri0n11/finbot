# Legacy parser module for backward compatibility# Legacy parser module for backward compatibility# Legacy parser module for backward compatibility

from services.parser_manager import parser_manager

from services.parser_manager import parser_manager

class Parser:

    """Legacy Parser class that wraps the new parser manager"""from services.parser_manager import parser_manager"""

    

    def __init__(self):class Parser:

        self.parser_manager = parser_manager

        """Legacy Parser class that wraps the new parser manager"""Legacy Parser class that now uses the new clean architecture parser system

    def parse_message(self, message: str) -> dict:

        """Legacy method that delegates to new parser manager"""    

        try:

            result = self.parser_manager.parse(message)    def __init__(self):class Parser:This maintains backward compatibility while leveraging the new modular design

            # Convert new format to legacy format

            return {        self.parser_manager = parser_manager

                'type': result.type.value,

                'data': result.data,        """Legacy Parser class that wraps the new parser manager""""""

                'original_message': result.original_message,

                'confidence': result.confidence,    def parse_message(self, message: str) -> dict:

                'errors': result.errors,

                'timestamp': result.timestamp,        """Legacy method that delegates to new parser manager"""    

                'parser_name': result.parser_name

            }        try:

        except Exception as e:

            return {            result = self.parser_manager.parse(message)    def __init__(self):from services.parser_manager import parser_manager_service

                'error': str(e),

                'original_message': message            # Convert new format to legacy format

            }

            return {        self.parser_manager = parser_manager

# Create legacy instance

parser = Parser()                'type': result.type.value,



# Legacy helper functions                'data': result.data,    

def get_transaction_from_message(message_text: str) -> dict:

    """Legacy function that uses the new parser system"""                'original_message': result.original_message,

    try:

        result = parser_manager.parse(message_text)                'confidence': result.confidence,    def parse_message(self, message: str) -> dict:class Parser:

        if result.type.value == 'transaction':

            return result.data                'errors': result.errors,

        else:

            return None                'timestamp': result.timestamp,        """Legacy method that delegates to new parser manager"""    """

    except Exception as e:

        return None                'parser_name': result.parser_name



def parse_money(amount_text: str) -> float:            }        try:    Legacy Parser class that now uses the new parser manager system

    """Legacy function that parses money amounts"""

    from utils.currency import convert_vnd_amount        except Exception as e:

    try:

        return convert_vnd_amount(amount_text)            return {            result = self.parser_manager.parse(message)    This maintains backward compatibility while leveraging clean architecture

    except Exception:

        return 0.0                'error': str(e),



def get_category(description: str) -> str:                'original_message': message            # Convert new format to legacy format    """

    """Legacy function that gets category from description"""

    from utils.text_processing import categorize_vietnamese_item            }

    try:

        return categorize_vietnamese_item(description)            return {    

    except Exception:

        return "khác"# Create legacy instance



__all__ = ['Parser', 'parser', 'get_transaction_from_message', 'parse_money', 'get_category']parser = Parser()                'type': result.type.value,    def __init__(self):



__all__ = ['Parser', 'parser']                'data': result.data,        self.parser_manager = parser_manager_service

                'original_message': result.original_message,    

                'confidence': result.confidence,    def parse_message_to_json(self, message: str) -> dict:

                'errors': result.errors,        """

                'timestamp': result.timestamp,        Parses a message string into a JSON-like dictionary.

                'parser_name': result.parser_name        Now uses the new parser manager system.

            }        

        except Exception as e:        Args:

            return {            message (str): The input message string to be parsed.

                'error': str(e),        

                'original_message': message        Returns:

            }            dict: A dictionary representation of the parsed message.

        """

# Create legacy instance        result = self.parser_manager.parse_message(message)

parser = Parser()        return result.to_dict()

    

__all__ = ['Parser', 'parser']    def parse_message_to_transaction(self, message: str) -> dict:
        """
        Parses a message string into a transaction dictionary.
        Uses the enhanced parsing logic from the new system.
        
        Args:
            message (str): The input message string to be parsed.
        
        Returns:
            dict: A dictionary representation of the transaction.
        """
        # Try to parse with transaction parser specifically
        result = self.parser_manager.parse_with_specific_parser(message, "TransactionParser")
        
        if result and result.is_successful():
            return result.data
        
        # Fallback to general parsing
        general_result = self.parser_manager.parse_message(message)
        
        if general_result.message_type.value == "transaction":
            return general_result.data
        elif general_result.message_type.value == "key_value":
            # Check if it has transaction-like keys
            data = general_result.data
            transaction_keys = {'amount', 'cost', 'price', 'description', 'category', 'location'}
            if any(key in data for key in transaction_keys):
                return data
        
        # Return original message if no transaction found
        return {"raw_message": message}
            dict: A dictionary representation of the transaction.
        """
        # Example implementation (to be replaced with actual parsing logic)
        transaction = {}
        lines = message.splitlines()
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                transaction[key.strip()] = value.strip()
        return transaction