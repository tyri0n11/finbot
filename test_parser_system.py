#!/usr/bin/env python3
"""
Test script for the new parser system with clean architecture
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.parser_manager import parser_manager


def test_parser_system():
    """Test the parser system with various message types"""
    
    test_messages = [
        # Command messages
        "/help",
        "/start",
        "/balance",
        "/giup",  # Vietnamese command
        "/sodu",  # Vietnamese command
        
        # Vietnamese transaction messages
        "mua bánh mì 20k",
        "chi tiền cafe 45k",
        "đi ăn phở 80k",
        "trả tiền xăng 500k",
        "mua laptop 25tr",
        "thanh toán điện 1.5m",
        
        # JSON messages
        '{"amount": 50000, "description": "lunch", "category": "food"}',
        '{"name": "John", "age": 30, "city": "Ho Chi Minh"}',
        
        # Key-value messages
        "amount: 200k\ndescription: coffee\ncategory: beverage",
        "price: 1.5tr\nitem: phone\nstore: FPT Shop",
        
        # Text messages
        "Hello world, this is a test message",
        "Xin chào, đây là tin nhắn thử nghiệm",
        
        # Complex transaction messages
        "spent 150,000 VND for groceries at Big C",
        "bought coffee for $5.50 at Starbucks",
        "paid 2.5m VND for rent this month",
    ]
    
    print("🚀 Testing Parser System with Clean Architecture")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing message: '{message}'")
        print("-" * 40)
        
        try:
            result = parser_manager.parse_message(message)
            
            print(f"✅ Parser: {result.parser_name}")
            print(f"✅ Type: {result.message_type.value}")
            print(f"✅ Success: {result.is_successful()}")
            print(f"✅ Data: {result.data}")
            
            if result.errors:
                print(f"⚠️  Errors: {result.errors}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("=" * 60)
    print("🎉 Parser system test completed!")


def test_specific_parsers():
    """Test specific parser types"""
    
    print("\n🔧 Testing Specific Parsers")
    print("=" * 60)
    
    # Test command parser specifically
    print("\n1. Testing Command Parser:")
    command_result = parser_manager.parse_with_specific_parser("/help", "CommandParser")
    if command_result:
        print(f"   Result: {command_result.to_dict()}")
    
    # Test transaction parser specifically
    print("\n2. Testing Transaction Parser:")
    transaction_result = parser_manager.parse_with_specific_parser("mua bánh mì 20k", "TransactionParser")
    if transaction_result:
        print(f"   Result: {transaction_result.to_dict()}")
    
    # Test JSON parser specifically
    print("\n3. Testing JSON Parser:")
    json_result = parser_manager.parse_with_specific_parser('{"test": "value"}', "JSONParser")
    if json_result:
        print(f"   Result: {json_result.to_dict()}")


def test_parser_priorities():
    """Test parser priority system"""
    
    print("\n📊 Testing Parser Priorities")
    print("=" * 60)
    
    # Message that could be parsed by multiple parsers
    ambiguous_message = "/help with transaction: amount 100k"
    
    print(f"Testing ambiguous message: '{ambiguous_message}'")
    result = parser_manager.parse_message(ambiguous_message)
    
    print(f"Selected parser: {result.parser_name}")
    print(f"Priority ensures commands are handled by CommandParser first")


if __name__ == "__main__":
    test_parser_system()
    test_specific_parsers()
    test_parser_priorities()