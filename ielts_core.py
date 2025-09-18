import openai
import random
import json
from datetime import datetime
from typing import Dict, List, Tuple
import requests
from dataclasses import dataclass

@dataclass
class IELTSQuestion:
    question_type: str
    difficulty: str
    question: str
    options: List[str] = None
    correct_answer: str = None
    explanation: str = None
    arabic_translation: str = None

class IELTSAIModel:
    def __init__(self, openai_api_key: str, google_translate_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.google_translate_api_key = google_translate_api_key
        openai.api_key = openai_api_key
        
        # IELTS Syllabus Structure
        self.syllabus = {
            "listening": {
                "sections": ["Section 1: Social Context", "Section 2: General Context", 
                           "Section 3: Academic Context", "Section 4: Academic Lecture"],
                "question_types": ["Multiple Choice", "Form Completion", "Map Labeling", 
                                 "Matching", "Short Answer", "Note Completion"]
            },
            "reading": {
                "sections": ["Academic Reading", "General Training Reading"],
                "question_types": ["Multiple Choice", "True/False/Not Given", 
                                 "Matching Headings", "Gap Fill", "Summary Completion",
                                 "Sentence Completion", "Diagram Labeling"]
            },
            "writing": {
                "sections": ["Task 1", "Task 2"],
                "task1_types": ["Line Graph", "Bar Chart", "Pie Chart", "Table", 
                              "Process Diagram", "Map Changes"],
                "task2_types": ["Opinion Essays", "Discussion Essays", "Problem-Solution",
                              "Advantages-Disadvantages", "Two-Part Questions"]
            },
            "speaking": {
                "sections": ["Part 1: Introduction", "Part 2: Long Turn", "Part 3: Discussion"],
                "topics": ["Family", "Work", "Education", "Travel", "Technology", 
                         "Environment", "Health", "Culture", "Sports", "Food"]
            }
        }
        
        # Previous Year Questions Database
        self.pyq_database = {
            "listening": [
                {
                    "type": "Multiple Choice",
                    "question": "What time does the library close on weekends?",
                    "options": ["A) 6:00 PM", "B) 8:00 PM", "C) 9:00 PM", "D) 10:00 PM"],
                    "answer": "B",
                    "difficulty": "easy"
                },
                {
                    "type": "Form Completion",
                    "question": "Complete the form with the missing information about the student accommodation.",
                    "answer": "shared kitchen",
                    "difficulty": "medium"
                }
            ],
            "reading": [
                {
                    "type": "True/False/Not Given",
                    "question": "The research shows that climate change affects bird migration patterns.",
                    "answer": "True",
                    "difficulty": "medium",
                    "passage": "Recent studies have demonstrated significant impacts of climate change on avian migration routes..."
                }
            ],
            "writing": [
                {
                    "type": "Task 1",
                    "question": "The chart shows the percentage of households with different types of internet connections in three countries. Summarize the information.",
                    "difficulty": "medium"
                },
                {
                    "type": "Task 2", 
                    "question": "Some people think that universities should accept equal numbers of male and female students in every subject. To what extent do you agree or disagree?",
                    "difficulty": "hard"
                }
            ],
            "speaking": [
                {
                    "type": "Part 1",
                    "question": "Do you prefer to study in the morning or evening? Why?",
                    "difficulty": "easy"
                },
                {
                    "type": "Part 2",
                    "question": "Describe a memorable journey you have taken. You should say: where you went, who you went with, what you did there, and explain why it was memorable.",
                    "difficulty": "medium"
                }
            ]
        }

    def translate_to_arabic(self, text: str) -> str:
        """Translate English text to Arabic using Google Translate API"""
        if not self.google_translate_api_key:
            # Fallback translations for common phrases
            common_translations = {
                "Multiple Choice": "اختيار متعدد",
                "True/False/Not Given": "صحيح/خطأ/غير مذكور", 
                "Reading": "القراءة",
                "Writing": "الكتابة",
                "Listening": "الاستماع",
                "Speaking": "المحادثة",
                "Question": "السؤال",
                "Answer": "الإجابة",
                "Difficulty": "المستوى",
                "Easy": "سهل",
                "Medium": "متوسط", 
                "Hard": "صعب"
            }
            return common_translations.get(text, f"[Arabic: {text}]")
        
        try:
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': self.google_translate_api_key,
                'q': text,
                'source': 'en',
                'target': 'ar'
            }
            response = requests.post(url, data=params)
            result = response.json()
            return result['data']['translations'][0]['translatedText']
        except Exception as e:
            return f"[Translation Error: {text}]"

    def generate_question_with_ai(self, section: str, question_type: str, difficulty: str) -> IELTSQuestion:
        """Generate new questions using OpenAI API based on PYQ patterns"""
        
        prompt = f"""
        Generate an IELTS {section} question of type '{question_type}' with {difficulty} difficulty level.
        Make it similar to actual IELTS exam questions, suitable for Omani students.
        
        Format your response as JSON with these fields:
        - question: the main question text
        - options: list of options (if applicable)  
        - correct_answer: the correct answer
        - explanation: brief explanation of the answer
        
        Section: {section}
        Type: {question_type}
        Difficulty: {difficulty}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            question_data = json.loads(content)
            
            question = IELTSQuestion(
                question_type=question_type,
                difficulty=difficulty,
                question=question_data["question"],
                options=question_data.get("options"),
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"],
                arabic_translation=self.translate_to_arabic(question_data["question"])
            )
            
            return question
            
        except Exception as e:
            # Fallback to PYQ if AI generation fails
            return self.get_pyq_question(section, question_type)

    def get_pyq_question(self, section: str, question_type: str = None) -> IELTSQuestion:
        """Get a random previous year question"""
        section_questions = self.pyq_database.get(section, [])
        
        if question_type:
            filtered_questions = [q for q in section_questions if q["type"] == question_type]
            section_questions = filtered_questions if filtered_questions else section_questions
        
        if not section_questions:
            return IELTSQuestion(
                question_type="Sample",
                difficulty="medium", 
                question="No questions available for this section yet.",
                arabic_translation="لا توجد أسئلة متاحة لهذا القسم حتى الآن."
            )
        
        pyq = random.choice(section_questions)
        
        question = IELTSQuestion(
            question_type=pyq["type"],
            difficulty=pyq.get("difficulty", "medium"),
            question=pyq["question"],
            options=pyq.get("options"),
            correct_answer=pyq.get("answer"),
            explanation=pyq.get("explanation"),
            arabic_translation=self.translate_to_arabic(pyq["question"])
        )
        
        return question

    def evaluate_answer(self, question: IELTSQuestion, user_answer: str) -> Dict:
        """Evaluate user's answer and provide feedback"""
        is_correct = False
        score = 0
        
        if question.correct_answer:
            is_correct = user_answer.strip().lower() == question.correct_answer.lower()
            score = 1 if is_correct else 0
        
        feedback = {
            "is_correct": is_correct,
            "score": score,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "user_answer": user_answer
        }
        
        return feedback

    def get_study_plan(self, target_band: float, current_level: str, weeks: int) -> Dict:
        """Generate a personalized study plan"""
        
        plan = {
            "target_band": target_band,
            "current_level": current_level,
            "duration_weeks": weeks,
            "daily_schedule": {
                "listening": "30 minutes",
                "reading": "45 minutes", 
                "writing": "30 minutes",
                "speaking": "20 minutes",
                "vocabulary": "15 minutes"
            },
            "weekly_goals": [],
            "resources": {
                "listening": ["BBC Learning English", "IELTS Podcasts"],
                "reading": ["Academic articles", "Cambridge IELTS books"],
                "writing": ["Essay templates", "Task 1 samples"],
                "speaking": ["Recording practice", "Topic discussions"]
            }
        }
        
        # Generate weekly goals based on target band
        for week in range(1, weeks + 1):
            goal = f"Week {week}: Focus on {'basic skills' if week <= 2 else 'advanced techniques' if week <= 4 else 'mock tests and refinement'}"
            plan["weekly_goals"].append(goal)
        
        return plan

    def get_band_score_prediction(self, practice_scores: Dict[str, List[float]]) -> Dict:
        """Predict likely IELTS band score based on practice performance"""
        
        section_scores = {}
        for section, scores in practice_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                # Convert to IELTS band scale (1-9)
                band_score = min(9.0, max(1.0, (avg_score * 9)))
                section_scores[section] = round(band_score, 0.5)
        
        overall_band = sum(section_scores.values()) / len(section_scores) if section_scores else 5.0
        
        prediction = {
            "section_scores": section_scores,
            "overall_band": round(overall_band, 0.5),
            "improvement_areas": [],
            "strengths": []
        }
        
        # Identify improvement areas and strengths
        for section, score in section_scores.items():
            if score < 6.0:
                prediction["improvement_areas"].append(f"{section}: {score}")
            elif score >= 7.0:
                prediction["strengths"].append(f"{section}: {score}")
        
        return prediction

    def get_vocabulary_builder(self, level: str) -> Dict:
        """Get vocabulary building exercises"""
        
        vocab_sets = {
            "beginner": {
                "academic": ["analyze", "research", "hypothesis", "methodology", "conclusion"],
                "general": ["accommodation", "facility", "convenient", "particular", "specific"]
            },
            "intermediate": {
                "academic": ["empirical", "paradigm", "correlation", "significant", "phenomenon"], 
                "general": ["substantial", "comprehensive", "inevitable", "preliminary", "subsequent"]
            },
            "advanced": {
                "academic": ["quintessential", "ubiquitous", "paradigmatic", "multifaceted", "intrinsic"],
                "general": ["meticulous", "articulate", "eloquent", "profound", "sophisticated"]
            }
        }
        
        selected_vocab = vocab_sets.get(level, vocab_sets["intermediate"])
        
        exercises = {
            "vocabulary_list": selected_vocab,
            "exercises": [
                "Write sentences using each word",
                "Find synonyms and antonyms", 
                "Use in IELTS writing tasks",
                "Practice pronunciation"
            ],
            "level": level
        }
        
        return exercises