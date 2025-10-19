"""
User Journey model for normalized user_journey table.

Handles journey state management with detailed tracking.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import uuid
from decimal import Decimal
from enum import Enum

from ...utils.errorHandler import get_logger
from ...models.enums import JourneyStage

logger = get_logger(__name__)


class JourneyStatus(str, Enum):
    """Journey status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class UserJourney:
    """
    User Journey model for normalized user_journey table.
    
    Handles journey state management:
    - Current stage tracking
    - Stage transition history
    - Progress metrics
    - Journey analytics
    """
    
    def __init__(self, **kwargs):
        """Initialize user journey from kwargs."""
        
        # Core identifiers
        self.email = kwargs.get('email')  # Partition key
        self.journey_id = kwargs.get('journey_id') or str(uuid.uuid4())  # Sort key
        self.is_active = kwargs.get('is_active', 'true')  # GSI key (string for DynamoDB)
        
        # Journey state
        self.current_stage = kwargs.get('current_stage', JourneyStage.AUTHENTICATED.value)
        self.status = kwargs.get('status', JourneyStatus.ACTIVE.value)
        self.progress_percentage = kwargs.get('progress_percentage', Decimal('0.0'))
        
        # Stage tracking
        self.stage_history = kwargs.get('stage_history', [])
        self.stage_transitions = kwargs.get('stage_transitions', [])
        self.completed_stages = kwargs.get('completed_stages', [])
        
        # Progress metrics
        self.total_steps = kwargs.get('total_steps', 7)  # Total journey steps
        self.completed_steps = kwargs.get('completed_steps', 0)
        self.current_step = kwargs.get('current_step', 1)
        
        # Journey data
        self.roadmap_id = kwargs.get('roadmap_id')  # Link to current roadmap
        self.assessment_ids = kwargs.get('assessment_ids', [])  # Completed assessments
        self.skill_progress = kwargs.get('skill_progress', {})  # Skill development tracking
        
        # Analytics
        self.time_in_stage = kwargs.get('time_in_stage', {})  # Time spent in each stage
        self.engagement_score = kwargs.get('engagement_score', Decimal('0.0'))
        self.completion_rate = kwargs.get('completion_rate', Decimal('0.0'))
        
        # Metadata
        self.journey_type = kwargs.get('journey_type', 'standard')  # standard, accelerated, custom
        self.priority = kwargs.get('priority', 'medium')  # low, medium, high
        self.tags = kwargs.get('tags', [])
        
        # Timestamps
        self.created_at = kwargs.get('created_at') or datetime.utcnow().isoformat()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow().isoformat()
        self.started_at = kwargs.get('started_at') or datetime.utcnow().isoformat()
        self.completed_at = kwargs.get('completed_at')
        self.last_activity_at = kwargs.get('last_activity_at') or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert journey to dictionary for DynamoDB."""
        
        data = {
            'email': self.email,  # Partition key
            'journey_id': self.journey_id,  # Sort key
            'is_active': self.is_active,  # GSI key
            'current_stage': self.current_stage,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'stage_history': self.stage_history,
            'stage_transitions': self.stage_transitions,
            'completed_stages': self.completed_stages,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'current_step': self.current_step,
            'roadmap_id': self.roadmap_id,
            'assessment_ids': self.assessment_ids,
            'skill_progress': self.skill_progress,
            'time_in_stage': self.time_in_stage,
            'engagement_score': self.engagement_score,
            'completion_rate': self.completion_rate,
            'journey_type': self.journey_type,
            'priority': self.priority,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'last_activity_at': self.last_activity_at
        }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    def transition_to_stage(self, new_stage: str, transition_data: Optional[Dict[str, Any]] = None):
        """Transition to a new journey stage."""
        
        # Record stage transition
        transition = {
            'from_stage': self.current_stage,
            'to_stage': new_stage,
            'timestamp': datetime.utcnow().isoformat(),
            'data': transition_data or {}
        }
        
        self.stage_transitions.append(transition)
        
        # Update stage history
        if self.current_stage not in self.stage_history:
            self.stage_history.append(self.current_stage)
        
        # Mark previous stage as completed if applicable
        if self.current_stage != JourneyStage.AUTHENTICATED.value:
            if self.current_stage not in self.completed_stages:
                self.completed_stages.append(self.current_stage)
        
        # Update current stage
        self.current_stage = new_stage
        
        # Update progress
        self._update_progress()
        
        # Update timestamps
        self.updated_at = datetime.utcnow().isoformat()
        self.last_activity_at = datetime.utcnow().isoformat()
        
        logger.info(f"User {self.email} transitioned from {transition['from_stage']} to {new_stage}")
    
    def _update_progress(self):
        """Update progress metrics based on current stage."""
        
        # Define stage weights for progress calculation
        stage_weights = {
            JourneyStage.AUTHENTICATED.value: 0.0,
            JourneyStage.BASIC_REGISTERED.value: 0.14,  # 1/7
            JourneyStage.PROFILE_COMPLETED.value: 0.29,  # 2/7
            JourneyStage.CAREER_PATHS_GENERATED.value: 0.43,  # 3/7
            JourneyStage.CAREER_PATH_SELECTED.value: 0.57,  # 4/7
            JourneyStage.ROADMAP_GENERATED.value: 0.71,  # 5/7
            JourneyStage.ROADMAP_ACTIVE.value: 0.86,  # 6/7
            JourneyStage.JOURNEY_COMPLETED.value: 1.0  # 7/7
        }
        
        # Update progress percentage
        self.progress_percentage = Decimal(str(stage_weights.get(self.current_stage, 0.0)))
        
        # Update completed steps
        self.completed_steps = len(self.completed_stages)
        
        # Update current step
        stage_order = [
            JourneyStage.AUTHENTICATED.value,
            JourneyStage.BASIC_REGISTERED.value,
            JourneyStage.PROFILE_COMPLETED.value,
            JourneyStage.CAREER_PATHS_GENERATED.value,
            JourneyStage.CAREER_PATH_SELECTED.value,
            JourneyStage.ROADMAP_GENERATED.value,
            JourneyStage.ROADMAP_ACTIVE.value,
            JourneyStage.JOURNEY_COMPLETED.value
        ]
        
        try:
            self.current_step = stage_order.index(self.current_stage) + 1
        except ValueError:
            self.current_step = 1
    
    def pause_journey(self, reason: Optional[str] = None):
        """Pause the journey."""
        self.status = JourneyStatus.PAUSED.value
        self.is_active = 'false'
        self.updated_at = datetime.utcnow().isoformat()
        
        if reason:
            self.add_tag(f"paused: {reason}")
    
    def resume_journey(self):
        """Resume the journey."""
        self.status = JourneyStatus.ACTIVE.value
        self.is_active = 'true'
        self.updated_at = datetime.utcnow().isoformat()
        self.last_activity_at = datetime.utcnow().isoformat()
    
    def complete_journey(self):
        """Mark journey as completed."""
        self.status = JourneyStatus.COMPLETED.value
        self.progress_percentage = 1.0
        self.completed_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        
        # Add completion to stage history
        if self.current_stage not in self.stage_history:
            self.stage_history.append(self.current_stage)
    
    def abandon_journey(self, reason: Optional[str] = None):
        """Mark journey as abandoned."""
        self.status = JourneyStatus.ABANDONED.value
        self.is_active = 'false'
        self.updated_at = datetime.utcnow().isoformat()
        
        if reason:
            self.add_tag(f"abandoned: {reason}")
    
    def add_assessment(self, assessment_id: str):
        """Add completed assessment."""
        if assessment_id not in self.assessment_ids:
            self.assessment_ids.append(assessment_id)
            self.updated_at = datetime.utcnow().isoformat()
            self.last_activity_at = datetime.utcnow().isoformat()
    
    def update_skill_progress(self, skill: str, progress: float):
        """Update skill development progress."""
        self.skill_progress[skill] = progress
        self.updated_at = datetime.utcnow().isoformat()
        self.last_activity_at = datetime.utcnow().isoformat()
    
    def add_tag(self, tag: str):
        """Add journey tag."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow().isoformat()
    
    def get_stage_info(self) -> Dict[str, Any]:
        """Get detailed stage information."""
        return {
            'current_stage': self.current_stage,
            'progress_percentage': self.progress_percentage,
            'completed_stages': self.completed_stages,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'current_step': self.current_step,
            'status': self.status,
            'is_active': self.is_active
        }
    
    def get_journey_summary(self) -> Dict[str, Any]:
        """Get journey summary for API responses."""
        return {
            'journey_id': self.journey_id,
            'current_stage': self.current_stage,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'completed_stages': self.completed_stages,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'current_step': self.current_step,
            'started_at': self.started_at,
            'last_activity_at': self.last_activity_at,
            'completed_at': self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserJourney':
        """Create journey from DynamoDB dictionary."""
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"UserJourney(email='{self.email}', stage='{self.current_stage}', progress={self.progress_percentage:.1%})"
