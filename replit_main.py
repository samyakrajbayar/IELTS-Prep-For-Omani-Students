#!/usr/bin/env python3
"""
IELTS AI Tutor - Main Entry Point for Replit
Run both Discord Bot and Streamlit App
"""

import os
import threading
import subprocess
import time
import requests
from flask import Flask

# Simple web server to keep Replit alive
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🇴🇲 IELTS AI Tutor is Running!</h1>
    <p>Discord Bot Status: ✅ Online</p>
    <p>Streamlit App: <a href="https://8080-{repl-id}.{cluster-id}.replit.dev" target="_blank">Open App</a></p>
    <h2>Quick Start:</h2>
    <ul>
        <li>Invite Discord Bot to your server</li>
        <li>Use command: <code>!ielts help</code></li>
        <li>Open Streamlit App for web interface</li>
    </ul>
    <h2>Features:</h2>
    <ul>
        <li>📝 Practice Sessions (All 4 Skills)</li>
        <li>📚 Previous Year Questions</li>
        <li>🤖 AI Question Generator</li>
        <li>📊 Progress Tracking</li>
        <li>📅 Personalized Study Plans</li>
        <li>🔄 Arabic Translation</li>
        <li>📖 Vocabulary Builder</li>
    </ul>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "message": "IELTS AI Tutor is running"}

def run_discord_bot():
    """Run the Discord bot in a separate thread"""
    print("🤖 Starting Discord Bot...")
    try:
        # Import and run bot
        from discord_bot import bot
        import os
        
        DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        if DISCORD_BOT_TOKEN:
            bot.run(DISCORD_BOT_TOKEN)
        else:
            print("❌ DISCORD_BOT_TOKEN not found in environment variables")
            print("Please add your Discord bot token to Replit Secrets")
    except Exception as e:
        print(f"❌ Discord Bot Error: {e}")
        print("Make sure you've installed discord.py: pip install discord.py")

def run_streamlit_app():
    """Run Streamlit app in a separate process"""
    print("🌐 Starting Streamlit App...")
    try:
        # Give Discord bot time to start
        time.sleep(5)
        
        # Run Streamlit on port 8080
        subprocess.Popen([
            "streamlit", "run", "streamlit_app.py",
            "--server.port", "8080",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.serverAddress", "0.0.0.0",
            "--browser.serverPort", "8080"
        ])
        
        print("✅ Streamlit app started on port 8080")
        
    except Exception as e:
        print(f"❌ Streamlit Error: {e}")
        print("Make sure you've installed streamlit: pip install streamlit")

def keep_alive():
    """Keep the Replit alive by self-pinging"""
    while True:
        try:
            time.sleep(300)  # Wait 5 minutes
            # Self-ping to keep alive
            requests.get("http://0.0.0.0:5000/health", timeout=10)
        except:
            pass

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['OPENAI_API_KEY']
    optional_vars = ['DISCORD_BOT_TOKEN', 'GOOGLE_TRANSLATE_API_KEY']
    
    print("🔍 Checking Environment Variables...")
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_required:
        print(f"❌ Missing required variables: {missing_required}")
        print("Please add these to your Replit Secrets")
        return False
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} is not set (optional)")
    
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        print("Please run manually: pip install -r requirements.txt")

def main():
    """Main function to orchestrate everything"""
    print("🚀 IELTS AI Tutor Starting Up...")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("Please set up your environment variables and restart")
        return
    
    # Install requirements if needed
    if not os.path.exists("requirements_installed.flag"):
        install_requirements()
        # Create flag file to avoid reinstalling every time
        with open("requirements_installed.flag", "w") as f:
            f.write("installed")
    
    print("🎯 Starting all services...")
    
    # Start Discord bot in background thread
    discord_thread = threading.Thread(target=run_discord_bot, daemon=True)
    discord_thread.start()
    
    # Start Streamlit app in background process
    streamlit_thread = threading.Thread(target=run_streamlit_app, daemon=True)
    streamlit_thread.start()
    
    # Start keep-alive thread
    keepalive_thread = threading.Thread(target=keep_alive, daemon=True)
    keepalive_thread.start()
    
    print("✅ All services started!")
    print("📱 Discord Bot: Ready for commands")
    print("🌐 Streamlit App: Available on port 8080")
    print("🔄 Keep-Alive: Running")
    print("=" * 50)
    
    # Run Flask app to keep Replit alive and show status
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()