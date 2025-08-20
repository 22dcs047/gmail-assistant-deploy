from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import json
import os
import base64
import time
import re

# Import Gmail API libraries with error handling
try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API not available - running in demo mode")

# Import OpenAI with error handling
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not available - using basic classification")

# Import email libraries
try:
    from email.mime.text import MIMEText
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

app = Flask(__name__)

class SafeGmailAssistant:
    def __init__(self):
        self.user_email = '22dcs047@charusat.edu.in'
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        
        self.gmail_service = None
        self.gmail_connected = False
        self.openai_available = False
        
        # Initialize components safely
        self._init_openai()
        self._init_gmail()
        
        print(f"✅ Gmail Assistant initialized")
        print(f"📧 Gmail: {'Connected' if self.gmail_connected else 'Demo Mode'}")
        print(f"🧠 OpenAI: {'Available' if self.openai_available else 'Basic Rules'}")
    
    def _init_openai(self):
        """Safely initialize OpenAI"""
        if not OPENAI_AVAILABLE:
            return
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                openai.api_key = api_key
                self.openai_available = True
                print("🧠 OpenAI initialized")
            except Exception as e:
                print(f"⚠️ OpenAI init failed: {e}")
    
    def _init_gmail(self):
        """Safely initialize Gmail API"""
        if not GMAIL_AVAILABLE:
            return
        
        try:
            refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
            client_id = os.getenv('GMAIL_CLIENT_ID')
            client_secret = os.getenv('GMAIL_CLIENT_SECRET')
            
            if not all([refresh_token, client_id, client_secret]):
                print("⚠️ Gmail credentials missing")
                return
            
            token_data = {
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'scopes': self.scopes
            }
            
            creds = Credentials.from_authorized_user_info(token_data, self.scopes)
            
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            if creds and creds.valid:
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                self.gmail_connected = True
                print(f"✅ Gmail connected: {profile.get('emailAddress')}")
            
        except Exception as e:
            print(f"⚠️ Gmail init failed: {e}")
    
    def classify_email(self, subject, body, sender):
        """Classify email with fallback logic"""
        try:
            if self.openai_available:
                return self._ai_classify(subject, body, sender)
            else:
                return self._rule_classify(subject, body, sender)
        except Exception as e:
            print(f"Classification error: {e}")
            return self._safe_classify(subject, sender)
    
    def _ai_classify(self, subject, body, sender):
        """AI-powered classification"""
        try:
            prompt = f"""Classify this email strictly:

Subject: {subject}
From: {sender}
Content: {body[:300]}

Rules:
- CRITICAL: Life-threatening, immediate security breaches
- HIGH: Deadlines, registrations, meetings, interviews
- MEDIUM: Announcements, course updates, reminders
- LOW: Promotional, automated, newsletters

If sender has "noreply" or promotional indicators, classify as LOW unless security-related.

Return JSON: {{"priority": "high/medium/low/critical", "type": "academic/promotional/security/general", "reason": "explanation"}}"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            result['ai_classified'] = True
            return result
            
        except Exception as e:
            print(f"AI classification error: {e}")
            return self._rule_classify(subject, body, sender)
    
    def _rule_classify(self, subject, body, sender):
        """Rule-based classification"""
        subject_lower = subject.lower()
        sender_lower = sender.lower()
        
        # Check for promotional first
        promotional_indicators = ['noreply', 'no-reply', 'unsubscribe', 'newsletter', 'marketing']
        is_promotional = any(indicator in sender_lower for indicator in promotional_indicators)
        
        if is_promotional:
            # Check if it's a security exception
            if any(word in subject_lower for word in ['security', 'alert', 'breach']):
                return {
                    'priority': 'high',
                    'type': 'security',
                    'reason': 'Security alert from automated system',
                    'ai_classified': False
                }
            return {
                'priority': 'low',
                'type': 'promotional',
                'reason': 'Promotional/automated email',
                'ai_classified': False
            }
        
        # High priority keywords
        high_keywords = ['deadline', 'urgent', 'registration', 'interview', 'meeting']
        if any(keyword in subject_lower for keyword in high_keywords):
            return {
                'priority': 'high',
                'type': 'academic' if '@charusat.edu.in' in sender else 'general',
                'reason': 'Contains high priority keywords',
                'ai_classified': False
            }
        
        # Medium priority for academic emails
        if '@charusat.edu.in' in sender or 'academic' in subject_lower:
            return {
                'priority': 'medium',
                'type': 'academic',
                'reason': 'Academic institution email',
                'ai_classified': False
            }
        
        # Default low priority
        return {
            'priority': 'low',
            'type': 'general',
            'reason': 'Default classification',
            'ai_classified': False
        }
    
    def _safe_classify(self, subject, sender):
        """Safe fallback classification"""
        return {
            'priority': 'medium',
            'type': 'general',
            'reason': 'Safe fallback classification',
            'ai_classified': False
        }
    
    def create_smart_summary(self, subject, snippet, body):
        """Create intelligent summary"""
        try:
            # Use snippet first, then body
            text = snippet if snippet else body
            if not text:
                return "No preview available"
            
            # Clean text
            text = re.sub(r'<[^>]+>', '', text)  # Remove HTML
            text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
            
            # Remove common footers
            footers = ['Thanks and Regards', 'Best regards', 'You received this message']
            for footer in footers:
                if footer in text:
                    text = text.split(footer)[0].strip()
            
            subject_lower = subject.lower()
            
            # Create contextual summaries
            if 'deadline' in subject_lower:
                return f"⏰ Registration deadline notice - {text[:60]}..."
            elif 'meeting' in subject_lower:
                return f"📅 Meeting invitation - {text[:60]}..."
            elif 'security' in subject_lower:
                return f"🔒 Security notification - {text[:60]}..."
            elif any(word in subject_lower for word in ['opportunity', 'job']):
                return f"💼 Career opportunity - {text[:60]}..."
            else:
                # Extract meaningful sentence
                sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
                if sentences:
                    return sentences[0][:80] + "..." if len(sentences[0]) > 80 else sentences[0]
                return text[:80] + "..." if len(text) > 80 else text
                
        except Exception as e:
            print(f"Summary error: {e}")
            return snippet[:80] + "..." if snippet else "Preview unavailable"
    
    def get_emails(self):
        """Get emails safely"""
        if not self.gmail_connected:
            return self.get_demo_emails()
        
        try:
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y/%m/%d')
            query = f'is:unread after:{three_days_ago} -from:me'
            
            result = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=20
            ).execute()
            
            messages = result.get('messages', [])
            emails = []
            
            for message in messages[:15]:  # Limit to 15 for safety
                try:
                    msg = self.gmail_service.users().messages().get(
                        userId='me', id=message['id'], format='full'
                    ).execute()
                    
                    headers = msg['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    to_field = next((h['value'] for h in headers if h['name'] == 'To'), '')
                    
                    snippet = msg.get('snippet', '')
                    body = self._extract_body(msg['payload'])
                    
                    # Parse date
                    try:
                        email_date = datetime.fromtimestamp(int(msg['internalDate']) / 1000)
                        date_str = email_date.strftime('%Y-%m-%d')
                        time_str = email_date.strftime('%H:%M')
                    except:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                        time_str = datetime.now().strftime('%H:%M')
                    
                    # Classify and summarize
                    classification = self.classify_email(subject, body, from_email)
                    summary = self.create_smart_summary(subject, snippet, body)
                    
                    emails.append({
                        'id': message['id'],
                        'subject': subject,
                        'from_email': from_email,
                        'to_field': to_field,
                        'snippet': snippet,
                        'display_snippet': summary,
                        'body': body,
                        'date': date_str,
                        'time': time_str,
                        'priority': classification['priority'],
                        'email_type': classification['type'],
                        'urgency_reason': classification['reason'],
                        'ai_classified': classification['ai_classified']
                    })
                    
                except Exception as e:
                    print(f"Error processing email: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return self.get_demo_emails()
    
    def _extract_body(self, payload):
        """Extract email body safely"""
        try:
            body = ""
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
            elif payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
            return body.strip()
        except Exception as e:
            print(f"Body extraction error: {e}")
            return ""
    
    def get_demo_emails(self):
        """Demo emails for testing"""
        now = datetime.now()
        return [
            {
                'id': 'demo_1',
                'subject': 'July 2025 Exam Registration Deadline - Aug 22, 2025 - 5:00 PM [12 week courses] – Last 3 days to Register!',
                'from_email': 'NPTEL',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'Registration deadline for July 2025 exam approaching',
                'display_snippet': '⏰ Registration deadline notice - Last 3 days to register for July 2025 Exam',
                'body': 'This is a reminder about the exam registration deadline.',
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'priority': 'high',
                'email_type': 'academic',
                'urgency_reason': 'Contains deadline keywords',
                'ai_classified': False
            },
            {
                'id': 'demo_2',
                'subject': 'Course Announcement - New Materials Available',
                'from_email': 'professor@charusat.edu.in',
                'to_field': '22dcs047@charusat.edu.in',
                'snippet': 'New course materials have been uploaded',
                'display_snippet': 'New course materials have been uploaded to the portal',
                'body': 'Dear students, new course materials are now available.',
                'date': now.strftime('%Y-%m-%d'),
                'time': (now - timedelta(hours=2)).strftime('%H:%M'),
                'priority': 'medium',
                'email_type': 'academic',
                'urgency_reason': 'Academic institution email',
                'ai_classified': False
            }
        ]
    
    def get_stats(self):
        """Get email statistics"""
        emails = self.get_emails()
        
        # Count direct emails
        direct_emails = [e for e in emails if self.user_email in e.get('to_field', '')]
        high_priority = [e for e in emails if e['priority'] in ['high', 'critical']]
        
        return {
            'all_emails': emails,
            'direct_emails': direct_emails,
            'stats': {
                'total_unread': len(emails),
                'direct_count': len(direct_emails),
                'high_priority_count': len(high_priority),
                'medium_priority_count': len([e for e in emails if e['priority'] == 'medium']),
                'low_priority_count': len([e for e in emails if e['priority'] == 'low'])
            },
            'gmail_connected': self.gmail_connected,
            'openai_connected': self.openai_available,
            'last_updated': datetime.now().isoformat()
        }
    
    def create_draft(self, email_data):
        """Create Gmail draft safely"""
        if not self.gmail_connected or not EMAIL_AVAILABLE:
            return False, "Draft creation not available"
        
        try:
            reply_body = f"""Thank you for your email regarding "{email_data['subject']}".

