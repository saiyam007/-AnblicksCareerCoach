"""
Roadmap model for normalized roadmaps table.

Handles roadmap data with clean separation and versioning.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import uuid
import json

from ...utils.errorHandler import get_logger

logger = get_logger(__name__)


class RoadmapStatus(str):
    """Roadmap status enumeration."""
    QUESTIONS_GENERATED = "QUESTIONS_GENERATED"
    ANSWERS_SUBMITTED = "ANSWERS_SUBMITTED"
    ROADMAP_COMPLETED = "ROADMAP_COMPLETED"
    DETAILED_ROADMAP_COMPLETED = "DETAILED_ROADMAP_COMPLETED"


class Roadmap:
    """
    Roadmap model for normalized roadmaps table.
    
    Handles roadmap data with clean separation:
    - Questions and answers
    - Career path recommendations
    - Detailed roadmaps
    - Selected career path
    - Versioning and history
    """
    
    def __init__(self, **kwargs):
        """Initialize roadmap from kwargs."""
        
        # Core identifiers
        self.email = kwargs.get('email')  # Partition key
        self.roadmap_id = kwargs.get('roadmap_id') or str(uuid.uuid4())  # Sort key
        
        # Roadmap status
        self.status = kwargs.get('status', RoadmapStatus.QUESTIONS_GENERATED)
        
        # Questions data
        self.questions = kwargs.get('questions')  # JSON string or dict
        self.questions_generated_at = kwargs.get('questions_generated_at')
        
        # Answers data
        self.answers = kwargs.get('answers')  # JSON string or dict
        self.answers_submitted_at = kwargs.get('answers_submitted_at')
        
        # Career paths
        self.career_paths = kwargs.get('career_paths')  # JSON string or dict
        self.career_paths_generated_at = kwargs.get('career_paths_generated_at')
        
        # Selected career path
        self.selected_career_path = kwargs.get('selected_career_path')  # JSON string or dict
        self.career_path_selected_at = kwargs.get('career_path_selected_at')
        
        # Detailed roadmap
        self.detailed_roadmap = kwargs.get('detailed_roadmap')  # JSON string or dict
        self.detailed_roadmap_generated_at = kwargs.get('detailed_roadmap_generated_at')
        
        # Profile data used for generation
        self.profile_snapshot = kwargs.get('profile_snapshot')  # JSON string or dict
        
        # Metadata
        self.version = kwargs.get('version', '1.0')
        self.tags = kwargs.get('tags', [])
        self.notes = kwargs.get('notes')
        
        # Timestamps
        self.created_at = kwargs.get('created_at') or datetime.utcnow().isoformat()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert roadmap to dictionary for DynamoDB."""
        
        data = {
            'email': self.email,  # Partition key
            'roadmap_id': self.roadmap_id,  # Sort key
            'status': self.status,
            'questions': self._serialize_json_field(self.questions),
            'questions_generated_at': self.questions_generated_at,
            'answers': self._serialize_json_field(self.answers),
            'answers_submitted_at': self.answers_submitted_at,
            'career_paths': self._serialize_json_field(self.career_paths),
            'career_paths_generated_at': self.career_paths_generated_at,
            'selected_career_path': self._serialize_json_field(self.selected_career_path),
            'career_path_selected_at': self.career_path_selected_at,
            'detailed_roadmap': self._serialize_json_field(self.detailed_roadmap),
            'detailed_roadmap_generated_at': self.detailed_roadmap_generated_at,
            'profile_snapshot': self._serialize_json_field(self.profile_snapshot),
            'version': self.version,
            'tags': self.tags,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
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
    
    def set_questions(self, questions: List[Dict[str, Any]], profile_snapshot: Optional[Dict[str, Any]] = None):
        """Set generated questions."""
        self.questions = questions
        self.questions_generated_at = datetime.utcnow().isoformat()
        self.status = RoadmapStatus.QUESTIONS_GENERATED
        
        if profile_snapshot:
            self.profile_snapshot = profile_snapshot
        
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Questions set for roadmap {self.roadmap_id}")
    
    def set_answers(self, answers: List[Dict[str, Any]]):
        """Set user answers."""
        self.answers = answers
        self.answers_submitted_at = datetime.utcnow().isoformat()
        self.status = RoadmapStatus.ANSWERS_SUBMITTED
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Answers submitted for roadmap {self.roadmap_id}")
    
    def set_career_paths(self, career_paths: List[Dict[str, Any]]):
        """Set generated career paths."""
        self.career_paths = career_paths
        self.career_paths_generated_at = datetime.utcnow().isoformat()
        self.status = RoadmapStatus.ROADMAP_COMPLETED
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Career paths generated for roadmap {self.roadmap_id}")
    
    def select_career_path(self, selected_path: Dict[str, Any]):
        """Set selected career path."""
        self.selected_career_path = selected_path
        self.career_path_selected_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Career path selected for roadmap {self.roadmap_id}: {selected_path.get('title', 'Unknown')}")
    
    def set_detailed_roadmap(self, detailed_roadmap: Dict[str, Any]):
        """Set detailed roadmap."""
        self.detailed_roadmap = detailed_roadmap
        self.detailed_roadmap_generated_at = datetime.utcnow().isoformat()
        self.status = RoadmapStatus.ROADMAP_COMPLETED  # ✅ FIXED: Should be ROADMAP_COMPLETED as per user specification
        self.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Detailed roadmap generated for roadmap {self.roadmap_id}")
    
    def get_questions(self) -> List[Dict[str, Any]]:
        """Get questions as list."""
        return self._deserialize_json_field(self.questions) or []
    
    def get_answers(self) -> List[Dict[str, Any]]:
        """Get answers as list."""
        return self._deserialize_json_field(self.answers) or []
    
    def get_career_paths(self) -> List[Dict[str, Any]]:
        """Get career paths as list."""
        return self._deserialize_json_field(self.career_paths) or []
    
    def get_selected_career_path(self) -> Optional[Dict[str, Any]]:
        """Get selected career path as dict."""
        return self._deserialize_json_field(self.selected_career_path)
    
    def get_detailed_roadmap(self) -> Optional[Dict[str, Any]]:
        """Get detailed roadmap as dict."""
        return self._deserialize_json_field(self.detailed_roadmap)
    
    def get_profile_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get profile snapshot as dict."""
        return self._deserialize_json_field(self.profile_snapshot)
    
    def add_tag(self, tag: str):
        """Add roadmap tag."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow().isoformat()
    
    def add_note(self, note: str):
        """Add roadmap note."""
        if self.notes:
            self.notes += f"\n{datetime.utcnow().isoformat()}: {note}"
        else:
            self.notes = f"{datetime.utcnow().isoformat()}: {note}"
        self.updated_at = datetime.utcnow().isoformat()
    
    def is_questions_ready(self) -> bool:
        """Check if questions are ready."""
        return self.questions is not None and self.status in [RoadmapStatus.QUESTIONS_GENERATED, RoadmapStatus.ANSWERS_SUBMITTED, RoadmapStatus.ROADMAP_COMPLETED, RoadmapStatus.DETAILED_ROADMAP_COMPLETED]
    
    def is_answers_ready(self) -> bool:
        """Check if answers are ready."""
        return self.answers is not None and self.status in [RoadmapStatus.ANSWERS_SUBMITTED, RoadmapStatus.ROADMAP_COMPLETED, RoadmapStatus.DETAILED_ROADMAP_COMPLETED]
    
    def is_career_paths_ready(self) -> bool:
        """Check if career paths are ready."""
        return self.career_paths is not None and self.status in [RoadmapStatus.ROADMAP_COMPLETED, RoadmapStatus.DETAILED_ROADMAP_COMPLETED]
    
    def is_detailed_roadmap_ready(self) -> bool:
        """Check if detailed roadmap is ready."""
        return self.detailed_roadmap is not None and self.status == RoadmapStatus.DETAILED_ROADMAP_COMPLETED
    
    def get_roadmap_summary(self) -> Dict[str, Any]:
        """Get roadmap summary for API responses."""
        return {
            'roadmap_id': self.roadmap_id,
            'status': self.status,
            'has_questions': self.is_questions_ready(),
            'has_answers': self.is_answers_ready(),
            'has_career_paths': self.is_career_paths_ready(),
            'has_detailed_roadmap': self.is_detailed_roadmap_ready(),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'questions_generated_at': self.questions_generated_at,
            'answers_submitted_at': self.answers_submitted_at,
            'career_paths_generated_at': self.career_paths_generated_at,
            'career_path_selected_at': self.career_path_selected_at,
            'detailed_roadmap_generated_at': self.detailed_roadmap_generated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Roadmap':
        """Create roadmap from DynamoDB dictionary."""
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"Roadmap(email='{self.email}', roadmap_id='{self.roadmap_id}', status='{self.status}')"
