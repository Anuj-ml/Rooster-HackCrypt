# backend/difficulty_engine.py

"""
Rooster-HackCrypt: Dynamic Difficulty Engine

This module handles all difficulty adjustment logic for both modes:
- ADAPTIVE mode: Adjusts difficulty based on recent performance
- GRIND mode: Optionally adjusts difficulty but at a slower interval

All intervals and thresholds are parameterized for flexibility.
"""

from typing import Dict, Any, Optional, List


# ═══════════════════════════════════════════════════════════════════════════════
# DIFFICULTY LEVELS
# ═══════════════════════════════════════════════════════════════════════════════

DIFFICULTY_LEVELS = ["EASY", "MEDIUM", "HARD"]


def get_next_difficulty(current: str, direction: str) -> str:
    """
    Get the next difficulty level based on direction.
    
    Args:
        current: Current difficulty level (EASY, MEDIUM, HARD)
        direction: Either "UP" or "DOWN"
        
    Returns:
        New difficulty level
    """
    idx = DIFFICULTY_LEVELS.index(current.upper())
    
    if direction.upper() == "UP":
        new_idx = min(idx + 1, len(DIFFICULTY_LEVELS) - 1)
    elif direction.upper() == "DOWN":
        new_idx = max(idx - 1, 0)
    else:
        new_idx = idx
    
    return DIFFICULTY_LEVELS[new_idx]


# ═══════════════════════════════════════════════════════════════════════════════
# DIFFICULTY ADJUSTMENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_difficulty_adjustment(
    accuracy: float,
    current_difficulty: str,
    level_up_threshold: float = 0.8,
    level_down_threshold: float = 0.4
) -> Dict[str, Any]:
    """
    Calculate whether difficulty should be adjusted based on accuracy.
    
    Args:
        accuracy: Quiz accuracy (0.0 to 1.0)
        current_difficulty: Current difficulty level
        level_up_threshold: Accuracy threshold to level up (default: 0.8 = 80%)
        level_down_threshold: Accuracy threshold to level down (default: 0.4 = 40%)
        
    Returns:
        Dictionary with adjustment details:
        - should_adjust: bool
        - direction: "UP", "DOWN", or "NONE"
        - new_difficulty: str
        - old_difficulty: str
    """
    old_difficulty = current_difficulty.upper()
    direction = "NONE"
    should_adjust = False
    
    if accuracy >= level_up_threshold:
        direction = "UP"
        should_adjust = old_difficulty != "HARD"
    elif accuracy <= level_down_threshold:
        direction = "DOWN"
        should_adjust = old_difficulty != "EASY"
    
    new_difficulty = get_next_difficulty(old_difficulty, direction) if should_adjust else old_difficulty
    
    return {
        "should_adjust": should_adjust,
        "direction": direction,
        "old_difficulty": old_difficulty,
        "new_difficulty": new_difficulty,
        "accuracy": accuracy
    }


def should_evaluate_difficulty(
    batch_count: int,
    evaluation_interval: int = 2
) -> bool:
    """
    Determine if difficulty should be evaluated based on batch count.
    
    Args:
        batch_count: Number of batches/quizzes completed
        evaluation_interval: How many batches between difficulty evaluations
                           (default: 2 for quiz mode)
                           (use 4 for grind mode)
    
    Returns:
        True if difficulty should be evaluated this batch
    """
    return batch_count > 0 and batch_count % evaluation_interval == 0


