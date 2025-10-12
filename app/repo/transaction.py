"""
Transaction Repository Service - Handles transaction data persistence
"""

from typing import List, Dict, Any, Optional
from interfaces.service import ITransactionRepository
from model import Transaction
from core.logger import get_logger
from core.database import Database
import json
from datetime import datetime, date
import uuid

TAG = "Transaction_Repository"

class TransactionRepository(ITransactionRepository):
    """
    Repository service for handling transaction data persistence
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.db = Database()
        
        # Test database connection on initialization
        health = self.db.check_health()
        if health['postgresql']['status'] != 'healthy':
            self.logger.warning(f"[{TAG}] PostgreSQL not healthy: {health['postgresql']['error']}")
        else:
            self.logger.info(f"[{TAG}] PostgreSQL connection established successfully")
    
    async def ensure_user_exists(self, telegram_user_id: int, user_data: Dict[str, Any] = None) -> bool:
        """
        Ensure user exists in database, create if not exists
        
        Args:
            telegram_user_id: Telegram user ID
            user_data: Optional user data (username, first_name, etc.)
            
        Returns:
            bool: True if user exists/created successfully
        """
        conn = None
        try:
            self.logger.debug(f"[{TAG}] Checking if user {telegram_user_id} exists in database")
            self.logger.debug(f"[{TAG}] User data provided: {user_data}")
            
            conn = self.db.get_postgres_connection()
            if not conn:
                self.logger.error(f"[{TAG}] Cannot get database connection for user check")
                return False
            self.logger.debug(f"[{TAG}] Database connection established for user check")
                
            cursor = conn.cursor()
            
            # Check if user exists
            self.logger.debug(f"[{TAG}] Executing user existence check query")
            cursor.execute(
                "SELECT telegram_user_id FROM finbot.users WHERE telegram_user_id = %s",
                (telegram_user_id,)
            )
            
            user_exists = cursor.fetchone()
            if user_exists:
                self.logger.debug(f"[{TAG}] User {telegram_user_id} already exists in database")
                cursor.close()
                return True
            
            self.logger.info(f"[{TAG}] User {telegram_user_id} does not exist, creating new user")
            
            # Create user if not exists
            username = user_data.get('username') if user_data else None
            first_name = user_data.get('first_name') if user_data else None
            last_name = user_data.get('last_name') if user_data else None
            language_code = user_data.get('language_code', 'vi') if user_data else 'vi'
            
            self.logger.debug(f"[{TAG}] Creating user with: username={username}, first_name={first_name}, last_name={last_name}, language_code={language_code}")
            
            cursor.execute("""
                INSERT INTO finbot.users (telegram_user_id, username, first_name, last_name, language_code)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (telegram_user_id) DO NOTHING
            """, (telegram_user_id, username, first_name, last_name, language_code))
            
            self.logger.debug(f"[{TAG}] User creation query executed")
            conn.commit()
            self.logger.debug(f"[{TAG}] User creation committed to database")
            cursor.close()
            
            self.logger.info(f"[{TAG}] User {telegram_user_id} successfully ensured in database")
            return True
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error ensuring user exists: {e}")
            self.logger.debug(f"[{TAG}] Exception details:", exc_info=True)
            if conn:
                self.logger.debug(f"[{TAG}] Rolling back user creation transaction")
                conn.rollback()
            return False
        finally:
            if conn:
                self.logger.debug(f"[{TAG}] Returning database connection to pool")
                self.db.return_postgres_connection(conn)

    async def save_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Save transaction to PostgreSQL database
        
        Args:
            transaction_data: Transaction data dictionary
            
        Returns:
            bool: True if saved successfully
        """
        conn = None
        try:
            self.logger.info(f"[{TAG}] Starting transaction save process")
            self.logger.debug(f"[{TAG}] Input transaction data: {transaction_data}")
            
            # Validate required fields
            required_fields = ['amount', 'chat_id']
            self.logger.debug(f"[{TAG}] Validating required fields: {required_fields}")
            for field in required_fields:
                if not transaction_data.get(field):
                    self.logger.warning(f"[{TAG}] Missing required field '{field}' in transaction data")
                    return False
            
            chat_id = transaction_data['chat_id']
            self.logger.info(f"[{TAG}] Processing transaction for user {chat_id}")
            
            # Ensure user exists
            user_data = transaction_data.get('user_data', {})
            self.logger.debug(f"[{TAG}] User data for user creation: {user_data}")
            self.logger.info(f"[{TAG}] Ensuring user {chat_id} exists in database")
            if not await self.ensure_user_exists(chat_id, user_data):
                self.logger.error(f"[{TAG}] Failed to ensure user {chat_id} exists")
                return False
            self.logger.debug(f"[{TAG}] User {chat_id} confirmed to exist in database")
            
            self.logger.info(f"[{TAG}] Establishing database connection for transaction save")
            conn = self.db.get_postgres_connection()
            if not conn:
                self.logger.error(f"[{TAG}] Cannot get database connection")
                return False
            self.logger.debug(f"[{TAG}] Database connection established successfully")
                
            cursor = conn.cursor()
            self.logger.debug(f"[{TAG}] Database cursor created")
            
            # Prepare transaction data
            self.logger.info(f"[{TAG}] Preparing transaction data for database insertion")
            transaction_id = str(uuid.uuid4())
            transaction_type = transaction_data.get('type', 'chi')  # Default to expense
            amount = float(transaction_data['amount'])
            currency = transaction_data.get('currency', 'VND')
            category = transaction_data.get('category')
            note = transaction_data.get('note')
            merchant = transaction_data.get('merchant')
            account = transaction_data.get('account')
            status = transaction_data.get('status', 'completed')
            
            self.logger.debug(f"[{TAG}] Generated transaction_id: {transaction_id}")
            self.logger.debug(f"[{TAG}] Transaction type: {transaction_type}")
            self.logger.debug(f"[{TAG}] Amount: {amount} {currency}")
            self.logger.debug(f"[{TAG}] Category: {category}")
            self.logger.debug(f"[{TAG}] Note: {note}")
            self.logger.debug(f"[{TAG}] Merchant: {merchant}")
            self.logger.debug(f"[{TAG}] Account: {account}")
            self.logger.debug(f"[{TAG}] Status: {status}")
            
            # Handle transaction date
            self.logger.debug(f"[{TAG}] Processing transaction date")
            transaction_date = transaction_data.get('date')
            original_date = transaction_date
            if isinstance(transaction_date, str):
                try:
                    transaction_date = datetime.fromisoformat(transaction_date.replace('Z', '+00:00')).date()
                    self.logger.debug(f"[{TAG}] Parsed date from string: {original_date} -> {transaction_date}")
                except:
                    transaction_date = date.today()
                    self.logger.debug(f"[{TAG}] Failed to parse date '{original_date}', using today: {transaction_date}")
            elif not isinstance(transaction_date, date):
                transaction_date = date.today()
                self.logger.debug(f"[{TAG}] No valid date provided, using today: {transaction_date}")
            else:
                self.logger.debug(f"[{TAG}] Using provided date: {transaction_date}")
            
            # Insert transaction
            self.logger.info(f"[{TAG}] Executing database INSERT for transaction {transaction_id}")
            sql_query = """
                INSERT INTO finbot.transactions 
                (id, user_id, type, amount, currency, category, note, merchant, account, status, transaction_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            sql_params = (
                transaction_id, chat_id, transaction_type, amount, currency,
                category, note, merchant, account, status, transaction_date
            )
            self.logger.debug(f"[{TAG}] SQL Query: {sql_query}")
            self.logger.debug(f"[{TAG}] SQL Parameters: {sql_params}")
            
            cursor.execute(sql_query, sql_params)
            self.logger.debug(f"[{TAG}] SQL query executed successfully")
            
            self.logger.debug(f"[{TAG}] Committing transaction to database")
            conn.commit()
            self.logger.debug(f"[{TAG}] Transaction committed successfully")
            
            cursor.close()
            self.logger.debug(f"[{TAG}] Database cursor closed")
            
            self.logger.info(f"[{TAG}] Successfully saved transaction {transaction_id} for user {chat_id}: {amount} {currency}")
            self.logger.info(f"[{TAG}] Transaction save process completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error saving transaction: {e}")
            self.logger.debug(f"[{TAG}] Exception details:", exc_info=True)
            if conn:
                self.logger.debug(f"[{TAG}] Rolling back database transaction due to error")
                conn.rollback()
                self.logger.debug(f"[{TAG}] Database rollback completed")
            return False
        finally:
            if conn:
                self.logger.debug(f"[{TAG}] Returning database connection to pool")
                self.db.return_postgres_connection(conn)
                self.logger.debug(f"[{TAG}] Database connection returned to pool")
    
    async def get_transactions(self, chat_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get recent transactions for a chat from PostgreSQL
        
        Args:
            chat_id: Chat ID to get transactions for
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip (for pagination)
            
        Returns:
            List of transaction dictionaries
        """
        conn = None
        try:
            self.logger.info(f"[{TAG}] Getting transactions for user {chat_id}, limit={limit}, offset={offset}")
            
            conn = self.db.get_postgres_connection()
            if not conn:
                self.logger.error(f"[{TAG}] Cannot get database connection for transaction retrieval")
                return []
            self.logger.debug(f"[{TAG}] Database connection established for transaction retrieval")
                
            cursor = conn.cursor()
            self.logger.debug(f"[{TAG}] Database cursor created for transaction query")
            
            # Get transactions with user info, ordered by creation time (most recent first)
            sql_query = """
                SELECT 
                    t.id, t.type, t.amount, t.currency, t.category, t.note,
                    t.merchant, t.account, t.status, t.transaction_date, t.created_at,
                    u.username, u.first_name, u.last_name
                FROM finbot.transactions t
                JOIN finbot.users u ON t.user_id = u.telegram_user_id
                WHERE t.user_id = %s
                ORDER BY t.created_at DESC
                LIMIT %s OFFSET %s
            """
            sql_params = (chat_id, limit, offset)
            self.logger.debug(f"[{TAG}] Executing transaction query with params: {sql_params}")
            self.logger.debug(f"[{TAG}] SQL Query: {sql_query}")
            
            cursor.execute(sql_query, sql_params)
            
            rows = cursor.fetchall()
            self.logger.debug(f"[{TAG}] Retrieved {len(rows)} rows from database")
            cursor.close()
            self.logger.debug(f"[{TAG}] Database cursor closed")
            
            # Convert to dictionaries
            self.logger.debug(f"[{TAG}] Converting database rows to transaction dictionaries")
            transactions = []
            for i, row in enumerate(rows):
                self.logger.debug(f"[{TAG}] Processing row {i+1}/{len(rows)}: transaction_id={row[0]}")
                transaction = {
                    'id': str(row[0]),
                    'type': row[1],
                    'amount': float(row[2]),
                    'currency': row[3],
                    'category': row[4],
                    'note': row[5],
                    'merchant': row[6],
                    'account': row[7],
                    'status': row[8],
                    'transaction_date': row[9].isoformat() if row[9] else None,
                    'created_at': row[10].isoformat() if row[10] else None,
                    'user': {
                        'username': row[11],
                        'first_name': row[12],
                        'last_name': row[13]
                    },
                    'chat_id': chat_id  # Add for backward compatibility
                }
                transactions.append(transaction)
                self.logger.debug(f"[{TAG}] Processed transaction: {transaction['amount']} {transaction['currency']} - {transaction['category']}")
            
            self.logger.info(f"[{TAG}] Successfully retrieved {len(transactions)} transactions for user {chat_id}")
            return transactions
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error getting transactions: {e}")
            self.logger.debug(f"[{TAG}] Exception details:", exc_info=True)
            return []
        finally:
            if conn:
                self.logger.debug(f"[{TAG}] Returning database connection to pool")
                self.db.return_postgres_connection(conn)
    
    async def get_transaction_summary(self, chat_id: int, days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive transaction summary for a chat from PostgreSQL
        
        Args:
            chat_id: Chat ID to get summary for
            days_back: Number of days to look back for summary
            
        Returns:
            Dictionary with detailed transaction summary
        """
        conn = None
        try:
            self.logger.info(f"[{TAG}] Getting transaction summary for user {chat_id}, days_back={days_back}")
            
            conn = self.db.get_postgres_connection()
            if not conn:
                self.logger.error(f"[{TAG}] Cannot get database connection for transaction summary")
                return {"total_transactions": 0, "total_amount": 0, "currency": "VND"}
            self.logger.debug(f"[{TAG}] Database connection established for transaction summary")
                
            cursor = conn.cursor()
            self.logger.debug(f"[{TAG}] Database cursor created for summary queries")
            
            # Get comprehensive summary with category breakdown
            self.logger.debug(f"[{TAG}] Executing comprehensive summary query")
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    SUM(CASE WHEN type = 'thu' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'chi' THEN amount ELSE 0 END) as total_expenses,
                    SUM(CASE WHEN type = 'vay' THEN amount ELSE 0 END) as total_loans,
                    AVG(CASE WHEN type = 'chi' THEN amount END) as avg_expense,
                    MAX(created_at) as last_transaction,
                    COUNT(DISTINCT category) as unique_categories,
                    array_agg(DISTINCT currency) as currencies_used
                FROM finbot.transactions 
                WHERE user_id = %s 
                AND created_at >= NOW() - INTERVAL '%s days'
            """, (chat_id, days_back))
            
            summary_row = cursor.fetchone()
            self.logger.debug(f"[{TAG}] Comprehensive summary query completed, found {summary_row[0] if summary_row else 0} transactions")
            
            # Get category breakdown
            self.logger.debug(f"[{TAG}] Executing category breakdown query")
            cursor.execute("""
                SELECT 
                    category, type,
                    COUNT(*) as count,
                    SUM(amount) as total,
                    AVG(amount) as average
                FROM finbot.transactions 
                WHERE user_id = %s 
                AND created_at >= NOW() - INTERVAL '%s days'
                AND category IS NOT NULL
                GROUP BY category, type
                ORDER BY total DESC
            """, (chat_id, days_back))
            
            category_rows = cursor.fetchall()
            self.logger.debug(f"[{TAG}] Category breakdown query completed, found {len(category_rows)} category groups")
            
            # Get spending trends (last 7 days vs previous 7 days)
            self.logger.debug(f"[{TAG}] Executing spending trends query")
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN created_at >= NOW() - INTERVAL '7 days' THEN 'recent'
                        ELSE 'previous'
                    END as period,
                    SUM(CASE WHEN type = 'chi' THEN amount ELSE 0 END) as expenses
                FROM finbot.transactions 
                WHERE user_id = %s 
                AND created_at >= NOW() - INTERVAL '14 days'
                AND type = 'chi'
                GROUP BY CASE 
                    WHEN created_at >= NOW() - INTERVAL '7 days' THEN 'recent'
                    ELSE 'previous'
                END
            """, (chat_id,))
            
            trend_rows = cursor.fetchall()
            self.logger.debug(f"[{TAG}] Spending trends query completed, found {len(trend_rows)} trend periods")
            cursor.close()
            self.logger.debug(f"[{TAG}] All summary queries completed, processing results")
            
            # Process results
            if not summary_row or summary_row[0] == 0:
                self.logger.info(f"[{TAG}] No transactions found for user {chat_id} in the last {days_back} days")
                return {
                    "total_transactions": 0,
                    "total_amount": 0,
                    "currency": "VND",
                    "period_days": days_back
                }
            
            self.logger.debug(f"[{TAG}] Processing summary data for {summary_row[0]} transactions")
            # Build categories dictionary
            categories = {}
            categories_by_type = {"chi": {}, "thu": {}, "vay": {}}
            
            for row in category_rows:
                category, trans_type, count, total, average = row
                if category:
                    # Overall categories (for backward compatibility)
                    if category not in categories:
                        categories[category] = 0
                    categories[category] += float(total or 0)
                    
                    # Categories by transaction type
                    categories_by_type[trans_type][category] = {
                        "count": count,
                        "total": float(total or 0),
                        "average": float(average or 0)
                    }
            
            # Calculate spending trend
            trend_data = {row[0]: float(row[1] or 0) for row in trend_rows}
            recent_spending = trend_data.get('recent', 0)
            previous_spending = trend_data.get('previous', 0)
            
            spending_trend = "stable"
            trend_percentage = 0
            if previous_spending > 0:
                trend_percentage = ((recent_spending - previous_spending) / previous_spending) * 100
                if trend_percentage > 10:
                    spending_trend = "increasing"
                elif trend_percentage < -10:
                    spending_trend = "decreasing"
            
            # Get most used currency
            currencies = summary_row[7] or ['VND']
            primary_currency = currencies[0] if currencies else 'VND'
            
            summary = {
                "total_transactions": summary_row[0] or 0,
                "total_income": float(summary_row[1] or 0),
                "total_expenses": float(summary_row[2] or 0),
                "total_loans": float(summary_row[3] or 0),
                "net_amount": float(summary_row[1] or 0) - float(summary_row[2] or 0),
                "avg_expense": float(summary_row[4] or 0),
                "currency": primary_currency,
                "last_transaction": summary_row[5].isoformat() if summary_row[5] else None,
                "unique_categories": summary_row[6] or 0,
                "period_days": days_back,
                
                # Category breakdowns
                "categories": categories,  # Backward compatibility
                "categories_by_type": categories_by_type,
                
                # Spending insights
                "spending_trend": {
                    "direction": spending_trend,
                    "percentage_change": round(trend_percentage, 2),
                    "recent_week_spending": recent_spending,
                    "previous_week_spending": previous_spending
                },
                
                # Additional metrics
                "currencies_used": currencies,
                "total_amount": float(summary_row[2] or 0)  # Backward compatibility (expenses)
            }
            
            self.logger.info(f"[{TAG}] Successfully generated comprehensive summary for user {chat_id}: {summary['total_transactions']} transactions, {summary['total_expenses']:.2f} {summary['currency']} expenses")
            self.logger.debug(f"[{TAG}] Summary details: income={summary['total_income']}, expenses={summary['total_expenses']}, net={summary['net_amount']}")
            return summary
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error getting transaction summary: {e}")
            self.logger.debug(f"[{TAG}] Exception details:", exc_info=True)
            return {
                "total_transactions": 0, 
                "total_amount": 0, 
                "currency": "VND",
                "period_days": days_back,
                "error": str(e)
            }
        finally:
            if conn:
                self.logger.debug(f"[{TAG}] Returning database connection to pool")
                self.db.return_postgres_connection(conn)

    async def save_parser_log(self, user_id: int, log_data: Dict[str, Any]) -> bool:
        """
        Save parser log data to PostgreSQL
        
        Args:
            user_id: Telegram user ID
            log_data: Parser log data dictionary
            
        Returns:
            bool: True if saved successfully
        """
        conn = None
        try:
            self.logger.info(f"[{TAG}] Starting parser log save for user {user_id}")
            self.logger.debug(f"[{TAG}] Parser log data: {log_data}")
            
            # Ensure user exists first
            self.logger.debug(f"[{TAG}] Ensuring user {user_id} exists before saving parser log")
            if not await self.ensure_user_exists(user_id):
                self.logger.error(f"[{TAG}] Failed to ensure user {user_id} exists for parser log")
                return False
            self.logger.debug(f"[{TAG}] User {user_id} confirmed for parser log save")
                
            self.logger.debug(f"[{TAG}] Establishing database connection for parser log save")
            conn = self.db.get_postgres_connection()
            if not conn:
                self.logger.error(f"[{TAG}] Cannot get database connection for parser log")
                return False
            self.logger.debug(f"[{TAG}] Database connection established for parser log")
                
            cursor = conn.cursor()
            self.logger.debug(f"[{TAG}] Database cursor created for parser log")
            
            # Extract data from log_data
            self.logger.debug(f"[{TAG}] Extracting and processing parser log data")
            original_message = log_data.get('original_message', '')
            parser_name = log_data.get('parser_name')
            message_type = log_data.get('message_type')
            parsed_data = log_data.get('parsed_data', {})
            extracted_verb = log_data.get('extracted_verb')
            extracted_item = log_data.get('extracted_item')
            extracted_amount = log_data.get('extracted_amount')
            extracted_currency = log_data.get('extracted_currency')
            extracted_category = log_data.get('extracted_category')
            extracted_time_info = log_data.get('extracted_time_info', {})
            success = log_data.get('success', True)
            error_message = log_data.get('error_message')
            processing_time_ms = log_data.get('processing_time_ms')
            confidence_score = log_data.get('confidence_score')
            
            self.logger.debug(f"[{TAG}] Parser log extracted data: parser={parser_name}, message_type={message_type}, success={success}")
            self.logger.debug(f"[{TAG}] Extracted financial data: verb={extracted_verb}, amount={extracted_amount}, currency={extracted_currency}")
            
            # Convert extracted_amount to decimal if it exists
            original_amount = extracted_amount
            if extracted_amount is not None:
                try:
                    extracted_amount = float(extracted_amount)
                    self.logger.debug(f"[{TAG}] Converted amount from {original_amount} to {extracted_amount}")
                except (ValueError, TypeError):
                    extracted_amount = None
                    self.logger.debug(f"[{TAG}] Failed to convert amount '{original_amount}' to float, setting to None")
            
            self.logger.info(f"[{TAG}] Executing parser log INSERT query")
            sql_query = """
                INSERT INTO finbot.parser_logs 
                (user_id, original_message, parser_name, message_type, parsed_data,
                 extracted_verb, extracted_item, extracted_amount, extracted_currency,
                 extracted_category, extracted_time_info, success, error_message,
                 processing_time_ms, confidence_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            sql_params = (
                user_id, original_message, parser_name, message_type, 
                json.dumps(parsed_data) if parsed_data else None,
                extracted_verb, extracted_item, extracted_amount, extracted_currency,
                extracted_category, json.dumps(extracted_time_info) if extracted_time_info else None,
                success, error_message, processing_time_ms, confidence_score
            )
            
            self.logger.debug(f"[{TAG}] Parser log SQL query: {sql_query}")
            self.logger.debug(f"[{TAG}] Parser log SQL params: {sql_params}")
            
            cursor.execute(sql_query, sql_params)
            self.logger.debug(f"[{TAG}] Parser log INSERT query executed successfully")
            
            self.logger.debug(f"[{TAG}] Committing parser log to database")
            conn.commit()
            self.logger.debug(f"[{TAG}] Parser log committed successfully")
            cursor.close()
            self.logger.debug(f"[{TAG}] Parser log database cursor closed")
            
            self.logger.info(f"[{TAG}] Successfully saved parser log for user {user_id}: {parser_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error saving parser log: {e}")
            self.logger.debug(f"[{TAG}] Exception details:", exc_info=True)
            if conn:
                self.logger.debug(f"[{TAG}] Rolling back parser log transaction")
                conn.rollback()
            return False
        finally:
            if conn:
                self.logger.debug(f"[{TAG}] Returning database connection to pool")
                self.db.return_postgres_connection(conn)

    async def get_user_stats(self, user_id: int, days_back: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive user statistics
        
        Args:
            user_id: Telegram user ID
            days_back: Number of days to analyze
            
        Returns:
            Dictionary with user statistics
        """
        conn = None
        try:
            conn = self.db.get_postgres_connection()
            if not conn:
                return {}
                
            cursor = conn.cursor()
            
            # Get basic user info and stats
            cursor.execute("""
                SELECT 
                    u.username, u.first_name, u.created_at,
                    COUNT(t.id) as total_transactions,
                    COUNT(pl.id) as total_messages
                FROM finbot.users u
                LEFT JOIN finbot.transactions t ON u.telegram_user_id = t.user_id
                    AND t.created_at >= NOW() - INTERVAL '%s days'
                LEFT JOIN finbot.parser_logs pl ON u.telegram_user_id = pl.user_id
                    AND pl.created_at >= NOW() - INTERVAL '%s days'
                WHERE u.telegram_user_id = %s
                GROUP BY u.telegram_user_id, u.username, u.first_name, u.created_at
            """, (days_back, days_back, user_id))
            
            user_row = cursor.fetchone()
            cursor.close()
            
            if not user_row:
                return {"error": "User not found"}
            
            stats = {
                "user_info": {
                    "username": user_row[0],
                    "first_name": user_row[1],
                    "member_since": user_row[2].isoformat() if user_row[2] else None
                },
                "activity": {
                    "total_transactions": user_row[3] or 0,
                    "total_messages": user_row[4] or 0,
                    "period_days": days_back
                }
            }
            
            # Get transaction summary
            transaction_summary = await self.get_transaction_summary(user_id, days_back)
            stats["financial_summary"] = transaction_summary
            
            return stats
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error getting user stats: {e}")
            return {"error": str(e)}
        finally:
            if conn:
                self.db.return_postgres_connection(conn)

    async def get_category_suggestions(self, text: str, language: str = 'vi') -> List[Dict[str, Any]]:
        """
        Get category suggestions based on text using database keywords
        
        Args:
            text: Text to analyze for category suggestions
            language: Language code (vi, en)
            
        Returns:
            List of category suggestions with confidence scores
        """
        conn = None
        try:
            conn = self.db.get_postgres_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            
            # Use the PostgreSQL function we created
            cursor.execute("""
                SELECT category, confidence 
                FROM finbot.suggest_category(%s, %s)
            """, (text, language))
            
            suggestions = []
            for row in cursor.fetchall():
                suggestions.append({
                    "category": row[0],
                    "confidence": float(row[1])
                })
            
            cursor.close()
            return suggestions
            
        except Exception as e:
            self.logger.error(f"[{TAG}] Error getting category suggestions: {e}")
            return []
        finally:
            if conn:
                self.db.return_postgres_connection(conn)


# Create global transaction repository instance
transaction_repository_service = TransactionRepository()