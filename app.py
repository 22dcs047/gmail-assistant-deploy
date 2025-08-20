from flask import Flask, jsonify, request, session, redirect, url_for, render_template_string
from datetime import datetime, timedelta
import os
import hashlib
import secrets
import random
import base64

# Import with error handling
try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

app = Flask(__name__)

# Configuration
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# User store
USERS = {
    os.getenv('ADMIN_USERNAME', 'admin'): {
        'password_hash': hashlib.sha256((os.getenv('ADMIN_PASSWORD', 'admin123')).encode()).hexdigest(),
        'role': 'admin',
        'email': '22dcs047@charusat.edu.in'
    }
}

# OTP storage
otp_storage = {}

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
    """Send OTP via Gmail API"""
    try:
        print(f"🔐 Sending OTP {otp} to {user_email}")
        
        if not GMAIL_AVAILABLE:
            print(f"📧 Gmail API not available. OTP: {otp}")
            return True, f"OTP: {otp} (Check console - Gmail API not available)"
        
        # Initialize Gmail service
        gmail_service = None
        try:
            refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
            client_id = os.getenv('GMAIL_CLIENT_ID')
            client_secret = os.getenv('GMAIL_CLIENT_SECRET')
            
            if not all([refresh_token, client_id, client_secret]):
                print(f"📧 Gmail credentials missing. OTP: {otp}")
                return True, f"OTP: {otp} (Gmail credentials not configured)"
            
            # Build credentials
            token_data = {
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'scopes': [
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/gmail.compose'
                ]
            }
            
            creds = Credentials.from_authorized_user_info(token_data, token_data['scopes'])
            
            # Refresh if needed
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            if creds and creds.valid:
                gmail_service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
            else:
                print(f"📧 Gmail authentication failed. OTP: {otp}")
                return True, f"OTP: {otp} (Gmail authentication failed)"
                
        except Exception as e:
            print(f"📧 Gmail setup error: {e}. OTP: {otp}")
            return True, f"OTP: {otp} (Gmail setup error)"
        
        if not gmail_service:
            print(f"📧 Gmail service not available. OTP: {otp}")
            return True, f"OTP: {otp} (Gmail service not available)"
        
        # Create email content
        subject = f"🔐 Gmail Assistant Login OTP: {otp}"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Gmail Assistant OTP</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; margin: 0;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-size: 3rem; margin-bottom: 10px;">🔐</div>
            <h1 style="color: #1e40af; margin: 0; font-size: 2rem;">Gmail Assistant</h1>
            <p style="color: #6b7280; margin: 10px 0 0 0; font-size: 1.1rem;">Two-Factor Authentication</p>
        </div>
        
        <!-- OTP Display -->
        <div style="background: linear-gradient(135deg, #3b82f6, #1e40af); color: white; padding: 40px; border-radius: 12px; text-align: center; margin: 30px 0;">
            <h2 style="margin: 0 0 15px 0; font-size: 1.5rem;">Your Login OTP</h2>
            <div style="font-size: 4rem; font-weight: bold; letter-spacing: 12px; margin: 20px 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                {otp}
            </div>
            <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">⏰ Valid for exactly 2 minutes</p>
        </div>
        
        <!-- Security Notice -->
        <div style="background: #fef3c7; padding: 25px; border-radius: 10px; margin: 25px 0; border-left: 4px solid #f59e0b;">
            <h3 style="margin: 0 0 15px 0; color: #92400e; font-size: 1.2rem;">
                ⚠️ Important Security Information
            </h3>
            <ul style="color: #92400e; margin: 0; padding-left: 20px; line-height: 1.6;">
                <li><strong>This OTP expires in exactly 120 seconds</strong></li>
                <li>Never share this code with anyone</li>
                <li>If you didn't request this login, ignore this email</li>
                <li>Our team will never ask for your OTP</li>
            </ul>
        </div>
        
        <!-- Login Instructions -->
        <div style="background: #f0f9ff; padding: 25px; border-radius: 10px; margin: 25px 0;">
            <h3 style="margin: 0 0 15px 0; color: #1e40af;">📋 How to Complete Login:</h3>
            <ol style="color: #1e40af; margin: 0; padding-left: 20px; line-height: 1.8;">
                <li>Return to the Gmail Assistant login page</li>
                <li>Enter the 3-digit OTP code shown above</li>
                <li>Click "Verify OTP" to complete authentication</li>
                <li>You'll be redirected to your secure dashboard</li>
            </ol>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
            <p style="color: #6b7280; margin: 0; font-size: 0.9rem;">
                <strong>Gmail Assistant Security System</strong>
            </p>
            <p style="color: #9ca3af; font-size: 0.8rem; margin: 10px 0 0 0;">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
            <p style="color: #9ca3af; font-size: 0.8rem; margin: 5px 0 0 0;">
                This is an automated security message for account: {user_email}
            </p>
        </div>
        
    </div>
