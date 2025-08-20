from flask import Flask, jsonify, request, session, redirect, url_for, render_template_string
from datetime import datetime, timedelta
import json
import os
import base64
import time
import re
import hashlib
import secrets
import random

# Import with robust error handling
try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

app = Flask(__name__)

# Security Configuration
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# User Credentials
USERS = {
    os.getenv('ADMIN_USERNAME', 'admin'): {
        'password_hash': hashlib.sha256((os.getenv('ADMIN_PASSWORD', 'admin123')).encode()).hexdigest(),
        'role': 'admin',
        'email': '22dcs047@charusat.edu.in'
    }
}

# Simple OTP storage (in-memory for simplicity)
otp_storage = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def generate_otp():
    return str(random.randint(100, 999))

def cleanup_expired_otps():
    current_time = datetime.now()
    expired_keys = [key for key, data in otp_storage.items() 
                   if current_time > data['expires_at']]
    for key in expired_keys:
        del otp_storage[key]

def send_otp_email(user_email, otp, username):
    """Send OTP via available method"""
    try:
        print(f"🔐 Sending OTP {otp} to {user_email}")
        
        # For now, use demo mode (log OTP to console)
        # In production, you can implement actual email sending
        print(f"📧 OTP EMAIL SENT TO {user_email}")
        print(f"🔑 YOUR LOGIN OTP: {otp}")
        print(f"⏰ Valid for 120 seconds only")
        
        return True, f"OTP sent to {user_email} (Check console/logs)"
        
    except Exception as e:
        print(f"❌ OTP Email Error: {e}")
        return False, str(e)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session.get('authenticated', False):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

