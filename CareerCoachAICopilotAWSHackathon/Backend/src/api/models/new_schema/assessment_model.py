"""
Assessment model for normalized assessments table.

Handles assessment and progress tracking with detailed analytics.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import uuid
import json
from decimal import Decimal
from enum import Enum

from ...utils.errorHandler import get_logger

logger = get_logger(__name__)


class AssessmentStatus(str, Enum):
    """Assessment status enumeration."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


class AssessmentType(str, Enum):
    """Assessment type enumeration."""
    SKILL_BASED = "skill_based"
    CAREER_READINESS = "career_readiness"
    LEARNING_STYLE = "learning_style"
    PERSONALITY = "personality"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"


class QuestionType(str, Enum):
    """Question type enumeration."""
    MULTIPLE_CHOICE = "multiple_choice"
    OPEN_ENDED = "open_ended"
    SCALE = "scale"
    YES_NO = "yes_no"
    RANKING = "ranking"


class Assessment:
    """
    Assessment model for normalized assessments table.
    
    Handles assessment and progress tracking:
    - Assessment creation and management
    - Question and answer tracking
    - Scoring and evaluation
    - Progress analytics
    - Skill gap analysis
    """
    
    def __init__(self, **kwargs):
        """Initialize assessment from kwargs."""
        
        # Core identifiers
        self.email = kwargs.get('email')  # Partition key
        self.assessment_id = kwargs.get('assessment_id') or str(uuid.uuid4())  # Sort key
        
        # Assessment metadata
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.assessment_type = kwargs.get('assessment_type', AssessmentType.SKILL_BASED.value)
        self.skill_name = kwargs.get('skill_name')  # GSI key
        self.status = kwargs.get('status', AssessmentStatus.CREATED.value)  # GSI key
        
        # Roadmap integration fields (NEW)
        self.roadmap_id = kwargs.get('roadmap_id')  # GSI key - Link to specific roadmap
        self.topic_name = kwargs.get('topic_name')  # The topic from roadmap being assessed
        self.phase = kwargs.get('phase')  # Beginner/Intermediate/Advanced
        self.subtopic_name = kwargs.get('subtopic_name')  # Optional, for granular tracking
        self.assessment_order = kwargs.get('assessment_order')  # Order within the roadmap
        self.is_required = kwargs.get('is_required', True)  # Whether this assessment is mandatory
        self.prerequisites = kwargs.get('prerequisites', [])  # Required completed assessments
        
        # Assessment configuration
        self.total_questions = kwargs.get('total_questions', 0)
        self.time_limit_minutes = kwargs.get('time_limit_minutes')
        self.passing_score = kwargs.get('passing_score', Decimal('60.0'))
        self.difficulty_level = kwargs.get('difficulty_level', 'medium')  # easy, medium, hard
        
        # Questions and answers
        self.questions = kwargs.get('questions')  # JSON string or list
        self.user_answers = kwargs.get('user_answers')  # JSON string or list
        self.correct_answers = kwargs.get('correct_answers')  # JSON string or list
        
        # Scoring and evaluation
        self.score = kwargs.get('score')
        self.max_score = kwargs.get('max_score')
        self.percentage_score = kwargs.get('percentage_score')
        if self.percentage_score is not None:
            self.percentage_score = Decimal(str(self.percentage_score))
        self.is_passed = kwargs.get('is_passed', False)
        self.evaluation = kwargs.get('evaluation')  # JSON string or dict
        
        # Progress tracking
        self.current_question = kwargs.get('current_question', 0)
        self.questions_answered = kwargs.get('questions_answered', 0)
        self.time_spent_seconds = kwargs.get('time_spent_seconds', 0)
        
        # Analytics
        self.skill_gaps_identified = kwargs.get('skill_gaps_identified', [])
        self.strengths_identified = kwargs.get('strengths_identified', [])
        self.improvement_areas = kwargs.get('improvement_areas', [])
        self.recommendations = kwargs.get('recommendations', [])
        
        # Metadata
        self.version = kwargs.get('version', '1.0')
        self.tags = kwargs.get('tags', [])
        self.notes = kwargs.get('notes')
        
        # Timestamps
        self.created_at = kwargs.get('created_at') or datetime.utcnow().isoformat()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow().isoformat()
        self.started_at = kwargs.get('started_at')
        self.completed_at = kwargs.get('completed_at')
        self.expires_at = kwargs.get('expires_at')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary for DynamoDB."""
        
        data = {
            'email': self.email,  # Partition key
            'assessment_id': self.assessment_id,  # Sort key
            'title': self.title,
            'description': self.description,
            'assessment_type': self.assessment_type,
            'skill_name': self.skill_name,  # GSI key
            'status': self.status,  # GSI key
            'roadmap_id': self.roadmap_id,  # GSI key - Link to specific roadmap
            'topic_name': self.topic_name,
            'phase': self.phase,
            'subtopic_name': self.subtopic_name,
            'assessment_order': self.assessment_order,
            'is_required': self.is_required,
            'prerequisites': self.prerequisites,
            'total_questions': self.total_questions,
            'time_limit_minutes': self.time_limit_minutes,
            'passing_score': self.passing_score,
            'difficulty_level': self.difficulty_level,
            'questions': self._serialize_json_field(self.questions),
            'user_answers': self._serialize_json_field(self.user_answers),
            'correct_answers': self._serialize_json_field(self.correct_answers),
            'score': self.score,
            'max_score': self.max_score,
            'percentage_score': self.percentage_score,
            'is_passed': self.is_passed,
            'evaluation': self._serialize_json_field(self.evaluation),
            'current_question': self.current_question,
            'questions_answered': self.questions_answered,
            'time_spent_seconds': self.time_spent_seconds,
            'skill_gaps_identified': self.skill_gaps_identified,
            'strengths_identified': self.strengths_identified,
            'improvement_areas': self.improvement_areas,
            'recommendations': self.recommendations,
            'version': self.version,
            'tags': self.tags,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'expires_at': self.expires_at
        }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    def _serialize_json_field(self, field: Any) -> Optional[str]:
        """Serialize JSON field for DynamoDB storage."""
        if field is None:
            return None
        if isinstance(field, str):
            return field  # Already serialized
        return json.dumps(field)
    
    def _deserialize_json_field(self, field: Any) -> Any:
        """Deserialize JSON field from DynamoDB."""
        if field is None:
            return None
        if isinstance(field, str):
            try:
                return json.loads(field)
            except json.JSONDecodeError:
                return field  # Return as string if not valid JSON
        return field
    
    def start_assessment(self):
        """Start the assessment."""
        self.status = AssessmentStatus.IN_PROGRESS.value
        self.started_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Assessment {self.assessment_id} started")
    
    def submit_answer(self, question_index: int, answer: Any):
        """Submit answer for a question."""
        answers = self.get_user_answers()
        
        # Ensure answers list is long enough
        while len(answers) <= question_index:
            answers.append(None)
        
        answers[question_index] = {
            'question_index': question_index,
            'answer': answer,
            'submitted_at': datetime.utcnow().isoformat()
        }
        
        self.user_answers = answers
        self.current_question = question_index + 1
        self.questions_answered = len([a for a in answers if a is not None])
        self.updated_at = datetime.utcnow().isoformat()
    
    def complete_assessment(self):
        """Mark assessment as completed."""
        self.status = AssessmentStatus.COMPLETED.value
        self.completed_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Assessment {self.assessment_id} completed")
    
    def calculate_score(self):
        """Calculate assessment score."""
        questions = self.get_questions()
        answers = self.get_user_answers()
        correct_answers = self.get_correct_answers()
        
        if not questions or not answers or not correct_answers:
            logger.warning(f"Cannot calculate score for assessment {self.assessment_id} - missing data")
            return
        
        correct_count = 0
        total_questions = len(questions)
        
        for i, (question, answer, correct) in enumerate(zip(questions, answers, correct_answers)):
            if answer and self._is_answer_correct(question, answer.get('answer'), correct):
                correct_count += 1
        
        self.score = correct_count
        self.max_score = total_questions
        self.percentage_score = Decimal(str((correct_count / total_questions) * 100)) if total_questions > 0 else Decimal('0')
        self.is_passed = self.percentage_score >= self.passing_score
        
        logger.info(f"Assessment {self.assessment_id} scored: {self.percentage_score:.1f}% ({correct_count}/{total_questions})")
    
    def _is_answer_correct(self, question: Dict[str, Any], user_answer: Any, correct_answer: Any) -> bool:
        """Check if user answer is correct."""
        question_type = question.get('type', QuestionType.MULTIPLE_CHOICE.value)
        
        if question_type == QuestionType.MULTIPLE_CHOICE.value:
            return str(user_answer).strip().lower() == str(correct_answer).strip().lower()
        elif question_type == QuestionType.YES_NO.value:
            return str(user_answer).strip().lower() == str(correct_answer).strip().lower()
        elif question_type == QuestionType.OPEN_ENDED.value:
            # For open-ended questions, we might need AI evaluation
            # For now, return True if answer is not empty
            return user_answer and len(str(user_answer).strip()) > 0
        else:
            return str(user_answer).strip().lower() == str(correct_answer).strip().lower()
    
    def set_questions(self, questions: List[Dict[str, Any]]):
        """Set assessment questions."""
        self.questions = questions
        self.total_questions = len(questions)
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Set {len(questions)} questions for assessment {self.assessment_id}")
    
    def set_correct_answers(self, correct_answers: List[Any]):
        """Set correct answers for scoring."""
        self.correct_answers = correct_answers
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Set correct answers for assessment {self.assessment_id}")
    
    def set_evaluation(self, evaluation: Dict[str, Any]):
        """Set AI evaluation results."""
        self.evaluation = evaluation
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Set evaluation for assessment {self.assessment_id}")
    
    def add_skill_gap(self, skill_gap: str):
        """Add identified skill gap."""
        if skill_gap not in self.skill_gaps_identified:
            self.skill_gaps_identified.append(skill_gap)
            self.updated_at = datetime.utcnow().isoformat()
    
    def add_strength(self, strength: str):
        """Add identified strength."""
        if strength not in self.strengths_identified:
            self.strengths_identified.append(strength)
            self.updated_at = datetime.utcnow().isoformat()
    
    def add_improvement_area(self, area: str):
        """Add improvement area."""
        if area not in self.improvement_areas:
            self.improvement_areas.append(area)
            self.updated_at = datetime.utcnow().isoformat()
    
    def add_recommendation(self, recommendation: Dict[str, Any]):
        """Add recommendation."""
        self.recommendations.append(recommendation)
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_questions(self) -> List[Dict[str, Any]]:
        """Get questions as list."""
        return self._deserialize_json_field(self.questions) or []
    
    def get_user_answers(self) -> List[Dict[str, Any]]:
        """Get user answers as list."""
        return self._deserialize_json_field(self.user_answers) or []
    
    def get_correct_answers(self) -> List[Any]:
        """Get correct answers as list."""
        return self._deserialize_json_field(self.correct_answers) or []
    
    def get_evaluation(self) -> Optional[Dict[str, Any]]:
        """Get evaluation as dict."""
        return self._deserialize_json_field(self.evaluation)
    
    def get_progress_percentage(self) -> float:
        """Get completion progress percentage."""
        if self.total_questions == 0:
            return 0.0
        return float(self.questions_answered / self.total_questions) * 100 if self.total_questions > 0 else 0.0
    
    def is_expired(self) -> bool:
        """Check if assessment is expired."""
        if not self.expires_at:
            return False
        return datetime.fromisoformat(self.expires_at) < datetime.utcnow()
    
    def get_assessment_summary(self) -> Dict[str, Any]:
        """Get assessment summary for API responses."""
        return {
            'assessment_id': self.assessment_id,
            'title': self.title,
            'skill_name': self.skill_name,
            'assessment_type': self.assessment_type,
            'status': self.status,
            'roadmap_id': self.roadmap_id,
            'topic_name': self.topic_name,
            'phase': self.phase,
            'assessment_order': self.assessment_order,
            'is_required': self.is_required,
            'total_questions': self.total_questions,
            'questions_answered': self.questions_answered,
            'progress_percentage': self.get_progress_percentage(),
            'score': self.score,
            'percentage_score': self.percentage_score,
            'is_passed': self.is_passed,
            'difficulty_level': self.difficulty_level,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'expires_at': self.expires_at
        }
    
    def is_roadmap_assessment(self) -> bool:
        """Check if this assessment is linked to a roadmap."""
        return self.roadmap_id is not None
    
    def get_roadmap_info(self) -> Dict[str, Any]:
        """Get roadmap-related information."""
        return {
            'roadmap_id': self.roadmap_id,
            'topic_name': self.topic_name,
            'phase': self.phase,
            'subtopic_name': self.subtopic_name,
            'assessment_order': self.assessment_order,
            'is_required': self.is_required,
            'prerequisites': self.prerequisites
        }
    
    def get_detailed_results(self) -> Dict[str, Any]:
        """Get detailed assessment results."""
        return {
            'assessment_summary': self.get_assessment_summary(),
            'questions': self.get_questions(),
            'user_answers': self.get_user_answers(),
            'evaluation': self.get_evaluation(),
            'skill_gaps_identified': self.skill_gaps_identified,
            'strengths_identified': self.strengths_identified,
            'improvement_areas': self.improvement_areas,
            'recommendations': self.recommendations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Assessment':
        """Create assessment from DynamoDB dictionary."""
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"Assessment(email='{self.email}', assessment_id='{self.assessment_id}', skill='{self.skill_name}', status='{self.status}')"
