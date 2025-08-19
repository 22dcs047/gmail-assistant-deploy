@echo off
echo 🚀 FRESH GMAIL ASSISTANT DEPLOYMENT GUIDE
echo.
echo ✅ FRESH PROJECT CREATED!
echo.
echo 📂 Location: C:\Users\joyme\OneDrive\Desktop\gmail-assistant\fresh-deploy
echo.
echo 📋 Files ready for deployment:
echo    ✅ api/app.py (Main Gmail application)
echo    ✅ api/index.py (Vercel entry point)
echo    ✅ requirements.txt (Python dependencies)
echo    ✅ vercel.json (Deployment config)
echo    ✅ README.md (Setup instructions)
echo    ✅ .gitignore (Git ignore file)
echo.
echo 🎯 STEP-BY-STEP DEPLOYMENT:
echo.
echo 📤 STEP 1: Upload to GitHub
echo    1. Go to your new repository: https://github.com/22dcs047/gmail-assistant-deploy
echo    2. Click "uploading an existing file"
echo    3. Drag and drop ALL files from: C:\Users\joyme\OneDrive\Desktop\gmail-assistant\fresh-deploy
echo    4. Commit with message: "Initial Gmail Assistant deployment"
echo.
echo 🔗 STEP 2: Connect to Vercel
echo    1. Go to: https://vercel.com/new
echo    2. Click "Import" next to your gmail-assistant-deploy repository
echo    3. Click "Deploy" (no configuration needed)
echo.
echo ⚙️ STEP 3: Set Environment Variables in Vercel
echo    After deployment, go to: Vercel Dashboard ^> Your Project ^> Settings ^> Environment Variables
echo    Add these 4 variables (I'll provide the actual values):
echo.
echo    GMAIL_REFRESH_TOKEN = [Value provided separately]
echo    GMAIL_CLIENT_ID = [Value provided separately]
echo    GMAIL_CLIENT_SECRET = [Value provided separately]
echo    OPENAI_API_KEY = [Value provided separately]
echo.
echo 🔄 STEP 4: Redeploy
echo    After setting environment variables:
echo    1. Go to Deployments tab in Vercel
echo    2. Click "Redeploy" on latest deployment
echo    3. Wait 2-3 minutes
echo.
echo ✅ STEP 5: Test Your Real Gmail Integration
echo    Visit your deployed site:
echo    1. Homepage: Shows connection status
echo    2. /debug: Verify Gmail API connection
echo    3. /dashboard: See your REAL emails!
echo.
echo 🎉 EXPECTED RESULTS:
echo    ✅ Gmail API: CONNECTED
echo    ✅ Your actual unread emails displayed
echo    ✅ AI-powered email classification
echo    ✅ Real Gmail integration working!
echo.

:: Open the deployment folder
explorer "C:\Users\joyme\OneDrive\Desktop\gmail-assistant\fresh-deploy"

echo 📁 Deployment folder opened - ready to upload to GitHub!
echo.
pause