import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from ielts_core import IELTSAIModel, IELTSQuestion

# Page configuration
st.set_page_config(
    page_title="IELTS AI Tutor for Omanis",
    page_icon="🇴🇲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'ielts_model' not in st.session_state:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
    st.session_state.ielts_model = IELTSAIModel(OPENAI_API_KEY, GOOGLE_TRANSLATE_API_KEY)

if 'user_scores' not in st.session_state:
    st.session_state.user_scores = {"listening": [], "reading": [], "writing": [], "speaking": []}

if 'current_question' not in st.session_state:
    st.session_state.current_question = None

if 'language' not in st.session_state:
    st.session_state.language = 'english'

if 'practice_history' not in st.session_state:
    st.session_state.practice_history = []

# Custom CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 30px;
}

.metric-card {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #007bff;
    margin: 10px 0;
}

.question-card {
    background: #fff;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 20px 0;
}

.correct-answer {
    background: #d4edda;
    color: #155724;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #c3e6cb;
}

.incorrect-answer {
    background: #f8d7da;
    color: #721c24;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #f5c6cb;
}

.arabic-text {
    direction: rtl;
    text-align: right;
    font-size: 18px;
    background: #f0f8ff;
    padding: 15px;
    border-radius: 8px;
    border-right: 4px solid #007bff;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🇴🇲 IELTS AI Tutor for Omanis</h1>
    <h3>مدرس الآيلتس الذكي للعمانيين</h3>
    <p>Your personalized IELTS preparation companion with Arabic support</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://flagcdn.com/w80/om.png", width=50)
    st.title("Navigation")
    
    # Language selector
    language = st.selectbox(
        "Language / اللغة",
        ["English", "العربية"],
        key="lang_selector"
    )
    
    st.session_state.language = 'arabic' if language == "العربية" else 'english'
    
    # Main navigation
    page = st.selectbox(
        "Choose Page",
        ["🏠 Dashboard", "📝 Practice", "📚 Previous Year Questions", 
         "🤖 AI Generator", "📊 Progress Tracking", "📅 Study Plan", 
         "📖 Vocabulary Builder", "🔄 Translator"]
    )

# Dashboard Page
if page == "🏠 Dashboard":
    st.header("Dashboard / لوحة التحكم")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    total_questions = sum(len(scores) for scores in st.session_state.user_scores.values())
    
    if total_questions > 0:
        all_scores = []
        for scores in st.session_state.user_scores.values():
            all_scores.extend(scores)
        avg_accuracy = sum(all_scores) / len(all_scores) * 100
        predicted_band = min(9.0, max(1.0, (avg_accuracy / 100) * 9))
    else:
        avg_accuracy = 0
        predicted_band = 0
    
    with col1:
        st.metric("Total Questions", total_questions)
    
    with col2:
        st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")
    
    with col3:
        st.metric("Predicted Band", f"{predicted_band:.1f}")
    
    with col4:
        practice_days = len(set(item['date'].date() for item in st.session_state.practice_history))
        st.metric("Practice Days", practice_days)
    
    # Progress charts
    if total_questions > 0:
        st.subheader("Section-wise Performance")
        
        # Create DataFrame for visualization
        section_data = []
        for section, scores in st.session_state.user_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores) * 100
                section_data.append({
                    'Section': section.title(),
                    'Average Score': avg_score,
                    'Questions Attempted': len(scores)
                })
        
        if section_data:
            df = pd.DataFrame(section_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df, x='Section', y='Average Score', 
                           title='Average Scores by Section',
                           color='Average Score',
                           color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(df, values='Questions Attempted', names='Section',
                           title='Practice Distribution by Section')
                st.plotly_chart(fig, use_container_width=True)
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Practice", use_container_width=True):
            st.session_state.page = "📝 Practice"
            st.rerun()
    
    with col2:
        if st.button("📚 View PYQs", use_container_width=True):
            st.session_state.page = "📚 Previous Year Questions"
            st.rerun()
    
    with col3:
        if st.button("📊 View Progress", use_container_width=True):
            st.session_state.page = "📊 Progress Tracking"
            st.rerun()

# Practice Page
elif page == "📝 Practice":
    st.header("Practice Session / جلسة التدريب")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        section = st.selectbox(
            "Choose Section",
            ["Listening", "Reading", "Writing", "Speaking"]
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"]
        )
    
    if st.button("Get New Question", type="primary"):
        question = st.session_state.ielts_model.get_pyq_question(section.lower())
        st.session_state.current_question = question
    
    # Display current question
    if st.session_state.current_question:
        question = st.session_state.current_question
        
        st.markdown(f"""
        <div class="question-card">
            <h4>Question Type: {question.question_type}</h4>
            <h4>Difficulty: {question.difficulty}</h4>
            <hr>
            <h3>{question.question}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Show Arabic translation if available and language is set to Arabic
        if st.session_state.language == 'arabic' and question.arabic_translation:
            st.markdown(f"""
            <div class="arabic-text">
                <strong>الترجمة العربية:</strong><br>
                {question.arabic_translation}
            </div>
            """, unsafe_allow_html=True)
        
        # Show options if available
        if question.options:
            st.subheader("Options:")
            for option in question.options:
                st.write(option)
        
        # Answer input
        user_answer = st.text_area("Your Answer:", height=100)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Submit Answer", type="primary"):
                if user_answer.strip():
                    feedback = st.session_state.ielts_model.evaluate_answer(question, user_answer)
                    
                    # Store score
                    section_key = section.lower()
                    if section_key in st.session_state.user_scores:
                        st.session_state.user_scores[section_key].append(feedback["score"])
                    
                    # Store practice history
                    st.session_state.practice_history.append({
                        'date': datetime.now(),
                        'section': section,
                        'question_type': question.question_type,
                        'score': feedback["score"],
                        'user_answer': user_answer,
                        'correct_answer': feedback["correct_answer"]
                    })
                    
                    # Show feedback
                    if feedback["is_correct"]:
                        st.markdown(f"""
                        <div class="correct-answer">
                            <h4>✅ Correct!</h4>
                            <p><strong>Your Answer:</strong> {user_answer}</p>
                            {f"<p><strong>Explanation:</strong> {feedback['explanation']}</p>" if feedback['explanation'] else ""}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="incorrect-answer">
                            <h4>❌ Incorrect</h4>
                            <p><strong>Your Answer:</strong> {user_answer}</p>
                            <p><strong>Correct Answer:</strong> {feedback['correct_answer']}</p>
                            {f"<p><strong>Explanation:</strong> {feedback['explanation']}</p>" if feedback['explanation'] else ""}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("Please enter an answer!")
        
        with col2:
            if st.button("Skip Question"):
                new_question = st.session_state.ielts_model.get_pyq_question(section.lower())
                st.session_state.current_question = new_question
                st.rerun()

# Previous Year Questions Page
elif page == "📚 Previous Year Questions":
    st.header("Previous Year Questions / أسئلة السنوات السابقة")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        section = st.selectbox("Select Section", ["Listening", "Reading", "Writing", "Speaking"])
    
    with col2:
        question_types = st.session_state.ielts_model.syllabus[section.lower()]["question_types"]
        question_type = st.selectbox("Question Type (Optional)", ["All Types"] + question_types)
    
    if st.button("Get PYQ", type="primary"):
        qtype = None if question_type == "All Types" else question_type
        question = st.session_state.ielts_model.get_pyq_question(section.lower(), qtype)
        st.session_state.current_question = question
    
    # Display PYQ
    if st.session_state.current_question:
        question = st.session_state.current_question
        
        st.info(f"**Section:** {section} | **Type:** {question.question_type} | **Difficulty:** {question.difficulty}")
        
        st.markdown(f"### Question:\n{question.question}")
        
        if st.session_state.language == 'arabic' and question.arabic_translation:
            st.markdown(f"""
            <div class="arabic-text">
                <strong>السؤال بالعربية:</strong><br>
                {question.arabic_translation}
            </div>
            """, unsafe_allow_html=True)
        
        if question.options:
            st.markdown("### Options:")
            for option in question.options:
                st.write(option)
        
        # Show answer button
        if st.button("Show Answer"):
            if question.correct_answer:
                st.success(f"**Correct Answer:** {question.correct_answer}")
            if question.explanation:
                st.info(f"**Explanation:** {question.explanation}")

# AI Generator Page
elif page == "🤖 AI Generator":
    st.header("AI Question Generator / مولد الأسئلة الذكي")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        section = st.selectbox("Section", ["Listening", "Reading", "Writing", "Speaking"])
    
    with col2:
        question_types = st.session_state.ielts_model.syllabus[section.lower()]["question_types"]
        question_type = st.selectbox("Question Type", question_types)
    
    with col3:
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
    
    if st.button("🎯 Generate AI Question", type="primary"):
        with st.spinner("Generating question with AI..."):
            try:
                question = st.session_state.ielts_model.generate_question_with_ai(
                    section.lower(), question_type, difficulty.lower()
                )
                st.session_state.current_question = question
                st.success("AI question generated successfully!")
            except Exception as e:
                st.error(f"Error generating AI question: {str(e)}")
                st.info("Falling back to previous year question...")
                question = st.session_state.ielts_model.get_pyq_question(section.lower())
                st.session_state.current_question = question
    
    # Display generated question
    if st.session_state.current_question:
        question = st.session_state.current_question
        
        st.markdown(f"""
        <div class="question-card">
            <h4>🤖 AI Generated Question</h4>
            <p><strong>Section:</strong> {section} | <strong>Type:</strong> {question.question_type} | <strong>Difficulty:</strong> {question.difficulty}</p>
            <hr>
            <h3>{question.question}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.language == 'arabic' and question.arabic_translation:
            st.markdown(f"""
            <div class="arabic-text">
                {question.arabic_translation}
            </div>
            """, unsafe_allow_html=True)
        
        if question.options:
            st.subheader("Options:")
            for option in question.options:
                st.write(option)
        
        # Answer input for AI questions
        user_answer = st.text_area("Your Answer:")
        
        if st.button("Check Answer") and user_answer.strip():
            feedback = st.session_state.ielts_model.evaluate_answer(question, user_answer)
            
            if feedback["is_correct"]:
                st.success(f"✅ Correct! {feedback.get('explanation', '')}")
            else:
                st.error(f"❌ Incorrect. Correct answer: {feedback['correct_answer']}")
                if feedback.get('explanation'):
                    st.info(f"Explanation: {feedback['explanation']}")

# Progress Tracking Page
elif page == "📊 Progress Tracking":
    st.header("Progress Tracking / تتبع التقدم")
    
    if not any(st.session_state.user_scores.values()):
        st.info("No practice data yet. Start practicing to see your progress!")
    else:
        # Overall statistics
        st.subheader("Overall Statistics")
        
        total_questions = sum(len(scores) for scores in st.session_state.user_scores.values())
        all_scores = []
        for scores in st.session_state.user_scores.values():
            all_scores.extend(scores)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Questions Attempted", total_questions)
        
        with col2:
            avg_accuracy = (sum(all_scores) / len(all_scores)) * 100 if all_scores else 0
            st.metric("Overall Accuracy", f"{avg_accuracy:.1f}%")
        
        with col3:
            predicted_band = st.session_state.ielts_model.get_band_score_prediction(st.session_state.user_scores)
            st.metric("Predicted IELTS Band", f"{predicted_band['overall_band']}")
        
        # Section-wise progress
        st.subheader("Section-wise Performance")
        
        for section, scores in st.session_state.user_scores.items():
            if scores:
                with st.expander(f"{section.title()} - {len(scores)} questions"):
                    avg_score = (sum(scores) / len(scores)) * 100
                    st.metric(f"Average Score", f"{avg_score:.1f}%")
                    
                    # Score trend
                    df = pd.DataFrame({
                        'Question': range(1, len(scores) + 1),
                        'Score': [s * 100 for s in scores]
                    })
                    
                    fig = px.line(df, x='Question', y='Score', 
                                title=f'{section.title()} Score Trend',
                                markers=True)
                    fig.add_hline(y=70, line_dash="dash", line_color="green", 
                                annotation_text="Target: 70%")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Band score prediction details
        if predicted_band['improvement_areas'] or predicted_band['strengths']:
            st.subheader("Detailed Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if predicted_band['improvement_areas']:
                    st.markdown("**🎯 Areas to Improve:**")
                    for area in predicted_band['improvement_areas']:
                        st.markdown(f"- {area}")
            
            with col2:
                if predicted_band['strengths']:
                    st.markdown("**💪 Your Strengths:**")
                    for strength in predicted_band['strengths']:
                        st.markdown(f"- {strength}")
        
        # Recent practice history
        if st.session_state.practice_history:
            st.subheader("Recent Practice History")
            
            recent_history = sorted(st.session_state.practice_history, 
                                  key=lambda x: x['date'], reverse=True)[:10]
            
            history_df = pd.DataFrame([
                {
                    'Date': item['date'].strftime('%Y-%m-%d %H:%M'),
                    'Section': item['section'],
                    'Question Type': item['question_type'],
                    'Score': '✅' if item['score'] == 1 else '❌'
                }
                for item in recent_history
            ])
            
            st.dataframe(history_df, use_container_width=True)

# Study Plan Page
elif page == "📅 Study Plan":
    st.header("Personalized Study Plan / خطة الدراسة الشخصية")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_band = st.slider("Target IELTS Band Score", 5.0, 9.0, 7.0, 0.5)
    
    with col2:
        study_weeks = st.slider("Study Duration (weeks)", 4, 24, 8)
    
    if st.button("Generate Study Plan", type="primary"):
        # Determine current level
        total_scores = []
        for scores in st.session_state.user_scores.values():
            total_scores.extend(scores)
        
        current_level = "intermediate"
        if total_scores:
            avg = sum(total_scores) / len(total_scores)
            if avg < 0.5:
                current_level = "beginner"
            elif avg > 0.75:
                current_level = "advanced"
        
        study_plan = st.session_state.ielts_model.get_study_plan(
            target_band, current_level, study_weeks
        )
        
        st.success(f"Study plan generated for {study_weeks} weeks!")
        
        # Display study plan
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Daily Study Schedule")
            
            schedule_df = pd.DataFrame([
                {'Skill': skill.title(), 'Daily Time': time}
                for skill, time in study_plan['daily_schedule'].items()
            ])
            
            st.table(schedule_df)
        
        with col2:
            st.subheader("Plan Overview")
            st.info(f"""
            **Target Band:** {target_band}
            **Current Level:** {current_level.title()}
            **Duration:** {study_weeks} weeks
            **Total Daily Time:** {sum(int(t.split()[0]) for t in study_plan['daily_schedule'].values())} minutes
            """)
        
        # Weekly goals
        st.subheader("Weekly Goals")
        for i, goal in enumerate(study_plan['weekly_goals'], 1):
            st.markdown(f"**Week {i}:** {goal.split(': ', 1)[1] if ': ' in goal else goal}")
        
        # Resources
        st.subheader("Recommended Resources")
        for skill, resources in study_plan['resources'].items():
            with st.expander(f"{skill.title()} Resources"):
                for resource in resources:
                    st.markdown(f"- {resource}")

# Vocabulary Builder Page
elif page == "📖 Vocabulary Builder":
    st.header("Vocabulary Builder / بناء المفردات")
    
    level = st.selectbox(
        "Select your level",
        ["Beginner", "Intermediate", "Advanced"]
    )
    
    vocab_data = st.session_state.ielts_model.get_vocabulary_builder(level.lower())
    
    st.subheader(f"{level} Level Vocabulary")
    
    for category, words in vocab_data['vocabulary_list'].items():
        with st.expander(f"{category.title()} Words"):
            
            # Display words in a nice format
            for i, word in enumerate(words, 1):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**{i}. {word}**")
                
                with col2:
                    # Get translation if Arabic mode
                    if st.session_state.language == 'arabic':
                        translation = st.session_state.ielts_model.translate_to_arabic(word)
                        st.markdown(f"*{translation}*")
                    
                    # Add example sentence button
                    if st.button(f"Example for '{word}'", key=f"example_{word}"):
                        example = f"Example: The research methodology was comprehensive and well-designed."
                        st.info(example)
    
    # Practice exercises
    st.subheader("Practice Exercises")
    
    exercises = vocab_data['exercises']
    selected_exercise = st.selectbox("Choose an exercise:", exercises)
    
    if selected_exercise == "Write sentences using each word":
        st.write("Write a sentence for each word below:")
        selected_words = vocab_data['vocabulary_list']['academic'][:3]  # First 3 words
        
        for word in selected_words:
            sentence = st.text_area(f"Write a sentence with '{word}':", key=f"sentence_{word}")
            if sentence:
                st.success(f"Great! Your sentence: {sentence}")

# Translator Page
elif page == "🔄 Translator":
    st.header("Arabic-English Translator / المترجم العربي-الإنجليزي")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("English to Arabic")
        english_text = st.text_area("Enter English text:", height=150)
        
        if st.button("Translate to Arabic") and english_text:
            arabic_translation = st.session_state.ielts_model.translate_to_arabic(english_text)
            st.markdown(f"""
            <div class="arabic-text">
                {arabic_translation}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Common IELTS Terms")
        
        terms = {
            "Reading": "القراءة",
            "Writing": "الكتابة", 
            "Listening": "الاستماع",
            "Speaking": "المحادثة",
            "Multiple Choice": "اختيار متعدد",
            "True/False": "صحيح/خطأ",
            "Essay": "مقال",
            "Graph": "رسم بياني",
            "Chart": "مخطط",
            "Summary": "ملخص"
        }
        
        st.subheader("مصطلحات الآيلتس الشائعة")
        for english, arabic in terms.items():
            st.markdown(f"**{english}** - {arabic}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🇴🇲 Made for Omani Students | صُنع للطلاب العمانيين</p>
    <p>Good luck with your IELTS preparation! | حظاً موفقاً في تحضيرك للآيلتس!</p>
</div>
""", unsafe_allow_html=True)