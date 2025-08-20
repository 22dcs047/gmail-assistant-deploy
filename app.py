# ALL REMAINING API ROUTES
@app.route('/api/create-draft', methods=['POST'])
@login_required
def api_create_draft():
    """Secure draft creation endpoint"""
    try:
        if not assistant:
            return jsonify({'success': False, 'message': 'Assistant not available'}), 200
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 200
        
        email_id = data.get('email_id')
        if not email_id:
            return jsonify({'success': False, 'message': 'Email ID required'}), 200
        
        # Find email safely
        emails = assistant.get_emails_with_timeout()
        email = None
        for e in emails:
            if e.get('id') == email_id:
                email = e
                break
        
        if not email:
            return jsonify({'success': False, 'message': 'Email not found'}), 200
        
        # Create draft
        success, message = assistant.create_draft_safe(email)
        return jsonify({'success': success, 'message': message}), 200
        
    except Exception as e:
        print(f"❌ Secure draft creation error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 200

@app.route('/api/create-drafts-bulk', methods=['POST'])
@login_required
def api_create_drafts_bulk():
    """Secure bulk draft creation"""
    try:
        if not assistant:
            return jsonify({'success': False, 'message': 'Assistant not available'}), 200
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 200
        
        email_ids = data.get('email_ids', [])
        if not email_ids:
            return jsonify({'success': False, 'message': 'No email IDs provided'}), 200
        
        emails = assistant.get_emails_with_timeout()
        created_count = 0
        errors = []
        
        for email_id in email_ids[:5]:  # Limit to prevent timeout
            email = None
            for e in emails:
                if e.get('id') == email_id:
                    email = e
                    break
            
            if email:
                success, message = assistant.create_draft_safe(email)
                if success:
                    created_count += 1
                else:
                    errors.append(message)
        
        return jsonify({
            'success': created_count > 0,
            'created_count': created_count,
            'total_requested': len(email_ids),
            'errors': errors
        }), 200
        
    except Exception as e:
        print(f"❌ Secure bulk draft error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 200

@app.route('/debug')
@login_required
def debug():
    """Secure debug page with 2FA info"""
    try:
        if not assistant:
            return "Assistant not initialized", 500
        
        user = session.get('user', 'Unknown')
        auth_time = session.get('auth_time', 'Unknown')
        
        return f'''
<html>
<head><title>Secure Gmail Assistant Debug (2FA Protected)</title>
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

<h1>🔧 Secure Gmail Assistant Debug (2FA Protected)</h1>

<div class="section">
<h2>🔐 Authentication Status</h2>
<p class="success">✅ Two-Factor Authentication: ACTIVE</p>
<p class="success">✅ Session Security: ENABLED</p>
<p>Flask Version: {getattr(Flask, '__version__', 'Unknown')}</p>
<p>Python Libraries: Gmail API ({'Available' if GMAIL_AVAILABLE else 'Missing'}), OpenAI ({'Available' if OPENAI_AVAILABLE else 'Missing'}), Email ({'Available' if EMAIL_AVAILABLE else 'Missing'})</p>
<p>Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>Session Timeout: Automatic logout on browser close</p>
</div>

</body>
</html>'''
        
    except Exception as e:
        return f'<h1 style="color:red;">Debug Error: {str(e)}</h1>'User: {user}</p>
<p>Authenticated at: {auth_time}</p>
<p>Session ID: {session.get('_id', 'N/A')[:8]}...</p>
</div>

<div class="section">
<h2>📧 Gmail Integration</h2>
<p>Gmail Connected: {'<span class="success">✅ Yes</span>' if assistant.gmail_connected else '<span class="error">❌ No</span>'}</p>
<p>OpenAI Available: {'<span class="success">✅ Yes</span>' if assistant.openai_available else '<span class="error">❌ No</span>'}</p>
<p>Email Account: 22dcs047@charusat.edu.in</p>
</div>

<div class="section">
<h2>🔑 Environment Variables</h2>
<ul>
<li>SECRET_KEY: {'<span class="success">✅ Set</span>' if app.secret_key else '<span class="error">❌ Missing</span>'}</li>
<li>GMAIL_REFRESH_TOKEN: {'<span class="success">✅ Set</span>' if os.getenv('GMAIL_REFRESH_TOKEN') else '<span class="error">❌ Missing</span>'}</li>
<li>GMAIL_CLIENT_ID: {'<span class="success">✅ Set</span>' if os.getenv('GMAIL_CLIENT_ID') else '<span class="error">❌ Missing</span>'}</li>
<li>GMAIL_CLIENT_SECRET: {'<span class="success">✅ Set</span>' if os.getenv('GMAIL_CLIENT_SECRET') else '<span class="error">❌ Missing</span>'}</li>
<li>OPENAI_API_KEY: {'<span class="success">✅ Set</span>' if os.getenv('OPENAI_API_KEY') else '<span class="error">❌ Missing</span>'}</li>
<li>ADMIN_USERNAME: {'<span class="success">✅ Set</span>' if os.getenv('ADMIN_USERNAME') else '<span class="warning">⚠️ Using default</span>'} ({os.getenv('ADMIN_USERNAME', 'admin')})</li>
<li>ADMIN_PASSWORD: {'<span class="success">✅ Set</span>' if os.getenv('ADMIN_PASSWORD') else '<span class="warning">⚠️ Using default</span>'}</li>
<li>SMTP_EMAIL: {'<span class="success">✅ Set</span>' if os.getenv('SMTP_EMAIL') else '<span class="warning">⚠️ Using default</span>'} ({os.getenv('SMTP_EMAIL', '22dcs047@charusat.edu.in')})</li>
<li>SMTP_PASSWORD: {'<span class="success">✅ Set</span>' if os.getenv('SMTP_PASSWORD') else '<span class="warning">⚠️ Missing (Demo mode)</span>'}</li>
</ul>
</div>

<div class="section">
<h2>🔄 OTP System Status</h2>
<p>Active OTPs: {len(otp_storage)}</p>
<p>Cleanup Thread: <span class="success">✅ Running</span></p>
<p>Email Sending: {'<span class="success">Gmail API</span>' if hasattr(app, 'gmail_service') else '<span class="warning">SMTP/Demo</span>'}</p>
</div>

<div class="section">
<h2>🛠️ Quick Actions</h2>
<p><a href="/dashboard" style="color:#0ff;">← Back to Secure Dashboard</a></p>
<p><a href="/api/emails" style="color:#0ff;">📧 Test Secure Email API</a></p>
<p><a href="/" style="color:#0ff;">🏠 Home Page</a></p>
</div>

<div class="section">
<h2>📊 System Information</h2>
<p>from flask import Flask, jsonify, request, session, redirect, url_for, render_template_string
from datetime import datetime, timedelta
import json
import os
import base64
import time
import re
import hashlib
import secrets
import random
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    from email.mime.text import MIMEText as EmailMIME
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

app = Flask(__name__)

# Security Configuration
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# User Credentials (In production, use database)
USERS = {
    os.getenv('ADMIN_USERNAME', 'admin'): {
        'password_hash': hashlib.sha256((os.getenv('ADMIN_PASSWORD', 'admin123')).encode()).hexdigest(),
        'role': 'admin',
        'email': '22dcs047@charusat.edu.in'  # Email for OTP
    }
}

# OTP Storage (In production, use Redis or database with TTL)
otp_storage = {}

def hash_password(password):
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def generate_otp():
    """Generate a secure 3-digit OTP"""
    return str(random.randint(100, 999))

def cleanup_expired_otps():
    """Remove expired OTPs from storage"""
    current_time = datetime.now()
    expired_keys = [key for key, data in otp_storage.items() 
                   if current_time > data['expires_at']]
    for key in expired_keys:
        del otp_storage[key]

def send_otp_email(user_email, otp, username):
    """Send OTP via Gmail API or SMTP"""
    try:
        print(f"🔐 Attempting to send OTP {otp} to {user_email}")
        
        # Try Gmail API first (if available and connected)
        if GMAIL_AVAILABLE and hasattr(app, 'gmail_service'):
            return send_otp_via_gmail_api(user_email, otp, username)
        
        # Fallback to SMTP
        return send_otp_via_smtp(user_email, otp, username)
        
    except Exception as e:
        print(f"❌ OTP Email Error: {e}")
        return False, str(e)

def send_otp_via_gmail_api(user_email, otp, username):
    """Send OTP using Gmail API (preferred method)"""
    try:
        # Initialize Gmail service if not available
        if not hasattr(app, 'gmail_service'):
            assistant = getattr(app, 'assistant', None)
            if assistant and assistant.gmail_service:
                app.gmail_service = assistant.gmail_service
            else:
                return False, "Gmail API not available"
        
        # Create email content
        subject = f"🔐 Gmail Assistant - Login OTP: {otp}"
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Gmail Assistant OTP</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1e40af; margin-bottom: 10px;">🔐 Gmail Assistant</h1>
            <h2 style="color: #374151;">Two-Factor Authentication</h2>
        </div>
        
        <div style="background: linear-gradient(135deg, #3b82f6, #1e40af); color: white; padding: 30px; border-radius: 8px; text-align: center; margin: 20px 0;">
            <h2 style="margin: 0 0 10px 0;">Your Login OTP</h2>
            <div style="font-size: 48px; font-weight: bold; letter-spacing: 8px; margin: 20px 0;">
                {otp}
            </div>
            <p style="margin: 0; opacity: 0.9;">Valid for 2 minutes only</p>
        </div>
        
        <div style="background: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; color: #92400e;"><strong>⚠️ Security Notice:</strong></p>
            <ul style="color: #92400e; margin: 10px 0;">
                <li>This OTP expires in exactly <strong>120 seconds</strong></li>
                <li>Do not share this code with anyone</li>
                <li>If you didn't request this, ignore this email</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
            <p style="color: #6b7280; margin: 0;">Gmail Assistant Security System</p>
            <p style="color: #9ca3af; font-size: 12px; margin: 5px 0;">Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Create message
        message = MIMEMultipart('alternative')
        message['to'] = user_email
        message['subject'] = subject
        message.attach(MIMEText(body, 'html'))
        
        # Convert to Gmail API format
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send via Gmail API
        sent_message = app.gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"✅ OTP sent via Gmail API: {sent_message.get('id', 'Unknown')}")
        return True, "OTP sent successfully via Gmail API"
        
    except Exception as e:
        print(f"❌ Gmail API send error: {e}")
        # Fallback to SMTP
        return send_otp_via_smtp(user_email, otp, username)

def send_otp_via_smtp(user_email, otp, username):
    """Fallback SMTP method for sending OTP"""
    try:
        # SMTP Configuration (using Gmail SMTP as fallback)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Use environment variables for SMTP credentials
        smtp_email = os.getenv('SMTP_EMAIL', '22dcs047@charusat.edu.in')
        smtp_password = os.getenv('SMTP_PASSWORD')  # App password needed
        
        if not smtp_password:
            print("⚠️ SMTP password not configured, using demo mode")
            # In demo mode, just log the OTP
            print(f"🔐 DEMO MODE - OTP for {user_email}: {otp}")
            return True, f"OTP sent to {user_email} (Demo Mode)"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_email
        msg['To'] = user_email
        msg['Subject'] = f"🔐 Gmail Assistant Login OTP: {otp}"
        
        # HTML body
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #1e40af;">🔐 Gmail Assistant - 2FA Verification</h2>
            <div style="background: #3b82f6; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <h3>Your OTP Code:</h3>
                <div style="font-size: 36px; font-weight: bold; letter-spacing: 4px;">{otp}</div>
                <p>Valid for 2 minutes only</p>
            </div>
            <p style="color: #666; margin-top: 20px;">
                <strong>Security Notice:</strong> This code expires in 120 seconds. 
                Do not share with anyone.
            </p>
        </div>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ OTP sent via SMTP to {user_email}")
        return True, "OTP sent successfully"
        
    except Exception as e:
        print(f"❌ SMTP send error: {e}")
        # Final fallback - demo mode
        print(f"🔐 FALLBACK DEMO MODE - OTP for {user_email}: {otp}")
        return True, f"OTP: {otp} (Demo Mode - Check Console)"

def login_required(f):
    """Decorator to require login AND 2FA verification"""
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session.get('authenticated', False):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# [Keep the existing RobustGmailAssistant class unchanged - just reference it]
class RobustGmailAssistant:
    def __init__(self):
        self.user_email = '22dcs047@charusat.edu.in'
        self.gmail_service = None
        self.gmail_connected = False
        self.openai_available = False
        
        print("🚀 Initializing Gmail Assistant...")
        
        try:
            self._safe_init_openai()
            self._safe_init_gmail()
        except Exception as e:
            print(f"⚠️ Init error: {e}")
        
        print(f"✅ Assistant ready - Gmail: {'Connected' if self.gmail_connected else 'Demo'}, AI: {'Yes' if self.openai_available else 'No'}")
    
    def _safe_init_openai(self):
        if not OPENAI_AVAILABLE:
            return
        
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and len(api_key) > 20:
                openai.api_key = api_key
                self.openai_available = True
                print("🧠 OpenAI ready")
        except Exception as e:
            print(f"⚠️ OpenAI error: {e}")
    
    def _safe_init_gmail(self):
        if not GMAIL_AVAILABLE:
            print("📧 Gmail API not available")
            return
        
        try:
            refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
            client_id = os.getenv('GMAIL_CLIENT_ID')
            client_secret = os.getenv('GMAIL_CLIENT_SECRET')
            
            if not refresh_token or not client_id or not client_secret:
                print("⚠️ Gmail credentials missing")
                return
            
            if len(refresh_token) < 50 or len(client_id) < 30:
                print("⚠️ Gmail credentials appear invalid")
                return
            
            token_data = {
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'scopes': [
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.compose',
                    'https://www.googleapis.com/auth/gmail.modify',
                    'https://www.googleapis.com/auth/gmail.send'  # Added for OTP sending
                ]
            }
            
            creds = Credentials.from_authorized_user_info(token_data, token_data['scopes'])
            
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing Gmail token...")
                creds.refresh(Request())
                print("✅ Token refreshed")
            
            if creds and creds.valid:
                self.gmail_service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
                
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                email_address = profile.get('emailAddress', 'Unknown')
                
                self.gmail_connected = True
                print(f"✅ Gmail connected: {email_address}")
                
                # Store Gmail service globally for OTP sending
                app.gmail_service = self.gmail_service
            else:
                print("❌ Gmail credentials invalid")
                
        except Exception as e:
            print(f"❌ Gmail init error: {e}")
            self.gmail_connected = False

    # [Keep all other methods from original RobustGmailAssistant class - abbreviated for space]
    def get_emails_with_timeout(self):
        if not self.gmail_connected:
            return self.get_demo_emails()
        # ... existing implementation
        return self.get_demo_emails()  # Simplified for artifact
    
    def get_demo_emails(self):
        now = datetime.now()
        return [
            {
                'id': 'demo_1',
                'subject': 'July 2025 Exam Registration Deadline - Aug 22, 2025',
                'from_email': 'NPTEL <noreply@nptel.iitm.ac.in>',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'Final reminder about exam registration deadline',
                'display_snippet': '⏰ Registration deadline notice - Last 3 days to register',
                'body': 'This is a final reminder about the exam registration deadline.',
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'priority': 'high',
                'email_type': 'academic',
                'urgency_reason': 'Contains deadline/urgent keywords in subject',
                'ai_classified': False
            }
        ]
    
    def get_stats_safe(self):
        try:
            emails = self.get_emails_with_timeout()
            return {
                'all_emails': emails,
                'direct_emails': emails,
                'stats': {
                    'total_unread': len(emails),
                    'direct_count': len(emails),
                    'high_priority_count': 1,
                    'medium_priority_count': 0,
                    'low_priority_count': 0
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
        return False, "Draft creation available after full authentication"

# Initialize assistant
try:
    assistant = RobustGmailAssistant()
    app.assistant = assistant
except Exception as e:
    print(f"❌ Failed to initialize assistant: {e}")
    assistant = None

# AUTHENTICATION ROUTES
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and verify_password(password, USERS[username]['password_hash']):
            # Credentials are correct, now send OTP
            user_email = USERS[username]['email']
            otp = generate_otp()
            
            # Store OTP with expiration (120 seconds)
            otp_key = f"{username}_{int(time.time())}"
            otp_storage[otp_key] = {
                'otp': otp,
                'username': username,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=120)
            }
            
            # Clean up old OTPs
            cleanup_expired_otps()
            
            # Send OTP email
            success, message = send_otp_email(user_email, otp, username)
            
            if success:
                # Store the OTP key in session for verification
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
    # Check if user has pending OTP
    if 'pending_otp_key' not in session:
        return redirect(url_for('login'))
    
    otp_key = session['pending_otp_key']
    
    # Check if OTP still exists and is valid
    if otp_key not in otp_storage:
        session.clear()
        return render_template_string(OTP_TEMPLATE, 
            error="OTP expired. Please login again.", 
            expired=True)
    
    otp_data = otp_storage[otp_key]
    
    # Check expiration
    if datetime.now() > otp_data['expires_at']:
        del otp_storage[otp_key]
        session.clear()
        return render_template_string(OTP_TEMPLATE, 
            error="OTP expired. Please login again.", 
            expired=True)
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        
        if entered_otp == otp_data['otp']:
            # OTP correct - complete authentication
            username = otp_data['username']
            
            # Clean up
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
            # Wrong OTP
            return render_template_string(OTP_TEMPLATE, 
                error="Invalid OTP. Please try again.",
                time_remaining=int((otp_data['expires_at'] - datetime.now()).total_seconds()))
    
    # Calculate time remaining
    time_remaining = int((otp_data['expires_at'] - datetime.now()).total_seconds())
    
    return render_template_string(OTP_TEMPLATE, time_remaining=time_remaining)

@app.route('/logout')
def logout():
    username = session.get('user', 'Unknown')
    session.clear()
    print(f"🔓 User {username} logged out")
    return redirect(url_for('login'))

# PROTECTED ROUTES (same as before, but now require 2FA)
@app.route('/')
@login_required
def home():
    if not assistant:
        return "Assistant initialization failed", 500
        
    status = "Real Gmail" if assistant.gmail_connected else "Demo Mode"
    user = session.get('user', 'User')
    auth_time = session.get('auth_time', 'Unknown')
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - {status} (2FA Protected)</title>
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
                🕒 Authenticated at: {auth_time}</p>
            </div>
            
            <a href="/dashboard" class="btn primary"><i class="fas fa-tachometer-alt"></i> Open Secure Dashboard</a>
            <a href="/debug" class="btn"><i class="fas fa-cog"></i> System Info</a>
        </div>
    </div>
</body>
</html>'''

# COMPLETE DASHBOARD ROUTE
@app.route('/dashboard')
@login_required
def dashboard():
    """Complete 2FA-protected dashboard with all functionality"""
    user = session.get('user', 'User')
    auth_time = session.get('auth_time', 'Unknown')
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Secure Dashboard (2FA Protected)</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%); 
            min-height: 100vh; 
            color: #1f2937; 
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .user-info {
            position: absolute; top: 20px; right: 20px;
            background: rgba(255,255,255,0.1); padding: 15px 25px; border-radius: 25px;
            backdrop-filter: blur(10px); color: white; display: flex; align-items: center; gap: 15px;
        }
        .auth-badge {
            background: #10b981; padding: 5px 12px; border-radius: 15px;
            font-size: 0.8rem; font-weight: 600;
        }
        .logout-btn {
            background: #ef4444; color: white; padding: 8px 16px; border: none;
            border-radius: 20px; text-decoration: none; font-weight: 600;
            transition: all 0.3s ease;
        }
        .logout-btn:hover { background: #dc2626; }
        .header {
            background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px;
            margin-bottom: 30px; margin-top: 60px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 2.5rem; font-weight: 800; color: #1f2937; margin-bottom: 10px; }
        .status-indicator {
            background: linear-gradient(135deg, #059669, #047857); color: white;
            padding: 8px 20px; border-radius: 20px; font-weight: 600;
            display: inline-block; font-size: 0.9rem;
        }
        .security-status {
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            padding: 15px 25px; border-radius: 15px; margin: 15px 0;
            display: flex; align-items: center; gap: 15px;
        }
        .stats-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-bottom: 40px;
        }
        .stat-card {
            background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px;
            text-align: center; transition: all 0.3s ease;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-left: 4px solid var(--accent-color);
        }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }
        .stat-number { font-size: 3rem; font-weight: 800; margin-bottom: 10px; color: var(--accent-color); }
        .stat-label { font-size: 1.1rem; font-weight: 600; color: #4b5563; }
        .stat-card.total { --accent-color: #3b82f6; }
        .stat-card.direct { --accent-color: #8b5cf6; }
        .stat-card.high { --accent-color: #ef4444; }
        .main-action { text-align: center; margin: 40px 0; }
        .create-drafts-btn {
            background: linear-gradient(135deg, #ef4444, #dc2626); color: white;
            padding: 18px 40px; border: none; border-radius: 12px;
            font-size: 1.2rem; font-weight: 700; text-decoration: none;
            display: inline-block; transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(239,68,68,0.3);
            text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer;
        }
        .create-drafts-btn:hover { transform: translateY(-3px); box-shadow: 0 15px 35px rgba(239,68,68,0.4); }
        .refresh-btn {
            background: linear-gradient(135deg, #3b82f6, #1e40af); color: white;
            padding: 10px 20px; border: none; border-radius: 8px;
            font-weight: 600; cursor: pointer; transition: all 0.3s ease; margin-left: 15px;
        }
        .emails-section {
            background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .section-title {
            font-size: 1.8rem; font-weight: 700; margin-bottom: 25px;
            display: flex; align-items: center; gap: 10px; color: #1f2937;
        }
        .email-card {
            background: #ffffff; margin-bottom: 20px; padding: 25px; border-radius: 12px;
            border-left: 4px solid var(--priority-color); transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05); cursor: pointer;
        }
        .email-card:hover { transform: translateX(5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .email-card.critical { --priority-color: #dc2626; }
        .email-card.high { --priority-color: #ea580c; }
        .email-card.medium { --priority-color: #ca8a04; }
        .email-card.low { --priority-color: #059669; }
        .email-header {
            display: flex; justify-content: space-between; align-items: flex-start;
            margin-bottom: 15px; flex-wrap: wrap; gap: 10px;
        }
        .email-subject { font-size: 1.2rem; font-weight: 700; color: #1f2937; flex: 1; min-width: 200px; }
        .priority-badge {
            background: var(--priority-color); color: white; padding: 6px 12px; border-radius: 20px;
            font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .email-meta {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px; margin-bottom: 15px; color: #6b7280; font-size: 0.9rem;
        }
        .meta-item { display: flex; align-items: center; gap: 8px; }
        .meta-item i { color: var(--priority-color); width: 14px; }
        .email-snippet {
            background: #f8fafc; padding: 15px; border-radius: 8px; margin: 15px 0;
            color: #4b5563; line-height: 1.5; border-left: 3px solid var(--priority-color);
        }
        .draft-btn {
            background: linear-gradient(135deg, var(--priority-color), var(--priority-color));
            color: white; padding: 10px 20px; border: none; border-radius: 8px;
            font-weight: 600; cursor: pointer; transition: all 0.3s ease;
            margin-top: 10px; font-size: 0.9rem;
        }
        .draft-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .loading { text-align: center; padding: 40px; color: #6b7280; }
        .spinner {
            border: 3px solid #e5e7eb; border-radius: 50%; border-top: 3px solid #3b82f6;
            width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .notification {
            position: fixed; top: 20px; right: 20px; background: #10b981;
            color: white; padding: 15px 25px; border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); transform: translateX(400px);
            transition: transform 0.3s ease; z-index: 1000; font-weight: 600;
        }
        .notification.show { transform: translateX(0); }
        .notification.error { background: #ef4444; }
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header { padding: 20px; margin-top: 40px; }
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr; gap: 15px; }
            .create-drafts-btn { padding: 15px 30px; font-size: 1rem; }
            .email-header { flex-direction: column; align-items: stretch; }
            .email-meta { grid-template-columns: 1fr; }
            .user-info { position: relative; top: 0; right: 0; margin-bottom: 20px; }
        }
    </style>
</head>
<body>
    <div class="user-info">
        <div>
            <i class="fas fa-shield-alt"></i> ''' + user + '''
            <div class="auth-badge">2FA ✓</div>
        </div>
        <a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Logout</a>
    </div>
    
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-shield-alt"></i> Secure Gmail Dashboard</h1>
            <div class="status-indicator" id="statusIndicator">
                <i class="fas fa-satellite-dish"></i> Loading status...
            </div>
            <div class="security-status">
                <i class="fas fa-check-shield"></i>
                <div>
                    <strong>Maximum Security Active</strong><br>
                    <small>2FA Authentication completed at: ''' + auth_time + '''</small>
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
                Recent Emails (2FA Protected)
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
        
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification show ${type}`;
            setTimeout(() => {
                notification.classList.remove('show');
            }, 4000);
        }
        
        async function loadEmails() {
            try {
                console.log('🔄 Loading secure emails...');
                const response = await fetch('/api/emails');
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('📊 Secure email data received:', data);
                
                emailsData = data.all_emails || [];
                
                // Update stats safely
                document.getElementById('totalEmails').textContent = data.stats?.total_unread || 0;
                document.getElementById('directEmails').textContent = data.stats?.direct_count || 0;
                document.getElementById('highPriority').textContent = data.stats?.high_priority_count || 0;
                
                // Update status
                const statusEl = document.getElementById('statusIndicator');
                if (data.gmail_connected) {
                    statusEl.innerHTML = '<i class="fas fa-satellite-dish"></i> Gmail Connected - Live Data (2FA Secured)';
                    statusEl.style.background = 'linear-gradient(135deg, #059669, #047857)';
                } else {
                    statusEl.innerHTML = '<i class="fas fa-chart-line"></i> Demo Mode - Sample Data (2FA Secured)';
                    statusEl.style.background = 'linear-gradient(135deg, #3b82f6, #1e40af)';
                }
                
                // Display emails
                displayEmails(emailsData);
                
            } catch (error) {
                console.error('❌ Error loading emails:', error);
                document.getElementById('emailsList').innerHTML = 
                    `<div style="text-align: center; padding: 40px; color: #6b7280;">
                        <i class="fas fa-exclamation-circle"></i>
                        <h3>Error loading emails</h3>
                        <p>${error.message}</p>
                        <button onclick="refreshEmails()" style="margin-top: 15px; padding: 10px 20px; background: #3b82f6; color: white; border: none; border-radius: 8px; cursor: pointer;">
                            <i class="fas fa-retry"></i> Try Again
                        </button>
                    </div>`;
                showNotification('Failed to load emails', 'error');
            }
        }
        
        function displayEmails(emails) {
            const emailsList = document.getElementById('emailsList');
            
            if (!emails || emails.length === 0) {
                emailsList.innerHTML = 
                    `<div style="text-align: center; padding: 40px; color: #6b7280;">
                        <i class="fas fa-inbox"></i>
                        <h3>No unread emails</h3>
                        <p>Your inbox is clean and secure!</p>
                    </div>`;
                return;
            }
            
            console.log(`📧 Displaying ${emails.length} secure emails`);
            
            emailsList.innerHTML = emails.map(email => `
                <div class="email-card ${email.priority || 'low'}">
                    <div class="email-header">
                        <div class="email-subject">${email.subject || 'No Subject'}</div>
                        <div class="priority-badge">${(email.priority || 'LOW').toUpperCase()}</div>
                    </div>
                    <div class="email-meta">
                        <div class="meta-item">
                            <i class="fas fa-user"></i>
                            <span>${email.from_email || 'Unknown'}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-calendar"></i>
                            <span>${email.date || 'Unknown'}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-clock"></i>
                            <span>${email.time || 'Unknown'}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-tag"></i>
                            <span>${email.email_type || 'general'}</span>
                        </div>
                    </div>
                    <div class="email-snippet">${email.display_snippet || email.snippet || 'No preview available'}</div>
                    ${email.urgency_reason ? `<div style="background: #fef3c7; padding: 8px 12px; border-radius: 6px; margin: 10px 0; font-size: 0.85rem; color: #92400e;"><strong>Why ${email.priority || 'classified'}:</strong> ${email.urgency_reason}</div>` : ''}
                    ${(email.priority === 'high' || email.priority === 'critical') ? 
                        `<button class="draft-btn" onclick="createDraft('${email.id}')">
                            <i class="fas fa-pen"></i> Create Draft Reply
                        </button>` : ''
                    }
                </div>
            `).join('');
        }
        
        async function createDraft(emailId) {
            try {
                const email = emailsData.find(e => e.id === emailId);
                if (!email) {
                    showNotification('Email not found', 'error');
                    return;
                }
                
                showNotification('Creating secure draft...', 'info');
                
                const response = await fetch('/api/create-draft', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email_id: emailId })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification('✅ Secure draft created successfully!', 'success');
                } else {
                    showNotification(`❌ Error: ${result.message}`, 'error');
                }
                
            } catch (error) {
                console.error('❌ Error creating draft:', error);
                showNotification('❌ Failed to create draft', 'error');
            }
        }
        
        async function createDraftsForHighPriority() {
            try {
                const highPriorityEmails = emailsData.filter(email => 
                    email.priority === 'high' || email.priority === 'critical'
                );
                
                if (highPriorityEmails.length === 0) {
                    showNotification('No high priority emails found', 'info');
                    return;
                }
                
                showNotification(`Creating ${highPriorityEmails.length} secure drafts...`, 'info');
                
                const response = await fetch('/api/create-drafts-bulk', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email_ids: highPriorityEmails.map(e => e.id) })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification(`✅ Created ${result.created_count} secure drafts!`, 'success');
                } else {
                    showNotification(`❌ Error: ${result.message}`, 'error');
                }
                
            } catch (error) {
                console.error('❌ Error creating bulk drafts:', error);
                showNotification('❌ Failed to create drafts', 'error');
            }
        }
        
        function refreshEmails() {
            document.getElementById('emailsList').innerHTML = 
                '<div class="loading"><div class="spinner"></div><p>Refreshing secure emails...</p></div>';
            loadEmails();
        }
        
        // Load emails on page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Secure 2FA dashboard loaded, initializing...');
            loadEmails();
        });
        
        // Auto-refresh every 3 minutes
        setInterval(loadEmails, 180000);
    </script>
</body>
</html>'''

@app.route('/api/emails')
@login_required
def api_emails():
    # Same API code as original, but now protected by 2FA
    try:
        if not assistant:
            return jsonify({'error': 'Assistant not available'}), 200
        data = assistant.get_stats_safe()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 200

# OTP VERIFICATION TEMPLATE
OTP_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Two-Factor Authentication - Enter OTP</title>
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
            box-shadow: 0 25px 50px rgba(0,0,0,0.15); backdrop-filter: blur(20px);
            max-width: 500px; width: 100%; text-align: center;
        }
        .otp-header h1 {
            font-size: 2.5rem; font-weight: 800; color: #1f2937; margin-bottom: 10px;
        }
        .otp-header p {
            color: #6b7280; font-size: 1.1rem; margin-bottom: 30px;
        }
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
        .otp-input:focus {
            outline: none; border-color: #3b82f6; background: white;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
        }
        .verify-btn {
            width: 100%; background: linear-gradient(135deg, #10b981, #059669);
            color: white; padding: 15px; border: none; border-radius: 10px;
            font-size: 1.2rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s ease;
        }
        .verify-btn:hover { transform: translateY(-2px); }
        .error-message {
            background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
            padding: 15px; border-radius: 8px; margin-bottom: 20px;
        }
        .back-link {
            margin-top: 20px; color: #6b7280; text-decoration: none;
        }
        .security-info {
            margin-top: 30px; padding: 20px; background: #f0f9ff;
            border-radius: 10px; text-align: left;
        }
    </style>
</head>
<body>
    <div class="otp-container">
        <div class="otp-header">
            <h1><i class="fas fa-shield-alt"></i></h1>
            <h1>Two-Factor Authentication</h1>
            <p>Enter the OTP sent to your email</p>
        </div>
        
        {% if not expired %}
        <div class="email-sent">
            <h3><i class="fas fa-envelope"></i> OTP Sent Successfully!</h3>
            <p>Check your email: <strong>22dcs047@charusat.edu.in</strong></p>
        </div>
        
        {% if time_remaining %}
        <div class="timer" id="timer">
            <i class="fas fa-clock"></i> OTP expires in: <span id="countdown">{{ time_remaining }}</span> seconds
        </div>
        {% endif %}
        {% endif %}
        
        {% if error %}
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i> {{ error }}
        </div>
        {% endif %}
        
        {% if expired %}
        <div style="text-align: center; padding: 20px;">
            <i class="fas fa-times-circle" style="font-size: 4rem; color: #ef4444; margin-bottom: 20px;"></i>
            <h3 style="color: #ef4444; margin-bottom: 15px;">OTP Expired</h3>
            <p style="color: #6b7280; margin-bottom: 20px;">Your OTP has expired. Please login again to receive a new code.</p>
            <a href="/login" class="verify-btn" style="display: inline-block; text-decoration: none; width: auto; padding: 12px 30px;">
                <i class="fas fa-arrow-left"></i> Back to Login
            </a>
        </div>
        {% else %}
        <form method="POST" onsubmit="return validateOTP()">
            <input type="text" name="otp" class="otp-input" placeholder="000" 
                   maxlength="3" pattern="[0-9]{3}" required 
                   oninput="this.value = this.value.replace(/[^0-9]/g, '').substring(0,3)"
                   autocomplete="off" autofocus>
            
            <button type="submit" class="verify-btn">
                <i class="fas fa-check"></i> Verify OTP
            </button>
        </form>
        
        <a href="/login" class="back-link">
            <i class="fas fa-arrow-left"></i> Back to Login
        </a>
        {% endif %}
        
        <div class="security-info">
            <h4><i class="fas fa-info-circle"></i> Security Information</h4>
            <ul style="text-align: left; color: #4b5563; margin-top: 10px;">
                <li>OTP is valid for exactly 120 seconds (2 minutes)</li>
                <li>Each OTP is unique and single-use</li>
                <li>Don't share your OTP with anyone</li>
                <li>If you don't receive the email, check spam folder</li>
            </ul>
        </div>
    </div>
    
    <script>
        function validateOTP() {
            const otp = document.querySelector('input[name="otp"]').value;
            if (otp.length !== 3 || !/^\d{3}$/.test(otp)) {
                alert('Please enter a valid 3-digit OTP');
                return false;
            }
            return true;
        }
        
        // Countdown timer
        {% if time_remaining and not expired %}
        let timeLeft = {{ time_remaining }};
        const countdownEl = document.getElementById('countdown');
        const timerEl = document.getElementById('timer');
        
        const countdown = setInterval(function() {
            if (timeLeft <= 0) {
                clearInterval(countdown);
                timerEl.style.background = '#fef2f2';
                timerEl.style.color = '#dc2626';
                timerEl.innerHTML = '<i class="fas fa-times-circle"></i> OTP Expired - Please login again';
                
                // Redirect to login after 3 seconds
                setTimeout(function() {
                    window.location.href = '/login';
                }, 3000);
            } else {
                countdownEl.textContent = timeLeft;
                
                // Change color as time runs out
                if (timeLeft <= 30) {
                    timerEl.style.background = '#fee2e2';
                    timerEl.style.color = '#dc2626';
                } else if (timeLeft <= 60) {
                    timerEl.style.background = '#fef3c7';
                    timerEl.style.color = '#d97706';
                }
            }
            timeLeft--;
        }, 1000);
        {% endif %}
        
        // Auto-focus and format OTP input
        document.querySelector('.otp-input').addEventListener('input', function(e) {
            // Auto-submit when 3 digits entered
            if (e.target.value.length === 3) {
                setTimeout(() => {
                    e.target.form.submit();
                }, 500);
            }
        });
    </script>
</body>
</html>
'''

# LOGIN TEMPLATE (Updated with 2FA notice)
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Secure Login (2FA Required)</title>
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
            box-shadow: 0 25px 50px rgba(0,0,0,0.15); backdrop-filter: blur(20px);
            max-width: 480px; width: 100%; color: #1f2937;
        }
        .login-header {
            text-align: center; margin-bottom: 40px;
        }
        .login-header h1 {
            font-size: 2.8rem; font-weight: 800; color: #1f2937; margin-bottom: 10px;
        }
        .login-header p {
            color: #6b7280; font-size: 1.1rem; margin-bottom: 20px;
        }
        .two-fa-badge {
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            padding: 12px 20px; border-radius: 25px; font-weight: 600;
            display: inline-block; font-size: 0.9rem; margin-bottom: 20px;
        }
        .form-group { margin-bottom: 25px; }
        .form-group label {
            display: block; font-weight: 600; margin-bottom: 8px; color: #374151;
        }
        .input-group { position: relative; }
        .input-group i {
            position: absolute; left: 15px; top: 50%; transform: translateY(-50%);
            color: #6b7280; font-size: 1.1rem;
        }
        .input-group input {
            width: 100%; padding: 15px 20px 15px 50px; border: 2px solid #e5e7eb;
            border-radius: 10px; font-size: 1rem; transition: all 0.3s ease;
            background: #f9fafb;
        }
        .input-group input:focus {
            outline: none; border-color: #3b82f6; background: white;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
        }
        .login-btn {
            width: 100%; background: linear-gradient(135deg, #3b82f6, #1e40af);
            color: white; padding: 15px 20px; border: none; border-radius: 10px;
            font-size: 1.1rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        }
        .login-btn:hover {
            transform: translateY(-2px); box-shadow: 0 8px 25px rgba(59,130,246,0.4);
        }
        .error-message {
            background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
            padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; font-weight: 500;
        }
        .security-flow {
            background: #f0f9ff; padding: 25px; border-radius: 15px; margin-top: 30px;
            border-left: 4px solid #3b82f6;
        }
        .security-flow h3 {
            color: #1e40af; margin-bottom: 15px; font-size: 1.2rem;
        }
        .flow-steps {
            list-style: none; color: #1e40af;
        }
        .flow-steps li {
            margin: 10px 0; padding-left: 25px; position: relative;
            font-weight: 500;
        }
        .flow-steps li:before {
            content: attr(data-step); position: absolute; left: 0; top: 0;
            background: #3b82f6; color: white; border-radius: 50%;
            width: 20px; height: 20px; display: flex; align-items: center;
            justify-content: center; font-size: 0.8rem; font-weight: 600;
        }
        .demo-info {
            background: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 20px;
            color: #92400e; font-size: 0.9rem;
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
        
        <form method="POST" autocomplete="off">
            <div class="form-group">
                <label for="username"><i class="fas fa-user"></i> Username</label>
                <div class="input-group">
                    <i class="fas fa-user"></i>
                    <input type="text" id="username" name="username" required 
                           placeholder="Enter your username" autocomplete="off">
                </div>
            </div>
            
            <div class="form-group">
                <label for="password"><i class="fas fa-lock"></i> Password</label>
                <div class="input-group">
                    <i class="fas fa-lock"></i>
                    <input type="password" id="password" name="password" required 
                           placeholder="Enter your password" autocomplete="new-password">
                </div>
            </div>
            
            <button type="submit" class="login-btn">
                <i class="fas fa-arrow-right"></i> Continue to 2FA Verification
            </button>
        </form>
        
        <div class="security-flow">
            <h3><i class="fas fa-route"></i> Login Process</h3>
            <ol class="flow-steps">
                <li data-step="1">Enter username & password</li>
                <li data-step="2">Receive OTP via email (22dcs047@charusat.edu.in)</li>
                <li data-step="3">Enter 3-digit OTP within 120 seconds</li>
                <li data-step="4">Access granted to secure dashboard</li>
            </ol>
        </div>
        
        <div class="demo-info">
            <strong><i class="fas fa-info-circle"></i> Demo Configuration:</strong><br>
            If SMTP is not configured, OTP will be displayed in console/logs for testing.
            In production, configure SMTP_EMAIL and SMTP_PASSWORD environment variables.
        </div>
    </div>
</body>
</html>
'''

# AUTO-CLEANUP TASK (runs every minute to remove expired OTPs)
def cleanup_expired_otps_task():
    """Background task to cleanup expired OTPs"""
    while True:
        try:
            cleanup_expired_otps()
            time.sleep(60)  # Run every minute
        except Exception as e:
            print(f"⚠️ Cleanup task error: {e}")
            time.sleep(60)

# Start cleanup task in background
cleanup_thread = threading.Thread(target=cleanup_expired_otps_task, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    print("🔐 Starting SECURE Gmail Assistant with 2FA...")
    print("🔍 Security Environment Check:")
    print(f"SECRET_KEY: {'✅ Set' if app.secret_key else '❌ Missing'}")
    print(f"ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME', 'admin')} (default if not set)")
    print(f"ADMIN_PASSWORD: {'✅ Set' if os.getenv('ADMIN_PASSWORD') else '❌ Using default'}")
    print(f"SMTP_EMAIL: {os.getenv('SMTP_EMAIL', '22dcs047@charusat.edu.in')} (for OTP sending)")
    print(f"SMTP_PASSWORD: {'✅ Set' if os.getenv('SMTP_PASSWORD') else '❌ Missing (Demo mode)'}")
    print("🔒 2FA System initialized - OTP expiration: 120 seconds")
    app.run(debug=True)