I have received your message and will respond appropriately based on the priority level.

Best regards,
Jai Mehtani
Computer Science Student & Developer
Charusat University
📧 22dcs047@charusat.edu.in

🤖 This is an automated acknowledgment."""
            
            message = MIMEText(reply_body)
            message['to'] = email_data['from_email']
            message['subject'] = f"Re: {email_data['subject']}"
            
            draft = {
                'message': {
                    'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
                }
            }
            
            created_draft = self.gmail_service.users().drafts().create(
                userId='me', body=draft
            ).execute()
            
            return True, f"Draft created successfully"
            
        except Exception as e:
            print(f"Draft creation error: {e}")
            return False, f"Error creating draft: {str(e)}"

# Initialize assistant
assistant = SafeGmailAssistant()

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
            font-family: 'Inter', 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%); 
            min-height: 100vh; 
            color: #ffffff; 
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 40px 20px; 
        }}
        .hero {{ 
            background: rgba(255,255,255,0.95); 
            padding: 60px 40px; 
            border-radius: 20px; 
            text-align: center; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            color: #1f2937;
            margin-bottom: 40px;
        }}
        .hero h1 {{ 
            font-size: 3.5rem; 
            margin-bottom: 20px; 
            font-weight: 800; 
            color: #1f2937;
        }}
        .hero p {{ 
            font-size: 1.3rem; 
            margin-bottom: 30px; 
            color: #4b5563;
            line-height: 1.6;
        }}
        .btn {{ 
            background: linear-gradient(135deg, #3b82f6, #1e40af);
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 10px; 
            font-size: 1.1rem; 
            font-weight: 600; 
            text-decoration: none; 
            display: inline-block; 
            margin: 10px 15px; 
            transition: all 0.3s ease; 
            box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        }}
        .btn:hover {{ 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(59,130,246,0.4); 
        }}
        .btn.primary {{
            background: linear-gradient(135deg, #059669, #047857);
            box-shadow: 0 4px 15px rgba(5,150,105,0.3);
        }}
        .status-badge {{ 
            background: linear-gradient(135deg, #{'059669, #047857' if assistant.gmail_connected else 'dc2626, #b91c1c'}); 
            color: white; 
            padding: 12px 24px; 
            border-radius: 25px; 
            font-weight: 600; 
            margin: 10px; 
            display: inline-block; 
            box-shadow: 0 4px 15px rgba({'5,150,105' if assistant.gmail_connected else '220,38,38'},0.3);
        }}
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }}
        .feature-card {{
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            color: #1f2937;
            transition: all 0.3s ease;
        }}
        .feature-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 20px;
            color: #3b82f6;
        }}
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .status-item {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .status-item strong {{
            display: block;
            font-size: 1.2rem;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <div class="status-badge">
                <i class="fas fa-{'satellite-dish' if assistant.gmail_connected else 'exclamation-triangle'}"></i> 
                {status.upper()} 
            </div>
            <h1><i class="fas fa-brain"></i> AI Gmail Assistant</h1>
            <p>{'Intelligent email management with real Gmail integration and smart priority detection' if assistant.gmail_connected else 'Demo mode - All features working with sample data'}</p>
            
            <div class="status-grid">
                <div class="status-item">
                    Gmail Status
                    <strong>{'✅ CONNECTED' if assistant.gmail_connected else '📋 DEMO MODE'}</strong>
                </div>
                <div class="status-item">
                    AI Classification
                    <strong>{'✅ ACTIVE' if assistant.openai_available else '📋 RULE-BASED'}</strong>
                </div>
                <div class="status-item">
                    Draft Creation
                    <strong>{'✅ ENABLED' if assistant.gmail_connected else '📋 DEMO'}</strong>
                </div>
            </div>
            
            <a href="/dashboard" class="btn primary"><i class="fas fa-tachometer-alt"></i> Open Dashboard</a>
            <a href="/debug" class="btn"><i class="fas fa-cog"></i> System Info</a>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-envelope-open-text"></i></div>
                <h3>Smart Email Classification</h3>
                <p>Advanced priority detection that correctly identifies important emails while filtering out promotional content with intelligent summary generation.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-robot"></i></div>
                <h3>AI-Powered Features</h3>
                <p>Optional OpenAI integration for enhanced classification, with robust rule-based fallbacks ensuring reliable operation.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-magic"></i></div>
                <h3>Draft Generation</h3>
                <p>Automatic draft creation for high-priority emails with professional formatting and contextual responses.</p>
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
    <title>Gmail Assistant - Dashboard</title>
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
        
        .header {
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            color: #1f2937;
            margin-bottom: 10px;
        }
        
        .status-indicator {
            background: linear-gradient(135deg, #059669, #047857);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            font-size: 0.9rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-left: 4px solid var(--accent-color);
        }
        
        .stat-card:hover { 
            transform: translateY(-5px); 
            box-shadow: 0 15px 35px rgba(0,0,0,0.15); 
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 10px;
            color: var(--accent-color);
        }
        
        .stat-label { 
            font-size: 1.1rem; 
            font-weight: 600; 
            color: #4b5563;
        }
        
        .stat-card.total { --accent-color: #3b82f6; }
        .stat-card.direct { --accent-color: #8b5cf6; }
        .stat-card.high { --accent-color: #ef4444; }
        
        .main-action {
            text-align: center;
            margin: 40px 0;
        }
        
        .create-drafts-btn {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            padding: 18px 40px;
            border: none;
            border-radius: 12px;
            font-size: 1.2rem;
            font-weight: 700;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(239,68,68,0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            cursor: pointer;
        }
        
        .create-drafts-btn:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 15px 35px rgba(239,68,68,0.4); 
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #3b82f6, #1e40af);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-left: 15px;
        }
        
        .emails-section {
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #1f2937;
        }
        
        .email-card {
            background: #ffffff;
            margin-bottom: 20px;
            padding: 25px;
            border-radius: 12px;
            border-left: 4px solid var(--priority-color);
            transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
            cursor: pointer;
        }
        
        .email-card:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .email-card.critical { --priority-color: #dc2626; }
        .email-card.high { --priority-color: #ea580c; }
        .email-card.medium { --priority-color: #ca8a04; }
        .email-card.low { --priority-color: #059669; }
        
        .email-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .email-subject {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1f2937;
            flex: 1;
            min-width: 200px;
        }
        
        .priority-badge {
            background: var(--priority-color);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .email-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
            color: #6b7280;
            font-size: 0.9rem;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .meta-item i {
            color: var(--priority-color);
            width: 14px;
        }
        
        .email-snippet {
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            color: #4b5563;
            line-height: 1.5;
            border-left: 3px solid var(--priority-color);
        }
        
        .draft-btn {
            background: linear-gradient(135deg, var(--priority-color), var(--priority-color));
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        .draft-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #6b7280;
        }
        
        .spinner {
            border: 3px solid #e5e7eb;
            border-radius: 50%;
            border-top: 3px solid #3b82f6;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1000;
            font-weight: 600;
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
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-tachometer-alt"></i> Gmail Dashboard</h1>
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
                    statusEl.innerHTML = '<i class="fas fa-satellite-dish"></i> Gmail Connected - Live Data';
                    statusEl.style.background = 'linear-gradient(135deg, #059669, #047857)';
                } else {
                    statusEl.innerHTML = '<i class="fas fa-chart-line"></i> Demo Mode - Sample Data';
                    statusEl.style.background = 'linear-gradient(135deg, #3b82f6, #1e40af)';
                }
                
                // Display emails
                displayEmails(emailsData);
                
            } catch (error) {
                console.error('Error loading emails:', error);
                document.getElementById('emailsList').innerHTML = 
                    '<div style="text-align: center; padding: 40px; color: #6b7280;"><i class="fas fa-exclamation-circle"></i><h3>Error loading emails</h3><p>Please refresh to try again</p></div>';
            }
        }
        
        function displayEmails(emails) {
            const emailsList = document.getElementById('emailsList');
            
            if (emails.length === 0) {
                emailsList.innerHTML = 
                    '<div style="text-align: center; padding: 40px; color: #6b7280;"><i class="fas fa-inbox"></i><h3>No unread emails</h3><p>Your inbox is clean!</p></div>';
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
                    <div class="email-snippet">${email.display_snippet}</div>
                    ${email.urgency_reason ? `<div style="background: #fef3c7; padding: 8px 12px; border-radius: 6px; margin: 10px 0; font-size: 0.85rem; color: #92400e;"><strong>Why ${email.priority}:</strong> ${email.urgency_reason}</div>` : ''}
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
        
        // Auto-refresh every 3 minutes
        setInterval(loadEmails, 180000);
    </script>
</body>
</html>'''

@app.route('/api/emails')
def api_emails():
    """API endpoint to get email data"""
    try:
        data = assistant.get_stats()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e), 'gmail_connected': False, 'stats': {'total_unread': 0, 'direct_count': 0, 'high_priority_count': 0}}), 200

@app.route('/api/create-draft', methods=['POST'])
def api_create_draft():
    """API endpoint to create a single draft"""
    try:
        data = request.get_json()
        email_id = data.get('email_id')
        
        if not email_id:
            return jsonify({'success': False, 'message': 'Email ID required'}), 400
        
        # Find the email
        emails = assistant.get_emails()
        email = next((e for e in emails if e['id'] == email_id), None)
        
        if not email:
            return jsonify({'success': False, 'message': 'Email not found'}), 404
        
        # Create draft
        success, message = assistant.create_draft(email)
        
        return jsonify({'success': success, 'message': message})
        
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
        
        emails = assistant.get_emails()
        created_count = 0
        errors = []
        
        for email_id in email_ids:
            email = next((e for e in emails if e['id'] == email_id), None)
            if email:
                success, message = assistant.create_draft(email)
                if success:
                    created_count += 1
                else:
                    errors.append(f"Failed: {message}")
        
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
    """Debug information"""
    try:
        emails = assistant.get_emails()
        stats = assistant.get_stats()
        
        debug_info = {
            'Gmail Connected': assistant.gmail_connected,
            'OpenAI Available': assistant.openai_available,
            'Total Emails': len(emails),
            'Environment Variables': {
                'GMAIL_REFRESH_TOKEN': bool(os.getenv('GMAIL_REFRESH_TOKEN')),
                'GMAIL_CLIENT_ID': bool(os.getenv('GMAIL_CLIENT_ID')),
                'GMAIL_CLIENT_SECRET': bool(os.getenv('GMAIL_CLIENT_SECRET')),
                'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY'))
            },
            'Stats': stats['stats'],
            'Sample Emails': [
                {
                    'subject': email.get('subject', ''),
                    'priority': email.get('priority', ''),
                    'summary': email.get('display_snippet', ''),
                    'reason': email.get('urgency_reason', '')
                } for email in emails[:3]
            ]
        }
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - System Debug</title>
    <style>
        body {{ font-family: monospace; background: #0f172a; color: #10b981; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .section {{ background: #1e293b; padding: 20px; margin: 15px 0; border-radius: 8px; border: 1px solid #334155; }}
        .success {{ color: #10b981; }}
        .error {{ color: #ef4444; }}
        .warning {{ color: #f59e0b; }}
        pre {{ background: #0f172a; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid #334155; }}
        h1, h2 {{ color: #06b6d4; }}
        .back-btn {{ 
            background: #06b6d4; color: #0f172a; padding: 10px 20px; 
            text-decoration: none; border-radius: 5px; font-weight: bold; 
            display: inline-block; margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Gmail Assistant Debug Console</h1>
        <a href="/dashboard" class="back-btn">← Back to Dashboard</a>
        
        <div class="section">
            <h2>🔍 System Status</h2>
            <p>Gmail: <span class="{'success' if assistant.gmail_connected else 'warning'}">{'✅ Connected' if assistant.gmail_connected else '📋 Demo Mode'}</span></p>
            <p>AI: <span class="{'success' if assistant.openai_available else 'warning'}">{'✅ Active' if assistant.openai_available else '📋 Rule-Based'}</span></p>
            <p>Emails: <span class="success">{len(emails)} loaded</span></p>
        </div>
        
        <div class="section">
            <h2>📊 Debug Information</h2>
            <pre>{json.dumps(debug_info, indent=2)}</pre>
        </div>
        
        <div class="section">
            <h2>🔗 Quick Links</h2>
            <p><a href="/api/emails" style="color: #06b6d4;">📧 Raw API Response</a></p>
            <p><a href="/" style="color: #06b6d4;">🏠 Home</a></p>
        </div>
    </div>
</body>
</html>'''
        
    except Exception as e:
        return f'<h1>Debug Error: {str(e)}</h1>'

if __name__ == '__main__':
    app.run(debug=True)
