#!/bin/bash
set -e

echo "Creating ClickHouse schemas for analytics..."

# Note: This script should be run after ClickHouse is up and running
# You might want to integrate this into your application startup or create a separate initialization step

# ClickHouse connection details from environment variables
CLICKHOUSE_HOST=${CLICKHOUSE_HOST:-localhost}
CLICKHOUSE_PORT=${CLICKHOUSE_PORT:-8123}
CLICKHOUSE_USER=${CLICKHOUSE_USER:-default}
CLICKHOUSE_PASSWORD=${CLICKHOUSE_PASSWORD:-}
CLICKHOUSE_DB=${CLICKHOUSE_DB:-finbot}

# Function to execute ClickHouse SQL
execute_clickhouse_sql() {
    local sql="$1"
    if [ -n "$CLICKHOUSE_PASSWORD" ]; then
        curl -s "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
             --user "${CLICKHOUSE_USER}:${CLICKHOUSE_PASSWORD}" \
             --data-binary "$sql"
    else
        curl -s "http://${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}/" \
             --user "${CLICKHOUSE_USER}:" \
             --data-binary "$sql"
    fi
}

# Wait for ClickHouse to be ready
echo "⏳ Waiting for ClickHouse to be ready..."
for i in {1..30}; do
    if execute_clickhouse_sql "SELECT 1" > /dev/null 2>&1; then
        echo "✅ ClickHouse is ready!"
        break
    fi
    echo "   Attempt $i/30: ClickHouse not ready yet, waiting..."
    sleep 2
done

# Create database
echo "📁 Creating database ${CLICKHOUSE_DB}..."
execute_clickhouse_sql "CREATE DATABASE IF NOT EXISTS ${CLICKHOUSE_DB}"

# Create transactions analytics table (optimized for time-series analytics)
echo "📊 Creating transactions analytics table..."
execute_clickhouse_sql "
CREATE TABLE IF NOT EXISTS ${CLICKHOUSE_DB}.transactions_analytics (
    id UUID,
    user_id UInt64,
    telegram_username String,
    type Enum8('chi' = 1, 'thu' = 2, 'vay' = 3),
    amount Decimal64(2),
    currency FixedString(3),
    category String,
    note String,
    merchant String,
    account String,
    status String,
    transaction_date Date,
    transaction_hour UInt8,
    day_of_week UInt8,
    month UInt8,
    year UInt16,
    created_at DateTime64(3, 'Asia/Ho_Chi_Minh'),
    updated_at DateTime64(3, 'Asia/Ho_Chi_Minh')
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(transaction_date)
ORDER BY (user_id, transaction_date, created_at)
SETTINGS index_granularity = 8192
"

# Create parser performance analytics table
echo "🔍 Creating parser analytics table..."
execute_clickhouse_sql "
CREATE TABLE IF NOT EXISTS ${CLICKHOUSE_DB}.parser_analytics (
    id UInt64,
    user_id UInt64,
    parser_name String,
    message_type String,
    message_length UInt32,
    success UInt8,
    processing_time_ms UInt32,
    error_type String,
    created_date Date,
    created_hour UInt8,
    created_at DateTime64(3, 'Asia/Ho_Chi_Minh')
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (created_date, parser_name, success)
SETTINGS index_granularity = 8192
"

# Create user activity analytics table
echo "👤 Creating user activity analytics table..."
execute_clickhouse_sql "
CREATE TABLE IF NOT EXISTS ${CLICKHOUSE_DB}.user_activity (
    user_id UInt64,
    telegram_username String,
    activity_type Enum8('message' = 1, 'transaction' = 2, 'command' = 3),
    activity_date Date,
    activity_hour UInt8,
    day_of_week UInt8,
    month UInt8,
    year UInt16,
    count UInt32,
    created_at DateTime64(3, 'Asia/Ho_Chi_Minh')
) ENGINE = SummingMergeTree(count)
PARTITION BY toYYYYMM(activity_date)
ORDER BY (user_id, activity_type, activity_date, activity_hour)
SETTINGS index_granularity = 8192
"

# Create materialized views for real-time analytics
echo "📈 Creating materialized views..."

# Daily transaction summary view
execute_clickhouse_sql "
CREATE MATERIALIZED VIEW IF NOT EXISTS ${CLICKHOUSE_DB}.daily_transaction_summary
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(transaction_date)
ORDER BY (user_id, transaction_date, type, currency)
AS SELECT
    user_id,
    transaction_date,
    type,
    currency,
    count() as transaction_count,
    sum(amount) as total_amount,
    avg(amount) as avg_amount,
    min(amount) as min_amount,
    max(amount) as max_amount
FROM ${CLICKHOUSE_DB}.transactions_analytics
GROUP BY user_id, transaction_date, type, currency
"

# Category spending analysis view
execute_clickhouse_sql "
CREATE MATERIALIZED VIEW IF NOT EXISTS ${CLICKHOUSE_DB}.category_spending_summary
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(transaction_date)
ORDER BY (user_id, category, transaction_date)
AS SELECT
    user_id,
    category,
    transaction_date,
    type,
    count() as transaction_count,
    sum(amount) as total_amount
FROM ${CLICKHOUSE_DB}.transactions_analytics
WHERE type = 'chi'
GROUP BY user_id, category, transaction_date, type
"

# Parser performance summary view
execute_clickhouse_sql "
CREATE MATERIALIZED VIEW IF NOT EXISTS ${CLICKHOUSE_DB}.parser_performance_summary
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (parser_name, created_date)
AS SELECT
    parser_name,
    message_type,
    created_date,
    count() as total_messages,
    sum(success) as successful_parses,
    avg(processing_time_ms) as avg_processing_time,
    max(processing_time_ms) as max_processing_time
FROM ${CLICKHOUSE_DB}.parser_analytics
GROUP BY parser_name, message_type, created_date
"

echo "✅ ClickHouse schemas created successfully!"
echo "📊 Created tables:"
echo "   - ${CLICKHOUSE_DB}.transactions_analytics (Time-series transaction data)"
echo "   - ${CLICKHOUSE_DB}.parser_analytics (Parser performance metrics)"
echo "   - ${CLICKHOUSE_DB}.user_activity (User activity tracking)"
echo "📈 Created materialized views:"
echo "   - ${CLICKHOUSE_DB}.daily_transaction_summary"
echo "   - ${CLICKHOUSE_DB}.category_spending_summary"
echo "   - ${CLICKHOUSE_DB}.parser_performance_summary"
echo "🚀 Ready for real-time analytics and reporting!"