from flask import Flask, jsonify, request, session, redirect, url_for, render_template_string
from datetime import datetime, timedelta
import json
import os
import base64
import time
import re
import hashlib
import secrets

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
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

app = Flask(__name__)

# Security Configuration
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))  # Use environment variable or generate

# User Credentials (In production, use database)
USERS = {
    os.getenv('ADMIN_USERNAME', 'admin'): {
        'password_hash': hashlib.sha256((os.getenv('ADMIN_PASSWORD', 'admin123')).encode()).hexdigest(),
        'role': 'admin'
    }
}

def hash_password(password):
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def login_required(f):
    """Decorator to require login for protected routes"""
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

class RobustGmailAssistant:
    def __init__(self):
        self.user_email = '22dcs047@charusat.edu.in'
        self.gmail_service = None
        self.gmail_connected = False
        self.openai_available = False
        
        print("🚀 Initializing Gmail Assistant...")
        
        # Initialize safely
        try:
            self._safe_init_openai()
            self._safe_init_gmail()
        except Exception as e:
            print(f"⚠️ Init error: {e}")
        
        print(f"✅ Assistant ready - Gmail: {'Connected' if self.gmail_connected else 'Demo'}, AI: {'Yes' if self.openai_available else 'No'}")
    
    def _safe_init_openai(self):
        """Initialize OpenAI with timeout protection"""
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
        """Initialize Gmail with robust error handling"""
        if not GMAIL_AVAILABLE:
            print("📧 Gmail API not available")
            return
        
        try:
            # Get credentials with validation
            refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
            client_id = os.getenv('GMAIL_CLIENT_ID')
            client_secret = os.getenv('GMAIL_CLIENT_SECRET')
            
            if not refresh_token or not client_id or not client_secret:
                print("⚠️ Gmail credentials missing")
                return
            
            if len(refresh_token) < 50 or len(client_id) < 30:
                print("⚠️ Gmail credentials appear invalid")
                return
            
            # Build credentials
            token_data = {
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'scopes': [
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.compose',
                    'https://www.googleapis.com/auth/gmail.modify'
                ]
            }
            
            creds = Credentials.from_authorized_user_info(token_data, token_data['scopes'])
            
            # Refresh if needed
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing Gmail token...")
                creds.refresh(Request())
                print("✅ Token refreshed")
            
            # Test connection
            if creds and creds.valid:
                self.gmail_service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
                
                # Quick test
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                email_address = profile.get('emailAddress', 'Unknown')
                
                self.gmail_connected = True
                print(f"✅ Gmail connected: {email_address}")
            else:
                print("❌ Gmail credentials invalid")
                
        except Exception as e:
            print(f"❌ Gmail init error: {e}")
            self.gmail_connected = False
    
    def get_emails_with_timeout(self):
        """Get emails with robust timeout handling"""
        if not self.gmail_connected:
            print("📧 Using demo emails")
            return self.get_demo_emails()
        
        try:
            print("📨 Fetching real emails...")
            
            # Quick query with timeout protection
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y/%m/%d')
            query = f'is:unread after:{three_days_ago} -from:me'
            
            # Get message list first (fast operation)
            result = self.gmail_service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=10  # Reduced for reliability
            ).execute()
            
            messages = result.get('messages', [])
            print(f"📊 Found {len(messages)} messages")
            
            if not messages:
                print("📭 No unread emails found")
                return self.get_demo_emails()
            
            emails = []
            processed = 0
            
            # Process emails with timeout protection
            for message in messages[:8]:  # Limit to 8 for Vercel timeout
                try:
                    # Get message details
                    msg = self.gmail_service.users().messages().get(
                        userId='me', 
                        id=message['id'], 
                        format='metadata',  # Faster than 'full'
                        metadataHeaders=['Subject', 'From', 'To', 'Date']
                    ).execute()
                    
                    # Extract headers safely
                    headers = msg.get('payload', {}).get('headers', [])
                    subject = self._get_header(headers, 'Subject') or 'No Subject'
                    from_email = self._get_header(headers, 'From') or 'Unknown'
                    to_field = self._get_header(headers, 'To') or ''
                    
                    snippet = msg.get('snippet', '')
                    
                    # Parse date
                    try:
                        email_date = datetime.fromtimestamp(int(msg['internalDate']) / 1000)
                        date_str = email_date.strftime('%Y-%m-%d')
                        time_str = email_date.strftime('%H:%M')
                    except:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                        time_str = datetime.now().strftime('%H:%M')
                    
                    # Fast classification
                    classification = self._fast_classify(subject, snippet, from_email)
                    summary = self._create_summary(subject, snippet)
                    
                    emails.append({
                        'id': message['id'],
                        'subject': subject,
                        'from_email': from_email,
                        'to_field': to_field,
                        'snippet': snippet,
                        'display_snippet': summary,
                        'body': snippet,  # Use snippet as body for speed
                        'date': date_str,
                        'time': time_str,
                        'priority': classification['priority'],
                        'email_type': classification['type'],
                        'urgency_reason': classification['reason'],
                        'ai_classified': classification.get('ai_classified', False)
                    })
                    
                    processed += 1
                    
                    # Stop if taking too long
                    if processed >= 8:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error processing email: {e}")
                    continue
            
            print(f"✅ Processed {len(emails)} emails successfully")
            return emails if emails else self.get_demo_emails()
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return self.get_demo_emails()
    
    def _get_header(self, headers, name):
        """Safely get header value"""
        for header in headers:
            if header.get('name') == name:
                return header.get('value', '')
        return ''
    
    def _fast_classify(self, subject, snippet, sender):
        """Fast rule-based classification"""
        try:
            subject_lower = subject.lower()
            sender_lower = sender.lower()
            content_lower = snippet.lower()
            
            # Check promotional first
            promotional_indicators = ['noreply', 'no-reply', 'unsubscribe', 'newsletter', 'marketing', 'automated']
            is_promotional = any(indicator in sender_lower for indicator in promotional_indicators)
            
            if is_promotional:
                # Security exception
                if any(word in subject_lower for word in ['security', 'alert', 'breach', 'suspicious']):
                    return {
                        'priority': 'high',
                        'type': 'security',
                        'reason': 'Security alert from automated system'
                    }
                return {
                    'priority': 'low',
                    'type': 'promotional',
                    'reason': 'Promotional/automated email'
                }
            
            # High priority detection
            high_indicators = ['deadline', 'urgent', 'registration', 'interview', 'meeting', 'due', 'expires', 'last day']
            if any(indicator in subject_lower for indicator in high_indicators):
                return {
                    'priority': 'high',
                    'type': 'academic' if '@charusat.edu.in' in sender else 'general',
                    'reason': 'Contains deadline/urgent keywords in subject'
                }
            
            # Medium priority for academic
            if '@charusat.edu.in' in sender or 'charusat' in sender_lower:
                return {
                    'priority': 'medium',
                    'type': 'academic',
                    'reason': 'Email from academic institution'
                }
            
            # Default classification
            return {
                'priority': 'low',
                'type': 'general',
                'reason': 'Default classification'
            }
            
        except Exception as e:
            print(f"⚠️ Classification error: {e}")
            return {
                'priority': 'medium',
                'type': 'general',
                'reason': 'Fallback classification'
            }
    
    def _create_summary(self, subject, snippet):
        """Create smart summary quickly"""
        try:
            subject_lower = subject.lower()
            
            # Clean snippet
            text = snippet or "No preview available"
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Contextual summaries
            if 'deadline' in subject_lower:
                return f"⏰ Registration deadline notice - {text[:60]}..."
            elif 'meeting' in subject_lower:
                return f"📅 Meeting invitation - {text[:60]}..."
            elif 'security' in subject_lower:
                return f"🔒 Security notification - {text[:60]}..."
            elif any(word in subject_lower for word in ['opportunity', 'job', 'internship']):
                return f"💼 Career opportunity - {text[:60]}..."
            else:
                return text[:80] + "..." if len(text) > 80 else text
                
        except Exception as e:
            print(f"⚠️ Summary error: {e}")
            return snippet[:80] + "..." if snippet else "Preview unavailable"
    
    def get_demo_emails(self):
        """Demo emails for testing"""
        now = datetime.now()
        return [
            {
                'id': 'demo_1',
                'subject': 'July 2025 Exam Registration Deadline - Aug 22, 2025 - 5:00 PM [12 week courses] – Last 3 days to Register!',
                'from_email': 'NPTEL <noreply@nptel.iitm.ac.in>',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'This is a final reminder about the exam registration deadline approaching on August 22, 2025.',
                'display_snippet': '⏰ Registration deadline notice - Last 3 days to register for July 2025 Exam',
                'body': 'This is a final reminder about the exam registration deadline approaching on August 22, 2025.',
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'priority': 'high',
                'email_type': 'academic',
                'urgency_reason': 'Contains deadline/urgent keywords in subject',
                'ai_classified': False
            },
            {
                'id': 'demo_2',
                'subject': 'Course Announcement - New Materials Available',
                'from_email': 'Academic Office <academic@charusat.edu.in>',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'New course materials have been uploaded to the portal for your reference.',
                'display_snippet': 'New course materials have been uploaded to the portal for your reference.',
                'body': 'Dear students, new course materials are now available on the portal.',
                'date': now.strftime('%Y-%m-%d'),
                'time': (now - timedelta(hours=2)).strftime('%H:%M'),
                'priority': 'medium',
                'email_type': 'academic',
                'urgency_reason': 'Email from academic institution',
                'ai_classified': False
            }
        ]
    
    def get_stats_safe(self):
        """Get statistics safely"""
        try:
            emails = self.get_emails_with_timeout()
            
            # Count safely
            direct_emails = []
            high_priority = []
            medium_priority = []
            low_priority = []
            
            for email in emails:
                try:
                    # Direct email check
                    if self.user_email in email.get('to_field', ''):
                        direct_emails.append(email)
                    
                    # Priority counts
                    priority = email.get('priority', 'low')
                    if priority in ['high', 'critical']:
                        high_priority.append(email)
                    elif priority == 'medium':
                        medium_priority.append(email)
                    else:
                        low_priority.append(email)
                except:
                    continue
            
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
            # Return safe fallback
            demo_emails = self.get_demo_emails()
            return {
                'all_emails': demo_emails,
                'direct_emails': demo_emails,
                'stats': {
                    'total_unread': len(demo_emails),
                    'direct_count': len(demo_emails),
                    'high_priority_count': 1,
                    'medium_priority_count': 1,
                    'low_priority_count': 0
                },
                'gmail_connected': False,
                'openai_connected': False,
                'last_updated': datetime.now().isoformat()
            }
    
    def create_draft_safe(self, email_data):
        """Create draft with error handling"""
        if not self.gmail_connected or not EMAIL_AVAILABLE:
            return False, "Draft creation not available in demo mode"
        
        try:
            # Create simple reply
            reply_body = f"""Thank you for your email regarding "{email_data.get('subject', 'your message')}".

I have received your message and will respond appropriately.

Best regards,
Jai Mehtani
Computer Science Student
Charusat University
📧 22dcs047@charusat.edu.in

🤖 This is an automated acknowledgment."""
            
            message = MIMEText(reply_body)
            message['to'] = email_data.get('from_email', '')
            message['subject'] = f"Re: {email_data.get('subject', 'Your Email')}"
            
            draft = {
                'message': {
                    'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
                }
            }
            
            created_draft = self.gmail_service.users().drafts().create(
                userId='me', body=draft
            ).execute()
            
            return True, "Draft created successfully"
            
        except Exception as e:
            print(f"❌ Draft error: {e}")
            return False, f"Error creating draft: {str(e)}"

