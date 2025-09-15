# 🚀 Deploy ClassTrack Backend to Render

## Step 1: Prepare MongoDB Atlas (Cloud Database)

1. **Go to [MongoDB Atlas](https://www.mongodb.com/atlas)**
2. **Create free account** and cluster
3. **Create database user** with username/password
4. **Whitelist IP addresses** (use 0.0.0.0/0 for development)
5. **Get connection string**: 
   ```
   mongodb+srv://username:password@cluster.mongodb.net/college_app
   ```

## Step 2: Get Google Gemini API Key

1. **Go to [Google AI Studio](https://makersuite.google.com/app/apikey)**
2. **Create new API key**
3. **Copy the key** for environment variables

## Step 3: Deploy to Render

### Option A: Web Interface (Recommended)

1. **Go to [Render.com](https://render.com)**
2. **Sign up with GitHub**
3. **Create New Web Service**
4. **Connect GitHub repository**: `Srujana-Hackathon`
5. **Configure service**:
   - **Name**: `classtrack-backend`
   - **Root Directory**: `detect`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

6. **Set Environment Variables**:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/college_app
   GOOGLE_API_KEY=your_gemini_api_key_here
   PORT=10000
   ```

7. **Click Deploy**

### Option B: Using render.yaml (Alternative)

If you have render.yaml in your repo, Render will auto-configure based on the file.

## Step 4: Verify Deployment

1. **Wait for deployment** (usually 5-10 minutes)
2. **Check logs** in Render dashboard
3. **Test health endpoint**: `https://your-app.onrender.com/health`
4. **Copy the deployment URL** for frontend configuration

## Step 5: Update Frontend

1. **Update environment variables** in your Vercel project:
   ```
   REACT_APP_API_URL=https://your-app.onrender.com
   ```
2. **Redeploy frontend**

## Troubleshooting

### Common Issues:
- **Build fails**: Check that all dependencies are in requirements.txt
- **Health check fails**: Verify MongoDB connection string
- **App crashes**: Check environment variables are set correctly

### Logs:
- Check Render dashboard logs for detailed error messages
- MongoDB Atlas logs for database connection issues

## Environment Variables Summary

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/college_app
GOOGLE_API_KEY=your_gemini_api_key_here
PORT=10000
```

## Success Indicators

✅ Build completes without errors  
✅ Health endpoint returns 200 status  
✅ MongoDB connection successful  
✅ API endpoints respond correctly  

Your backend will be available at: `https://classtrack-backend.onrender.com`