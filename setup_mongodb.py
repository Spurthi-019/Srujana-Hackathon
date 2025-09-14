#!/usr/bin/env python3
"""
MongoDB Setup Script for Windows
================================

This script helps set up MongoDB for the attendance system.
It provides options for local MongoDB installation or MongoDB Atlas setup.

Author: SmartClass AI
Date: September 2025
"""

import os
import json
import subprocess
import requests
import zipfile
import shutil
from pathlib import Path

class MongoDBSetup:
    def __init__(self):
        """Initialize MongoDB setup."""
        print("🗄️  MongoDB Setup for AI Attendance System")
        print("=" * 50)
        
    def check_mongodb_installed(self):
        """Check if MongoDB is already installed."""
        try:
            result = subprocess.run(['mongod', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ MongoDB is already installed!")
                print(f"Version: {result.stdout.splitlines()[0]}")
                return True
        except:
            pass
        
        print("❌ MongoDB not found in system PATH")
        return False
    
    def install_mongodb_windows(self):
        """Install MongoDB Community Server on Windows."""
        print("\n🔧 Installing MongoDB Community Server...")
        
        # MongoDB download URL (Community Server 7.0)
        mongodb_url = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.12.zip"
        download_path = "mongodb-windows.zip"
        install_dir = "C:\\mongodb"
        
        try:
            print("📥 Downloading MongoDB...")
            response = requests.get(mongodb_url, stream=True)
            response.raise_for_status()
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("✅ Download completed")
            
            print("📦 Extracting MongoDB...")
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall("temp_mongodb")
            
            # Move to install directory
            extracted_dir = list(Path("temp_mongodb").glob("mongodb-*"))[0]
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            shutil.move(str(extracted_dir), install_dir)
            
            print(f"✅ MongoDB installed to {install_dir}")
            
            # Create data directory
            data_dir = "C:\\data\\db"
            os.makedirs(data_dir, exist_ok=True)
            print(f"✅ Created data directory: {data_dir}")
            
            # Add to PATH
            bin_path = f"{install_dir}\\bin"
            current_path = os.environ.get('PATH', '')
            if bin_path not in current_path:
                print(f"⚠️  Add to PATH manually: {bin_path}")
                print("   Or run MongoDB with full path:")
                print(f"   {bin_path}\\mongod.exe --dbpath C:\\data\\db")
            
            # Cleanup
            os.remove(download_path)
            shutil.rmtree("temp_mongodb")
            
            return True
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def setup_mongodb_service(self):
        """Set up MongoDB as a Windows service."""
        print("\n🔧 Setting up MongoDB as Windows service...")
        
        try:
            # Create MongoDB config file
            config_content = """
systemLog:
  destination: file
  path: C:\\data\\log\\mongod.log
storage:
  dbPath: C:\\data\\db
net:
  bindIp: 127.0.0.1
  port: 27017
"""
            
            config_dir = "C:\\data\\config"
            os.makedirs(config_dir, exist_ok=True)
            
            with open(f"{config_dir}\\mongod.cfg", 'w') as f:
                f.write(config_content)
            
            # Create log directory
            os.makedirs("C:\\data\\log", exist_ok=True)
            
            print("✅ MongoDB configuration created")
            
            # Install as service (requires admin privileges)
            service_cmd = [
                "C:\\mongodb\\bin\\mongod.exe",
                "--config", "C:\\data\\config\\mongod.cfg",
                "--install"
            ]
            
            print("⚠️  Installing MongoDB service (requires administrator privileges)...")
            result = subprocess.run(service_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ MongoDB service installed successfully")
                
                # Start the service
                subprocess.run(["net", "start", "MongoDB"], check=True)
                print("✅ MongoDB service started")
                return True
            else:
                print(f"❌ Service installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Service setup failed: {e}")
            print("💡 Try running as administrator or start manually:")
            print("   C:\\mongodb\\bin\\mongod.exe --dbpath C:\\data\\db")
            return False
    
    def start_mongodb_manually(self):
        """Start MongoDB manually."""
        print("\n🚀 Starting MongoDB manually...")
        
        try:
            # Create data directory if it doesn't exist
            os.makedirs("C:\\data\\db", exist_ok=True)
            
            # Start MongoDB
            mongodb_cmd = ["C:\\mongodb\\bin\\mongod.exe", "--dbpath", "C:\\data\\db"]
            
            print("🔄 Starting MongoDB server...")
            print("   Database path: C:\\data\\db")
            print("   Port: 27017")
            print("   Press Ctrl+C to stop")
            
            subprocess.run(mongodb_cmd)
            
        except KeyboardInterrupt:
            print("\n⚠️  MongoDB stopped by user")
        except Exception as e:
            print(f"❌ Failed to start MongoDB: {e}")
    
    def test_mongodb_connection(self):
        """Test MongoDB connection."""
        print("\n🧪 Testing MongoDB connection...")
        
        try:
            from pymongo import MongoClient
            
            client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            
            print("✅ MongoDB connection successful!")
            
            # Test database operations
            db = client["smartclass_attendance"]
            collection = db["test_collection"]
            
            # Insert test document
            test_doc = {"test": True, "message": "MongoDB is working!"}
            result = collection.insert_one(test_doc)
            print(f"✅ Test write successful (ID: {result.inserted_id})")
            
            # Read test document
            found_doc = collection.find_one({"_id": result.inserted_id})
            print(f"✅ Test read successful: {found_doc['message']}")
            
            # Clean up
            collection.delete_one({"_id": result.inserted_id})
            client.close()
            
            return True
            
        except ImportError:
            print("❌ PyMongo not installed. Run: pip install pymongo")
            return False
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    def create_config_file(self):
        """Create MongoDB configuration file for the attendance system."""
        config = {
            "connection_string": "mongodb://localhost:27017/",
            "database_name": "smartclass_attendance"
        }
        
        with open("mongodb_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("✅ Created mongodb_config.json")
        
    def setup_mongodb_atlas(self):
        """Provide instructions for MongoDB Atlas setup."""
        print("\n☁️  MongoDB Atlas (Cloud) Setup")
        print("=" * 40)
        print("MongoDB Atlas provides a free cloud database perfect for this project.")
        print("\nSteps to set up MongoDB Atlas:")
        print("\n1. 📝 Create Account:")
        print("   • Go to https://www.mongodb.com/atlas")
        print("   • Click 'Try Free' and create an account")
        
        print("\n2. 🗄️  Create Cluster:")
        print("   • Choose 'FREE Shared' cluster")
        print("   • Select a region close to you")
        print("   • Click 'Create Cluster'")
        
        print("\n3. 👤 Create Database User:")
        print("   • Go to 'Database Access'")
        print("   • Click 'Add New Database User'")
        print("   • Username: smartclass")
        print("   • Password: (generate a strong password)")
        print("   • Give 'Read and write to any database' permission")
        
        print("\n4. 🌐 Configure Network Access:")
        print("   • Go to 'Network Access'")
        print("   • Click 'Add IP Address'")
        print("   • Click 'Allow Access from Anywhere' (0.0.0.0/0)")
        print("   • Or add your specific IP address")
        
        print("\n5. 🔗 Get Connection String:")
        print("   • Go to 'Clusters' and click 'Connect'")
        print("   • Choose 'Connect your application'")
        print("   • Copy the connection string")
        print("   • Replace <password> with your actual password")
        
        print("\n6. ⚙️  Update Configuration:")
        print("   • Create/update mongodb_config.json:")
        
        atlas_config = {
            "connection_string": "mongodb+srv://smartclass:<password>@cluster0.mongodb.net/",
            "database_name": "smartclass_attendance"
        }
        
        print(f"   {json.dumps(atlas_config, indent=4)}")
        
        response = input("\n❓ Do you want to create this config file template? (y/n): ")
        if response.lower() == 'y':
            with open("mongodb_atlas_config_template.json", "w") as f:
                json.dump(atlas_config, f, indent=2)
            print("✅ Created mongodb_atlas_config_template.json")
            print("   Update the password and rename to mongodb_config.json")
    
    def main_menu(self):
        """Main setup menu."""
        while True:
            print("\n🗄️  MongoDB Setup Options")
            print("=" * 30)
            print("1. 🔍 Check if MongoDB is installed")
            print("2. 📥 Install MongoDB locally (Windows)")
            print("3. 🔧 Set up MongoDB as service")
            print("4. 🚀 Start MongoDB manually")
            print("5. 🧪 Test MongoDB connection")
            print("6. ⚙️  Create config file (local)")
            print("7. ☁️  MongoDB Atlas setup (cloud)")
            print("8. ❌ Exit")
            
            choice = input("\nSelect option (1-8): ").strip()
            
            if choice == '1':
                self.check_mongodb_installed()
            elif choice == '2':
                if self.install_mongodb_windows():
                    self.create_config_file()
            elif choice == '3':
                self.setup_mongodb_service()
            elif choice == '4':
                self.start_mongodb_manually()
            elif choice == '5':
                if self.test_mongodb_connection():
                    print("\n🎉 MongoDB is ready for the attendance system!")
            elif choice == '6':
                self.create_config_file()
            elif choice == '7':
                self.setup_mongodb_atlas()
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option, please try again.")

def main():
    """Main function."""
    setup = MongoDBSetup()
    setup.main_menu()

if __name__ == "__main__":
    main()