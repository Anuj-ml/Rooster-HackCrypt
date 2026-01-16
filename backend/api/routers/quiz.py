# backend/api/routers/quiz.py

"""
Quiz and session management endpoints.
Handle adaptive/grind sessions and quiz generation.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List

from ..models.requests import (
    AdaptiveSessionRequest,
    GrindSessionRequest,
    QuizGenerateRequest,
    QuizSubmitRequest
)
from ..models.responses import (
    APIResponse,
    SessionCreatedResponse,
    SessionInfo,
    SessionListResponse,
    SessionStatsResponse,
    QuizResponse,
    QuizQuestionResponse,
    QuizSubmitResponse
)
from ..services.orchestrator import QuizOrchestrator
from ..dependencies import get_quiz_orchestrator, get_knowledge_base

router = APIRouter(prefix="/sessions", tags=["Sessions & Quizzes"])


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@router.post(
    "/adaptive",
    response_model=APIResponse[SessionCreatedResponse],
    summary="Create Adaptive Session",
    description="Start a new adaptive learning session with auto-adjusting difficulty"
)
async def create_adaptive_session(
    request: AdaptiveSessionRequest,
    orchestrator: QuizOrchestrator = Depends(get_quiz_orchestrator),
    kb=Depends(get_knowledge_base)
):
    """
    Create a new adaptive learning session.
    
    The adaptive engine will automatically adjust difficulty based on performance:
    - Mastery > 80% + streak > 2 → Increase difficulty
    - Mastery < 40% + streak < -2 → Decrease difficulty
    
    Args:
        request: Session configuration including user_id, source_id, topic, initial_difficulty
    
    Returns:
        Session ID and initial configuration
    """
    # Validate source exists
    sources = kb.get_all_pdf_sources()
    if request.source_id not in sources:
        raise HTTPException(
            status_code=404,
            detail=f"Source '{request.source_id}' not found. Available: {sources}"
        )
    
    try:
        result = await orchestrator.create_adaptive_session(
            user_id=request.user_id,
            source_id=request.source_id,
            topic=request.topic,
            initial_difficulty=request.initial_difficulty.value
        )
        
        return APIResponse(
            success=True,
            message="Adaptive session created successfully",
            data=SessionCreatedResponse(
                session_id=result["session_id"],
                mode="ADAPTIVE",
                initial_difficulty=request.initial_difficulty.value,
                topic=request.topic,
                source_id=request.source_id
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post(
    "/grind",
    response_model=APIResponse[SessionCreatedResponse],
    summary="Create Grind Session",
    description="Start a grind mode session for focused practice"
)
async def create_grind_session(
    request: GrindSessionRequest,
    orchestrator: QuizOrchestrator = Depends(get_quiz_orchestrator),
    kb=Depends(get_knowledge_base)
):
    """
    Create a new grind mode session.
    
    Grind mode allows:
    - Fixed difficulty or slow dynamic adjustment
    - Focused practice on specific topics
    - No mastery-based progression (unless dynamic_difficulty=True)
    
    Args:
        request: Session configuration including difficulty and dynamic_difficulty flag
    
    Returns:
        Session ID and initial configuration
    """
    # Validate source exists
    sources = kb.get_all_pdf_sources()
    if request.source_id not in sources:
        raise HTTPException(
            status_code=404,
            detail=f"Source '{request.source_id}' not found. Available: {sources}"
        )
    
    try:
        result = await orchestrator.create_grind_session(
            user_id=request.user_id,
            source_id=request.source_id,
            topic=request.topic,
            difficulty=request.difficulty.value,
            dynamic_difficulty=request.dynamic_difficulty
        )
        
        return APIResponse(
            success=True,
            message="Grind session created successfully",
            data=SessionCreatedResponse(
                session_id=result["session_id"],
                mode="GRIND",
                initial_difficulty=request.difficulty.value,
                topic=request.topic,
                source_id=request.source_id
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get(
    "",
    response_model=APIResponse[SessionListResponse],
    summary="List Active Sessions",
    description="Get all active learning sessions"
)
async def list_sessions(
    orchestrator: QuizOrchestrator = Depends(get_quiz_orchestrator)
):
    """
    List all active sessions with basic info.
    
    Returns:
        List of session IDs and their metadata
    """
    try:
        sessions = await orchestrator.list_sessions()
        
        return APIResponse(
            success=True,
            message=f"Found {len(sessions)} active sessions",
            data=SessionListResponse(
                sessions=sessions,
                count=len(sessions)
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get(
    "/{session_id}",
    response_model=APIResponse[SessionStatsResponse],
    summary="Get Session Stats",
    description="Get detailed statistics for a specific session"
)
async def get_session_stats(
    session_id: str = Path(..., description="Session identifier"),
    orchestrator: QuizOrchestrator = Depends(get_quiz_orchestrator)
):
    """
    Get detailed statistics for a session.
    
    Includes:
    - Current difficulty
    - Total questions answered
    - Correct answers
    - Mastery score
    - Streak
    - Difficulty history
    
    Args:
        session_id: The session identifier
    
    Returns:
        Comprehensive session statistics
    """
    try:
        stats = await orchestrator.get_session_stats(session_id)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{session_id}' not found"
            )
        
        return APIResponse(
            success=True,
            message="Session stats retrieved",
            data=SessionStatsResponse(**stats)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session stats: {str(e)}"
        )


@router.delete(
    "/{session_id}",
    response_model=APIResponse,
    summary="Delete Session",
    description="Delete a learning session"
)
async def delete_session(
    session_id: str = Path(..., description="Session identifier"),
    orchestrator: QuizOrchestrator = Depends(get_quiz_orchestrator)
):
    """
    Delete a session and all its state.
    
    Args:
        session_id: The session identifier
    
    Returns:
        Success confirmation
    """
    try:
        success = await orchestrator.delete_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{session_id}' not found"
            )
        
        return APIResponse(
            success=True,
            message=f"Session '{session_id}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


# ============================================================================
# QUIZ GENERATION & SUBMISSION
# ============================================================================

@router.post(
    "/{session_id}/quiz",
    response_model=APIResponse[QuizResponse],
    summary="Generate Quiz",
    description="Generate a new quiz batch for the session"
)
async def generate_quiz(
    session_id: str = Path(..., description="Session identifier"),
    request: QuizGenerateRequest = QuizGenerateRequest(),
    orchestrator: QuizOrchestrator = Depends(get_quiz_orchestrator)
):
    """
    Generate a quiz for the given session.
    
    The quiz will be:
    1. Generated at the session's current difficulty level
    2. Based on relevant documents from the session's source material
    3. Grounded in actual content (RAG)
    
    Args:
        session_id: The session identifier
        request: Number of questions to generate (default: 5)
    
    Returns:
        Quiz with questions, options, and correct answers
    """
    try:
        result = await orchestrator.generate_quiz(
            session_id=session_id,
            num_questions=request.num_questions
        )
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate quiz. No context available."
            )
        
        # Convert to response model
        questions = [
            QuizQuestionResponse(
                question=q.question,
                options=q.options[:4],  # Ensure max 4 options
                correct_answer=q.correct_answer,
                explanation=q.explanation
            )
            for q in result["questions"]
        ]
        
        return APIResponse(
            success=True,
            message=f"Generated {len(questions)} questions",
            data=QuizResponse(
                session_id=session_id,
                difficulty=result["difficulty"],
                questions=questions,
                question_count=len(questions)
            )
        )
        
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate quiz: {str(e)}"
        )


@router.post(
    "/{session_id}/submit",
    response_model=APIResponse[QuizSubmitResponse],
    summary="Submit Quiz Answers",
    description="Submit answers for a quiz and get feedback"
)
async def submit_quiz(
    session_id: str = Path(..., description="Session identifier"),
    request: QuizSubmitRequest = ...,
    orchestrator: QuizOrchestrator = Depends(get_quiz_orchestrator)
):
    """
    Submit quiz answers and receive feedback.
    
    The system will:
    1. Record the results
    2. Update mastery score
    3. Adjust difficulty if thresholds are met
    4. Return detailed feedback
    
    Args:
        session_id: The session identifier
        request: List of boolean answers (True=correct)
    
    Returns:
        Score, updated stats, and whether difficulty changed
    """
    try:
        result = await orchestrator.submit_results(
            session_id=session_id,
            answers=request.answers
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Session '{session_id}' not found"
            )
        
        return APIResponse(
            success=True,
            message="Quiz submitted successfully",
            data=QuizSubmitResponse(
                session_id=session_id,
                correct_count=result["correct_count"],
                total_count=result["total_count"],
                score_percentage=result["score_percentage"],
                new_difficulty=result["new_difficulty"],
                mastery_score=result["mastery_score"],
                streak=result["streak"],
                difficulty_changed=result["difficulty_changed"],
                feedback_message=result["feedback_message"]
            )
        )
        
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit quiz: {str(e)}"
        )
