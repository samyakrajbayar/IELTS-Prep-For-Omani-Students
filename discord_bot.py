import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime
from ielts_core import IELTSAIModel, IELTSQuestion

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!ielts ', intents=intents)

# Initialize IELTS AI Model
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY') 
ielts_model = IELTSAIModel(OPENAI_API_KEY, GOOGLE_TRANSLATE_API_KEY)

# User session storage (in production, use a database)
user_sessions = {}

class UserSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_question = None
        self.score_history = {"listening": [], "reading": [], "writing": [], "speaking": []}
        self.practice_mode = None
        self.language = "english"  # or "arabic"

@bot.event
async def on_ready():
    print(f'{bot.user} has landed in Oman! Ready to help with IELTS preparation! 🇴🇲')

def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id)
    return user_sessions[user_id]

@bot.command(name='help')
async def help_command(ctx):
    """Display help information"""
    embed = discord.Embed(
        title="🎓 IELTS AI Bot Commands / أوامر بوت الآيلتس",
        description="Your personal IELTS preparation assistant for Omani students",
        color=0x00ff00
    )
    
    embed.add_field(
        name="📚 Practice Commands / أوامر التدريب",
        value="""
        `!ielts practice <section>` - Start practice session
        `!ielts pyq <section>` - Get previous year questions
        `!ielts generate <section> <type> <difficulty>` - Generate new question
        
        Sections: listening, reading, writing, speaking
        Difficulty: easy, medium, hard
        """,
        inline=False
    )
    
    embed.add_field(
        name="📊 Progress Commands / أوامر التقدم", 
        value="""
        `!ielts score` - View your progress
        `!ielts predict` - Get band score prediction
        `!ielts plan <target_band> <weeks>` - Get study plan
        """,
        inline=False
    )
    
    embed.add_field(
        name="🔧 Settings / الإعدادات",
        value="""
        `!ielts language <english/arabic>` - Change language
        `!ielts vocab <level>` - Get vocabulary builder
        `!ielts translate <text>` - Translate to Arabic
        """,
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='practice')
async def practice_session(ctx, section: str = None):
    """Start a practice session"""
    if not section:
        await ctx.send("Please specify a section: `!ielts practice <listening/reading/writing/speaking>`")
        return
    
    if section.lower() not in ['listening', 'reading', 'writing', 'speaking']:
        await ctx.send("Invalid section. Choose from: listening, reading, writing, speaking")
        return
    
    session = get_user_session(ctx.author.id)
    session.practice_mode = section.lower()
    
    # Get a question
    question = ielts_model.get_pyq_question(section.lower())
    session.current_question = question
    
    embed = discord.Embed(
        title=f"📝 {section.title()} Practice",
        description=f"**Question Type:** {question.question_type}\n**Difficulty:** {question.difficulty}",
        color=0x3498db
    )
    
    embed.add_field(name="Question", value=question.question, inline=False)
    
    if session.language == "arabic" and question.arabic_translation:
        embed.add_field(name="الترجمة العربية", value=question.arabic_translation, inline=False)
    
    if question.options:
        options_text = "\n".join(question.options)
        embed.add_field(name="Options", value=options_text, inline=False)
    
    embed.set_footer(text="Type your answer below, or use '!ielts skip' to get another question")
    
    await ctx.send(embed=embed)

@bot.command(name='answer')
async def submit_answer(ctx, *, user_answer: str):
    """Submit an answer to the current question"""
    session = get_user_session(ctx.author.id)
    
    if not session.current_question:
        await ctx.send("No active question. Start a practice session first with `!ielts practice <section>`")
        return
    
    # Evaluate the answer
    feedback = ielts_model.evaluate_answer(session.current_question, user_answer)
    
    # Update score history
    if session.practice_mode:
        session.score_history[session.practice_mode].append(feedback["score"])
    
    # Create feedback embed
    color = 0x00ff00 if feedback["is_correct"] else 0xff0000
    title = "✅ Correct!" if feedback["is_correct"] else "❌ Incorrect"
    
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="Your Answer", value=user_answer, inline=True)
    
    if feedback["correct_answer"]:
        embed.add_field(name="Correct Answer", value=feedback["correct_answer"], inline=True)
    
    if feedback["explanation"]:
        embed.add_field(name="Explanation", value=feedback["explanation"], inline=False)
    
    embed.set_footer(text="Use '!ielts practice <section>' to continue practicing")
    
    await ctx.send(embed=embed)
    
    # Clear current question
    session.current_question = None

