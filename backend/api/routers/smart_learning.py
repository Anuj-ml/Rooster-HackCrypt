"""
Smart Learning API Router

Provides endpoints for advanced tutoring capabilities:
- Socratic hints (guiding questions)
- Session analysis (AI Sensei)
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends

from ..dependencies import get_llm
from ..models.responses import APIResponse
from src.models.schemas import HintRequest, AnalysisRequest
from src.features.smart_learning import SocraticTutor, SessionAnalyzer


router = APIRouter(tags=["Smart Learning"])


# Singleton instances
_socratic_tutor_instance = None
_session_analyzer_instance = None


async def get_socratic_tutor(llm = Depends(get_llm)) -> SocraticTutor:
    """Dependency injection for SocraticTutor with singleton pattern."""
    global _socratic_tutor_instance
    
    if _socratic_tutor_instance is None:
        _socratic_tutor_instance = SocraticTutor(llm=llm)
        print("✓ SocraticTutor initialized")
    
    return _socratic_tutor_instance


async def get_session_analyzer(llm = Depends(get_llm)) -> SessionAnalyzer:
    """Dependency injection for SessionAnalyzer with singleton pattern."""
    global _session_analyzer_instance
    
    if _session_analyzer_instance is None:
        _session_analyzer_instance = SessionAnalyzer(llm=llm)
        print("✓ SessionAnalyzer initialized")
    
    return _session_analyzer_instance


@router.post("/hint/socratic", response_model=APIResponse)
async def generate_socratic_hint(
    request: HintRequest,
    tutor: SocraticTutor = Depends(get_socratic_tutor)
):
    """
    Generate a Socratic hint - a guiding question instead of the direct answer.
    
    **The Socratic Method:**
    Instead of telling students the answer, ask them a question that guides
    their thinking in the right direction. This promotes deeper understanding
    and critical thinking skills.
    
    **Request Body:**
    - **question**: The question the student is trying to answer
    - **correct_answer**: The actual correct answer (not revealed to student)
    - **student_answer**: Optional - the student's incorrect attempt
    
    **Response:**
    - **hint**: A guiding question (under 20 words) that helps the student
    
    **Example:**
    ```
    Question: "What is the capital of France?"
    Student Answer: "London"
    Hint: "Which country is Paris the capital of?"
    ```
    
    **Use Cases:**
    - Student gets quiz question wrong → provide hint instead of explanation
    - Student asks for help → guide them with questions instead of answers
    - Encourage critical thinking and self-discovery
    """
    try:
        # Run synchronous method in thread pool
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            tutor.generate_hint,
            request
        )
        
        return APIResponse(
            success=True,
            message="Socratic hint generated",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate hint: {str(e)}"
        )


@router.post("/analyze-session", response_model=APIResponse)
async def analyze_quiz_session(
    request: AnalysisRequest,
    analyzer: SessionAnalyzer = Depends(get_session_analyzer)
):
    """
    Analyze a quiz session to identify learning gaps and provide personalized feedback.
    
    **AI Sensei** analyzes your quiz performance to:
    - Identify patterns in mistakes
    - Pinpoint weak concepts
    - Provide constructive, actionable advice
    - Encourage continued learning
    
    **Request Body:**
    - **results**: List of quiz results with:
      - question: The quiz question
      - is_correct: Whether student answered correctly
      - user_answer: What the student answered
      - correct_answer: The correct answer
    
    **Response:**
    - **feedback**: Personalized analysis and recommendations
    - **total_questions**: Number of questions analyzed
    - **correct_count**: Number of correct answers
    - **incorrect_count**: Number of mistakes
    - **accuracy**: Percentage score
    
    **Example Response:**
    ```json
    {
      "feedback": "You're struggling with the difference between 'affect' and 'effect'. 
                   Review the rule: 'affect' is usually a verb, 'effect' is usually a noun. 
                   Practice with example sentences to reinforce this distinction.",
      "total_questions": 10,
      "correct_count": 7,
      "incorrect_count": 3,
      "accuracy": 70.0
    }
    ```
    
    **Use Cases:**
    - After completing a quiz → get targeted feedback
    - Identify recurring mistakes → focus study efforts
    - Track progress over multiple sessions
    - Get encouragement and specific next steps
    """
    try:
        # Run synchronous method in thread pool
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            analyzer.analyze_session,
            request
        )
        
        # Determine success message based on performance
        if result["accuracy"] == 100.0:
            message = "Perfect session! All answers correct"
        elif result["accuracy"] >= 70.0:
            message = "Good session analyzed - areas for improvement identified"
        else:
            message = "Session analyzed - significant learning opportunities identified"
        
        return APIResponse(
            success=True,
            message=message,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze session: {str(e)}"
        )