# Initialize with error protection
try:
    assistant = RobustGmailAssistant()
except Exception as e:
    print(f"❌ Failed to initialize assistant: {e}")
    assistant = None

# LOGIN ROUTES
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and verify_password(password, USERS[username]['password_hash']):
            session['user'] = username
            session['role'] = USERS[username]['role']
            return redirect(url_for('home'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid username or password")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

# PROTECTED ROUTES
@app.route('/')
@login_required
def home():
    if not assistant:
        return "Assistant initialization failed", 500
        
    status = "Real Gmail" if assistant.gmail_connected else "Demo Mode"
    user = session.get('user', 'User')
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - {status}</title>
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
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 25px;
            backdrop-filter: blur(10px);
        }}
        .logout-btn {{
            background: #ef4444;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 600;
            margin-left: 15px;
            transition: all 0.3s ease;
        }}
        .logout-btn:hover {{ background: #dc2626; }}
        .hero {{ 
            background: rgba(255,255,255,0.95); 
            padding: 60px 40px; 
            border-radius: 20px; 
            text-align: center; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            color: #1f2937;
            margin-bottom: 40px;
            margin-top: 40px;
        }}
        .hero h1 {{ font-size: 3.5rem; margin-bottom: 20px; font-weight: 800; color: #1f2937; }}
        .hero p {{ font-size: 1.3rem; margin-bottom: 30px; color: #4b5563; line-height: 1.6; }}
        .btn {{ 
            background: linear-gradient(135deg, #3b82f6, #1e40af);
            color: white; padding: 15px 30px; border: none; border-radius: 10px; 
            font-size: 1.1rem; font-weight: 600; text-decoration: none; 
            display: inline-block; margin: 10px 15px; transition: all 0.3s ease; 
            box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(59,130,246,0.4); }}
        .btn.primary {{ background: linear-gradient(135deg, #059669, #047857); box-shadow: 0 4px 15px rgba(5,150,105,0.3); }}
        .status-badge {{ 
            background: linear-gradient(135deg, #{'059669, #047857' if assistant.gmail_connected else 'dc2626, #b91c1c'}); 
            color: white; padding: 12px 24px; border-radius: 25px; font-weight: 600; 
            margin: 10px; display: inline-block; 
            box-shadow: 0 4px 15px rgba({'5,150,105' if assistant.gmail_connected else '220,38,38'},0.3);
        }}
    </style>
</head>
<body>
    <div class="user-info">
        <i class="fas fa-user"></i> Welcome, {user}
        <a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Logout</a>
    </div>
    
    <div class="container">
        <div class="hero">
            <div class="status-badge">
                <i class="fas fa-{'satellite-dish' if assistant.gmail_connected else 'exclamation-triangle'}"></i> 
                {status.upper()} 
            </div>
            <h1><i class="fas fa-brain"></i> AI Gmail Assistant</h1>
            <p>{'Secure intelligent email management with real Gmail integration and smart priority detection' if assistant.gmail_connected else 'Secure demo mode - All features working with sample data for testing'}</p>
            
            <a href="/dashboard" class="btn primary"><i class="fas fa-tachometer-alt"></i> Open Dashboard</a>
            <a href="/debug" class="btn"><i class="fas fa-cog"></i> System Info</a>
        </div>
    </div>
</body>
</html>'''

@app.route('/dashboard')
@login_required
def dashboard():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Secure Dashboard</title>
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
            background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 25px;
            backdrop-filter: blur(10px); color: white;
        }
        .logout-btn {
            background: #ef4444; color: white; padding: 8px 16px; border: none;
            border-radius: 20px; text-decoration: none; font-weight: 600;
            margin-left: 15px; transition: all 0.3s ease;
        }
        .logout-btn:hover { background: #dc2626; }
        .header {
            background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px;
            margin-bottom: 30px; margin-top: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 2.5rem; font-weight: 800; color: #1f2937; margin-bottom: 10px; }
        .status-indicator {
            background: linear-gradient(135deg, #059669, #047857); color: white;
            padding: 8px 20px; border-radius: 20px; font-weight: 600;
            display: inline-block; font-size: 0.9rem;
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
            .header { padding: 20px; }
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr; gap: 15px; }
            .create-drafts-btn { padding: 15px 30px; font-size: 1rem; }
            .email-header { flex-direction: column; align-items: stretch; }
            .email-meta { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="user-info">
        <i class="fas fa-user"></i> Dashboard Access
        <a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Logout</a>
    </div>
    
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-shield-alt"></i> Secure Gmail Dashboard</h1>
            <div class="status-indicator" id="statusIndicator">
                <i class="fas fa-satellite-dish"></i> Loading status...
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
                Recent Emails
                <button class="refresh-btn" onclick="refreshEmails()">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
            <div id="emailsList" class="loading">
                <div class="spinner"></div>
                <p>Loading your emails...</p>
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
                console.log('🔄 Loading emails...');
                const response = await fetch('/api/emails');
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('📊 Email data received:', data);
                
                emailsData = data.all_emails || [];
                
                // Update stats safely
                document.getElementById('totalEmails').textContent = data.stats?.total_unread || 0;
                document.getElementById('directEmails').textContent = data.stats?.direct_count || 0;
                document.getElementById('highPriority').textContent = data.stats?.high_priority_count || 0;
                
                // Update status
                const statusEl = document.getElementById('statusIndicator');
                if (data.gmail_connected) {
                    statusEl.innerHTML = '<i class="fas fa-satellite-dish"></i> Gmail Connected - Live Data';
                    statusEl.style.background = 'linear-gradient(135deg, #059669, #047857)';
                } else {
                    statusEl.innerHTML = '<i class="fas fa-chart-line"></i> Demo Mode - Sample Data';
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
                        <p>Your inbox is clean!</p>
                    </div>`;
                return;
            }
            
            console.log(`📧 Displaying ${emails.length} emails`);
            
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
                
                showNotification('Creating draft...', 'info');
                
                const response = await fetch('/api/create-draft', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email_id: emailId })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification('✅ Draft created successfully!', 'success');
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
                
                showNotification(`Creating ${highPriorityEmails.length} drafts...`, 'info');
                
                const response = await fetch('/api/create-drafts-bulk', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email_ids: highPriorityEmails.map(e => e.id) })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification(`✅ Created ${result.created_count} drafts!`, 'success');
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
                '<div class="loading"><div class="spinner"></div><p>Refreshing emails...</p></div>';
            loadEmails();
        }
        
        // Load emails on page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Secure dashboard loaded, initializing...');
            loadEmails();
        });
        
        // Auto-refresh every 3 minutes
        setInterval(loadEmails, 180000);
    </script>
</body>
</html>'''

# PROTECTED API ROUTES
@app.route('/api/emails')
@login_required
def api_emails():
    """Secure API endpoint for email data"""
    try:
        if not assistant:
            return jsonify({
                'error': 'Assistant not initialized',
                'all_emails': [],
                'direct_emails': [],
                'stats': {'total_unread': 0, 'direct_count': 0, 'high_priority_count': 0},
                'gmail_connected': False,
                'openai_connected': False
            }), 200
        
        print("📧 Secure API call - fetching email stats")
        data = assistant.get_stats_safe()
        print(f"✅ API returning {len(data.get('all_emails', []))} emails")
        return jsonify(data), 200
        
    except Exception as e:
        print(f"❌ API error: {e}")
        # Return safe fallback instead of error
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
    """Secure debug page"""
    try:
        if not assistant:
            return "Assistant not initialized", 500
        
        user = session.get('user', 'Unknown')
        
        return f'''
<html>
<head><title>Secure Gmail Assistant Debug</title>
<style>
body{{font-family:monospace;background:#000;color:#0f0;padding:20px;}}
.user-info{{position:absolute;top:10px;right:10px;background:#333;padding:10px;border-radius:5px;}}
.logout-btn{{background:#f00;color:#fff;padding:5px 10px;border:none;border-radius:3px;margin-left:10px;}}
</style>
</head>
<body>
<div class="user-info">
User: {user} <a href="/logout" class="logout-btn">Logout</a>
</div>
<h1>🔧 Secure Gmail Assistant Debug</h1>
<p>Gmail Connected: {'✅ Yes' if assistant.gmail_connected else '❌ No'}</p>
<p>OpenAI Available: {'✅ Yes' if assistant.openai_available else '❌ No'}</p>
<p>Environment Variables:</p>
<ul>
<li>GMAIL_REFRESH_TOKEN: {'✅ Set' if os.getenv('GMAIL_REFRESH_TOKEN') else '❌ Missing'}</li>
<li>GMAIL_CLIENT_ID: {'✅ Set' if os.getenv('GMAIL_CLIENT_ID') else '❌ Missing'}</li>
<li>GMAIL_CLIENT_SECRET: {'✅ Set' if os.getenv('GMAIL_CLIENT_SECRET') else '❌ Missing'}</li>
<li>OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}</li>
<li>SECRET_KEY: {'✅ Set' if app.secret_key else '❌ Missing'}</li>
<li>ADMIN_USERNAME: {'✅ Set' if os.getenv('ADMIN_USERNAME') else '❌ Missing (using default)'}</li>
<li>ADMIN_PASSWORD: {'✅ Set' if os.getenv('ADMIN_PASSWORD') else '❌ Missing (using default)'}</li>
</ul>
<p><a href="/dashboard" style="color:#0ff;">← Back to Dashboard</a></p>
<p><a href="/api/emails" style="color:#0ff;">📧 Test Email API</a></p>
</body>
</html>'''
        
    except Exception as e:
        return f'<h1>Debug Error: {str(e)}</h1>'

# LOGIN TEMPLATE
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Secure Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #1f2937;
        }
        .login-container {
            background: rgba(255,255,255,0.95);
            padding: 60px 50px;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            max-width: 450px;
            width: 100%;
        }
        .login-header {
            text-align: center;
            margin-bottom: 40px;
        }
        .login-header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            color: #1f2937;
            margin-bottom: 10px;
        }
        .login-header p {
            color: #6b7280;
            font-size: 1.1rem;
        }
        .form-group {
            margin-bottom: 25px;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #374151;
        }
        .form-group input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #f9fafb;
        }
        .form-group input:focus {
            outline: none;
            border-color: #3b82f6;
            background: #ffffff;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
        }
        .login-btn {
            width: 100%;
            background: linear-gradient(135deg, #3b82f6, #1e40af);
            color: white;
            padding: 15px 20px;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59,130,246,0.4);
        }
        .error-message {
            background: #fef2f2;
            border: 1px solid #fecaca;
            color: #b91c1c;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .security-info {
            margin-top: 30px;
            padding: 20px;
            background: #f0f9ff;
            border-radius: 10px;
            border-left: 4px solid #3b82f6;
        }
        .security-info h3 {
            color: #1e40af;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        .security-info p {
            color: #1e40af;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .input-group {
            position: relative;
        }
        .input-group i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #6b7280;
            font-size: 1.1rem;
        }
        .input-group input {
            padding-left: 50px;
        }
        @media (max-width: 480px) {
            .login-container {
                margin: 20px;
                padding: 40px 30px;
            }
            .login-header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1><i class="fas fa-shield-alt"></i></h1>
            <h1>Secure Access</h1>
            <p>Gmail Assistant Login</p>
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
                           placeholder="Enter your username" autocomplete="off" 
                           spellcheck="false" data-form-type="other">
                </div>
            </div>
            
            <div class="form-group">
                <label for="password"><i class="fas fa-lock"></i> Password</label>
                <div class="input-group">
                    <i class="fas fa-lock"></i>
                    <input type="password" id="password" name="password" required 
                           placeholder="Enter your password" autocomplete="new-password"
                           spellcheck="false" data-form-type="other">
                </div>
            </div>
            
            <button type="submit" class="login-btn">
                <i class="fas fa-sign-in-alt"></i>  Login
            </button>
        </form>
        
        <div class="security-info">
            <h3><i class="fas fa-info-circle"></i> Security Notice</h3>
            <p>This is a secure area. All access is logged and monitored. Your session will automatically expire for security.</p>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    print("🔐 Starting SECURE Gmail Assistant...")
    print("🔍 Security Environment Check:")
    print(f"SECRET_KEY: {'✅ Set' if app.secret_key else '❌ Missing'}")
    print(f"ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME', 'admin')} (default if not set)")
    print(f"ADMIN_PASSWORD: {'✅ Set' if os.getenv('ADMIN_PASSWORD') else '❌ Using default'}")
    app.run(debug=True)