def apply_adaptive_difficulty(
    accuracy: float,
    current_difficulty: str,
    batch_count: int,
    evaluation_interval: int = 2,
    level_up_threshold: float = 0.8,
    level_down_threshold: float = 0.4
) -> Dict[str, Any]:
    """
    Apply adaptive difficulty logic for quiz mode.
    
    Difficulty changes after every N batches (default: 2) based on performance.
    
    Args:
        accuracy: Quiz accuracy (0.0 to 1.0)
        current_difficulty: Current difficulty level
        batch_count: Number of batches completed (after this one)
        evaluation_interval: Batches between difficulty evaluations (default: 2)
        level_up_threshold: Accuracy threshold to level up (default: 0.8)
        level_down_threshold: Accuracy threshold to level down (default: 0.4)
        
    Returns:
        Dictionary with:
        - new_difficulty: Updated difficulty
        - difficulty_changed: bool
        - reason: Explanation string
    """
    if not should_evaluate_difficulty(batch_count, evaluation_interval):
        return {
            "new_difficulty": current_difficulty.upper(),
            "difficulty_changed": False,
            "reason": f"Waiting for evaluation interval ({batch_count}/{evaluation_interval} batches)"
        }
    
    adjustment = calculate_difficulty_adjustment(
        accuracy=accuracy,
        current_difficulty=current_difficulty,
        level_up_threshold=level_up_threshold,
        level_down_threshold=level_down_threshold
    )
    
    if adjustment["should_adjust"]:
        reason = f"Performance {accuracy:.0%} triggered {adjustment['direction']} adjustment"
    else:
        reason = f"Performance {accuracy:.0%} - staying at {current_difficulty}"
    
    return {
        "new_difficulty": adjustment["new_difficulty"],
        "difficulty_changed": adjustment["should_adjust"],
        "reason": reason,
        "direction": adjustment["direction"]
    }


