import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests

def test_google_services():
    """Test Google API services"""
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    print(f"🔑 Google API Key found: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        return False
    
    try:
        # Test Google Generative AI (Gemini)
        print("🧠 Testing Google Generative AI (Gemini)...")
        genai.configure(api_key=api_key)
        
        # Test with a simple prompt
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test. Please respond with 'API Working'")
        
        print(f"✅ Gemini API Response: {response.text}")
        print("✅ Google Generative AI is working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Google API Error: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition setup"""
    try:
        import speech_recognition as sr
        print("🎤 Testing Speech Recognition setup...")
        
        # Create recognizer instance
        r = sr.Recognizer()
        
        # Check available microphones
        mics = sr.Microphone.list_microphone_names()
        print(f"✅ Available microphones: {len(mics)} found")
        
        if mics:
            print(f"   Default microphone: {mics[0] if mics else 'None'}")
        
        print("✅ Speech Recognition setup is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Speech Recognition Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Services and Speech Recognition...")
    
    google_ok = test_google_services()
    speech_ok = test_speech_recognition()
    
    if google_ok and speech_ok:
        print("\n🎉 All Google services are working correctly!")
    else:
        print("\n⚠️ Some services have issues!")
        
    print(f"\n📊 Test Results:")
    print(f"   Google AI: {'✅' if google_ok else '❌'}")
    print(f"   Speech Recognition: {'✅' if speech_ok else '❌'}")