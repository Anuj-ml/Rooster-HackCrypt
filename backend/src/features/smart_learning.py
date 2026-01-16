"""
Smart Learning Features

Provides advanced tutoring capabilities:
1. Socratic Hints - Guiding questions instead of direct answers
2. AI Sensei - Session analysis and personalized feedback
"""

from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from src.models.schemas import HintRequest, AnalysisRequest, QuizResultItem


class SocraticTutor:
    """
    Generates Socratic hints - guiding questions that help students
    discover answers themselves without revealing the solution directly.
    
    Based on the Socratic method of teaching through questioning.
    """
    
    def __init__(self, llm):
        """
        Initialize the Socratic Tutor.
        
        Args:
            llm: Language model for generating hints
        """
        self.llm = llm
    
    def generate_hint(self, request: HintRequest) -> dict:
        """
        Generate a Socratic hint for a student's question.
        
        Instead of revealing the answer, asks a guiding question that
        helps the student think through the problem.
        
        Args:
            request: HintRequest with question, correct_answer, and optional student_answer
            
        Returns:
            Dictionary with the hint question
        """
        # Build the prompt based on whether student provided an answer
        if request.student_answer:
            context = f"""You are a helpful Socratic tutor. A student is trying to answer: '{request.question}'.
The correct answer is: '{request.correct_answer}'.
The student incorrectly guessed: '{request.student_answer}'.

Task: Provide a single, short guiding question that helps the student figure out the answer themselves. 
Do NOT reveal the answer directly. Keep it under 20 words.
Focus on pointing out what they should reconsider or think about differently."""
        else:
            context = f"""You are a helpful Socratic tutor. A student is trying to answer: '{request.question}'.
The correct answer is: '{request.correct_answer}'.

Task: Provide a single, short guiding question that helps the student figure out the answer themselves. 
Do NOT reveal the answer directly. Keep it under 20 words.
Ask a question that guides their thinking in the right direction."""
        
        prompt = ChatPromptTemplate.from_template("{context}\n\nProvide only the guiding question:")
        
        try:
            print(f"   💡 Generating Socratic hint for: '{request.question[:50]}...'")
            
            response = self.llm.invoke(prompt.format(context=context))
            hint = response.content.strip()
            
            # Remove quotes if the LLM wrapped the hint in them
            if hint.startswith('"') and hint.endswith('"'):
                hint = hint[1:-1]
            if hint.startswith("'") and hint.endswith("'"):
                hint = hint[1:-1]
            
            print(f"   ✓ Generated hint ({len(hint)} characters)")
            
            return {"hint": hint}
            
        except Exception as e:
            print(f"   ✗ Hint generation failed: {str(e)[:200]}")
            return {
                "hint": "What key information from the question can help you solve this?"
            }


class SessionAnalyzer:
    """
    AI Sensei - Analyzes quiz session results to identify learning gaps
    and provide personalized, constructive feedback.
    
    Focuses on incorrect answers to pinpoint weak spots and suggest
    specific areas for review.
    """
    
    def __init__(self, llm):
        """
        Initialize the Session Analyzer.
        
        Args:
            llm: Language model for generating analysis
        """
        self.llm = llm
    
    def analyze_session(self, request: AnalysisRequest) -> dict:
        """
        Analyze a batch of quiz results to identify weak spots.
        
        Provides qualitative feedback on what concepts the student
        is struggling with and constructive advice on what to review.
        
        Args:
            request: AnalysisRequest with list of quiz results
            
        Returns:
            Dictionary with feedback and statistics
        """
        if not request.results:
            return {
                "feedback": "No quiz results to analyze. Complete a quiz first!",
                "total_questions": 0,
                "correct_count": 0,
                "incorrect_count": 0,
                "accuracy": 0.0
            }
        
        # Calculate statistics
        total = len(request.results)
        correct = sum(1 for r in request.results if r.is_correct)
        incorrect = total - correct
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        # If all correct, return congratulatory message without LLM call
        if incorrect == 0:
            return {
                "feedback": "🎉 Perfect score! You've mastered this topic. Keep up the excellent work! "
                           "Challenge yourself with harder difficulty levels or explore new topics.",
                "total_questions": total,
                "correct_count": correct,
                "incorrect_count": 0,
                "accuracy": 100.0
            }
        
        # Filter to get only incorrect answers
        incorrect_items = [
            {
                "question": r.question,
                "user_answer": r.user_answer,
                "correct_answer": r.correct_answer
            }
            for r in request.results
            if not r.is_correct
        ]
        
        # Prepare prompt for LLM
        incorrect_summary = "\n".join([
            f"Q: {item['question']}\n"
            f"Student answered: {item['user_answer']}\n"
            f"Correct answer: {item['correct_answer']}\n"
            for item in incorrect_items
        ])
        
        prompt = ChatPromptTemplate.from_template("""Analyze these incorrect quiz attempts:

{incorrect_items}

The student got {incorrect_count} out of {total_questions} questions wrong ({accuracy:.1f}% accuracy).

Task:
1. Identify the core concept or pattern the student is misunderstanding (be specific, e.g., 'calculation of velocity' or 'historical dates' or 'syntax of conditional statements')
2. Give 2-3 sentences of constructive advice on what specific topics to review
3. Be encouraging but direct - focus on actionable next steps

Provide your analysis:""")
        
        try:
            print(f"   🧠 Analyzing session: {total} questions, {incorrect} incorrect")
            
            response = self.llm.invoke(
                prompt.format(
                    incorrect_items=incorrect_summary,
                    incorrect_count=incorrect,
                    total_questions=total,
                    accuracy=accuracy
                )
            )
            
            feedback = response.content.strip()
            
            print(f"   ✓ Analysis generated ({len(feedback)} characters)")
            
            return {
                "feedback": feedback,
                "total_questions": total,
                "correct_count": correct,
                "incorrect_count": incorrect,
                "accuracy": round(accuracy, 2)
            }
            
        except Exception as e:
            print(f"   ✗ Analysis failed: {str(e)[:200]}")
            return {
                "feedback": f"You got {correct}/{total} questions correct ({accuracy:.1f}%). "
                           f"Review the {incorrect} incorrect answers to identify patterns in your mistakes.",
                "total_questions": total,
                "correct_count": correct,
                "incorrect_count": incorrect,
                "accuracy": round(accuracy, 2)
            }
