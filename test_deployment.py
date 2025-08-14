#!/usr/bin/env python3
"""
Simple test script to debug deployment issues
"""

import os
import sys
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_telegram_connection():
    """Test basic Telegram connection"""
    print("🔍 Testing Telegram connection...")
    
    try:
        # Test config loading
        from config import config
        print(f"✅ Config loaded successfully")
        print(f"   API_ID: {config.api_id}")
        print(f"   PHONE: {config.phone_number}")
        print(f"   CHANNELS: {len(config.target_channels)} channels")
        print(f"   TARGET_USER: {config.target_user_id}")
        
        # Test Telegram client creation
        from telegram_client import TelegramJobClient
        print(f"✅ Telegram client imported successfully")
        
        # Test connection
        client = TelegramJobClient()
        print(f"✅ Client created successfully")
        
        # Try to start (this will show any errors)
        await client.start()
        print(f"✅ Telegram client started successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting deployment test...")
    print("=" * 50)
    
    # Test environment variables
    print("📋 Environment Variables:")
    required_vars = ['API_ID', 'API_HASH', 'PHONE_NUMBER', 'TARGET_CHANNELS', 'TARGET_USER_ID']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var in ['API_HASH']:
                print(f"   {var}: {value[:10]}... ✅")
            else:
                print(f"   {var}: {value} ✅")
        else:
            print(f"   {var}: NOT SET ❌")
    
    print()
    
    # Test Telegram connection
    try:
        success = asyncio.run(test_telegram_connection())
        if success:
            print("\n🎉 All tests passed! Telegram scraper should work.")
        else:
            print("\n❌ Tests failed. Check the errors above.")
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")

if __name__ == "__main__":
    main()
