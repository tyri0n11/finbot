import clickhouse_connect
from typing import Optional
import os


class ClickHouseClient:
    def __init__(self):
        self.host = os.getenv("CLICKHOUSE_HOST", "localhost")
        self.port = int(os.getenv("CLICKHOUSE_PORT", "8123"))
        self.username = os.getenv("CLICKHOUSE_USER", "default")
        self.password = os.getenv("CLICKHOUSE_PASSWORD", "")
        self.database = os.getenv("CLICKHOUSE_DB", "weather")
        self.client = None
        
    def connect(self):
        """Establish connection to ClickHouse"""
        try:
            self.client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database
            )
            return True
        except Exception as e:
            print(f"Failed to connect to ClickHouse: {e}")
            return False
    
    def disconnect(self):
        """Close connection"""
        if self.client:
            self.client.close()
            self.client = None
    
    def execute_query(self, query: str, parameters: Optional[dict] = None):
        """Execute a query and return results"""
        if not self.client:
            if not self.connect():
                raise Exception("Cannot connect to ClickHouse")
        
        try:
            if parameters:
                return self.client.query(query, parameters=parameters)
            else:
                return self.client.query(query)
        except Exception as e:
            print(f"Query execution failed: {e}")
            raise
    
    def insert_data(self, table: str, data: list):
        """Insert data into table"""
        if not self.client:
            if not self.connect():
                raise Exception("Cannot connect to ClickHouse")
        
        try:
            # Convert list of dicts to format expected by ClickHouse
            if data and isinstance(data[0], dict):
                # Convert to column format
                columns = list(data[0].keys())
                rows = []
                for row in data:
                    rows.append([row[col] for col in columns])
                self.client.insert(table, rows, column_names=columns)
            else:
                self.client.insert(table, data)
        except Exception as e:
            print(f"Insert failed: {e}")
            print(f"Table: {table}")
            print(f"Data: {data}")
            print(f"Data type: {type(data)}")
            if data:
                print(f"First row: {data[0]}")
                print(f"First row type: {type(data[0])}")
            raise


# Global client instance
clickhouse_client = ClickHouseClient()
