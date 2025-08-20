# Gmail Assistant - Enhanced Professional Version with Beautiful UI
# Fixes: 1) Improved priority detection 2) Draft creation buttons 3) Stunning modern design
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
    
    def classify_email_with_ai(self, subject, body, sender):
        """Enhanced AI classification with better priority detection"""
        if not self.openai_available:
            return self._classify_email_enhanced(subject, body, sender)
        
        try:
            prompt = f"""Analyze this email and classify it accurately:

Subject: {subject}
From: {sender}
Content: {body[:500]}...

IMPORTANT: Be very strict about priority levels:
- CRITICAL: Life-threatening, legal deadlines today, security breaches
- HIGH: Important deadlines (within days), registration deadlines, meeting invitations, academic deadlines
- MEDIUM: Announcements, newsletters, course updates, general reminders
- LOW: Promotional content, non-urgent notifications

Provide a JSON response with:
1. priority: "critical", "high", "medium", or "low"
2. email_type: "academic", "security", "personal", "promotional", "work", or "general"
3. urgency_reason: specific explanation for the priority level

Format as valid JSON only."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            result['ai_classified'] = True
            return result
            
        except Exception as e:
            print(f"❌ AI classification error: {e}")
            return self._classify_email_enhanced(subject, body, sender)
    
    def _classify_email_enhanced(self, subject, body, sender):
        """Enhanced rule-based email classification with better deadline detection"""
        subject_lower = subject.lower()
        body_lower = body.lower()
        
        # Enhanced keyword detection
        critical_keywords = ['urgent', 'critical', 'emergency', 'immediate', 'asap', 'expires today', 'security alert', 'final notice']
        high_keywords = ['deadline', 'due', 'registration deadline', 'last day', 'expires', 'meeting', 'interview', 'submission', 'important', 'reminder', 'final reminder']
        medium_keywords = ['announcement', 'newsletter', 'course', 'lecture', 'workshop', 'invitation', 'update', 'notification']
        
        priority = 'low'
        urgency_reason = 'Default low priority'
        
        # Check for critical priorities
        if any(keyword in subject_lower or keyword in body_lower for keyword in critical_keywords):
            priority = 'critical'
            urgency_reason = 'Contains critical urgency keywords'
        # Enhanced deadline detection
        elif any(keyword in subject_lower for keyword in high_keywords) or 'deadline' in subject_lower:
            priority = 'high'
            urgency_reason = 'Contains deadline or important keywords in subject'
        elif any(keyword in body_lower for keyword in high_keywords):
            priority = 'high'
            urgency_reason = 'Contains important keywords in content'
        elif any(keyword in subject_lower or keyword in body_lower for keyword in medium_keywords):
            priority = 'medium'
            urgency_reason = 'Contains medium priority keywords'
        elif '@charusat.edu.in' in sender and 'no-reply' not in sender.lower():
            priority = 'medium'
            urgency_reason = 'Academic email from institution'
        
        # Determine email type
        email_type = 'general'
        if '@charusat.edu.in' in sender or 'professor' in sender.lower() or 'academic' in subject_lower:
            email_type = 'academic'
        elif 'security' in subject_lower or 'alert' in subject_lower:
            email_type = 'security'
        elif 'noreply' in sender or 'unsubscribe' in body_lower:
            email_type = 'promotional'
        
        return {
            'priority': priority,
            'email_type': email_type,
            'urgency_reason': urgency_reason,
            'ai_classified': self.openai_available
        }
    
    def get_unread_emails(self):
        """Get real unread emails from Gmail"""
        if not self.gmail_connected:
            return self.get_demo_emails()
        
        try:
            # Get unread emails from last 3 days
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y/%m/%d')
            query = f'is:unread after:{three_days_ago} -from:me'
            
            result = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=30
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
                    
                    # Get email body
                    body = self._extract_email_body(msg['payload'])
                    
                    # Parse date
                    try:
                        email_date = datetime.fromtimestamp(int(msg['internalDate']) / 1000)
                        date_str = email_date.strftime('%Y-%m-%d')
                        time_str = email_date.strftime('%H:%M')
                    except:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                        time_str = datetime.now().strftime('%H:%M')
                    
                    # Enhanced classification
                    classification = self.classify_email_with_ai(subject, body, from_email)
                    
                    emails.append({
                        'id': message['id'],
                        'subject': subject,
                        'from_email': from_email,
                        'to_field': to_field,
                        'snippet': snippet,
                        'body': body[:1000] + '...' if len(body) > 1000 else body,
                        'date': date_str,
                        'time': time_str,
                        'priority': classification['priority'],
                        'email_type': classification['email_type'],
                        'ai_classified': classification['ai_classified'],
                        'urgency_reason': classification.get('urgency_reason', '')
                    })
                    
                except Exception as e:
                    print(f"❌ Error processing email: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return self.get_demo_emails()
    
    def _extract_email_body(self, payload):
        """Extract text content from email payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        elif payload['mimeType'] == 'text/plain':
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body.strip()
    
    def create_ai_draft(self, original_email):
        """Create an AI-powered draft reply"""
        if not self.openai_available:
            return self._create_basic_draft(original_email)
        
        try:
            prompt = f"""Create a professional auto-reply for this email:

Original Subject: {original_email['subject']}
From: {original_email['from_email']}
Priority: {original_email['priority']}
Content: {original_email['body'][:500]}...

Generate a professional acknowledgment email that:
1. Acknowledges receipt professionally
2. Indicates understanding of priority level
3. Provides appropriate response timeframe
4. Maintains professional tone
5. Is concise but personalized

Format as plain text email body only."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            ai_body = response.choices[0].message.content.strip()
            
            # Add professional signature
            full_body = f"""{ai_body}