def apply_grind_difficulty(
    recent_accuracies: List[float],
    current_difficulty: str,
    batch_count: int,
    evaluation_interval: int = 4,
    level_up_threshold: float = 0.8,
    level_down_threshold: float = 0.4,
    dynamic_enabled: bool = True
) -> Dict[str, Any]:
    """
    Apply grind mode difficulty logic with optional dynamic adjustment.
    
    In grind mode, difficulty can optionally change but at a slower interval
    (default: every 4 batches instead of 2).
    
    Args:
        recent_accuracies: List of recent accuracy values for averaging
        current_difficulty: Current difficulty level
        batch_count: Number of batches completed
        evaluation_interval: Batches between evaluations (default: 4 for grind)
        level_up_threshold: Accuracy threshold to level up (default: 0.8)
        level_down_threshold: Accuracy threshold to level down (default: 0.4)
        dynamic_enabled: Whether dynamic difficulty is enabled (default: True)
        
    Returns:
        Dictionary with:
        - new_difficulty: Updated difficulty
        - difficulty_changed: bool
        - reason: Explanation string
    """
    if not dynamic_enabled:
        return {
            "new_difficulty": current_difficulty.upper(),
            "difficulty_changed": False,
            "reason": "Dynamic difficulty disabled in grind mode"
        }
    
    if not should_evaluate_difficulty(batch_count, evaluation_interval):
        return {
            "new_difficulty": current_difficulty.upper(),
            "difficulty_changed": False,
            "reason": f"Waiting for evaluation interval ({batch_count}/{evaluation_interval} batches)"
        }
    
    # Use average of recent accuracies for grind mode
    if recent_accuracies:
        avg_accuracy = sum(recent_accuracies) / len(recent_accuracies)
    else:
        avg_accuracy = 0.0
    
    adjustment = calculate_difficulty_adjustment(
        accuracy=avg_accuracy,
        current_difficulty=current_difficulty,
        level_up_threshold=level_up_threshold,
        level_down_threshold=level_down_threshold
    )
    
    if adjustment["should_adjust"]:
        reason = f"Average performance {avg_accuracy:.0%} over {len(recent_accuracies)} batches triggered {adjustment['direction']}"
    else:
        reason = f"Average performance {avg_accuracy:.0%} - staying at {current_difficulty}"
    
    return {
        "new_difficulty": adjustment["new_difficulty"],
        "difficulty_changed": adjustment["should_adjust"],
        "reason": reason,
        "direction": adjustment.get("direction", "NONE"),
        "average_accuracy": avg_accuracy
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STREAK LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_streak(
    accuracy: float,
    current_streak: int,
    streak_threshold: float = 0.8
) -> Dict[str, Any]:
    """
    Calculate streak based on accuracy.
    
    Args:
        accuracy: Quiz accuracy (0.0 to 1.0)
        current_streak: Current streak value
        streak_threshold: Minimum accuracy to maintain/build streak (default: 0.8)
        
    Returns:
        Dictionary with:
        - new_streak: Updated streak value
        - streak_broken: bool
        - streak_continued: bool
    """
    if accuracy >= streak_threshold:
        return {
            "new_streak": current_streak + 1,
            "streak_broken": False,
            "streak_continued": True
        }
    else:
        return {
            "new_streak": 0,
            "streak_broken": current_streak > 0,
            "streak_continued": False
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MASTERY CALCULATION
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_mastery_score(
    accuracy: float,
    current_mastery: float,
    current_difficulty: str,
    weight_new: float = 0.3,
    difficulty_bonus: Dict[str, float] = None
) -> float:
    """
    Calculate updated mastery score.
    
    Mastery is weighted by difficulty - higher difficulty contributes more.
    
    Args:
        accuracy: Quiz accuracy (0.0 to 1.0)
        current_mastery: Current mastery score (0.0 to 1.0)
        current_difficulty: Current difficulty level
        weight_new: Weight for new accuracy vs existing mastery (default: 0.3)
        difficulty_bonus: Dict mapping difficulty to bonus multiplier
                         (default: {"EASY": 0.8, "MEDIUM": 1.0, "HARD": 1.2})
        
    Returns:
        Updated mastery score (0.0 to 1.0)
    """
    if difficulty_bonus is None:
        difficulty_bonus = {
            "EASY": 0.8,
            "MEDIUM": 1.0,
            "HARD": 1.2
        }
    
    bonus = difficulty_bonus.get(current_difficulty.upper(), 1.0)
    weighted_accuracy = accuracy * bonus
    
    new_mastery = (1 - weight_new) * current_mastery + weight_new * weighted_accuracy
    
    return min(1.0, max(0.0, new_mastery))


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_QUIZ_CONFIG = {
    "evaluation_interval": 2,  # Evaluate difficulty every 2 batches
    "level_up_threshold": 0.8,
    "level_down_threshold": 0.4,
    "streak_threshold": 0.8,
    "mastery_weight": 0.3
}

DEFAULT_GRIND_CONFIG = {
    "evaluation_interval": 4,  # Evaluate difficulty every 4 batches (slower)
    "level_up_threshold": 0.8,
    "level_down_threshold": 0.4,
    "streak_threshold": 0.8,
    "mastery_weight": 0.3,
    "dynamic_enabled": True
}


def get_quiz_config(
    evaluation_interval: int = None,
    level_up_threshold: float = None,
    level_down_threshold: float = None,
    streak_threshold: float = None,
    mastery_weight: float = None
) -> Dict[str, Any]:
    """
    Get quiz mode configuration with optional overrides.
    
    Args:
        evaluation_interval: Override default (2 batches)
        level_up_threshold: Override default (0.8)
        level_down_threshold: Override default (0.4)
        streak_threshold: Override default (0.8)
        mastery_weight: Override default (0.3)
        
    Returns:
        Configuration dictionary
    """
    config = DEFAULT_QUIZ_CONFIG.copy()
    
    if evaluation_interval is not None:
        config["evaluation_interval"] = evaluation_interval
    if level_up_threshold is not None:
        config["level_up_threshold"] = level_up_threshold
    if level_down_threshold is not None:
        config["level_down_threshold"] = level_down_threshold
    if streak_threshold is not None:
        config["streak_threshold"] = streak_threshold
    if mastery_weight is not None:
        config["mastery_weight"] = mastery_weight
    
    return config


def get_grind_config(
    evaluation_interval: int = None,
    level_up_threshold: float = None,
    level_down_threshold: float = None,
    streak_threshold: float = None,
    mastery_weight: float = None,
    dynamic_enabled: bool = None
) -> Dict[str, Any]:
    """
    Get grind mode configuration with optional overrides.
    
    Args:
        evaluation_interval: Override default (4 batches)
        level_up_threshold: Override default (0.8)
        level_down_threshold: Override default (0.4)
        streak_threshold: Override default (0.8)
        mastery_weight: Override default (0.3)
        dynamic_enabled: Override default (True)
        
    Returns:
        Configuration dictionary
    """
    config = DEFAULT_GRIND_CONFIG.copy()
    
    if evaluation_interval is not None:
        config["evaluation_interval"] = evaluation_interval
    if level_up_threshold is not None:
        config["level_up_threshold"] = level_up_threshold
    if level_down_threshold is not None:
        config["level_down_threshold"] = level_down_threshold
    if streak_threshold is not None:
        config["streak_threshold"] = streak_threshold
    if mastery_weight is not None:
        config["mastery_weight"] = mastery_weight
    if dynamic_enabled is not None:
        config["dynamic_enabled"] = dynamic_enabled
    
    return config
