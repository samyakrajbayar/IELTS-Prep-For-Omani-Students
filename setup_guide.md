# IELTS AI Tutor Setup Guide for Replit

## 🚀 Quick Setup Instructions

### 1. Create New Replit Project
1. Go to [Replit.com](https://replit.com) and create account
2. Click "Create Repl" 
3. Choose "Python" template
4. Name it "IELTS-AI-Tutor"

### 2. Upload Files
Upload these files to your Replit project:
- `ielts_core.py` - Core AI model
- `discord_bot.py` - Discord bot
- `streamlit_app.py` - Streamlit web app  
- `requirements.txt` - Dependencies

### 3. Install Dependencies
In the Replit shell, run:
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
In Replit, go to "Secrets" tab and add:

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `DISCORD_BOT_TOKEN` - Your Discord bot token

**Optional:**
- `GOOGLE_TRANSLATE_API_KEY` - For better Arabic translation

### 5. Getting API Keys

#### OpenAI API Key:
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create account and go to API Keys
3. Create new secret key
4. Copy and paste into Replit Secrets

#### Discord Bot Token:
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create "New Application"
3. Go to "Bot" section
4. Click "Add Bot"
5. Copy token and paste into Replit Secrets
6. Enable these permissions:
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands

#### Google Translate API (Optional):
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Translate API
3. Create credentials
4. Copy API key to Replit Secrets

### 6. Running the Applications

#### For Discord Bot:
In Replit shell:
```bash
python discord_bot.py
```

#### For Streamlit App:
In Replit shell:
```bash
streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
```

### 7. Discord Bot Setup
1. Invite bot to your Discord server using this URL format:
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=2048&scope=bot
   ```
   Replace `YOUR_BOT_CLIENT_ID` with your actual bot's client ID from Discord Developer Portal.

2. Bot permissions needed:
   - Send Messages
   - Embed Links  
   - Read Message History
   - Use External Emojis

### 8. Main Files Structure

```
IELTS-AI-Tutor/
├── ielts_core.py          # Core AI functionality
├── discord_bot.py         # Discord bot implementation
├── streamlit_app.py       # Web app interface
├── requirements.txt       # Python dependencies
└── README.md             # This setup guide
```

### 9. Discord Bot Commands

Once running, users can use these commands in Discord:

**Practice Commands:**
- `!ielts help` - Show all commands
- `!ielts practice <section>` - Start practice (listening/reading/writing/speaking)
- `!ielts pyq <section>` - Get previous year questions
- `!ielts generate <section> <type> <difficulty>` - Generate AI questions

**Progress Commands:**
- `!ielts score` - View practice scores
- `!ielts predict` - Get predicted IELTS band score
- `!ielts plan <target_band> <weeks>` - Get personalized study plan

**Utility Commands:**
- `!ielts language <english/arabic>` - Change interface language
- `!ielts vocab <level>` - Get vocabulary builder
- `!ielts translate <text>` - Translate English to Arabic
- `!ielts skip` - Skip current question

### 10. Streamlit App Features

The web app includes:
- **Dashboard:** Overview of progress and statistics
- **Practice Sessions:** Interactive question practice
- **Previous Year Questions:** Access to PYQ database
- **AI Generator:** Create new questions with AI
- **Progress Tracking:** Detailed analytics and charts
- **Study Plans:** Personalized preparation schedules
- **Vocabulary Builder:** Level-based word learning
- **Translator:** Arabic-English translation tool

### 11. Keeping Bot Online (24/7)

For production use, consider:

**Option 1: Replit Always On (Paid)**
- Upgrade to Replit Hacker plan
- Enable "Always On" for your repl

**Option 2: UptimeRobot (Free)**
- Create account at [UptimeRobot](https://uptimerobot.com)
- Add HTTP monitor pointing to your Replit URL
- Set check interval to 5 minutes

**Option 3: Self-Ping (Free)**
Add this to your Discord bot for self-pinging:
```python
import requests
import threading
import time

def keep_alive():
    while True:
        try:
            requests.get("YOUR_REPLIT_URL")
            time.sleep(300)  # Ping every 5 minutes
        except:
            pass

# Start keep-alive in background
threading.Thread(target=keep_alive, daemon=True).start()
```

### 12. Customization Options

#### Adding More Questions:
Edit the `pyq_database` in `ielts_core.py`:
```python
self.pyq_database = {
    "listening": [
        {
            "type": "Multiple Choice",
            "question": "Your new question here",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3"],
            "answer": "A",
            "difficulty": "medium"
        }
        # Add more questions...
    ]
}
```

#### Customizing Study Plans:
Modify the `get_study_plan()` method in `ielts_core.py` to adjust:
- Daily study time recommendations
- Weekly goals and milestones
- Resource recommendations
- Skill focus areas

#### Adding New Features:
- Band score calculation algorithms
- More vocabulary categories
- Additional question types
- Progress analytics
- Export functionality

### 13. Troubleshooting

**Common Issues:**

**Bot not responding:**
- Check if bot token is correct in Secrets
- Verify bot permissions in Discord server
- Check Replit console for error messages

**OpenAI API errors:**
- Verify API key is valid and has credits
- Check if you've exceeded rate limits
- Ensure `openai` library version matches (0.28.0)

**Streamlit app not loading:**
- Check if running on correct port (8080)
- Verify all dependencies are installed
- Look for Python import errors in console

**Translation not working:**
- Arabic translations work with fallback even without Google API
- For better translations, add Google Translate API key
- Check if requests to Google API are successful

### 14. Performance Optimization

**For better performance:**

1. **Database Upgrade:** Replace in-memory storage with SQLite:
```python
import sqlite3
# Create database connection
conn = sqlite3.connect('ielts_data.db')
```

2. **Caching:** Add response caching for AI-generated content
3. **Async Operations:** Use async/await for API calls
4. **Question Pool:** Expand the PYQ database with more questions

### 15. Security Best Practices

1. **Never commit API keys to code**
2. **Use environment variables for all secrets**
3. **Validate user inputs** to prevent injection attacks
4. **Rate limit API calls** to prevent abuse
5. **Log activities** for monitoring and debugging

### 16. Deployment Alternatives

**If Replit doesn't work:**

**Heroku:**
```bash
# Create Procfile
web: streamlit run streamlit_app.py --server.port=$PORT
worker: python discord_bot.py
```

**Railway:**
```bash
# railway.json
{
  "build": {
    "builder": "heroku/python"
  },
  "deploy": {
    "startCommand": "python discord_bot.py"
  }
}
```

**PythonAnywhere:**
- Upload files via Files tab
- Set up scheduled task for bot
- Configure web app for Streamlit

### 17. Monitoring and Analytics

Track usage with:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log user activities
logger.info(f"User {user_id} completed {section} question")
```

### 18. Scaling for Multiple Users

For production with many users:
1. **Database:** Use PostgreSQL or MongoDB
2. **Caching:** Implement Redis for session storage
3. **Load Balancing:** Use multiple bot instances
4. **Queue System:** Handle API requests asynchronously

### 19. Legal Considerations

- **Data Privacy:** Inform users about data collection
- **API Usage:** Respect OpenAI and Google API terms
- **Educational Use:** Ensure content complies with IELTS guidelines
- **Copyright:** Only use original or licensed question content

### 20. Support and Updates

**Getting Help:**
- Check Replit console for error messages
- Review Discord bot logs
- Test API keys with simple requests
- Verify all environment variables are set

**Regular Updates:**
- Update dependencies monthly
- Expand question database
- Add new features based on user feedback
- Monitor API usage and costs

---

## 🎉 You're All Set!

Your IELTS AI Tutor is now ready to help Omani students prepare for their IELTS exams with:

✅ **Discord Bot** - Interactive practice sessions  
✅ **Streamlit Web App** - Comprehensive learning platform  
✅ **Arabic Support** - Native language assistance  
✅ **AI-Generated Questions** - Unlimited practice content  
✅ **Progress Tracking** - Detailed performance analytics  
✅ **Study Plans** - Personalized preparation schedules  

**Test your setup:**
1. Run Discord bot and invite to server
2. Try `!ielts help` command
3. Start Streamlit app and open in browser
4. Test a practice session
5. Check Arabic translation feature

Good luck with your IELTS preparation platform! 🇴🇲📚