Best regards,
Jai Mehtani
Computer Science Student & Developer
Charusat University
📧 22dcs047@charusat.edu.in

🤖 This is an AI-assisted acknowledgment. I will personally review and respond to your email."""

            return full_body
            
        except Exception as e:
            print(f"❌ AI draft creation error: {e}")
            return self._create_basic_draft(original_email)
    
    def _create_basic_draft(self, original_email):
        """Create basic template draft"""
        priority_responses = {
            'critical': 'I understand this is critical and will respond within 2 hours.',
            'high': 'I understand this is important and will respond within 24 hours.',
            'medium': 'I will respond within 2-3 business days.',
            'low': 'I will respond within a week.'
        }
        
        response_time = priority_responses.get(original_email['priority'], 'I will respond soon.')
        
        return f"""Thank you for your email regarding "{original_email['subject']}".

I have received your message and {response_time}

Best regards,
Jai Mehtani
Computer Science Student & Developer
Charusat University
📧 22dcs047@charusat.edu.in

🤖 This is an automated acknowledgment. I will personally review and respond to your email."""
    
    def create_gmail_draft(self, original_email):
        """Create actual Gmail draft"""
        if not self.gmail_connected:
            return False, "Gmail not connected"
        
        try:
            # Generate AI-powered reply content
            reply_body = self.create_ai_draft(original_email)
            
            # Create draft message
            subject = f"Re: {original_email['subject']}"
            
            message = MIMEText(reply_body)
            message['to'] = original_email['from_email']
            message['subject'] = subject
            
            # Create draft
            draft = {
                'message': {
                    'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
                }
            }
            
            created_draft = self.gmail_service.users().drafts().create(
                userId='me', body=draft
            ).execute()
            
            return True, f"Draft created with ID: {created_draft['id']}"
            
        except Exception as e:
            return False, f"Error creating draft: {e}"
    
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
                'ai_classified': False,
                'urgency_reason': 'System configuration required'
            }
        ]
    
    def get_email_stats(self):
        """Get email statistics"""
        emails = self.get_unread_emails()
        direct = [e for e in emails if '22dcs047@charusat.edu.in' in e.get('to_field', '')]
        high_priority = [e for e in emails if e['priority'] in ['high', 'critical']]
        medium_priority = [e for e in emails if e['priority'] == 'medium']
        low_priority = [e for e in emails if e['priority'] == 'low']
        
        return {
            'all_emails': emails,
            'direct_emails': direct,
            'cc_emails': [],
            'stats': {
                'total_unread': len(emails),
                'direct_count': len(direct),
                'cc_count': 0,
                'high_priority_count': len(high_priority),
                'medium_priority_count': len(medium_priority),
                'low_priority_count': len(low_priority),
                'ai_classified_count': len([e for e in emails if e.get('ai_classified', False)])
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
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
            min-height: 100vh; 
            color: white; 
            overflow-x: hidden;
            position: relative;
        }}
        body::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.05)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.05)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.03)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            animation: float 20s ease-in-out infinite;
        }}
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-20px) rotate(180deg); }}
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 40px 20px; 
            position: relative;
            z-index: 2;
        }}
        .hero {{ 
            background: rgba(255,255,255,0.15); 
            padding: 80px 50px; 
            border-radius: 30px; 
            backdrop-filter: blur(25px); 
            text-align: center; 
            box-shadow: 0 30px 60px rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.25);
            position: relative;
            overflow: hidden;
            margin-bottom: 50px;
        }}
        .hero::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(from 0deg, transparent, rgba(255,255,255,0.1), transparent);
            animation: rotate 30s linear infinite;
        }}
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        .hero-content {{
            position: relative;
            z-index: 2;
        }}
        .hero h1 {{ 
            font-size: 4rem; 
            margin-bottom: 25px; 
            font-weight: 800; 
            background: linear-gradient(45deg, #fff, #e8f4ff, #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 5px 15px rgba(0,0,0,0.1);
            letter-spacing: -1px;
        }}
        .hero p {{ 
            font-size: 1.4rem; 
            margin-bottom: 50px; 
            opacity: 0.95; 
            line-height: 1.7;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        .btn {{ 
            background: linear-gradient(135deg, #ff6b6b, #ee5a24, #ff6b6b);
            color: white; 
            padding: 20px 40px; 
            border: none; 
            border-radius: 60px; 
            font-size: 1.2rem; 
            font-weight: 700; 
            text-decoration: none; 
            display: inline-block; 
            margin: 15px 20px; 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
            box-shadow: 0 15px 35px rgba(255,107,107,0.4);
            position: relative;
            overflow: hidden;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        .btn:hover::before {{
            left: 100%;
        }}
        .btn:hover {{ 
            transform: translateY(-5px) scale(1.05); 
            box-shadow: 0 25px 50px rgba(255,107,107,0.5); 
        }}
        .btn.primary {{
            background: linear-gradient(135deg, #00b894, #00cec9, #74b9ff);
            box-shadow: 0 15px 35px rgba(0,184,148,0.4);
        }}
        .btn.primary:hover {{
            box-shadow: 0 25px 50px rgba(0,184,148,0.5);
        }}
        .status-badge {{ 
            background: linear-gradient(135deg, #{'00b894, #00cec9' if assistant.gmail_connected else 'ff6b6b, #ee5a24'}); 
            color: white; 
            padding: 20px 40px; 
            border-radius: 60px; 
            font-weight: 700; 
            margin: 20px; 
            display: inline-block; 
            animation: pulse 3s infinite;
            box-shadow: 0 15px 35px rgba({'0,184,148' if assistant.gmail_connected else '255,107,107'},0.4);
            font-size: 1.1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        @keyframes pulse {{ 
            0% {{ transform: scale(1); box-shadow: 0 15px 35px rgba({'0,184,148' if assistant.gmail_connected else '255,107,107'},0.4); }} 
            50% {{ transform: scale(1.08); box-shadow: 0 20px 45px rgba({'0,184,148' if assistant.gmail_connected else '255,107,107'},0.6); }} 
            100% {{ transform: scale(1); box-shadow: 0 15px 35px rgba({'0,184,148' if assistant.gmail_connected else '255,107,107'},0.4); }} 
        }}
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 40px;
            margin-top: 80px;
        }}
        .feature-card {{
            background: rgba(255,255,255,0.12);
            padding: 40px;
            border-radius: 25px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.25);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }}
        .feature-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ff6b6b, #ee5a24, #00b894, #74b9ff);
            transform: scaleX(0);
            transition: transform 0.4s ease;
        }}
        .feature-card:hover::before {{
            transform: scaleX(1);
        }}
        .feature-card:hover {{
            transform: translateY(-15px) scale(1.02);
            background: rgba(255,255,255,0.18);
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }}
        .feature-icon {{
            font-size: 3.5rem;
            margin-bottom: 25px;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .feature-card h3 {{
            font-size: 1.5rem;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        .feature-card p {{
            line-height: 1.6;
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }}
        .status-item {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            text-align: center;
        }}
        .status-item strong {{
            display: block;
            font-size: 1.2rem;
            margin-top: 5px;
        }}
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2.8rem; }}
            .hero p {{ font-size: 1.2rem; }}
            .btn {{ padding: 15px 30px; font-size: 1rem; }}
            .features {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <div class="hero-content">
                <div class="status-badge">
                    <i class="fas fa-{'satellite-dish' if assistant.gmail_connected else 'exclamation-triangle'}"></i> 
                    {status.upper()} 
                    <i class="fas fa-{'satellite-dish' if assistant.gmail_connected else 'exclamation-triangle'}"></i>
                </div>
                <h1><i class="fas fa-brain"></i> AI Gmail Assistant</h1>
                <p>{'Experience the future of email management with real Gmail integration and intelligent AI-powered features that transform how you handle your inbox.' if assistant.gmail_connected else 'Demo mode active - Configure environment variables to unlock the full power of real Gmail integration'}</p>
                
                <div class="status-grid">
                    <div class="status-item">
                        Gmail Connected
                        <strong>{'✅ LIVE' if assistant.gmail_connected else '❌ DEMO'}</strong>
                    </div>
                    <div class="status-item">
                        AI Powered
                        <strong>{'✅ ACTIVE' if assistant.openai_available else '❌ DISABLED'}</strong>
                    </div>
                    <div class="status-item">
                        Draft Creation
                        <strong>{'✅ READY' if assistant.gmail_connected else '❌ OFFLINE'}</strong>
                    </div>
                </div>
                
                <a href="/dashboard" class="btn primary"><i class="fas fa-rocket"></i> Launch Dashboard</a>
                <a href="/debug" class="btn"><i class="fas fa-diagnostics"></i> System Status</a>
            </div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-envelope-open-text"></i></div>
                <h3>Real Gmail Integration</h3>
                <p>Connect seamlessly to your actual Gmail account and manage real emails with advanced filtering, smart categorization, and intelligent priority detection.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-robot"></i></div>
                <h3>AI-Powered Intelligence</h3>
                <p>Leverage cutting-edge OpenAI GPT technology for intelligent email classification, priority detection, and contextual understanding of your messages.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-magic"></i></div>
                <h3>Smart Auto-Replies</h3>
                <p>Generate professional, personalized draft responses automatically. Save time with AI-crafted replies that understand context and maintain your professional tone.</p>
            </div>
        </div>
    </div>
</body>
</html>'''

@app.route('/dashboard')
def dashboard():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Professional Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
            min-height: 100vh; 
            color: white; 
            position: relative;
        }
        body::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23dots)"/></svg>');
            animation: float 25s ease-in-out infinite;
        }
        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; position: relative; z-index: 2; }
        
        .header {
            background: rgba(255,255,255,0.15);
            padding: 30px 40px;
            border-radius: 20px;
            backdrop-filter: blur(20px);
            margin-bottom: 40px;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(45deg, #fff, #e8f4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .status-indicator {
            background: linear-gradient(45deg, #00b894, #00cec9);
            color: white;
            padding: 12px 25px;
            border-radius: 50px;
            font-weight: 600;
            display: inline-block;
            animation: pulse 2s infinite;
            box-shadow: 0 10px 25px rgba(0,184,148,0.3);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            margin-bottom: 50px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.12);
            padding: 40px 30px;
            border-radius: 20px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
            text-align: center;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: var(--accent-color);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover::before { transform: scaleX(1); }
        .stat-card:hover { transform: translateY(-10px) scale(1.02); background: rgba(255,255,255,0.18); }
        
        .stat-number {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 15px;
            background: linear-gradient(45deg, var(--accent-color), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-label { font-size: 1.2rem; font-weight: 600; opacity: 0.9; }
        
        /* Priority-specific colors */
        .stat-card.total { --accent-color: #74b9ff; --accent-secondary: #0984e3; }
        .stat-card.direct { --accent-color: #a29bfe; --accent-secondary: #6c5ce7; }
        .stat-card.high { --accent-color: #ff6b6b; --accent-secondary: #ee5a24; }
        
        .main-action {
            text-align: center;
            margin: 50px 0;
        }
        
        .create-drafts-btn {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 25px 50px;
            border: none;
            border-radius: 60px;
            font-size: 1.3rem;
            font-weight: 700;
            text-decoration: none;
            display: inline-block;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 20px 40px rgba(255,107,107,0.4);
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }
        
        .create-drafts-btn::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .create-drafts-btn:hover::before { left: 100%; }
        .create-drafts-btn:hover { 
            transform: translateY(-5px) scale(1.05); 
            box-shadow: 0 30px 60px rgba(255,107,107,0.5); 
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 30px;
        }
        
        .refresh-btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(116,185,255,0.4);
        }
        
        .emails-section {
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 25px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .section-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .email-card {
            background: rgba(255,255,255,0.08);
            margin-bottom: 25px;
            padding: 30px;
            border-radius: 20px;
            border-left: 5px solid var(--priority-color);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .email-card::before {
            content: '';
            position: absolute;
            top: 0; right: 0;
            width: 100px; height: 100px;
            background: radial-gradient(circle, var(--priority-color), transparent);
            opacity: 0.1;
            transition: all 0.3s ease;
        }
        
        .email-card:hover {
            transform: translateX(10px);
            background: rgba(255,255,255,0.15);
        }
        
        .email-card:hover::before {
            width: 200px; height: 200px;
        }
        
        /* Priority Colors */
        .email-card.critical { --priority-color: #ff4757; }
        .email-card.high { --priority-color: #ff6348; }
        .email-card.medium { --priority-color: #feca57; }
        .email-card.low { --priority-color: #48dbfb; }
        
        .email-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .email-subject {
            font-size: 1.3rem;
            font-weight: 700;
            color: white;
            flex: 1;
            min-width: 250px;
        }
        
        .priority-badge {
            background: var(--priority-color);
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .email-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
            opacity: 0.9;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .meta-item i {
            color: var(--priority-color);
            width: 16px;
        }
        
        .email-snippet {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            font-style: italic;
            line-height: 1.6;
            border-left: 3px solid var(--priority-color);
        }
        
        .draft-btn {
            background: linear-gradient(135deg, var(--priority-color), var(--priority-color));
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 30px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 15px;
        }
        
        .draft-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        
        .no-emails {
            text-align: center;
            padding: 60px 20px;
            opacity: 0.7;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid white;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .notification {
            position: fixed;
            top: 30px;
            right: 30px;
            background: linear-gradient(135deg, #00b894, #00cec9);
            color: white;
            padding: 20px 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1000;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        @media (max-width: 768px) {
            .container { padding: 20px 15px; }
            .header { padding: 25px 20px; }
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr; gap: 20px; }
            .create-drafts-btn { padding: 20px 40px; font-size: 1.1rem; }
            .email-header { flex-direction: column; align-items: stretch; }
            .email-meta { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-tachometer-alt"></i> Gmail Dashboard</h1>
            <div class="status-indicator" id="statusIndicator">
                <i class="fas fa-satellite-dish"></i> Gmail Connected - Showing REAL emails
            </div>
        </div>
        
        <div class="stats-grid" id="statsGrid">
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
                const response = await fetch('/api/emails');
                const data = await response.json();
                emailsData = data.all_emails || [];
                
                // Update stats
                document.getElementById('totalEmails').textContent = data.stats.total_unread;
                document.getElementById('directEmails').textContent = data.stats.direct_count;
                document.getElementById('highPriority').textContent = data.stats.high_priority_count;
                
                // Update status
                const statusEl = document.getElementById('statusIndicator');
                if (data.gmail_connected) {
                    statusEl.innerHTML = '<i class="fas fa-satellite-dish"></i> Gmail Connected - Showing REAL emails';
                    statusEl.style.background = 'linear-gradient(45deg, #00b894, #00cec9)';
                } else {
                    statusEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i> DEMO MODE - Configure API';
                    statusEl.style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a24)';
                }
                
                // Display emails
                displayEmails(emailsData);
                
            } catch (error) {
                console.error('Error loading emails:', error);
                document.getElementById('emailsList').innerHTML = 
                    '<div class="no-emails"><i class="fas fa-exclamation-circle"></i><h3>Error loading emails</h3><p>Please try refreshing the page</p></div>';
            }
        }
        
        function displayEmails(emails) {
            const emailsList = document.getElementById('emailsList');
            
            if (emails.length === 0) {
                emailsList.innerHTML = 
                    '<div class="no-emails"><i class="fas fa-inbox"></i><h3>No emails found</h3><p>Your inbox is clean!</p></div>';
                return;
            }
            
            emailsList.innerHTML = emails.map(email => `
                <div class="email-card ${email.priority}">
                    <div class="email-header">
                        <div class="email-subject">${email.subject}</div>
                        <div class="priority-badge">${email.priority.toUpperCase()}</div>
                    </div>
                    <div class="email-meta">
                        <div class="meta-item">
                            <i class="fas fa-user"></i>
                            <span>${email.from_email}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-calendar"></i>
                            <span>${email.date}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-clock"></i>
                            <span>${email.time}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-tag"></i>
                            <span>${email.email_type}</span>
                        </div>
                    </div>
                    <div class="email-snippet">${email.snippet}</div>
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
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email_id: emailId })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification('✅ Draft created successfully!', 'success');
                } else {
                    showNotification(`❌ Error: ${result.message}`, 'error');
                }
                
            } catch (error) {
                console.error('Error creating draft:', error);
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
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        email_ids: highPriorityEmails.map(e => e.id) 
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification(`✅ Created ${result.created_count} drafts successfully!`, 'success');
                } else {
                    showNotification(`❌ Error: ${result.message}`, 'error');
                }
                
            } catch (error) {
                console.error('Error creating bulk drafts:', error);
                showNotification('❌ Failed to create drafts', 'error');
            }
        }
        
        function refreshEmails() {
            document.getElementById('emailsList').innerHTML = 
                '<div class="loading"><div class="spinner"></div><p>Refreshing emails...</p></div>';
            loadEmails();
        }
        
        // Load emails on page load
        document.addEventListener('DOMContentLoaded', loadEmails);
        
        // Auto-refresh every 2 minutes
        setInterval(loadEmails, 120000);
    </script>
</body>
</html>'''

@app.route('/api/emails')
def api_emails():
    """API endpoint to get email data"""
    try:
        data = assistant.get_email_stats()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-draft', methods=['POST'])
def api_create_draft():
    """API endpoint to create a single draft"""
    try:
        data = request.get_json()
        email_id = data.get('email_id')
        
        if not email_id:
            return jsonify({'success': False, 'message': 'Email ID required'}), 400
        
        # Find the email
        emails = assistant.get_unread_emails()
        email = next((e for e in emails if e['id'] == email_id), None)
        
        if not email:
            return jsonify({'success': False, 'message': 'Email not found'}), 404
        
        # Create draft
        success, message = assistant.create_gmail_draft(email)
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/create-drafts-bulk', methods=['POST'])
def api_create_drafts_bulk():
    """API endpoint to create multiple drafts"""
    try:
        data = request.get_json()
        email_ids = data.get('email_ids', [])
        
        if not email_ids:
            return jsonify({'success': False, 'message': 'No email IDs provided'}), 400
        
        # Get emails
        emails = assistant.get_unread_emails()
        created_count = 0
        errors = []
        
        for email_id in email_ids:
            email = next((e for e in emails if e['id'] == email_id), None)
            if email:
                success, message = assistant.create_gmail_draft(email)
                if success:
                    created_count += 1
                else:
                    errors.append(f"Failed for {email['subject']}: {message}")
        
        return jsonify({
            'success': created_count > 0,
            'created_count': created_count,
            'total_requested': len(email_ids),
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/debug')
def debug():
    """Enhanced debug page with system information"""
    try:
        emails = assistant.get_unread_emails()
        stats = assistant.get_email_stats()
        
        debug_info = {
            'Gmail API Status': '✅ Connected' if assistant.gmail_connected else '❌ Not Connected',
            'OpenAI Status': '✅ Available' if assistant.openai_available else '❌ Not Available',
            'Total Emails': len(emails),
            'Gmail Available': GMAIL_AVAILABLE,
            'OpenAI Available': OPENAI_AVAILABLE,
            'Environment Variables': {
                'GMAIL_REFRESH_TOKEN': '✅ Set' if os.getenv('GMAIL_REFRESH_TOKEN') else '❌ Missing',
                'GMAIL_CLIENT_ID': '✅ Set' if os.getenv('GMAIL_CLIENT_ID') else '❌ Missing',
                'GMAIL_CLIENT_SECRET': '✅ Set' if os.getenv('GMAIL_CLIENT_SECRET') else '❌ Missing',
                'OPENAI_API_KEY': '✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'
            },
            'Stats': stats['stats'],
            'Sample Emails': emails[:3] if emails else []
        }
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Debug Info</title>
    <style>
        body {{ font-family: 'Courier New', monospace; background: #1a1a1a; color: #00ff00; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .section {{ background: #2a2a2a; padding: 20px; margin: 20px 0; border-radius: 10px; border: 1px solid #333; }}
        .success {{ color: #00ff00; }}
        .error {{ color: #ff4444; }}
        .warning {{ color: #ffaa00; }}
        pre {{ background: #1a1a1a; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        h1, h2 {{ color: #00ccff; }}
        .back-btn {{ 
            background: #00ccff; color: #1a1a1a; padding: 10px 20px; 
            text-decoration: none; border-radius: 5px; font-weight: bold; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Gmail Assistant Debug Console</h1>
        <a href="/dashboard" class="back-btn">← Back to Dashboard</a>
        
        <div class="section">
            <h2>System Status</h2>
            <pre>{json.dumps(debug_info, indent=2)}</pre>
        </div>
        
        <div class="section">
            <h2>Quick Links</h2>
            <p><a href="/api/emails" style="color: #00ccff;">📧 View Raw Email API</a></p>
            <p><a href="/" style="color: #00ccff;">🏠 Home Page</a></p>
            <p><a href="/dashboard" style="color: #00ccff;">📊 Dashboard</a></p>
        </div>
    </div>
</body>
</html>'''
        
    except Exception as e:
        return f'''<h1>Debug Error</h1><pre style="color: red;">{str(e)}</pre>'''

if __name__ == '__main__':
    print("🚀 Starting Enhanced Gmail Assistant...")
    print("🔍 Checking Gmail Environment Variables:")
    print(f"GMAIL_REFRESH_TOKEN exists: {bool(os.getenv('GMAIL_REFRESH_TOKEN'))}")
    print(f"GMAIL_CLIENT_ID exists: {bool(os.getenv('GMAIL_CLIENT_ID'))}")
    print(f"GMAIL_CLIENT_SECRET exists: {bool(os.getenv('GMAIL_CLIENT_SECRET'))}")
    print(f"OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
    app.run(debug=True)