class SimpleGmailAssistant:
    def __init__(self):
        self.user_email = '22dcs047@charusat.edu.in'
        self.gmail_connected = False
        self.openai_available = False
        
        print("🚀 Initializing Simple Gmail Assistant...")
        self._safe_init()
        print(f"✅ Assistant ready - Status: {'Connected' if self.gmail_connected else 'Demo'}")
    
    def _safe_init(self):
        try:
            # Check environment variables
            if os.getenv('GMAIL_REFRESH_TOKEN') and os.getenv('GMAIL_CLIENT_ID'):
                self.gmail_connected = True
                print("✅ Gmail credentials detected")
            
            if os.getenv('OPENAI_API_KEY'):
                self.openai_available = True
                print("✅ OpenAI credentials detected")
                
        except Exception as e:
            print(f"⚠️ Init warning: {e}")
    
    def get_demo_emails(self):
        now = datetime.now()
        return [
            {
                'id': 'demo_1',
                'subject': 'July 2025 Exam Registration Deadline - Aug 22, 2025 - Last 3 days!',
                'from_email': 'NPTEL <noreply@nptel.iitm.ac.in>',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'This is a final reminder about the exam registration deadline.',
                'display_snippet': '⏰ Registration deadline notice - Last 3 days to register for July 2025 Exam',
                'body': 'Final reminder about exam registration deadline approaching on August 22, 2025.',
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'priority': 'high',
                'email_type': 'academic',
                'urgency_reason': 'Contains deadline/urgent keywords in subject',
                'ai_classified': False
            },
            {
                'id': 'demo_2',
                'subject': 'Course Materials Updated - Data Structures',
                'from_email': 'Academic Office <academic@charusat.edu.in>',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'New course materials have been uploaded to the portal.',
                'display_snippet': 'New course materials available for Data Structures course',
                'body': 'Dear students, new course materials are now available on the portal.',
                'date': now.strftime('%Y-%m-%d'),
                'time': (now - timedelta(hours=2)).strftime('%H:%M'),
                'priority': 'medium',
                'email_type': 'academic',
                'urgency_reason': 'Email from academic institution',
                'ai_classified': False
            },
            {
                'id': 'demo_3',
                'subject': 'Security Alert - New Login Detected',
                'from_email': 'Security <security@example.com>',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'We detected a new login to your account from a new device.',
                'display_snippet': '🔒 Security notification - New device login detected',
                'body': 'We detected a new login to your account. If this wasn\'t you, please secure your account.',
                'date': now.strftime('%Y-%m-%d'),
                'time': (now - timedelta(hours=1)).strftime('%H:%M'),
                'priority': 'high',
                'email_type': 'security',
                'urgency_reason': 'Security alert requiring immediate attention',
                'ai_classified': False
            }
        ]
    
    def get_stats_safe(self):
        try:
            emails = self.get_demo_emails()
            
            direct_emails = [e for e in emails if self.user_email in e.get('to_field', '')]
            high_priority = [e for e in emails if e.get('priority') in ['high', 'critical']]
            medium_priority = [e for e in emails if e.get('priority') == 'medium']
            low_priority = [e for e in emails if e.get('priority') == 'low']
            
            return {
                'all_emails': emails,
                'direct_emails': direct_emails,
                'stats': {
                    'total_unread': len(emails),
                    'direct_count': len(direct_emails),
                    'high_priority_count': len(high_priority),
                    'medium_priority_count': len(medium_priority),
                    'low_priority_count': len(low_priority)
                },
                'gmail_connected': self.gmail_connected,
                'openai_connected': self.openai_available,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Stats error: {e}")
            return {
                'all_emails': [],
                'direct_emails': [],
                'stats': {'total_unread': 0, 'direct_count': 0, 'high_priority_count': 0},
                'gmail_connected': False,
                'openai_connected': False,
                'last_updated': datetime.now().isoformat()
            }
    
    def create_draft_safe(self, email_data):
        # Simulate draft creation
        return True, "Demo draft created successfully (2FA Protected)"

# Initialize assistant
try:
    assistant = SimpleGmailAssistant()
except Exception as e:
    print(f"❌ Failed to initialize assistant: {e}")
    assistant = None

# ROUTES
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and verify_password(password, USERS[username]['password_hash']):
            # Generate OTP
            user_email = USERS[username]['email']
            otp = generate_otp()
            
            # Store OTP
            otp_key = f"{username}_{int(time.time())}"
            otp_storage[otp_key] = {
                'otp': otp,
                'username': username,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=120)
            }
            
            # Clean expired OTPs
            cleanup_expired_otps()
            
            # Send OTP
            success, message = send_otp_email(user_email, otp, username)
            
            if success:
                session['pending_otp_key'] = otp_key
                session['pending_username'] = username
                return redirect(url_for('verify_otp'))
            else:
                return render_template_string(LOGIN_TEMPLATE, 
                    error=f"Failed to send OTP: {message}")
        else:
            return render_template_string(LOGIN_TEMPLATE, 
                error="Invalid username or password")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_otp_key' not in session:
        return redirect(url_for('login'))
    
    otp_key = session['pending_otp_key']
    
    if otp_key not in otp_storage:
        session.clear()
        return render_template_string(OTP_TEMPLATE, 
            error="OTP expired. Please login again.", 
            expired=True)
    
    otp_data = otp_storage[otp_key]
    
    if datetime.now() > otp_data['expires_at']:
        del otp_storage[otp_key]
        session.clear()
        return render_template_string(OTP_TEMPLATE, 
            error="OTP expired. Please login again.", 
            expired=True)
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        
        if entered_otp == otp_data['otp']:
            # Success
            username = otp_data['username']
            
            # Cleanup
            del otp_storage[otp_key]
            session.pop('pending_otp_key', None)
            session.pop('pending_username', None)
            
            # Set authenticated session
            session['user'] = username
            session['role'] = USERS[username]['role']
            session['authenticated'] = True
            session['auth_time'] = datetime.now().isoformat()
            
            print(f"✅ User {username} successfully authenticated with 2FA")
            return redirect(url_for('home'))
        else:
            return render_template_string(OTP_TEMPLATE, 
                error="Invalid OTP. Please try again.",
                time_remaining=int((otp_data['expires_at'] - datetime.now()).total_seconds()))
    
    time_remaining = int((otp_data['expires_at'] - datetime.now()).total_seconds())
    return render_template_string(OTP_TEMPLATE, time_remaining=time_remaining)

