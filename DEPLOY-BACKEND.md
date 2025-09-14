# ClassTrack Backend - Production Ready

## Quick Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project from GitHub repo
4. Select 'detect' folder as root directory
5. Set environment variables:
   - MONGODB_URI=your_atlas_connection_string
   - GOOGLE_API_KEY=your_gemini_key
   - PORT=5001

## Quick Deploy to Render

1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Create Web Service with:
   - Root Directory: detect
   - Build Command: pip install -r requirements.txt
   - Start Command: python main.py

## MongoDB Atlas Setup

1. Go to [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create free cluster
3. Create database user
4. Get connection string
5. Replace in environment variables

## Get API Keys

- Google Gemini: [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- MongoDB Atlas: Get from your cluster connection

Your backend is ready for deployment! 🚀