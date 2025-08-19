# Gmail Assistant - Real API Integration
# Environment variables required: GMAIL_REFRESH_TOKEN, GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, OPENAI_API_KEY
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import json
import os
import base64
from email.mime.text import MIMEText
import time

# Import Gmail API libraries
try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

# Import OpenAI
try:
    import openai
    from dotenv import load_dotenv
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = Flask(__name__)

# Load environment variables
if OPENAI_AVAILABLE:
    load_dotenv()

class RealGmailAssistant:
    def __init__(self):
        self.user_email = os.getenv('GMAIL_USER_EMAIL', '22dcs047@charusat.edu.in')
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly', 
                      'https://www.googleapis.com/auth/gmail.compose',
                      'https://www.googleapis.com/auth/gmail.modify']
        
        # Initialize OpenAI
        self.openai_available = False
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.openai_available = True
                print(f"🧠 OpenAI initialized successfully")
            except Exception as e:
                print(f"❌ OpenAI initialization failed: {e}")
        
        # Initialize Gmail
        self.gmail_service = None
        self.gmail_connected = False
        if GMAIL_AVAILABLE:
            self._initialize_gmail()
        
        print(f"🚀 Gmail Assistant initialized")
        print(f"📧 Gmail Connected: {self.gmail_connected}")
        print(f"🧠 OpenAI Available: {self.openai_available}")
    
    def _initialize_gmail(self):
        """Initialize Gmail API connection with production-ready error handling"""
        try:
            creds = None
            
            # Debug environment variables
            print("🔍 Checking Gmail Environment Variables:")
            print(f"GMAIL_REFRESH_TOKEN exists: {bool(os.getenv('GMAIL_REFRESH_TOKEN'))}")
            print(f"GMAIL_CLIENT_ID exists: {bool(os.getenv('GMAIL_CLIENT_ID'))}")
            print(f"GMAIL_CLIENT_SECRET exists: {bool(os.getenv('GMAIL_CLIENT_SECRET'))}")
            
            # For Vercel deployment, use environment variables
            if os.getenv('GMAIL_REFRESH_TOKEN') and os.getenv('GMAIL_CLIENT_ID'):
                token_data = {
                    'refresh_token': os.getenv('GMAIL_REFRESH_TOKEN'),
                    'client_id': os.getenv('GMAIL_CLIENT_ID'),
                    'client_secret': os.getenv('GMAIL_CLIENT_SECRET'),
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'scopes': self.scopes
                }
                creds = Credentials.from_authorized_user_info(token_data, self.scopes)
                print("📱 Using environment variable credentials")
            else:
                print("⚠️ Environment variables not found - running in demo mode")
                return False
            
            # Refresh token if expired
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("🔄 Refreshing expired token...")
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                except Exception as e:
                    print(f"❌ Token refresh failed: {e}")
                    return False
            
            # Build Gmail service
            if creds and creds.valid:
                try:
                    self.gmail_service = build('gmail', 'v1', credentials=creds)
                    profile = self.gmail_service.users().getProfile(userId='me').execute()
                    print(f"✅ Gmail API connected for {profile.get('emailAddress')}")
                    self.gmail_connected = True
                    return True
                except Exception as e:
                    print(f"❌ Gmail service build failed: {e}")
                    return False
            else:
                print("❌ No valid Gmail credentials")
                return False
                
        except Exception as e:
            print(f"❌ Gmail initialization error: {e}")
            return False
    
    def get_unread_emails(self):
        """Get real unread emails from Gmail"""
        if not self.gmail_connected:
            return self.get_demo_emails()
        
        try:
            # Get unread emails from last 24 hours
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
            query = f'is:unread after:{yesterday} -from:me'
            
            result = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=20
            ).execute()
            
            messages = result.get('messages', [])
            emails = []
            
            for message in messages:
                try:
                    msg = self.gmail_service.users().messages().get(
                        userId='me', id=message['id'], format='full'
                    ).execute()
                    
                    headers = msg['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    to_field = next((h['value'] for h in headers if h['name'] == 'To'), '')
                    
                    snippet = msg.get('snippet', '')
                    
                    # Parse date
                    try:
                        email_date = datetime.fromtimestamp(int(msg['internalDate']) / 1000)
                        date_str = email_date.strftime('%Y-%m-%d')
                        time_str = email_date.strftime('%H:%M')
                    except:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                        time_str = datetime.now().strftime('%H:%M')
                    
                    # Basic classification
                    priority = 'medium'
                    if any(word in subject.lower() for word in ['urgent', 'critical', 'important']):
                        priority = 'high'
                    elif 'no-reply' in from_email.lower():
                        priority = 'low'
                    
                    emails.append({
                        'id': message['id'],
                        'subject': subject,
                        'from_email': from_email,
                        'to_field': to_field,
                        'snippet': snippet,
                        'date': date_str,
                        'time': time_str,
                        'priority': priority,
                        'email_type': 'real',
                        'ai_classified': False
                    })
                    
                except Exception as e:
                    print(f"❌ Error processing email: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return self.get_demo_emails()
    
    def get_demo_emails(self):
        """Demo emails when Gmail not connected"""
        now = datetime.now()
        return [
            {
                'id': 'demo_1',
                'subject': '⚠️ DEMO MODE - Connect Real Gmail API',
                'from_email': 'system@gmail-assistant.local',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'Set environment variables in Vercel to connect your real Gmail account',
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'priority': 'high',
                'email_type': 'system',
                'ai_classified': False
            }
        ]
    
    def get_email_stats(self):
        """Get email statistics"""
        emails = self.get_unread_emails()
        direct = [e for e in emails if '22dcs047@charusat.edu.in' in e.get('to_field', '')]
        high_priority = [e for e in emails if e['priority'] == 'high']
        
        return {
            'all_emails': emails,
            'direct_emails': direct,
            'cc_emails': [],
            'stats': {
                'total_unread': len(emails),
                'direct_count': len(direct),
                'cc_count': 0,
                'high_priority_count': len(high_priority),
                'ai_classified_count': 0
            },
            'last_updated': datetime.now().isoformat(),
            'gmail_connected': self.gmail_connected,
            'openai_connected': self.openai_available,
            'capabilities': {
                'gmail_api': self.gmail_connected,
                'ai_classification': self.openai_available,
                'real_draft_creation': self.gmail_connected
            }
        }

# Initialize assistant
assistant = RealGmailAssistant()

@app.route('/')
def home():
    status = "Real Gmail" if assistant.gmail_connected else "Demo Mode"
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - {status}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               min-height: 100vh; color: white; text-align: center; padding: 50px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .status {{ background: {'#28a745' if assistant.gmail_connected else '#ffc107'}; 
                   padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .btn {{ background: white; color: #667eea; padding: 15px 30px; border: none; 
                border-radius: 25px; text-decoration: none; display: inline-block; margin: 10px; }}
        .btn:hover {{ transform: translateY(-2px); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Gmail Assistant</h1>
        <div class="status">
            <h2>Status: {status}</h2>
            <p>Gmail Connected: {'✅ YES' if assistant.gmail_connected else '❌ NO'}</p>
            <p>OpenAI Available: {'✅ YES' if assistant.openai_available else '❌ NO'}</p>
        </div>
        <a href="/dashboard" class="btn">📊 Open Dashboard</a>
        <a href="/debug" class="btn">🔧 Debug Info</a>
    </div>
</body>
</html>'''

@app.route('/dashboard')
def dashboard():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: #667eea; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stat-card h3 { font-size: 2rem; margin: 0; color: #333; }
        .emails { background: white; padding: 20px; border-radius: 10px; }
        .email-item { border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; background: #f9f9f9; }
        .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📧 Gmail Dashboard</h1>
        <div id="status">Loading...</div>
    </div>
    
    <div class="stats">
        <div class="stat-card"><h3 id="totalEmails">0</h3><p>Total Emails</p></div>
        <div class="stat-card"><h3 id="directEmails">0</h3><p>Direct Emails</p></div>
        <div class="stat-card"><h3 id="highPriority">0</h3><p>High Priority</p></div>
    </div>
    
    <div class="emails">
        <h2>Recent Emails</h2>
        <button class="btn" onclick="refreshEmails()">🔄 Refresh</button>
        <div id="emailList">Loading emails...</div>
    </div>

    <script>
        async function loadEmails() {
            try {
                const response = await fetch('/api/emails');
                const data = await response.json();
                
                document.getElementById('totalEmails').textContent = data.stats.total_unread;
                document.getElementById('directEmails').textContent = data.stats.direct_count;
                document.getElementById('highPriority').textContent = data.stats.high_priority_count;
                
                const statusEl = document.getElementById('status');
                if (data.gmail_connected) {
                    statusEl.innerHTML = '✅ Gmail Connected - Showing REAL emails';
                    statusEl.style.background = '#28a745';
                } else {
                    statusEl.innerHTML = '⚠️ Demo Mode - Set environment variables for real Gmail';
                    statusEl.style.background = '#ffc107';
                }
                
                const emailList = document.getElementById('emailList');
                if (data.all_emails.length === 0) {
                    emailList.innerHTML = '<p>No emails found</p>';
                    return;
                }
                
                let html = '';
                data.all_emails.forEach(email => {
                    html += `
                        <div class="email-item">
                            <h4>${email.subject}</h4>
                            <p><strong>From:</strong> ${email.from_email}</p>
                            <p><strong>Time:</strong> ${email.date} ${email.time}</p>
                            <p><strong>Priority:</strong> ${email.priority}</p>
                            <p>${email.snippet}</p>
                        </div>
                    `;
                });
                emailList.innerHTML = html;
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('status').innerHTML = '❌ Error loading data';
            }
        }
        
        function refreshEmails() {
            document.getElementById('emailList').innerHTML = 'Refreshing...';
            loadEmails();
        }
        
        loadEmails();
        setInterval(loadEmails, 60000); // Refresh every minute
    </script>
</body>
</html>'''

@app.route('/debug')
def debug():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Debug Information</title>
    <style>
        body { font-family: monospace; padding: 20px; background: #f0f0f0; }
        .debug-section { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .status { padding: 10px; margin: 5px 0; border-radius: 3px; }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow: auto; }
    </style>
</head>
<body>
    <h1>🔧 Debug Information</h1>
    
    <div class="debug-section">
        <h2>System Status</h2>
        <div id="systemStatus">Loading...</div>
    </div>
    
    <div class="debug-section">
        <h2>Environment Variables</h2>
        <div id="envVars">Loading...</div>
    </div>
    
    <div class="debug-section">
        <h2>Raw Debug Data</h2>
        <pre id="debugData">Loading...</pre>
    </div>

    <script>
        async function loadDebug() {
            try {
                const response = await fetch('/api/debug');
                const data = await response.json();
                
                // System Status
                const systemStatus = document.getElementById('systemStatus');
                systemStatus.innerHTML = `
                    <div class="status ${data.gmail_connected ? 'connected' : 'disconnected'}">
                        Gmail API: ${data.gmail_connected ? '✅ CONNECTED' : '❌ NOT CONNECTED'}
                    </div>
                    <div class="status ${data.openai_connected ? 'connected' : 'disconnected'}">
                        OpenAI API: ${data.openai_connected ? '✅ CONNECTED' : '❌ NOT CONNECTED'}
                    </div>
                `;
                
                // Environment Variables
                const envVars = document.getElementById('envVars');
                const env = data.environment;
                envVars.innerHTML = `
                    <p>Gmail Refresh Token: ${env.gmail_refresh_token_exists ? '✅ SET' : '❌ MISSING'}</p>
                    <p>Gmail Client ID: ${env.gmail_client_id_exists ? '✅ SET' : '❌ MISSING'}</p>
                    <p>Gmail Client Secret: ${env.gmail_client_secret_exists ? '✅ SET' : '❌ MISSING'}</p>
                    <p>OpenAI API Key: ${env.openai_key_exists ? '✅ SET' : '❌ MISSING'}</p>
                `;
                
                // Raw Data
                document.getElementById('debugData').textContent = JSON.stringify(data, null, 2);
                
            } catch (error) {
                console.error('Debug error:', error);
            }
        }
        
        loadDebug();
    </script>
</body>
</html>'''

@app.route('/api/emails')
def api_emails():
    return jsonify(assistant.get_email_stats())

@app.route('/api/debug')
def api_debug():
    return jsonify({
        'gmail_connected': assistant.gmail_connected,
        'openai_connected': assistant.openai_available,
        'capabilities': assistant.get_email_stats()['capabilities'],
        'stats': assistant.get_email_stats()['stats'],
        'environment': {
            'gmail_refresh_token_exists': bool(os.getenv('GMAIL_REFRESH_TOKEN')),
            'gmail_client_id_exists': bool(os.getenv('GMAIL_CLIENT_ID')),
            'gmail_client_secret_exists': bool(os.getenv('GMAIL_CLIENT_SECRET')),
            'openai_key_exists': bool(os.getenv('OPENAI_API_KEY')),
            'gmail_libraries_available': GMAIL_AVAILABLE,
            'openai_libraries_available': OPENAI_AVAILABLE
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