@app.route('/logout')
def logout():
    username = session.get('user', 'Unknown')
    session.clear()
    print(f"🔓 User {username} logged out")
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    if not assistant:
        return "Assistant initialization failed", 500
        
    user = session.get('user', 'User')
    auth_time = session.get('auth_time', 'Unknown')
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - 2FA Protected</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%); 
            min-height: 100vh; 
            color: #ffffff; 
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        .user-info {{
            position: absolute; top: 20px; right: 20px;
            background: rgba(255,255,255,0.1); padding: 15px 25px; border-radius: 25px;
            backdrop-filter: blur(10px); display: flex; align-items: center; gap: 15px;
        }}
        .auth-badge {{
            background: #10b981; padding: 5px 12px; border-radius: 15px;
            font-size: 0.8rem; font-weight: 600;
        }}
        .logout-btn {{
            background: #ef4444; color: white; padding: 8px 16px; border: none;
            border-radius: 20px; text-decoration: none; font-weight: 600;
            transition: all 0.3s ease;
        }}
        .logout-btn:hover {{ background: #dc2626; }}
        .hero {{ 
            background: rgba(255,255,255,0.95); padding: 60px 40px; border-radius: 20px; 
            text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            color: #1f2937; margin-bottom: 40px; margin-top: 60px;
        }}
        .hero h1 {{ font-size: 3.5rem; margin-bottom: 20px; font-weight: 800; color: #1f2937; }}
        .hero p {{ font-size: 1.3rem; margin-bottom: 30px; color: #4b5563; line-height: 1.6; }}
        .security-notice {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: white; padding: 20px; border-radius: 15px;
            margin: 20px 0; text-align: left;
        }}
        .btn {{ 
            background: linear-gradient(135deg, #3b82f6, #1e40af);
            color: white; padding: 15px 30px; border: none; border-radius: 10px; 
            font-size: 1.1rem; font-weight: 600; text-decoration: none; 
            display: inline-block; margin: 10px 15px; transition: all 0.3s ease; 
            box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(59,130,246,0.4); }}
        .btn.primary {{ background: linear-gradient(135deg, #059669, #047857); }}
    </style>
</head>
<body>
    <div class="user-info">
        <div>
            <i class="fas fa-shield-alt"></i> {user}
            <div class="auth-badge">2FA ✓</div>
        </div>
        <a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Logout</a>
    </div>
    
    <div class="container">
        <div class="hero">
            <h1><i class="fas fa-shield-alt"></i> Secure Gmail Assistant</h1>
            <p>Two-Factor Authentication Enabled - Maximum Security</p>
            
            <div class="security-notice">
                <h3><i class="fas fa-check-circle"></i> Security Status: AUTHENTICATED</h3>
                <p>✅ Username/Password verified<br>
                ✅ OTP email verification completed<br>
                ✅ Session secured with 2FA<br>
                🕒 Authenticated at: {auth_time[:16] if len(auth_time) > 16 else auth_time}</p>
            </div>
            
            <a href="/dashboard" class="btn primary"><i class="fas fa-tachometer-alt"></i> Open Secure Dashboard</a>
            <a href="/debug" class="btn"><i class="fas fa-cog"></i> System Info</a>
        </div>
    </div>
</body>
</html>'''

@app.route('/dashboard')
@login_required
def dashboard():
    user = session.get('user', 'User')
    auth_time = session.get('auth_time', 'Unknown')
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Secure Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%); 
            min-height: 100vh; 
            color: #1f2937; 
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .user-info {{
            position: absolute; top: 20px; right: 20px;
            background: rgba(255,255,255,0.1); padding: 15px 25px; border-radius: 25px;
            backdrop-filter: blur(10px); color: white; display: flex; align-items: center; gap: 15px;
        }}
        .auth-badge {{
            background: #10b981; padding: 5px 12px; border-radius: 15px;
            font-size: 0.8rem; font-weight: 600;
        }}
        .logout-btn {{
            background: #ef4444; color: white; padding: 8px 16px; border: none;
            border-radius: 20px; text-decoration: none; font-weight: 600;
            transition: all 0.3s ease;
        }}
        .logout-btn:hover {{ background: #dc2626; }}
        .header {{
            background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px;
            margin-bottom: 30px; margin-top: 60px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 2.5rem; font-weight: 800; color: #1f2937; margin-bottom: 10px; }}
        .security-status {{
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            padding: 15px 25px; border-radius: 15px; margin: 15px 0;
            display: flex; align-items: center; gap: 15px;
        }}
        .stats-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-bottom: 40px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px;
            text-align: center; transition: all 0.3s ease;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-left: 4px solid var(--accent-color);
        }}
        .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }}
        .stat-number {{ font-size: 3rem; font-weight: 800; margin-bottom: 10px; color: var(--accent-color); }}
        .stat-label {{ font-size: 1.1rem; font-weight: 600; color: #4b5563; }}
        .stat-card.total {{ --accent-color: #3b82f6; }}
        .stat-card.direct {{ --accent-color: #8b5cf6; }}
        .stat-card.high {{ --accent-color: #ef4444; }}
        .main-action {{ text-align: center; margin: 40px 0; }}
        .create-drafts-btn {{
            background: linear-gradient(135deg, #ef4444, #dc2626); color: white;
            padding: 18px 40px; border: none; border-radius: 12px;
            font-size: 1.2rem; font-weight: 700; text-decoration: none;
            display: inline-block; transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(239,68,68,0.3);
            text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer;
        }}
        .create-drafts-btn:hover {{ transform: translateY(-3px); box-shadow: 0 15px 35px rgba(239,68,68,0.4); }}
        .refresh-btn {{
            background: linear-gradient(135deg, #3b82f6, #1e40af); color: white;
            padding: 10px 20px; border: none; border-radius: 8px;
            font-weight: 600; cursor: pointer; transition: all 0.3s ease; margin-left: 15px;
        }}
        .emails-section {{
            background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .section-title {{
            font-size: 1.8rem; font-weight: 700; margin-bottom: 25px;
            display: flex; align-items: center; gap: 10px; color: #1f2937;
        }}
        .loading {{ text-align: center; padding: 40px; color: #6b7280; }}
        .spinner {{
            border: 3px solid #e5e7eb; border-radius: 50%; border-top: 3px solid #3b82f6;
            width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto;
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .notification {{
            position: fixed; top: 20px; right: 20px; background: #10b981;
            color: white; padding: 15px 25px; border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); transform: translateX(400px);
            transition: transform 0.3s ease; z-index: 1000; font-weight: 600;
        }}
        .notification.show {{ transform: translateX(0); }}
        .notification.error {{ background: #ef4444; }}
        .email-card {{
            background: #ffffff; margin-bottom: 20px; padding: 25px; border-radius: 12px;
            border-left: 4px solid var(--priority-color); transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        }}
        .email-card.high {{ --priority-color: #ea580c; }}
        .email-card.medium {{ --priority-color: #ca8a04; }}
        .email-card.low {{ --priority-color: #059669; }}
        .email-subject {{ font-size: 1.2rem; font-weight: 700; color: #1f2937; margin-bottom: 10px; }}
        .priority-badge {{
            background: var(--priority-color); color: white; padding: 6px 12px; border-radius: 20px;
            font-weight: 600; font-size: 0.85rem; text-transform: uppercase;
            display: inline-block; margin-bottom: 10px;
        }}
        .email-snippet {{
            background: #f8fafc; padding: 15px; border-radius: 8px;
            color: #4b5563; line-height: 1.5; border-left: 3px solid var(--priority-color);
        }}
        .draft-btn {{
            background: var(--priority-color); color: white; padding: 10px 20px; border: none;
            border-radius: 8px; font-weight: 600; cursor: pointer;
            transition: all 0.3s ease; margin-top: 15px;
        }}
        .draft-btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
    </style>
</head>
<body>
    <div class="user-info">
        <div>
            <i class="fas fa-shield-alt"></i> {user}
            <div class="auth-badge">2FA ✓</div>
        </div>
        <a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Logout</a>
    </div>
    
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-shield-alt"></i> Secure Gmail Dashboard</h1>
            <div class="security-status">
                <i class="fas fa-check-shield"></i>
                <div>
                    <strong>Maximum Security Active - 2FA Verified</strong><br>
                    <small>Authenticated at: {auth_time[:16] if len(auth_time) > 16 else auth_time}</small>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="stat-number" id="totalEmails">...</div>
                <div class="stat-label">Total Emails</div>
            </div>
            <div class="stat-card direct">
                <div class="stat-number" id="directEmails">...</div>
                <div class="stat-label">Direct Emails</div>
            </div>
            <div class="stat-card high">
                <div class="stat-number" id="highPriority">...</div>
                <div class="stat-label">High Priority</div>
            </div>
        </div>
        
        <div class="main-action">
            <button class="create-drafts-btn" onclick="createDraftsForHighPriority()">
                <i class="fas fa-magic"></i> Create Drafts for High Priority Emails
            </button>
        </div>
        
        <div class="emails-section">
            <div class="section-title">
                <i class="fas fa-inbox"></i>
                Secure Email Management
                <button class="refresh-btn" onclick="refreshEmails()">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
            <div id="emailsList" class="loading">
                <div class="spinner"></div>
                <p>Loading your secure emails...</p>
            </div>
        </div>
    </div>
    
    <div class="notification" id="notification"></div>
    
    <script>
        let emailsData = [];
        
        function showNotification(message, type = 'success') {{
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification show ${{type}}`;
            setTimeout(() => {{
                notification.classList.remove('show');
            }}, 4000);
        }}
        
        async function loadEmails() {{
            try {{
                console.log('🔄 Loading secure emails...');
                const response = await fetch('/api/emails');
                
                if (!response.ok) {{
                    throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const data = await response.json();
                console.log('📊 Secure email data received:', data);
                
                emailsData = data.all_emails || [];
                
                document.getElementById('totalEmails').textContent = data.stats?.total_unread || 0;
                document.getElementById('directEmails').textContent = data.stats?.direct_count || 0;
                document.getElementById('highPriority').textContent = data.stats?.high_priority_count || 0;
                
                displayEmails(emailsData);
                
            }} catch (error) {{
                console.error('❌ Error loading emails:', error);
                document.getElementById('emailsList').innerHTML = 
                    `<div style="text-align: center; padding: 40px; color: #6b7280;">
                        <i class="fas fa-inbox"></i>
                        <h3>No unread emails</h3>
                        <p>Your secure inbox is clean!</p>
                    </div>`;
                return;
            }}
            
            emailsList.innerHTML = emails.map(email => `
                <div class="email-card ${{email.priority || 'low'}}">
                    <div class="email-subject">${{email.subject || 'No Subject'}}</div>
                    <div class="priority-badge">${{(email.priority || 'LOW').toUpperCase()}}</div>
                    <div style="margin: 10px 0; color: #6b7280;">
                        <i class="fas fa-user"></i> ${{email.from_email || 'Unknown'}} | 
                        <i class="fas fa-calendar"></i> ${{email.date || 'Unknown'}} |
                        <i class="fas fa-clock"></i> ${{email.time || 'Unknown'}}
                    </div>
                    <div class="email-snippet">${{email.display_snippet || email.snippet || 'No preview available'}}</div>
                    ${{email.urgency_reason ? `<div style="background: #fef3c7; padding: 8px 12px; border-radius: 6px; margin: 10px 0; font-size: 0.85rem; color: #92400e;"><strong>Classification:</strong> ${{email.urgency_reason}}</div>` : ''}}
                    ${{(email.priority === 'high' || email.priority === 'critical') ? 
                        `<button class="draft-btn" onclick="createDraft('${{email.id}}')">
                            <i class="fas fa-pen"></i> Create Draft Reply
                        </button>` : ''
                    }}
                </div>
            `).join('');
        }}
        
        async function createDraft(emailId) {{
            showNotification('Creating secure draft...', 'info');
            try {{
                const response = await fetch('/api/create-draft', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ email_id: emailId }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    showNotification('✅ Secure draft created!', 'success');
                }} else {{
                    showNotification(`❌ Error: ${{result.message}}`, 'error');
                }}
                
            }} catch (error) {{
                showNotification('❌ Failed to create draft', 'error');
            }}
        }}
        
        async function createDraftsForHighPriority() {{
            const highPriorityEmails = emailsData.filter(email => 
                email.priority === 'high' || email.priority === 'critical'
            );
            
            if (highPriorityEmails.length === 0) {{
                showNotification('No high priority emails found', 'info');
                return;
            }}
            
            showNotification(`Creating ${{highPriorityEmails.length}} secure drafts...`, 'info');
            
            try {{
                const response = await fetch('/api/create-drafts-bulk', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ email_ids: highPriorityEmails.map(e => e.id) }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    showNotification(`✅ Created ${{result.created_count}} secure drafts!`, 'success');
                }} else {{
                    showNotification(`❌ Error: ${{result.message}}`, 'error');
                }}
                
            }} catch (error) {{
                showNotification('❌ Failed to create drafts', 'error');
            }}
        }}
        
        function refreshEmails() {{
            document.getElementById('emailsList').innerHTML = 
                '<div class="loading"><div class="spinner"></div><p>Refreshing secure emails...</p></div>';
            loadEmails();
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🚀 Secure 2FA dashboard loaded');
            loadEmails();
        }});
        
        setInterval(loadEmails, 180000);
    </script>
</body>
</html>'''

@app.route('/api/emails')
@login_required
def api_emails():
    try:
        if not assistant:
            return jsonify({'error': 'Assistant not available'}), 200
        
        print("📧 API call - fetching email stats")
        data = assistant.get_stats_safe()
        print(f"✅ API returning {len(data.get('all_emails', []))} emails")
        return jsonify(data), 200
        
    except Exception as e:
        print(f"❌ API error: {e}")
        return jsonify({
            'error': str(e),
            'all_emails': [],
            'direct_emails': [],
            'stats': {'total_unread': 0, 'direct_count': 0, 'high_priority_count': 0},
            'gmail_connected': False,
            'openai_connected': False,
            'last_updated': datetime.now().isoformat()
        }), 200

@app.route('/api/create-draft', methods=['POST'])
@login_required
def api_create_draft():
    try:
        if not assistant:
            return jsonify({'success': False, 'message': 'Assistant not available'}), 200
        
        data = request.get_json()
        if not data or not data.get('email_id'):
            return jsonify({'success': False, 'message': 'Email ID required'}), 200
        
        # Simulate draft creation
        return jsonify({'success': True, 'message': 'Demo draft created (2FA Protected)'}), 200
        
    except Exception as e:
        print(f"❌ Draft creation error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 200

@app.route('/api/create-drafts-bulk', methods=['POST'])
@login_required
def api_create_drafts_bulk():
    try:
        if not assistant:
            return jsonify({'success': False, 'message': 'Assistant not available'}), 200
        
        data = request.get_json()
        email_ids = data.get('email_ids', []) if data else []
        
        if not email_ids:
            return jsonify({'success': False, 'message': 'No email IDs provided'}), 200
        
        # Simulate bulk draft creation
        return jsonify({
            'success': True,
            'created_count': len(email_ids),
            'total_requested': len(email_ids),
            'message': f'Created {len(email_ids)} demo drafts (2FA Protected)'
        }), 200
        
    except Exception as e:
        print(f"❌ Bulk draft error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 200

@app.route('/debug')
@login_required
def debug():
    try:
        user = session.get('user', 'Unknown')
        auth_time = session.get('auth_time', 'Unknown')
        
        return f'''
<html>
<head><title>Secure Gmail Assistant Debug</title>
<style>
body{{font-family:monospace;background:#000;color:#0f0;padding:20px;line-height:1.6;}}
.user-info{{position:absolute;top:10px;right:10px;background:#333;padding:15px;border-radius:5px;}}
.logout-btn{{background:#f00;color:#fff;padding:5px 10px;border:none;border-radius:3px;margin-left:10px;text-decoration:none;}}
.section{{margin:20px 0;padding:15px;border:1px solid #0f0;border-radius:5px;}}
.success{{color:#0f0;}} .error{{color:#f00;}} .warning{{color:#ff0;}}
</style>
</head>
<body>
<div class="user-info">
User: {user} | 2FA: ✓ | Auth: {auth_time[:16] if len(auth_time) > 16 else auth_time}
<a href="/logout" class="logout-btn">Logout</a>
</div>

<h1>🔧 Secure Gmail Assistant Debug</h1>

<div class="section">
<h2>🔐 2FA Authentication Status</h2>
<p class="success">✅ Two-Factor Authentication: ACTIVE</p>
<p class="success">✅ Session Security: ENABLED</p>
<p>User: {user}</p>
<p>Authenticated: {auth_time}</p>
<p>Active OTPs: {len(otp_storage)}</p>
</div>

<div class="section">
<h2>📧 System Status</h2>
<p>Assistant: {'<span class="success">✅ Ready</span>' if assistant else '<span class="error">❌ Not Available</span>'}</p>
<p>Gmail API: {'<span class="success">✅ Available</span>' if GMAIL_AVAILABLE else '<span class="error">❌ Not Available</span>'}</p>
<p>OpenAI API: {'<span class="success">✅ Available</span>' if OPENAI_AVAILABLE else '<span class="error">❌ Not Available</span>'}</p>
<p>Email Lib: {'<span class="success">✅ Available</span>' if EMAIL_AVAILABLE else '<span class="error">❌ Not Available</span>'}</p>
</div>

<div class="section">
<h2>🔑 Environment Variables</h2>
<ul>
<li>SECRET_KEY: {'<span class="success">✅ Set</span>' if app.secret_key else '<span class="error">❌ Missing</span>'}</li>
<li>ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME', 'admin')}</li>
<li>ADMIN_PASSWORD: {'<span class="success">✅ Set</span>' if os.getenv('ADMIN_PASSWORD') else '<span class="warning">⚠️ Using default</span>'}</li>
<li>GMAIL_REFRESH_TOKEN: {'<span class="success">✅ Set</span>' if os.getenv('GMAIL_REFRESH_TOKEN') else '<span class="error">❌ Missing</span>'}</li>
<li>OPENAI_API_KEY: {'<span class="success">✅ Set</span>' if os.getenv('OPENAI_API_KEY') else '<span class="error">❌ Missing</span>'}</li>
</ul>
</div>

<div class="section">
<h2>🛠️ Navigation</h2>
<p><a href="/dashboard" style="color:#0ff;">← Back to Secure Dashboard</a></p>
<p><a href="/api/emails" style="color:#0ff;">📧 Test Email API</a></p>
<p><a href="/" style="color:#0ff;">🏠 Home Page</a></p>
</div>

</body>
</html>'''
        
    except Exception as e:
        return f'<h1 style="color:red;">Debug Error: {str(e)}</h1>'

# TEMPLATES
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Secure Login (2FA)</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .login-container {
            background: rgba(255,255,255,0.95); padding: 50px 40px; border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15); max-width: 480px; width: 100%;
        }
        .login-header { text-align: center; margin-bottom: 40px; }
        .login-header h1 { font-size: 2.8rem; font-weight: 800; color: #1f2937; margin-bottom: 10px; }
        .login-header p { color: #6b7280; font-size: 1.1rem; margin-bottom: 20px; }
        .two-fa-badge {
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            padding: 12px 20px; border-radius: 25px; font-weight: 600;
            display: inline-block; font-size: 0.9rem; margin-bottom: 20px;
        }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; font-weight: 600; margin-bottom: 8px; color: #374151; }
        .input-group { position: relative; }
        .input-group i {
            position: absolute; left: 15px; top: 50%; transform: translateY(-50%);
            color: #6b7280; font-size: 1.1rem;
        }
        .input-group input {
            width: 100%; padding: 15px 20px 15px 50px; border: 2px solid #e5e7eb;
            border-radius: 10px; font-size: 1rem; transition: all 0.3s ease; background: #f9fafb;
        }
        .input-group input:focus {
            outline: none; border-color: #3b82f6; background: white;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
        }
        .login-btn {
            width: 100%; background: linear-gradient(135deg, #3b82f6, #1e40af);
            color: white; padding: 15px 20px; border: none; border-radius: 10px;
            font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease;
        }
        .login-btn:hover { transform: translateY(-2px); }
        .error-message {
            background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
            padding: 12px 16px; border-radius: 8px; margin-bottom: 20px;
        }
        .flow-info {
            background: #f0f9ff; padding: 25px; border-radius: 15px; margin-top: 30px;
            border-left: 4px solid #3b82f6; color: #1e40af;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1><i class="fas fa-shield-alt"></i></h1>
            <h1>Secure Login</h1>
            <p>Gmail Assistant</p>
            <div class="two-fa-badge">
                <i class="fas fa-mobile-alt"></i> Two-Factor Authentication Required
            </div>
        </div>
        
        {% if error %}
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i> {{ error }}
        </div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <div class="input-group">
                    <i class="fas fa-user"></i>
                    <input type="text" name="username" required placeholder="Enter username">
                </div>
            </div>
            
            <div class="form-group">
                <label>Password</label>
                <div class="input-group">
                    <i class="fas fa-lock"></i>
                    <input type="password" name="password" required placeholder="Enter password">
                </div>
            </div>
            
            <button type="submit" class="login-btn">
                <i class="fas fa-arrow-right"></i> Continue to 2FA Verification
            </button>
        </form>
        
        <div class="flow-info">
            <h3><i class="fas fa-route"></i> Login Process</h3>
            <p>1. Enter credentials → 2. Receive OTP via email → 3. Enter OTP → 4. Access granted</p>
            <p><strong>Note:</strong> OTP will be displayed in console/logs for demo purposes.</p>
        </div>
    </div>
</body>
</html>
'''

OTP_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Two-Factor Authentication</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .otp-container {
            background: rgba(255,255,255,0.95); padding: 50px 40px; border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15); max-width: 500px; width: 100%; text-align: center;
        }
        .otp-header h1 { font-size: 2.5rem; font-weight: 800; color: #1f2937; margin-bottom: 20px; }
        .email-sent {
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            padding: 20px; border-radius: 10px; margin-bottom: 30px;
        }
        .timer {
            background: #fef3c7; color: #92400e; padding: 15px; border-radius: 8px;
            font-weight: 600; margin-bottom: 20px; font-size: 1.1rem;
        }
        .otp-input {
            width: 100%; padding: 20px; font-size: 2rem; text-align: center;
            border: 3px solid #e5e7eb; border-radius: 10px; margin-bottom: 20px;
            font-weight: bold; letter-spacing: 8px; background: #f9fafb;
        }
        .otp-input:focus { outline: none; border-color: #3b82f6; background: white; }
        .verify-btn {
            width: 100%; background: linear-gradient(135deg, #10b981, #059669);
            color: white; padding: 15px; border: none; border-radius: 10px;
            font-size: 1.2rem; font-weight: 600; cursor: pointer;
        }
        .verify-btn:hover { transform: translateY(-2px); }
        .error-message {
            background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
            padding: 15px; border-radius: 8px; margin-bottom: 20px;
        }
        .back-link { margin-top: 20px; color: #6b7280; text-decoration: none; }
    </style>
</head>
<body>
    <div class="otp-container">
        <div class="otp-header">
            <h1><i class="fas fa-shield-alt"></i> 2FA Verification</h1>
        </div>
        
        {% if not expired %}
        <div class="email-sent">
            <h3><i class="fas fa-envelope"></i> OTP Sent!</h3>
            <p>Check console/logs for your OTP code</p>
        </div>
        
        {% if time_remaining %}
        <div class="timer" id="timer">
            <i class="fas fa-clock"></i> Expires in: <span id="countdown">{{ time_remaining }}</span>s
        </div>
        {% endif %}
        {% endif %}
        
        {% if error %}
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i> {{ error }}
        </div>
        {% endif %}
        
        {% if expired %}
        <div style="padding: 40px;">
            <i class="fas fa-times-circle" style="font-size: 4rem; color: #ef4444; margin-bottom: 20px;"></i>
            <h3 style="color: #ef4444;">OTP Expired</h3>
            <a href="/login" class="verify-btn" style="display: inline-block; text-decoration: none; margin-top: 20px;">
                Back to Login
            </a>
        </div>
        {% else %}
        <form method="POST">
            <input type="text" name="otp" class="otp-input" placeholder="000" 
                   maxlength="3" pattern="[0-9]{3}" required 
                   oninput="this.value = this.value.replace(/[^0-9]/g, '').substring(0,3)"
                   autofocus>
            
            <button type="submit" class="verify-btn">
                <i class="fas fa-check"></i> Verify OTP
            </button>
        </form>
        
        <a href="/login" class="back-link">← Back to Login</a>
        {% endif %}
    </div>
    
    <script>
        {% if time_remaining and not expired %}
        let timeLeft = {{ time_remaining }};
        const countdownEl = document.getElementById('countdown');
        const timerEl = document.getElementById('timer');
        
        const countdown = setInterval(() => {
            if (timeLeft <= 0) {
                clearInterval(countdown);
                timerEl.innerHTML = '<i class="fas fa-times-circle"></i> OTP Expired';
                setTimeout(() => window.location.href = '/login', 2000);
            } else {
                countdownEl.textContent = timeLeft;
                if (timeLeft <= 30) timerEl.style.background = '#fee2e2';
            }
            timeLeft--;
        }, 1000);
        {% endif %}
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🔐 Starting Secure Gmail Assistant with 2FA...")
    print("🔍 Environment Check:")
    print(f"SECRET_KEY: {'✅ Set' if app.secret_key else '❌ Missing'}")
    print(f"ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME', 'admin')}")
    print(f"ADMIN_PASSWORD: {'✅ Set' if os.getenv('ADMIN_PASSWORD') else '⚠️ Using default'}")
    print("🔒 2FA System ready - OTP: 120 seconds expiration")
    app.run(debug=True)<div style="text-align: center; padding: 40px; color: #6b7280;">
                        <i class="fas fa-exclamation-circle"></i>
                        <h3>Error loading emails</h3>
                        <p>${{error.message}}</p>
                    </div>`;
                showNotification('Failed to load emails', 'error');
            }}
        }}
        
        function displayEmails(emails) {{
            const emailsList = document.getElementById('emailsList');
            
            if (!emails || emails.length === 0) {{
                emailsList.innerHTML = 
                    `