@bot.command(name='pyq')
async def previous_year_question(ctx, section: str = None):
    """Get a previous year question"""
    if not section:
        sections = ", ".join(ielts_model.syllabus.keys())
        await ctx.send(f"Please specify a section: {sections}")
        return
    
    question = ielts_model.get_pyq_question(section.lower())
    session = get_user_session(ctx.author.id)
    session.current_question = question
    session.practice_mode = section.lower()
    
    embed = discord.Embed(
        title=f"📚 {section.title()} - Previous Year Question",
        description=f"**Type:** {question.question_type} | **Level:** {question.difficulty}",
        color=0x9b59b6
    )
    
    embed.add_field(name="Question", value=question.question, inline=False)
    
    if session.language == "arabic" and question.arabic_translation:
        embed.add_field(name="السؤال بالعربية", value=question.arabic_translation, inline=False)
    
    if question.options:
        embed.add_field(name="Options", value="\n".join(question.options), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='generate')
async def generate_question(ctx, section: str = None, question_type: str = None, difficulty: str = "medium"):
    """Generate a new AI question"""
    if not section:
        await ctx.send("Usage: `!ielts generate <section> <type> <difficulty>`")
        return
    
    try:
        question = ielts_model.generate_question_with_ai(section, question_type or "general", difficulty)
        session = get_user_session(ctx.author.id)
        session.current_question = question
        session.practice_mode = section.lower()
        
        embed = discord.Embed(
            title=f"🤖 AI Generated {section.title()} Question",
            description=f"**Type:** {question.question_type} | **Level:** {question.difficulty}",
            color=0xe74c3c
        )
        
        embed.add_field(name="Question", value=question.question, inline=False)
        
        if session.language == "arabic" and question.arabic_translation:
            embed.add_field(name="الترجمة", value=question.arabic_translation, inline=False)
        
        if question.options:
            embed.add_field(name="Options", value="\n".join(question.options), inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Error generating question: {str(e)}")

@bot.command(name='score')
async def view_scores(ctx):
    """View practice scores"""
    session = get_user_session(ctx.author.id)
    
    embed = discord.Embed(
        title="📊 Your IELTS Practice Scores",
        color=0xf39c12
    )
    
    for section, scores in session.score_history.items():
        if scores:
            avg_score = sum(scores) / len(scores)
            recent_scores = scores[-5:]  # Last 5 scores
            embed.add_field(
                name=f"{section.title()}",
                value=f"Average: {avg_score:.1%}\nRecent: {recent_scores}\nTotal Questions: {len(scores)}",
                inline=True
            )
        else:
            embed.add_field(
                name=f"{section.title()}",
                value="No practice yet",
                inline=True
            )
    
    await ctx.send(embed=embed)

@bot.command(name='predict')
async def predict_band(ctx):
    """Predict IELTS band score"""
    session = get_user_session(ctx.author.id)
    
    # Convert scores to percentage for prediction
    practice_scores = {}
    for section, scores in session.score_history.items():
        if scores:
            practice_scores[section] = scores
    
    if not practice_scores:
        await ctx.send("No practice data available. Complete some practice questions first!")
        return
    
    prediction = ielts_model.get_band_score_prediction(practice_scores)
    
    embed = discord.Embed(
        title="🔮 IELTS Band Score Prediction",
        description=f"**Predicted Overall Band: {prediction['overall_band']}**",
        color=0x2ecc71
    )
    
    for section, score in prediction['section_scores'].items():
        embed.add_field(name=section.title(), value=f"Band {score}", inline=True)
    
    if prediction['improvement_areas']:
        embed.add_field(
            name="🎯 Areas to Improve",
            value="\n".join(prediction['improvement_areas']),
            inline=False
        )
    
    if prediction['strengths']:
        embed.add_field(
            name="💪 Strengths",
            value="\n".join(prediction['strengths']),
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='plan')
async def study_plan(ctx, target_band: float = 7.0, weeks: int = 8):
    """Generate a study plan"""
    session = get_user_session(ctx.author.id)
    
    # Determine current level based on practice scores
    total_scores = []
    for scores in session.score_history.values():
        total_scores.extend(scores)
    
    current_level = "intermediate"
    if total_scores:
        avg = sum(total_scores) / len(total_scores)
        if avg < 0.5:
            current_level = "beginner"
        elif avg > 0.75:
            current_level = "advanced"
    
    plan = ielts_model.get_study_plan(target_band, current_level, weeks)
    
    embed = discord.Embed(
        title=f"📅 {weeks}-Week IELTS Study Plan",
        description=f"Target Band: {target_band} | Current Level: {current_level.title()}",
        color=0x8e44ad
    )
    
    # Daily schedule
    schedule_text = ""
    for skill, time in plan['daily_schedule'].items():
        schedule_text += f"• {skill.title()}: {time}\n"
    
    embed.add_field(name="Daily Study Schedule", value=schedule_text, inline=False)
    
    # Weekly goals
    goals_text = "\n".join(plan['weekly_goals'][:4])  # Show first 4 weeks
    embed.add_field(name="Weekly Goals", value=goals_text, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='vocab')
async def vocabulary_builder(ctx, level: str = "intermediate"):
    """Get vocabulary building exercises"""
    if level not in ["beginner", "intermediate", "advanced"]:
        level = "intermediate"
    
    vocab_data = ielts_model.get_vocabulary_builder(level)
    
    embed = discord.Embed(
        title=f"📖 Vocabulary Builder - {level.title()} Level",
        color=0x16a085
    )
    
    for category, words in vocab_data['vocabulary_list'].items():
        embed.add_field(
            name=f"{category.title()} Words",
            value=", ".join(words),
            inline=False
        )
    
    exercises_text = "\n".join(f"• {exercise}" for exercise in vocab_data['exercises'])
    embed.add_field(name="Practice Exercises", value=exercises_text, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='translate')
async def translate_text(ctx, *, text: str):
    """Translate English text to Arabic"""
    translation = ielts_model.translate_to_arabic(text)
    
    embed = discord.Embed(title="🔄 Translation", color=0x34495e)
    embed.add_field(name="English", value=text, inline=False)
    embed.add_field(name="Arabic / العربية", value=translation, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='language')
async def set_language(ctx, lang: str = None):
    """Set interface language"""
    if not lang or lang.lower() not in ['english', 'arabic']:
        await ctx.send("Usage: `!ielts language <english/arabic>`")
        return
    
    session = get_user_session(ctx.author.id)
    session.language = lang.lower()
    
    if lang.lower() == 'arabic':
        await ctx.send("تم تغيير اللغة إلى العربية! ✅")
    else:
        await ctx.send("Language changed to English! ✅")

@bot.command(name='skip')
async def skip_question(ctx):
    """Skip current question and get a new one"""
    session = get_user_session(ctx.author.id)
    
    if not session.practice_mode:
        await ctx.send("No active practice session. Use `!ielts practice <section>` to start.")
        return
    
    # Get new question
    question = ielts_model.get_pyq_question(session.practice_mode)
    session.current_question = question
    
    embed = discord.Embed(
        title=f"⏭️ New {session.practice_mode.title()} Question",
        description=f"**Type:** {question.question_type} | **Level:** {question.difficulty}",
        color=0x95a5a6
    )
    
    embed.add_field(name="Question", value=question.question, inline=False)
    
    if question.options:
        embed.add_field(name="Options", value="\n".join(question.options), inline=False)
    
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `!ielts help` to see available commands.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Run the bot
if __name__ == "__main__":
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Please set DISCORD_BOT_TOKEN environment variable")