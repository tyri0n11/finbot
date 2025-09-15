from datetime import datetime
from typing import List, Optional
from models.weather import WeatherCreate, WeatherUpdate, WeatherResponse
from services.clickhouse_client import clickhouse_client


class WeatherService:
    def __init__(self):
        self.client = clickhouse_client
        self.table_name = "weather_data"
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """Create weather_data table if it doesn't exist"""
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id UInt64,
            location String,
            temperature Float64,
            humidity Float64,
            pressure Float64,
            description String,
            wind_speed Nullable(Float64),
            wind_direction Nullable(String),
            created_at DateTime DEFAULT now(),
            updated_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (id, created_at)
        """
        try:
            self.client.execute_query(create_table_query)
        except Exception as e:
            print(f"Failed to create table: {e}")
    
    def create_weather(self, weather_data: WeatherCreate) -> WeatherResponse:
        """Create new weather record"""
        # Generate ID (simple approach - in production, use UUID or better ID generation)
        max_id_query = f"SELECT max(id) as max_id FROM {self.table_name}"
        result = self.client.execute_query(max_id_query)
        next_id = (result.result_rows[0][0] + 1) if result.result_rows and result.result_rows[0][0] else 1
        
        now = datetime.now()
        insert_data = [{
            'id': next_id,
            'location': weather_data.location,
            'temperature': weather_data.temperature,
            'humidity': weather_data.humidity,
            'pressure': weather_data.pressure,
            'description': weather_data.description,
            'wind_speed': weather_data.wind_speed,
            'wind_direction': weather_data.wind_direction,
            'created_at': now,
            'updated_at': now
        }]
        
        self.client.insert_data(self.table_name, insert_data)
        
        return WeatherResponse(
            id=next_id,
            location=weather_data.location,
            temperature=weather_data.temperature,
            humidity=weather_data.humidity,
            pressure=weather_data.pressure,
            description=weather_data.description,
            wind_speed=weather_data.wind_speed,
            wind_direction=weather_data.wind_direction,
            created_at=now,
            updated_at=now
        )
    
    def get_weather(self, weather_id: int) -> Optional[WeatherResponse]:
        """Get weather record by ID"""
        query = f"""
        SELECT id, location, temperature, humidity, pressure, description, 
               wind_speed, wind_direction, created_at, updated_at
        FROM {self.table_name}
        WHERE id = {{weather_id:UInt64}}
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        result = self.client.execute_query(query, {"weather_id": weather_id})
        
        if not result.result_rows:
            return None
        
        row = result.result_rows[0]
        return WeatherResponse(
            id=row[0],
            location=row[1],
            temperature=row[2],
            humidity=row[3],
            pressure=row[4],
            description=row[5],
            wind_speed=row[6],
            wind_direction=row[7],
            created_at=row[8],
            updated_at=row[9]
        )
    
    def get_weather_list(self, skip: int = 0, limit: int = 100) -> List[WeatherResponse]:
        """Get list of weather records"""
        query = f"""
        SELECT id, location, temperature, humidity, pressure, description,
               wind_speed, wind_direction, created_at, updated_at
        FROM {self.table_name}
        ORDER BY created_at DESC
        LIMIT {{limit:UInt32}} OFFSET {{skip:UInt32}}
        """
        
        result = self.client.execute_query(query, {"limit": limit, "skip": skip})
        
        weather_list = []
        for row in result.result_rows:
            weather_list.append(WeatherResponse(
                id=row[0],
                location=row[1],
                temperature=row[2],
                humidity=row[3],
                pressure=row[4],
                description=row[5],
                wind_speed=row[6],
                wind_direction=row[7],
                created_at=row[8],
                updated_at=row[9]
            ))
        
        return weather_list
    
    def update_weather(self, weather_id: int, weather_update: WeatherUpdate) -> Optional[WeatherResponse]:
        """Update weather record - ClickHouse doesn't support UPDATE, so we insert new record"""
        # First get existing record
        existing = self.get_weather(weather_id)
        if not existing:
            return None
        
        # Create updated data
        update_data = existing.dict()
        update_data.update({k: v for k, v in weather_update.dict().items() if v is not None})
        update_data['updated_at'] = datetime.now()
        
        # Insert updated record
        insert_data = [update_data]
        self.client.insert_data(self.table_name, insert_data)
        
        return WeatherResponse(**update_data)
    
    def delete_weather(self, weather_id: int) -> bool:
        """Delete weather record - ClickHouse doesn't support DELETE in all versions,
        so we'll mark as deleted or use ALTER DELETE for specific versions"""
        # For this example, we'll use ALTER DELETE (available in newer ClickHouse versions)
        try:
            delete_query = f"""
            ALTER TABLE {self.table_name} DELETE WHERE id = {{weather_id:UInt64}}
            """
            self.client.execute_query(delete_query, {"weather_id": weather_id})
            return True
        except Exception as e:
            print(f"Delete failed: {e}")
            return False
    
    def get_weather_by_location(self, location: str, limit: int = 10) -> List[WeatherResponse]:
        """Get weather records by location"""
        query = f"""
        SELECT id, location, temperature, humidity, pressure, description,
               wind_speed, wind_direction, created_at, updated_at
        FROM {self.table_name}
        WHERE location = {{location:String}}
        ORDER BY created_at DESC
        LIMIT {{limit:UInt32}}
        """
        
        result = self.client.execute_query(query, {"location": location, "limit": limit})
        
        weather_list = []
        for row in result.result_rows:
            weather_list.append(WeatherResponse(
                id=row[0],
                location=row[1],
                temperature=row[2],
                humidity=row[3],
                pressure=row[4],
                description=row[5],
                wind_speed=row[6],
                wind_direction=row[7],
                created_at=row[8],
                updated_at=row[9]
            ))
        
        return weather_list


# Global service instance
weather_service = WeatherService()