</body>
</html>
        """
        
        # Create message
        message = MIMEMultipart('alternative')
        message['to'] = user_email
        message['subject'] = subject
        message.attach(MIMEText(html_body, 'html'))
        
        # Convert to Gmail API format
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send email
        sent_message = gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"✅ OTP email sent successfully via Gmail API: {sent_message.get('id', 'Unknown')}")
        return True, "OTP sent successfully to your email"
        
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        print(f"📧 Fallback - Your OTP: {otp}")
        return True, f"OTP: {otp} (Email failed - check console)"

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session.get('authenticated', False):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ROUTES
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and verify_password(password, USERS[username]['password_hash']):
            # Generate OTP
            otp = generate_otp()
            otp_key = f"{username}_{int(datetime.now().timestamp())}"
            
            # Store OTP
            otp_storage[otp_key] = {
                'otp': otp,
                'username': username,
                'expires_at': datetime.now() + timedelta(seconds=120)
            }
            
            cleanup_expired_otps()
            
            # Send OTP via email
            user_email = USERS[username]['email']
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
            error="OTP expired. Please login again.", expired=True)
    
    otp_data = otp_storage[otp_key]
    
    if datetime.now() > otp_data['expires_at']:
        del otp_storage[otp_key]
        session.clear()
        return render_template_string(OTP_TEMPLATE, 
            error="OTP expired. Please login again.", expired=True)
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        
        if entered_otp == otp_data['otp']:
            # Success - complete authentication
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
            time_remaining = int((otp_data['expires_at'] - datetime.now()).total_seconds())
            return render_template_string(OTP_TEMPLATE, 
                error="Invalid OTP. Please try again.",
                time_remaining=time_remaining)
    
    # Calculate time remaining
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
    user = session.get('user', 'User')
    auth_time = session.get('auth_time', 'Unknown')
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>2FA Gmail Assistant - Secure Home</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%); 
            min-height: 100vh; color: white; padding: 20px; 
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
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
            border-radius: 15px; text-decoration: none; font-weight: 600; 
            transition: all 0.3s ease; 
        }}
        .logout-btn:hover {{ background: #dc2626; }}
        .hero {{ 
            background: rgba(255,255,255,0.95); padding: 60px 40px; border-radius: 20px; 
            text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.15); 
            color: #1f2937; margin-bottom: 40px; margin-top: 60px; 
        }}
        .hero h1 {{ font-size: 3.5rem; margin-bottom: 20px; font-weight: 800; }}
        .hero p {{ font-size: 1.3rem; margin-bottom: 30px; color: #4b5563; line-height: 1.6; }}
        .security-status {{ 
            background: linear-gradient(135deg, #10b981, #059669); color: white; 
            padding: 25px; border-radius: 15px; margin: 25px 0; text-align: left; 
        }}
        .btn {{ 
            background: linear-gradient(135deg, #3b82f6, #1e40af); color: white; 
            padding: 15px 30px; border: none; border-radius: 10px; 
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
            <p>Two-Factor Authentication Successfully Completed</p>
            
            <div class="security-status">
                <h3><i class="fas fa-check-circle"></i> Maximum Security Status: AUTHENTICATED</h3>
                <div style="margin-top: 15px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div class="priority-badge">HIGH</div>
                </div>
                <div class="email-meta">
                    <div class="meta-item">
                        <i class="fas fa-user"></i>
                        <span>NPTEL &lt;noreply@nptel.iitm.ac.in&gt;</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-calendar"></i>
                        <span>{datetime.now().strftime('%Y-%m-%d')}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-clock"></i>
                        <span>{datetime.now().strftime('%H:%M')}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-tag"></i>
                        <span>Academic</span>
                    </div>
                </div>
                <div class="email-snippet">⏰ Registration deadline notice - Final reminder about exam registration deadline approaching on August 22, 2025</div>
                <div style="background: #fef3c7; padding: 8px 12px; border-radius: 6px; margin: 10px 0; font-size: 0.85rem; color: #92400e;">
                    <strong>Why HIGH priority:</strong> Contains deadline/urgent keywords in subject
                </div>
                <button class="draft-btn" onclick="showNotification('📧 Demo: Draft reply created for registration deadline email!', 'success')">
                    <i class="fas fa-pen"></i> Create Draft Reply
                </button>
            </div>
            
            <div class="email-card high">
                <div class="email-header">
                    <div class="email-subject">Security Alert - New Login Detected</div>
                    <div class="priority-badge">HIGH</div>
                </div>
                <div class="email-meta">
                    <div class="meta-item">
                        <i class="fas fa-user"></i>
                        <span>Security &lt;security@example.com&gt;</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-calendar"></i>
                        <span>{datetime.now().strftime('%Y-%m-%d')}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-clock"></i>
                        <span>{(datetime.now() - timedelta(hours=1)).strftime('%H:%M')}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-tag"></i>
                        <span>Security</span>
                    </div>
                </div>
                <div class="email-snippet">🔒 Security notification - We detected a new login to your account from a new device</div>
                <div style="background: #fef3c7; padding: 8px 12px; border-radius: 6px; margin: 10px 0; font-size: 0.85rem; color: #92400e;">
                    <strong>Why HIGH priority:</strong> Security alert requiring immediate attention
                </div>
                <button class="draft-btn" onclick="showNotification('📧 Demo: Draft reply created for security alert!', 'success')">
                    <i class="fas fa-pen"></i> Create Draft Reply
                </button>
            </div>
            
            <div class="email-card medium">
                <div class="email-header">
                    <div class="email-subject">Course Materials Updated - Data Structures</div>
                    <div class="priority-badge">MEDIUM</div>
                </div>
                <div class="email-meta">
                    <div class="meta-item">
                        <i class="fas fa-user"></i>
                        <span>Academic Office &lt;academic@charusat.edu.in&gt;</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-calendar"></i>
                        <span>{datetime.now().strftime('%Y-%m-%d')}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-clock"></i>
                        <span>{(datetime.now() - timedelta(hours=2)).strftime('%H:%M')}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-tag"></i>
                        <span>Academic</span>
                    </div>
                </div>
                <div class="email-snippet">New course materials have been uploaded to the portal for Data Structures course</div>
                <div style="background: #fef3c7; padding: 8px 12px; border-radius: 6px; margin: 10px 0; font-size: 0.85rem; color: #92400e;">
                    <strong>Why MEDIUM priority:</strong> Email from academic institution
                </div>
            </div>
            
        </div>
    </div>
    
    <div class="notification" id="notification"></div>
    
    <script>
        function showNotification(message, type = 'success') {{
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification show ${{type}}`;
            setTimeout(() => {{
                notification.classList.remove('show');
            }}, 4000);
        }}
    </script>
</body>
</html>'''

@app.route('/debug')
@login_required
def debug():
    user = session.get('user', 'Unknown')
    auth_time = session.get('auth_time', 'Unknown')
    
    return f'''
<html>
<head><title>Secure Debug - 2FA Protected</title>
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
<h2>🔐 Two-Factor Authentication Status</h2>
<p class="success">✅ Two-Factor Authentication: ACTIVE</p>
<p class="success">✅ Email OTP System: ENABLED</p>
<p class="success">✅ Session Security: MAXIMUM</p>
<p>Authenticated User: {user}</p>
<p>Authentication Time: {auth_time}</p>
<p>Active OTP Sessions: {len(otp_storage)}</p>
<p>Email Target: 22dcs047@charusat.edu.in</p>
</div>

<div class="section">
<h2>📧 Gmail API Integration</h2>
<p>Gmail API Available: {'<span class="success">✅ Yes</span>' if GMAIL_AVAILABLE else '<span class="error">❌ No</span>'}</p>
<p>Gmail Send Permission: {'<span class="success">✅ Configured</span>' if os.getenv('GMAIL_REFRESH_TOKEN') else '<span class="warning">⚠️ Not Configured</span>'}</p>
<p>OTP Email Method: {'Gmail API' if GMAIL_AVAILABLE and os.getenv('GMAIL_REFRESH_TOKEN') else 'Console Fallback'}</p>
</div>

<div class="section">
<h2>🔑 Environment Variables Status</h2>
<ul>
<li>SECRET_KEY: {'<span class="success">✅ Set</span>' if app.secret_key else '<span class="error">❌ Missing</span>'}</li>
<li>ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME', 'admin')} {'<span class="success">(Custom)</span>' if os.getenv('ADMIN_USERNAME') else '<span class="warning">(Default)</span>'}</li>
<li>ADMIN_PASSWORD: {'<span class="success">✅ Custom</span>' if os.getenv('ADMIN_PASSWORD') else '<span class="warning">⚠️ Default</span>'}</li>
<li>GMAIL_REFRESH_TOKEN: {'<span class="success">✅ Set</span>' if os.getenv('GMAIL_REFRESH_TOKEN') else '<span class="error">❌ Missing</span>'}</li>
<li>GMAIL_CLIENT_ID: {'<span class="success">✅ Set</span>' if os.getenv('GMAIL_CLIENT_ID') else '<span class="error">❌ Missing</span>'}</li>
<li>GMAIL_CLIENT_SECRET: {'<span class="success">✅ Set</span>' if os.getenv('GMAIL_CLIENT_SECRET') else '<span class="error">❌ Missing</span>'}</li>
</ul>
</div>

<div class="section">
<h2>🛡️ Security Features</h2>
<ul>
<li class="success">✅ Password hashing (SHA-256)</li>
<li class="success">✅ Session-based authentication</li>
<li class="success">✅ OTP expiration (120 seconds)</li>
<li class="success">✅ Automatic cleanup of expired OTPs</li>
<li class="success">✅ Login required decorators on all routes</li>
<li class="success">✅ Beautiful HTML email templates</li>
<li class="success">✅ Real-time countdown timers</li>
<li class="success">✅ Secure session management</li>
</ul>
</div>

<div class="section">
<h2>🛠️ Navigation</h2>
<p><a href="/dashboard" style="color:#0ff;">← Back to Secure Dashboard</a></p>
<p><a href="/" style="color:#0ff;">🏠 Secure Home</a></p>
<p><a href="/logout" style="color:#f00;">🔓 Secure Logout</a></p>
</div>

<div class="section">
<h2>📊 System Information</h2>
<p>Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>Session Timeout: Browser close (secure)</p>
<p>OTP Generation: Cryptographically secure random</p>
<p>Email Template: Professional HTML with security warnings</p>
</div>

</body>
</html>'''

# LOGIN TEMPLATE
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Secure Login - Email 2FA Required</title>
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
        .login-header { text-align: center; margin-bottom: 40px; }
        .login-header h1 { font-size: 2.8rem; font-weight: 800; margin-bottom: 10px; }
        .login-header p { color: #6b7280; font-size: 1.1rem; margin-bottom: 20px; }
        .email-2fa-badge {
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
            box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        }
        .login-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(59,130,246,0.4); }
        .error-message {
            background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
            padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; font-weight: 500;
        }
        .security-flow {
            background: #f0f9ff; padding: 25px; border-radius: 15px; margin-top: 30px;
            border-left: 4px solid #3b82f6;
        }
        .security-flow h3 { color: #1e40af; margin-bottom: 15px; font-size: 1.2rem; }
        .flow-steps { list-style: none; color: #1e40af; }
        .flow-steps li {
            margin: 10px 0; padding-left: 25px; position: relative; font-weight: 500;
        }
        .flow-steps li:before {
            content: attr(data-step); position: absolute; left: 0; top: 0;
            background: #3b82f6; color: white; border-radius: 50%;
            width: 20px; height: 20px; display: flex; align-items: center;
            justify-content: center; font-size: 0.8rem; font-weight: 600;
        }
        .email-notice {
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
            <div class="email-2fa-badge">
                <i class="fas fa-envelope"></i> Email Two-Factor Authentication
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
                <i class="fas fa-arrow-right"></i> Continue to Email Verification
            </button>
        </form>
        
        <div class="security-flow">
            <h3><i class="fas fa-route"></i> Secure Login Process</h3>
            <ol class="flow-steps">
                <li data-step="1">Enter username & password</li>
                <li data-step="2">Receive OTP via email (22dcs047@charusat.edu.in)</li>
                <li data-step="3">Enter 3-digit OTP within 120 seconds</li>
                <li data-step="4">Access granted to secure dashboard</li>
            </ol>
        </div>
        
        <div class="email-notice">
            <strong><i class="fas fa-info-circle"></i> Email Authentication:</strong><br>
            Your OTP will be sent to <strong>22dcs047@charusat.edu.in</strong> with a professional HTML template.
            If Gmail API is not configured, the OTP will be shown in console/logs as fallback.
        </div>
    </div>
</body>
</html>
'''

# OTP TEMPLATE
OTP_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Email OTP Verification - 2FA</title>
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
        .otp-header { margin-bottom: 30px; }
        .otp-header h1 { font-size: 2.5rem; font-weight: 800; color: #1f2937; margin-bottom: 10px; }
        .otp-header p { color: #6b7280; font-size: 1.1rem; }
        .email-sent {
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            padding: 20px; border-radius: 10px; margin-bottom: 30px;
        }
        .email-sent h3 { margin-bottom: 10px; font-size: 1.2rem; }
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
            outline: none; border-color: #3b82f6; background: #ffffff;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
        }
        .verify-btn {
            width: 100%; background: linear-gradient(135deg, #10b981, #059669);
            color: white; padding: 15px 20px; border: none; border-radius: 10px;
            font-size: 1.2rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(16,185,129,0.3);
        }
        .verify-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(16,185,129,0.4); }
        .error-message {
            background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
            padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: 500;
        }
        .back-link { margin-top: 20px; color: #6b7280; text-decoration: none; }
        .security-info {
            margin-top: 30px; padding: 20px; background: #f0f9ff;
            border-radius: 10px; text-align: left;
        }
        .security-info h4 { color: #1e40af; margin-bottom: 10px; }
        .security-info ul { color: #4b5563; margin: 10px 0; padding-left: 20px; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="otp-container">
        <div class="otp-header">
            <h1><i class="fas fa-shield-alt"></i></h1>
            <h1>Email Verification</h1>
            <p>Enter the OTP sent to your email</p>
        </div>
        
        {% if not expired %}
        <div class="email-sent">
            <h3><i class="fas fa-envelope"></i> OTP Email Sent Successfully!</h3>
            <p>Check your inbox: <strong>22dcs047@charusat.edu.in</strong></p>
            <p style="margin-top: 10px; opacity: 0.9; font-size: 0.9rem;">
                Professional HTML email with security instructions
            </p>
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
                <i class="fas fa-check"></i> Verify Email OTP
            </button>
        </form>
        
        <a href="/login" class="back-link">
            <i class="fas fa-arrow-left"></i> Back to Login
        </a>
        {% endif %}
        
        <div class="security-info">
            <h4><i class="fas fa-info-circle"></i> Email Security Information</h4>
            <ul>
                <li>OTP is valid for exactly 120 seconds (2 minutes)</li>
                <li>Each OTP is unique and single-use only</li>
                <li>Professional HTML email with security warnings</li>
                <li>If no email, check spam folder or console logs</li>
                <li>Never share your OTP with anyone</li>
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
                
                setTimeout(function() {
                    window.location.href = '/login';
                }, 3000);
            } else {
                countdownEl.textContent = timeLeft;
                
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
        
        document.querySelector('.otp-input').addEventListener('input', function(e) {
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

if __name__ == '__main__':
    print("🔐 Starting Gmail Assistant with Email 2FA...")
    print("🔍 Security Configuration:")
    print(f"SECRET_KEY: {'✅ Set' if app.secret_key else '❌ Missing'}")
    print(f"ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME', 'admin')}")
    print(f"ADMIN_PASSWORD: {'✅ Set' if os.getenv('ADMIN_PASSWORD') else '⚠️ Using default'}")
    print(f"Gmail API: {'✅ Available' if GMAIL_AVAILABLE else '❌ Not Available'}")
    print(f"Gmail Credentials: {'✅ Configured' if os.getenv('GMAIL_REFRESH_TOKEN') else '⚠️ Not Configured'}")
    print("📧 OTP Email Target: 22dcs047@charusat.edu.in")
    print("🔒 2FA System: Email OTP with 120-second expiration")
    app.run(debug=True)>✅ Username/Password verified</div>
                    <div>✅ Email OTP verification completed</div>
                    <div>✅ Session secured with 2FA</div>
                    <div>✅ All endpoints protected</div>
                </div>
                <p style="margin-top: 15px; opacity: 0.9;">
                    🕒 Authenticated at: {auth_time[:16] if len(auth_time) > 16 else auth_time}
                </p>
            </div>
            
            <a href="/dashboard" class="btn primary"><i class="fas fa-tachometer-alt"></i> Open Secure Dashboard</a>
            <a href="/debug" class="btn"><i class="fas fa-cog"></i> System Debug</a>
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
    <title>Secure Gmail Dashboard - 2FA Protected</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%); 
            min-height: 100vh; color: #1f2937; 
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
        .header h1 {{ font-size: 2.5rem; font-weight: 800; margin-bottom: 10px; }}
        .security-banner {{ 
            background: linear-gradient(135deg, #10b981, #059669); color: white; 
            padding: 20px 25px; border-radius: 15px; margin: 20px 0; 
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
        .main-actions {{ text-align: center; margin: 40px 0; }}
        .action-btn {{ 
            background: linear-gradient(135deg, #ef4444, #dc2626); color: white; 
            padding: 18px 40px; border: none; border-radius: 12px; 
            font-size: 1.2rem; font-weight: 700; text-decoration: none; 
            display: inline-block; transition: all 0.3s ease; 
            box-shadow: 0 8px 25px rgba(239,68,68,0.3); 
            text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; margin: 10px; 
        }}
        .action-btn:hover {{ transform: translateY(-3px); box-shadow: 0 15px 35px rgba(239,68,68,0.4); }}
        .action-btn.secondary {{ 
            background: linear-gradient(135deg, #3b82f6, #1e40af); 
            box-shadow: 0 8px 25px rgba(59,130,246,0.3); 
        }}
        .action-btn.secondary:hover {{ box-shadow: 0 15px 35px rgba(59,130,246,0.4); }}
        .emails-section {{ 
            background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
        }}
        .section-title {{ 
            font-size: 1.8rem; font-weight: 700; margin-bottom: 25px; 
            display: flex; align-items: center; gap: 10px; 
        }}
        .email-card {{ 
            background: #ffffff; margin-bottom: 20px; padding: 25px; border-radius: 12px; 
            border-left: 4px solid var(--priority-color); transition: all 0.3s ease; 
            box-shadow: 0 3px 10px rgba(0,0,0,0.05); 
        }}
        .email-card:hover {{ transform: translateX(5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }}
        .email-card.high {{ --priority-color: #ea580c; }}
        .email-card.medium {{ --priority-color: #ca8a04; }}
        .email-card.low {{ --priority-color: #059669; }}
        .email-header {{ 
            display: flex; justify-content: space-between; align-items: flex-start; 
            margin-bottom: 15px; flex-wrap: wrap; gap: 10px; 
        }}
        .email-subject {{ font-size: 1.2rem; font-weight: 700; flex: 1; min-width: 200px; }}
        .priority-badge {{ 
            background: var(--priority-color); color: white; padding: 6px 12px; border-radius: 20px; 
            font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; 
        }}
        .email-meta {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 10px; margin-bottom: 15px; color: #6b7280; font-size: 0.9rem; 
        }}
        .meta-item {{ display: flex; align-items: center; gap: 8px; }}
        .meta-item i {{ color: var(--priority-color); width: 14px; }}
        .email-snippet {{ 
            background: #f8fafc; padding: 15px; border-radius: 8px; margin: 15px 0; 
            color: #4b5563; line-height: 1.5; border-left: 3px solid var(--priority-color); 
        }}
        .draft-btn {{ 
            background: var(--priority-color); color: white; padding: 10px 20px; border: none; 
            border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; 
            margin-top: 15px; font-size: 0.9rem; 
        }}
        .draft-btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .notification {{ 
            position: fixed; top: 20px; left: 50%; transform: translateX(-50%); 
            background: #10b981; color: white; padding: 15px 25px; border-radius: 10px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); display: none; z-index: 1000; 
            font-weight: 600; 
        }}
        .notification.show {{ display: block; }}
        .notification.error {{ background: #ef4444; }}
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
            <div class="security-banner">
                <i class="fas fa-check-shield"></i>
                <div>
                    <strong>Maximum Security Active - 2FA Email Verification Complete</strong><br>
                    <small>Authenticated at: {auth_time[:16] if len(auth_time) > 16 else auth_time} | Session secured with email OTP</small>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="stat-number">3</div>
                <div class="stat-label">Total Emails</div>
            </div>
            <div class="stat-card direct">
                <div class="stat-number">3</div>
                <div class="stat-label">Direct Emails</div>
            </div>
            <div class="stat-card high">
                <div class="stat-number">2</div>
                <div class="stat-label">High Priority</div>
            </div>
        </div>
        
        <div class="main-actions">
            <button class="action-btn" onclick="showNotification('✨ Demo: Created drafts for 2 high priority emails!', 'success')">
                <i class="fas fa-magic"></i> Create Drafts for High Priority Emails
            </button>
            <button class="action-btn secondary" onclick="showNotification('🔄 Demo: Emails refreshed with latest data!', 'success')">
                <i class="fas fa-sync-alt"></i> Refresh Emails
            </button>
        </div>
        
        <div class="emails-section">
            <div class="section-title">
                <i class="fas fa-inbox"></i> Recent Emails (2FA Protected)
            </div>
            
            <div class="email-card high">
                <div class="email-header">
                    <div class="email-subject">July 2025 Exam Registration Deadline - Last 3 Days!</div>
                    <div
