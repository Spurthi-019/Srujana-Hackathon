from pymongo import MongoClient
import json

# Load MongoDB configuration
with open('mongodb_config.json', 'r') as f:
    config = json.load(f)

try:
    # Test connection
    client = MongoClient(config['connection_string'])
    client.admin.command('ping')
    print('✅ MongoDB connection successful!')
    print(f'📊 Database: {config["database_name"]}')
    print(f'🔗 Connection string: {config["connection_string"]}')
    
    # Test database access
    db = client[config['database_name']]
    collections = db.list_collection_names()
    print(f'📁 Collections: {collections if collections else "No collections yet"}')
    
    client.close()
    print('🎯 Ready for attendance system!')
    
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    print('💡 Make sure MongoDB is running on localhost:27017')