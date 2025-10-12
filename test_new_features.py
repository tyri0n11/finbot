#!/usr/bin/env python3
"""
Test script for new income and time features
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from utils.text_processing import extract_vietnamese_transaction_parts, extract_vietnamese_time_reference
from utils.validation import is_transaction_message
from services.parser import parser_manager_service


def test_income_detection():
    """Test income detection functionality"""
    print("\n🚀 Testing Income Detection")
    print("=" * 50)
    
    income_messages = [
        "nhận lương 15tr hôm nay",
        "được thưởng 5m tuần trước", 
        "bán laptop 20tr",
        "kiếm được 500k hôm qua",
        "thu nhập freelance 10tr tháng này",
        "tiền lương tháng 8tr",
        "received salary $3000 yesterday",
        "earned $500 from freelance work",
    ]
    
    for i, message in enumerate(income_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 30)
        
        # Test validation
        is_transaction = is_transaction_message(message)
        print(f"   ✅ Is transaction: {is_transaction}")
        
        # Test extraction
        parts = extract_vietnamese_transaction_parts(message)
        print(f"   📊 Type: {parts.get('type', 'Not detected')}")
        print(f"   📊 Verb: {parts.get('verb', 'Not detected')}")
        print(f"   💰 Amount: {parts.get('amount', 'Not detected')}")
        print(f"   📝 Item: {parts.get('item', 'Not detected')}")
        print(f"   🏷️ Category: {parts.get('category', 'Not detected')}")
        
        # Test full parser
        result = parser_manager_service.parse_message(message)
        print(f"   🤖 Parser: {result.parser_name}")
        print(f"   📋 Success: {result.is_successful()}")


def test_time_extraction():
    """Test time extraction functionality"""
    print("\n🕐 Testing Time Extraction")
    print("=" * 50)
    
    time_messages = [
        "mua bánh mì 20k hôm nay",
        "chi tiền cafe 45k hôm qua", 
        "trả tiền xăng 500k 15/10",
        "nhận lương 15tr tuần trước",
        "mua laptop 25tr 2 ngày trước",
        "đi ăn phở 80k ngày mai",
        "spent $50 yesterday",
        "bought coffee today",
    ]
    
    for i, message in enumerate(time_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 30)
        
        # Test time extraction
        time_info = extract_vietnamese_time_reference(message)
        if time_info:
            print(f"   📅 Time type: {time_info.get('type', 'Unknown')}")
            print(f"   📅 Date value: {time_info.get('value', 'Unknown')}")
            print(f"   📅 Original: {time_info.get('original', 'Unknown')}")
        else:
            print(f"   ❌ No time reference found")
        
        # Test full extraction
        parts = extract_vietnamese_transaction_parts(message)
        if 'time' in parts:
            print(f"   🕐 Full time info: {parts['time']}")
        
        # Test full parser
        result = parser_manager_service.parse_message(message)
        if result.is_successful():
            time_data = result.data.get('time_reference')
            if time_data:
                print(f"   🤖 Parser time: {time_data}")


def test_combined_features():
    """Test combined income + time features"""
    print("\n💡 Testing Combined Features (Income + Time)")
    print("=" * 60)
    
    combined_messages = [
        "nhận lương 15tr hôm qua",
        "được thưởng 5m tuần trước",
        "bán điện thoại 20tr 15/10", 
        "kiếm được 500k freelance hôm nay",
        "thu tiền bán đồ 2tr 3 ngày trước",
    ]
    
    for i, message in enumerate(combined_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 40)
        
        # Full parser test
        result = parser_manager_service.parse_message(message)
        print(f"   🤖 Parser: {result.parser_name}")
        print(f"   📋 Success: {result.is_successful()}")
        print(f"   📊 Type: {result.message_type.value}")
        
        if result.is_successful():
            data = result.data
            print(f"   💰 Amount: {data.get('amount', 'N/A')}")
            print(f"   💱 Currency: {data.get('currency', 'N/A')}")
            print(f"   📝 Description: {data.get('description', 'N/A')}")
            print(f"   🏷️ Category: {data.get('category', 'N/A')}")
            print(f"   💼 Transaction type: {data.get('transaction_type', 'N/A')}")
            print(f"   📅 Date: {data.get('date', 'N/A')}")
            
            if 'time_reference' in data:
                time_ref = data['time_reference']
                print(f"   🕐 Time ref: {time_ref.get('type', 'N/A')} - {time_ref.get('value', 'N/A')}")
        
        if result.errors:
            print(f"   ❌ Errors: {result.errors}")


if __name__ == "__main__":
    print("🧪 Testing New Parser Features: Income & Time Detection")
    print("=" * 70)
    
    test_income_detection()
    test_time_extraction() 
    test_combined_features()
    
    print("\n" + "=" * 70)
    print("🎉 Test completed! Check results above.")