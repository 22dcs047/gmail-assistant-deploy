# Gmail Assistant - Real API Integration

🚀 **A smart Gmail assistant that uses REAL Gmail API to read your actual emails and create AI-powered responses.**

## Features
- ✅ **Real Gmail Integration** - Connects to your actual Gmail account
- ✅ **AI-Powered Classification** - Intelligent email priority detection
- ✅ **Auto-Reply Generation** - AI creates professional responses
- ✅ **Live Dashboard** - Real-time email management interface
- ✅ **Secure Authentication** - Environment variable based credentials

## Quick Setup for Vercel

### Step 1: Upload Files
Upload all these files to your new GitHub repository:
- `api/app.py` - Main application
- `api/index.py` - Vercel entry point  
- `requirements.txt` - Python dependencies
- `vercel.json` - Deployment configuration

### Step 2: Set Environment Variables in Vercel
Go to Vercel Dashboard → Your Project → Settings → Environment Variables

Add these 4 variables:
```
GMAIL_REFRESH_TOKEN = [Your Gmail Refresh Token]
GMAIL_CLIENT_ID = [Your Gmail Client ID]
GMAIL_CLIENT_SECRET = [Your Gmail Client Secret]
OPENAI_API_KEY = [Your OpenAI API Key]
```

**Note**: The actual values will be provided separately for security.

### Step 3: Deploy & Test
1. Connect your GitHub repository to Vercel
2. Deploy the project
3. Visit `/debug` to verify connections
4. Check `/dashboard` for your real emails!

## Expected Results
- 🟢 **Gmail API: CONNECTED** (reads your real unread emails)
- 🟢 **OpenAI: ENABLED** (AI-powered email classification)
- 🟢 **Dashboard: FUNCTIONAL** (shows your actual Gmail data)

## Endpoints
- `/` - Home page with status
- `/dashboard` - Email management interface  
- `/debug` - System diagnostics
- `/api/emails` - JSON email data
- `/api/debug` - JSON system status

---
**Note**: This connects to your REAL Gmail account and shows actual emails from 22dcs047@charusat.edu.in