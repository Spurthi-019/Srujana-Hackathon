import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_database_connection():
    """Test MongoDB connection and basic operations"""
    try:
        # Get MongoDB URI from environment
        MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        DATABASE_NAME = os.getenv('DATABASE_NAME', 'college_app')
        
        print(f"🔌 Connecting to MongoDB: {MONGODB_URI}")
        
        # Create client and connect
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        # Test connection by pinging the server
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test basic operations
        test_collection = db.test_connection
        
        # Insert test document
        test_doc = {"test": "connection", "timestamp": "2025-09-15"}
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read test document
        doc = await test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Test document retrieved: {doc}")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"✅ Available collections: {collections}")
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        # Close connection
        client.close()
        print("✅ Database connection test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_database_connection())
    if result:
        print("\n🎉 Database is ready for use!")
    else:
        print("\n💥 Database connection issues detected!")