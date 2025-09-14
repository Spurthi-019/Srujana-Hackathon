# Update Frontend Environment Variables

# After your backend is deployed to Render, follow these steps:

## Step 1: Update .env.production file
# Replace YOUR_BACKEND_URL with your actual Render URL

REACT_APP_API_URL=https://YOUR_BACKEND_URL.onrender.com
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_demo_key_placeholder
REACT_APP_GEMINI_API_KEY=your_gemini_api_key_here
GENERATE_SOURCEMAP=false
CI=false

## Step 2: Update Vercel Environment Variables
# Go to: https://vercel.com/dashboard
# Select your project: classtrack
# Go to Settings > Environment Variables
# Add/Update these variables:

# REACT_APP_API_URL = https://your-backend-url.onrender.com
# REACT_APP_CLERK_PUBLISHABLE_KEY = pk_test_demo_key_placeholder  
# REACT_APP_GEMINI_API_KEY = your_gemini_api_key_here

## Step 3: Redeploy Frontend
# Run these commands after updating environment variables:

# git add .
# git commit -m "feat: Update API URL to point to deployed backend"
# npx vercel --prod

## Step 4: Test Integration
# Your frontend will be at: https://classtrack-du7y6ruym-kumar-ankit369s-projects.vercel.app
# Backend health check: https://your-backend-url.onrender.com/health

# Full app should now work with:
# ✅ Frontend on Vercel
# ✅ Backend on Render  
# ✅ Database on MongoDB Atlas
# ✅ Complete integration