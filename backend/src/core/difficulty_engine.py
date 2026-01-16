# backend/difficulty_engine.py

"""
Rooster-HackCrypt: Dynamic Difficulty Engine

This module handles all difficulty adjustment logic for both modes:
- ADAPTIVE mode: Adjusts difficulty based on recent performance
- GRIND mode: Optionally adjusts difficulty but at a slower interval

All intervals and thresholds are parameterized for flexibility.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DifficultyConfig:
    """Configuration for difficulty adjustment."""
    evaluation_interval: int = 2
    level_up_threshold: float = 0.8
    level_down_threshold: float = 0.4
    streak_threshold: float = 0.8
    mastery_weight: float = 0.3


@dataclass
class GrindConfig(DifficultyConfig):
    """Configuration for grind mode difficulty."""
    evaluation_interval: int = 4
    dynamic_enabled: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# DIFFICULTY ENGINE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class DifficultyEngine:
    """
    Engine for handling difficulty adjustments.
    
    Manages difficulty levels and provides methods for:
    - Calculating difficulty adjustments based on accuracy
    - Managing streaks
    - Computing mastery scores
    """
    
    DIFFICULTY_LEVELS = ["EASY", "MEDIUM", "HARD"]
    
    DEFAULT_DIFFICULTY_BONUS = {
        "EASY": 0.8,
        "MEDIUM": 1.0,
        "HARD": 1.2
    }
    
    def __init__(self, config: Optional[DifficultyConfig] = None):
        """
        Initialize the difficulty engine.
        
        Args:
            config: Optional configuration (uses defaults if not provided)
        """
        self.config = config or DifficultyConfig()
    
    def get_next_difficulty(self, current: str, direction: str) -> str:
        """
        Get the next difficulty level based on direction.
        
        Args:
            current: Current difficulty level (EASY, MEDIUM, HARD)
            direction: Either "UP" or "DOWN"
            
        Returns:
            New difficulty level
        """
        idx = self.DIFFICULTY_LEVELS.index(current.upper())
        
        if direction.upper() == "UP":
            new_idx = min(idx + 1, len(self.DIFFICULTY_LEVELS) - 1)
        elif direction.upper() == "DOWN":
            new_idx = max(idx - 1, 0)
        else:
            new_idx = idx
        
        return self.DIFFICULTY_LEVELS[new_idx]
    
    def calculate_difficulty_adjustment(
        self,
        accuracy: float,
        current_difficulty: str,
        level_up_threshold: Optional[float] = None,
        level_down_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate whether difficulty should be adjusted based on accuracy.
        
        Args:
            accuracy: Quiz accuracy (0.0 to 1.0)
            current_difficulty: Current difficulty level
            level_up_threshold: Accuracy threshold to level up
            level_down_threshold: Accuracy threshold to level down
            
        Returns:
            Dictionary with adjustment details
        """
        up_threshold = level_up_threshold or self.config.level_up_threshold
        down_threshold = level_down_threshold or self.config.level_down_threshold
        
        old_difficulty = current_difficulty.upper()
        direction = "NONE"
        should_adjust = False
        
        if accuracy >= up_threshold:
            direction = "UP"
            should_adjust = old_difficulty != "HARD"
        elif accuracy <= down_threshold:
            direction = "DOWN"
            should_adjust = old_difficulty != "EASY"
        
        new_difficulty = self.get_next_difficulty(old_difficulty, direction) if should_adjust else old_difficulty
        
        return {
            "should_adjust": should_adjust,
            "direction": direction,
            "old_difficulty": old_difficulty,
            "new_difficulty": new_difficulty,
            "accuracy": accuracy
        }
    
    def should_evaluate_difficulty(
        self,
        batch_count: int,
        evaluation_interval: Optional[int] = None
    ) -> bool:
        """
        Determine if difficulty should be evaluated based on batch count.
        
        Args:
            batch_count: Number of batches/quizzes completed
            evaluation_interval: How many batches between difficulty evaluations
            
        Returns:
            True if difficulty should be evaluated this batch
        """
        interval = evaluation_interval or self.config.evaluation_interval
        return batch_count > 0 and batch_count % interval == 0
    
    def apply_adaptive_difficulty(
        self,
        accuracy: float,
        current_difficulty: str,
        batch_count: int,
        evaluation_interval: Optional[int] = None,
        level_up_threshold: Optional[float] = None,
        level_down_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Apply adaptive difficulty logic for quiz mode.
        
        Args:
            accuracy: Quiz accuracy (0.0 to 1.0)
            current_difficulty: Current difficulty level
            batch_count: Number of batches completed
            evaluation_interval: Batches between difficulty evaluations
            level_up_threshold: Accuracy threshold to level up
            level_down_threshold: Accuracy threshold to level down
            
        Returns:
            Dictionary with difficulty update information
        """
        interval = evaluation_interval or self.config.evaluation_interval
        
        if not self.should_evaluate_difficulty(batch_count, interval):
            return {
                "new_difficulty": current_difficulty.upper(),
                "difficulty_changed": False,
                "reason": f"Waiting for evaluation interval ({batch_count}/{interval} batches)"
            }
        
        adjustment = self.calculate_difficulty_adjustment(
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
        self,
        recent_accuracies: List[float],
        current_difficulty: str,
        batch_count: int,
        evaluation_interval: Optional[int] = None,
        level_up_threshold: Optional[float] = None,
        level_down_threshold: Optional[float] = None,
        dynamic_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Apply grind mode difficulty logic with optional dynamic adjustment.
        
        Args:
            recent_accuracies: List of recent accuracy values for averaging
            current_difficulty: Current difficulty level
            batch_count: Number of batches completed
            evaluation_interval: Batches between evaluations
            level_up_threshold: Accuracy threshold to level up
            level_down_threshold: Accuracy threshold to level down
            dynamic_enabled: Whether dynamic difficulty is enabled
            
        Returns:
            Dictionary with difficulty update information
        """
        if not dynamic_enabled:
            return {
                "new_difficulty": current_difficulty.upper(),
                "difficulty_changed": False,
                "reason": "Dynamic difficulty disabled in grind mode"
            }
        
        interval = evaluation_interval or self.config.evaluation_interval
        
        if not self.should_evaluate_difficulty(batch_count, interval):
            return {
                "new_difficulty": current_difficulty.upper(),
                "difficulty_changed": False,
                "reason": f"Waiting for evaluation interval ({batch_count}/{interval} batches)"
            }
        
        # Use average of recent accuracies for grind mode
        avg_accuracy = sum(recent_accuracies) / len(recent_accuracies) if recent_accuracies else 0.0
        
        adjustment = self.calculate_difficulty_adjustment(
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
    
    def calculate_streak(
        self,
        accuracy: float,
        current_streak: int,
        streak_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate streak based on accuracy.
        
        Args:
            accuracy: Quiz accuracy (0.0 to 1.0)
            current_streak: Current streak value
            streak_threshold: Minimum accuracy to maintain/build streak
            
        Returns:
            Dictionary with streak update information
        """
        threshold = streak_threshold or self.config.streak_threshold
        
        if accuracy >= threshold:
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
    
    def calculate_mastery_score(
        self,
        accuracy: float,
        current_mastery: float,
        current_difficulty: str,
        weight_new: Optional[float] = None,
        difficulty_bonus: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate updated mastery score with difficulty weighting.
        
        Args:
            accuracy: Quiz accuracy (0.0 to 1.0)
            current_mastery: Current mastery score (0.0 to 1.0)
            current_difficulty: Current difficulty level
            weight_new: Weight for new accuracy vs existing mastery
            difficulty_bonus: Dict mapping difficulty to bonus multiplier
            
        Returns:
            Updated mastery score (0.0 to 1.0)
        """
        weight = weight_new or self.config.mastery_weight
        bonus_map = difficulty_bonus or self.DEFAULT_DIFFICULTY_BONUS
        
        bonus = bonus_map.get(current_difficulty.upper(), 1.0)
        weighted_accuracy = accuracy * bonus
        
        new_mastery = (1 - weight) * current_mastery + weight * weighted_accuracy
        
        return min(1.0, max(0.0, new_mastery))


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════

DIFFICULTY_LEVELS = DifficultyEngine.DIFFICULTY_LEVELS

DEFAULT_QUIZ_CONFIG = {
    "evaluation_interval": 2,
    "level_up_threshold": 0.8,
    "level_down_threshold": 0.4,
    "streak_threshold": 0.8,
    "mastery_weight": 0.3
}

DEFAULT_GRIND_CONFIG = {
    "evaluation_interval": 4,
    "level_up_threshold": 0.8,
    "level_down_threshold": 0.4,
    "streak_threshold": 0.8,
    "mastery_weight": 0.3,
    "dynamic_enabled": True
}


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL FUNCTIONS (Backward Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

_default_engine = None

def _get_engine() -> DifficultyEngine:
    """Get the default difficulty engine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = DifficultyEngine()
    return _default_engine


def get_next_difficulty(current: str, direction: str) -> str:
    """Get the next difficulty level based on direction."""
    return _get_engine().get_next_difficulty(current, direction)


def calculate_difficulty_adjustment(
    accuracy: float,
    current_difficulty: str,
    level_up_threshold: float = 0.8,
    level_down_threshold: float = 0.4
) -> Dict[str, Any]:
    """Calculate whether difficulty should be adjusted based on accuracy."""
    return _get_engine().calculate_difficulty_adjustment(
        accuracy, current_difficulty, level_up_threshold, level_down_threshold
    )


def should_evaluate_difficulty(
    batch_count: int,
    evaluation_interval: int = 2
) -> bool:
    """Determine if difficulty should be evaluated based on batch count."""
    return _get_engine().should_evaluate_difficulty(batch_count, evaluation_interval)


def apply_adaptive_difficulty(
    accuracy: float,
    current_difficulty: str,
    batch_count: int,
    evaluation_interval: int = 2,
    level_up_threshold: float = 0.8,
    level_down_threshold: float = 0.4
) -> Dict[str, Any]:
    """Apply adaptive difficulty logic for quiz mode."""
    return _get_engine().apply_adaptive_difficulty(
        accuracy, current_difficulty, batch_count,
        evaluation_interval, level_up_threshold, level_down_threshold
    )


def apply_grind_difficulty(
    recent_accuracies: List[float],
    current_difficulty: str,
    batch_count: int,
    evaluation_interval: int = 4,
    level_up_threshold: float = 0.8,
    level_down_threshold: float = 0.4,
    dynamic_enabled: bool = True
) -> Dict[str, Any]:
    """Apply grind mode difficulty logic with optional dynamic adjustment."""
    return _get_engine().apply_grind_difficulty(
        recent_accuracies, current_difficulty, batch_count,
        evaluation_interval, level_up_threshold, level_down_threshold, dynamic_enabled
    )


def calculate_streak(
    accuracy: float,
    current_streak: int,
    streak_threshold: float = 0.8
) -> Dict[str, Any]:
    """Calculate streak based on accuracy."""
    return _get_engine().calculate_streak(accuracy, current_streak, streak_threshold)


def calculate_mastery_score(
    accuracy: float,
    current_mastery: float,
    current_difficulty: str,
    weight_new: float = 0.3,
    difficulty_bonus: Dict[str, float] = None
) -> float:
    """Calculate updated mastery score."""
    return _get_engine().calculate_mastery_score(
        accuracy, current_mastery, current_difficulty, weight_new, difficulty_bonus
    )


def get_quiz_config(
    evaluation_interval: int = None,
    level_up_threshold: float = None,
    level_down_threshold: float = None,
    streak_threshold: float = None,
    mastery_weight: float = None
) -> Dict[str, Any]:
    """Get quiz mode configuration with optional overrides."""
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
    """Get grind mode configuration with optional overrides."""
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
