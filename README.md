# Email Outreach Automation App

A free, automated email outreach system with intelligent follow-ups, Gmail integration, and Google Sheets management.

## 🚀 Features

- ✅ **Two-Layer Security**: Access gate + user authentication
- ✅ **Gmail Integration**: OAuth-based email sending
- ✅ **Google Sheets Integration**: Manage contacts via spreadsheet
- ✅ **Automated Follow-ups**: 5-email sequence with smart timing
  - Day 0: Initial email
  - Day 7: Follow-up #1
  - Day 14: Follow-up #2
  - Day 74: Retry #1 (after 60 days)
  - Day 134: Retry #2 (after 60 days)
- ✅ **Reply Detection**: Automatically stops sending when recipient replies
- ✅ **Bounce Detection**: Identifies invalid email addresses
- ✅ **Custom Templates**: Personalized email templates with placeholders
- ✅ **Rate Limiting**: Safe sending limits (50 emails/day, 2-5 min delays)
- ✅ **Admin Panel**: Monitor and control all users
- ✅ **Email Logs**: Track all sent emails and their status

## 📋 Prerequisites

- Python 3.9+
- Gmail account
- Google Cloud Console project with:
  - Gmail API enabled
  - OAuth 2.0 credentials
  - Service Account for Google Sheets

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/email-outreach-app.git
cd email-outreach-app
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up credentials

Create a `credentials/` folder and add:

- `client_secret.json` - Gmail OAuth credentials from Google Cloud Console
- `sheets_service.json` - Service account key for Google Sheets

### 5. Configure environment variables

Create a `.env` file:
```env
SECRET_KEY=your-super-secret-random-string-here
WEBSITE_ACCESS_ID=admin
WEBSITE_ACCESS_PASSWORD=your-secure-password
ENV=development
```

### 6. Run the application
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Visit: `http://localhost:8000`

## 📊 Google Sheet Format

Your Google Sheet should have these columns:

| Column | Name | Description |
|--------|------|-------------|
| A | Email | Recipient email address |
| B | Name | Recipient name |
| C | Company | Company name |
| D | Status | Email status (auto-updated) |
| E | Replied | TRUE/FALSE (auto-updated) |
| F | Bounce | TRUE/FALSE (auto-updated) |
| G | Followup_Count | Number of emails sent (auto-updated) |
| H | Last_Sent_Date | Date of last email (auto-updated) |
| I | Next_Send_Date | Next scheduled send (auto-updated) |
| J | Notes | Your notes |
| K | Last_Error | Error messages (auto-updated) |

**Important:** Make sure your sheet is shared with the service account email.

## 🔧 Configuration

### Email Template Placeholders

- `{MyName}` or `{My Name}` - Your full name
- `{Name}` - Recipient's name (from Column B)
- `{Company}` or `{company}` - Company name (from Column C)
- `{ResumeLink}` or `{Resume Link}` - Your resume link

### Sending Limits

- Maximum 50 emails per day
- 2-5 minute delay between emails
- Maximum 5 emails per contact

## 🌐 Deployment on Render

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/email-outreach-app.git
git push -u origin main
```

### 2. Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: email-outreach-app
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 3. Add Environment Variables on Render

Add all variables from your `.env` file:
```
SECRET_KEY=your-production-secret-key
WEBSITE_ACCESS_ID=admin
WEBSITE_ACCESS_PASSWORD=your-secure-password
ENV=production
RENDER_EXTERNAL_URL=https://your-app-name.onrender.com
```

### 4. Add Credential Files

Since credentials can't be in git, you need to add them as secret files on Render:

1. Go to your Render service
2. Navigate to "Environment" → "Secret Files"
3. Add:
   - `credentials/client_secret.json`
   - `credentials/sheets_service.json`

### 5. Update Google OAuth Redirect URI

In Google Cloud Console, add your Render URL:
```
https://your-app-name.onrender.com/auth/gmail/callback
```

## 🔐 Security Notes

- Never commit `.env`, credential files, or tokens to Git
- Change default gate password in production
- Use strong SECRET_KEY (50+ characters)
- Keep credentials secure

## 📝 Usage

1. **Access Gate**: Enter fixed ID and password
2. **Sign Up**: Create account with your name and email
3. **Connect Gmail**: Authorize Gmail access
4. **Add Settings**:
   - Resume link
   - Google Sheet ID
   - Email subject
   - Email templates (initial + follow-up)
5. **Start Sending**: Click "Start Sending Emails"

## 🐛 Troubleshooting

### Emails not sending?

Check:
- Gmail is connected
- Sheet ID is correct
- Templates are saved
- Sheet has correct format
- Followup_Count is 0 for new contacts

### Connection pool errors?

Restart the application.

### Sheet not updating?

Ensure service account has edit access to your sheet.

## 📄 License

MIT License

## 👤 Author

Your Name - [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI for the web framework
- Google APIs for Gmail and Sheets integration
- SQLAlchemy for database management