#!/usr/bin/env python3
"""
Test script to send messages to the Telegram bot via webhook
"""

import requests
import json
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.settings import settings

def send_test_message(message_text, chat_id=123456789):
    """Send a test message to the bot via webhook"""
    
    webhook_url = "http://localhost:8000/webhook"
    
    # Create a fake Telegram update
    telegram_update = {
        "update_id": 123456,
        "message": {
            "message_id": 789,
            "from": {
                "id": chat_id,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": chat_id,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": 1633536000,
            "text": message_text
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=telegram_update,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ Sent message: '{message_text}'")
        print(f"📋 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Message processed successfully")
        else:
            print(f"❌ Error: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


def test_parser_messages():
    """Test various message types with the new parser system"""
    
    test_messages = [
        # Command tests
        "/help",
        "/giup",  # Vietnamese command
        "/start",
        "/balance",
        "/sodu",  # Vietnamese command
        
        # Vietnamese transaction tests
        "mua bánh mì 20k",
        "chi tiền cafe 45k", 
        "đi ăn phở 80k",
        "trả tiền xăng 500k",
        "mua laptop 25tr",
        "thanh toán điện 1.5m",
        
        # English transaction tests
        "spent $5.50 for coffee at Starbucks",
        "bought groceries for 150,000 VND",
        "paid 2.5m VND for rent",
        
        # JSON tests
        '{"amount": 50000, "description": "lunch", "category": "food"}',
        
        # Key-value tests
        "amount: 200k\ndescription: coffee\ncategory: beverage",
        
        # Text tests
        "Hello, this is a test message",
        "Xin chào, đây là tin nhắn thử nghiệm"
    ]
    
    print("🚀 Testing Telegram Bot with New Parser System")
    print("=" * 60)
    
    successful = 0
    total = len(test_messages)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 40)
        
        if send_test_message(message):
            successful += 1
        
        # Small delay between messages
        import time
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"🎉 Test completed: {successful}/{total} messages sent successfully")
    print("Check Docker logs for parsing results!")


if __name__ == "__main__":
    test_parser_messages()