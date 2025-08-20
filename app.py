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
        
        .refresh-btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(59,130,246,0.3);
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
        
        .no-emails {
            text-align: center;
            padding: 40px 20px;
            color: #6b7280;
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
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.error {
            background: #ef4444;
        }
        
        /* Email Detail Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 0;
            border-radius: 15px;
            width: 90%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 25px 50px rgba(0,0,0,0.25);
        }
        
        .modal-header {
            background: linear-gradient(135deg, #3b82f6, #1e40af);
            color: white;
            padding: 25px 30px;
            border-radius: 15px 15px 0 0;
            position: relative;
        }
        
        .modal-header h2 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        .close {
            position: absolute;
            right: 20px;
            top: 20px;
            color: white;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.3s;
        }
        
        .close:hover {
            background-color: rgba(255,255,255,0.2);
        }
        
        .modal-body {
            padding: 30px;
        }
        
        .email-full-content {
            background: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #3b82f6;
            white-space: pre-wrap;
            line-height: 1.6;
            color: #374151;
        }
        
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header { padding: 20px; }
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr; gap: 15px; }
            .create-drafts-btn { padding: 15px 30px; font-size: 1rem; }
            .email-header { flex-direction: column; align-items: stretch; }
            .email-meta { grid-template-columns: 1fr; }
            .modal-content { width: 95%; margin: 2% auto; }
            .modal-body { padding: 20px; }
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
    
    <!-- Email Detail Modal -->
    <div id="emailModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Email Details</h2>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div id="modalEmailMeta"></div>
                <div id="modalEmailContent" class="email-full-content"></div>
                <div id="modalEmailActions"></div>
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
                    statusEl.style.background = 'linear-gradient(135deg, #059669, #047857)';
                } else {
                    statusEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i> DEMO MODE - Configure API';
                    statusEl.style.background = 'linear-gradient(135deg, #dc2626, #b91c1c)';
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
                    '<div class="no-emails"><i class="fas fa-inbox"></i><h3>No unread emails</h3><p>Your inbox is clean!</p></div>';
                return;
            }
            
            emailsList.innerHTML = emails.map(email => `
                <div class="email-card ${email.priority}" onclick="openEmailModal('${email.id}')">
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
                    <div class="email-snippet">${email.display_snippet || email.snippet}</div>
                    ${(email.priority === 'high' || email.priority === 'critical') ? 
                        `<button class="draft-btn" onclick="event.stopPropagation(); createDraft('${email.id}')">
                            <i class="fas fa-pen"></i> Create Draft Reply
                        </button>` : ''
                    }
                </div>
            `).join('');
        }
        
        function openEmailModal(emailId) {
            const email = emailsData.find(e => e.id === emailId);
            if (!email) return;
            
            document.getElementById('modalTitle').textContent = email.subject;
            document.getElementById('modalEmailMeta').innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div><strong>From:</strong> ${email.from_email}</div>
                    <div><strong>Date:</strong> ${email.date} ${email.time}</div>
                    <div><strong>Priority:</strong> <span style="color: var(--priority-color);">${email.priority.toUpperCase()}</span></div>
                    <div><strong>Type:</strong> ${email.email_type}</div>
                </div>
                ${email.urgency_reason ? `<div style="background: #fef3c7; padding: 10px; border-radius: 8px; margin-bottom: 15px;"><strong>Classification reason:</strong> ${email.urgency_reason}</div>` : ''}
            `;
            document.getElementById('modalEmailContent').textContent = email.body || email.snippet;
            document.getElementById('modalEmailActions').innerHTML = 
                (email.priority === 'high' || email.priority === 'critical') ? 
                `<button class="draft-btn" onclick="createDraft('${email.id}')">
                    <i class="fas fa-pen"></i> Create Draft Reply
                </button>` : '';
            
            document.getElementById('emailModal').style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('emailModal').style.display = 'none';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('emailModal');
            if (event.target == modal) {
                closeModal();
            }
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
            'Sample Emails': emails[:3] if emails else [],
            'Classification Examples': [
                {
                    'subject': email.get('subject', ''),
                    'sender': email.get('from_email', ''),
                    'priority': email.get('priority', ''),
                    'reason': email.get('urgency_reason', ''),
                    'summary': email.get('display_snippet', '')
                } for email in emails[:5]
            ]
        }
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Gmail Assistant - Debug Info</title>
    <style>
        body {{ font-family: 'Courier New', monospace; background: #0f172a; color: #10b981; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .section {{ background: #1e293b; padding: 25px; margin: 20px 0; border-radius: 12px; border: 1px solid #334155; }}
        .success {{ color: #10b981; }}
        .error {{ color: #ef4444; }}
        .warning {{ color: #f59e0b; }}
        pre {{ background: #0f172a; padding: 20px; border-radius: 8px; overflow-x: auto; border: 1px solid #334155; }}
        h1, h2 {{ color: #06b6d4; margin-bottom: 15px; }}
        .back-btn {{ 
            background: #06b6d4; color: #0f172a; padding: 12px 24px; 
            text-decoration: none; border-radius: 8px; font-weight: bold; 
            display: inline-block; margin-bottom: 20px;
        }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .stat-item {{ background: #1e293b; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Gmail Assistant Debug Console</h1>
        <a href="/dashboard" class="back-btn">← Back to Dashboard</a>
        
        <div class="section">
            <h2>🔍 System Status</h2>
            <div class="stats">
                <div class="stat-item">
                    <strong>Gmail Connection:</strong><br>
                    <span class="{'success' if assistant.gmail_connected else 'error'}">
                        {'✅ CONNECTED' if assistant.gmail_connected else '❌ DISCONNECTED'}
                    </span>
                </div>
                <div class="stat-item">
                    <strong>AI Classification:</strong><br>
                    <span class="{'success' if assistant.openai_available else 'warning'}">
                        {'✅ ACTIVE' if assistant.openai_available else '⚠️ BASIC RULES'}
                    </span>
                </div>
                <div class="stat-item">
                    <strong>Email Count:</strong><br>
                    <span class="success">{len(emails)} emails</span>
                </div>
                <div class="stat-item">
                    <strong>High Priority:</strong><br>
                    <span class="error">{stats['stats']['high_priority_count']} emails</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Detailed Information</h2>
            <pre>{json.dumps(debug_info, indent=2)}</pre>
        </div>
        
        <div class="section">
            <h2>🔗 Quick Actions</h2>
            <p><a href="/api/emails" style="color: #06b6d4;">📧 View Raw Email API Response</a></p>
            <p><a href="/" style="color: #06b6d4;">🏠 Return to Home</a></p>
            <p><a href="/dashboard" style="color: #06b6d4;">📊 Open Dashboard</a></p>
        </div>
    </div>
</body>
</html>'''
        
    except Exception as e:
        return f'''<h1 style="color: #ef4444;">Debug Error</h1><pre style="color: #ef4444;">{str(e)}</pre>'''

if __name__ == '__main__':
    print("🚀 Starting FIXED Gmail Assistant...")
    print("🔍 Environment Check:")
    print(f"GMAIL_REFRESH_TOKEN: {bool(os.getenv('GMAIL_REFRESH_TOKEN'))}")
    print(f"GMAIL_CLIENT_ID: {bool(os.getenv('GMAIL_CLIENT_ID'))}")
    print(f"GMAIL_CLIENT_SECRET: {bool(os.getenv('GMAIL_CLIENT_SECRET'))}")
    print(f"OPENAI_API_KEY: {bool(os.getenv('OPENAI_API_KEY'))}")
    app.run(debug=True)# Gmail Assistant - WORKING VERSION with Fixed Summary
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import json
import os
import base64
from email.mime.text import MIMEText
import time
import re

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
        """Enhanced AI classification with stricter priority rules"""
        if not self.openai_available:
            return self._classify_email_strict(subject, body, sender)
        
        try:
            prompt = f"""Analyze this email and classify it VERY STRICTLY:

Subject: {subject}
From: {sender}
Content: {body[:500]}...

STRICT PRIORITY RULES:
- CRITICAL: Only life-threatening emergencies, immediate legal deadlines (today), security breaches
- HIGH: Academic deadlines, registration deadlines, meeting invitations, interview calls, urgent work matters
- MEDIUM: Course announcements, academic updates, general reminders, institutional emails
- LOW: Promotional emails, newsletters, automated notifications, marketing content

IMPORTANT: If sender contains "noreply", "no-reply", or has promotional content, it should be LOW priority unless it's a critical security alert.

Provide a JSON response with:
1. priority: "critical", "high", "medium", or "low"
2. email_type: "academic", "security", "personal", "promotional", "work", or "general"
3. urgency_reason: specific explanation for the priority level

Format as valid JSON only."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            result['ai_classified'] = True
            return result
            
        except Exception as e:
            print(f"❌ AI classification error: {e}")
            return self._classify_email_strict(subject, body, sender)
    
    def _classify_email_strict(self, subject, body, sender):
        """STRICT rule-based email classification to prevent over-classification"""
        subject_lower = subject.lower()
        body_lower = body.lower()
        sender_lower = sender.lower()
        
        # First check if it's promotional/automated
        promotional_indicators = [
            'noreply', 'no-reply', 'donotreply', 'unsubscribe', 'marketing',
            'newsletter', 'promotional', 'offer', 'deal', 'sale', 'discount',
            'subscribe', 'automated', 'system@', 'support@', 'hello@'
        ]
        
        is_promotional = any(indicator in sender_lower or indicator in subject_lower for indicator in promotional_indicators)
        
        # Security alerts are exception - can be high even if from automated systems
        security_keywords = ['security alert', 'login attempt', 'password reset', 'account breach', 'suspicious activity']
        is_security = any(keyword in subject_lower or keyword in body_lower for keyword in security_keywords)
        
        # If promotional and not security, automatically low priority
        if is_promotional and not is_security:
            return {
                'priority': 'low',
                'email_type': 'promotional',
                'urgency_reason': 'Promotional/automated email',
                'ai_classified': False
            }
        
        # Critical keywords (very strict)
        critical_keywords = ['emergency', 'urgent medical', 'life threatening', 'immediate danger', 'security breach']
        
        # High priority keywords (strict)
        high_keywords = [
            'deadline', 'due today', 'due tomorrow', 'registration deadline', 'last day to',
            'meeting invitation', 'interview', 'exam registration', 'assignment due',
            'project deadline', 'submission deadline'
        ]
        
        # Medium priority keywords
        medium_keywords = [
            'announcement', 'course update', 'lecture', 'workshop', 'seminar',
            'academic calendar', 'schedule change', 'reminder'
        ]
        
        priority = 'low'
        urgency_reason = 'Default low priority'
        
        # Check for critical priorities (very rare)
        if any(keyword in subject_lower or keyword in body_lower for keyword in critical_keywords):
            priority = 'critical'
            urgency_reason = 'Contains critical emergency keywords'
        # Check for high priorities (strict matching)
        elif any(keyword in subject_lower for keyword in high_keywords):
            priority = 'high'
            urgency_reason = 'Contains deadline/important keywords in subject'
        elif 'deadline' in subject_lower and not is_promotional:
            priority = 'high'
            urgency_reason = 'Subject contains deadline'
        # Medium priority for academic content
        elif any(keyword in subject_lower or keyword in body_lower for keyword in medium_keywords):
            priority = 'medium'
            urgency_reason = 'Academic/institutional content'
        elif '@charusat.edu.in' in sender and not is_promotional:
            priority = 'medium'
            urgency_reason = 'Email from academic institution'
        
        # Determine email type
        email_type = 'general'
        if is_promotional:
            email_type = 'promotional'
        elif '@charusat.edu.in' in sender or 'professor' in sender_lower or 'academic' in subject_lower:
            email_type = 'academic'
        elif is_security:
            email_type = 'security'
        
        return {
            'priority': priority,
            'email_type': email_type,
            'urgency_reason': urgency_reason,
            'ai_classified': False
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
                    
                    # STRICT classification
                    classification = self.classify_email_with_ai(subject, body, from_email)
                    
                    # Create better snippet for display
                    display_snippet = self._create_smart_summary(subject, snippet, body)
                    
                    emails.append({
                        'id': message['id'],
                        'subject': subject,
                        'from_email': from_email,
                        'to_field': to_field,
                        'snippet': snippet,
                        'display_snippet': display_snippet,
                        'body': body,
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
    
    def _create_smart_summary(self, subject, snippet, body):
        """Create intelligent 1-2 line summary for dashboard"""
        try:
            # Use snippet first (Gmail's summary), then body
            text = snippet if snippet else body
            if not text:
                return "No preview available"
            
            # Clean text
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Remove common footers
            footers = ['Thanks and Regards', 'Best regards', 'You received this message', 'To unsubscribe']
            for footer in footers:
                if footer in text:
                    text = text.split(footer)[0].strip()
            
            subject_lower = subject.lower()
            
            # Create contextual summaries based on email type
            if 'deadline' in subject_lower:
                return f"⏰ Registration deadline notice - {text[:60]}..."
            elif 'meeting' in subject_lower or 'invitation' in subject_lower:
                return f"📅 Meeting invitation - {text[:60]}..."
            elif 'security' in subject_lower or 'alert' in subject_lower:
                return f"🔒 Security notification - {text[:60]}..."
            elif any(word in subject_lower for word in ['opportunity', 'job', 'internship']):
                return f"💼 Career opportunity - {text[:60]}..."
            else:
                # General summary - take meaningful content
                sentences = text.split('.')
                for sentence in sentences:
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 15 and not clean_sentence.startswith('http'):
                        return clean_sentence[:80] + "..." if len(clean_sentence) > 80 else clean_sentence
                
                # Fallback
                return text[:80] + "..." if len(text) > 80 else text
        except Exception as e:
            print(f"Error creating summary: {e}")
            return snippet[:80] + "..." if snippet and len(snippet) > 80 else snippet or "Preview unavailable"
    
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
                'display_snippet': '⚙️ System configuration required - Set up environment variables to enable real Gmail connection.',
                'body': 'This is a demo email. Set your environment variables to connect real Gmail.',
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'priority': 'high',
                'email_type': 'system',
                'ai_classified': False,
                'urgency_reason': 'System configuration required'
            }
        ]
    
    def get_email_stats(self):
        """Get email statistics with better direct email detection"""
        emails = self.get_unread_emails()
        
        # Better direct email detection
        direct = []
        for email in emails:
            to_field = email.get('to_field', '').lower()
            # Check if user email is directly in To field (not CC/BCC)
            if '22dcs047@charusat.edu.in' in to_field:
                direct.append(email)
        
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
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%); 
            min-height: 100vh; 
            color: #ffffff; 
            overflow-x: hidden;
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
        .btn.primary:hover {{
            box-shadow: 0 8px 25px rgba(5,150,105,0.4);
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
        .feature-card h3 {{
            font-size: 1.4rem;
            margin-bottom: 15px;
            font-weight: 700;
            color: #1f2937;
        }}
        .feature-card p {{
            color: #4b5563;
            line-height: 1.6;
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
            backdrop-filter: blur(10px);
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
            <p>{'Intelligent email management with real Gmail integration and smart priority detection' if assistant.gmail_connected else 'Demo mode - Configure environment variables for real Gmail connection'}</p>
            
            <div class="status-grid">
                <div class="status-item">
                    Gmail Status
                    <strong>{'✅ CONNECTED' if assistant.gmail_connected else '❌ DEMO MODE'}</strong>
                </div>
                <div class="status-item">
                    AI Classification
                    <strong>{'✅ ACTIVE' if assistant.openai_available else '❌ BASIC RULES'}</strong>
                </div>
                <div class="status-item">
                    Draft Creation
                    <strong>{'✅ ENABLED' if assistant.gmail_connected else '❌ DISABLED'}</strong>
                </div>
            </div>
            
            <a href="/dashboard" class="btn primary"><i class="fas fa-tachometer-alt"></i> Open Dashboard</a>
            <a href="/debug" class="btn"><i class="fas fa-cog"></i> System Info</a>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-envelope-open-text"></i></div>
                <h3>Real Gmail Integration</h3>
                <p>Connect to your actual Gmail account with secure OAuth authentication and manage real unread emails with intelligent filtering.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-robot"></i></div>
                <h3>Smart Classification</h3>
                <p>Advanced AI-powered email prioritization that correctly identifies important emails while filtering out promotional content.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-magic"></i></div>
                <h3>Auto-Draft Creation</h3>
                <p>Generate professional draft responses for high-priority emails with contextual AI understanding and proper formatting.</p>
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
