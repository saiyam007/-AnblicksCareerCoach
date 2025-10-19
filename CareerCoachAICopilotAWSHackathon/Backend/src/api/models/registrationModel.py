"""
DynamoDB Registration model.
Contains Registration model and registration-related operations.
"""

from datetime import datetime
from typing import Any, Optional, Dict
import uuid
from botocore.exceptions import ClientError

from ..utils.errorHandler import get_logger
from ..utils.database import get_dynamodb_table


logger = get_logger(__name__)


# ============================================================================
# Registration Model
# ============================================================================

class Registration:
    """
    Registration model for DynamoDB (career-coach-data table).
    
    Stores user registration data with primary details and future information.
    """
    
    TABLE_NAME = "career-coach-data"
    
    def __init__(self, **kwargs):
        """Initialize registration from kwargs."""
        self.id = kwargs.get('id') or str(uuid.uuid4())
        self.u_id = kwargs.get('u_id')  # User ID from auth token
        self.email = kwargs.get('email')
        self.type = kwargs.get('type')  # Student | Professional
        
        # Meta information
        self.meta = kwargs.get('meta', {'stage': 'REGISTRATION'})
        
        # Primary details
        self.primary_details = kwargs.get('primary_details', {})
        
        # Future info
        self.future_info = kwargs.get('future_info', {})
        
        # Timestamps
        self.created_at = kwargs.get('created_at') or datetime.utcnow().isoformat()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registration to dictionary for DynamoDB."""
        data = {
            'id': self.id,
            'u_id': self.u_id,
            'email': self.email,
            'type': self.type,
            'meta': self.meta,
            'primary_details': self.primary_details,
            'future_info': self.future_info,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Registration':
        """Create registration from DynamoDB item."""
        return cls(**data)
    
    async def save(self):
        """Save registration to DynamoDB."""
        table = get_dynamodb_table(self.TABLE_NAME)
        self.updated_at = datetime.utcnow().isoformat()
        
        try:
            table.put_item(Item=self.to_dict())
            logger.info(f"Registration saved: {self.email} (u_id: {self.u_id})")
        except ClientError as e:
            logger.error(f"Error saving registration: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def get_by_id_and_u_id(cls, id: str, u_id: str) -> Optional['Registration']:
        """
        Get registration by ID and u_id (composite key).
        
        Args:
            id: Registration ID (partition key)
            u_id: User ID (sort key)
            
        Returns:
            Registration object or None
        """
        table = get_dynamodb_table(cls.TABLE_NAME)
        
        try:
            response = table.get_item(Key={'id': id, 'u_id': u_id})
            if 'Item' in response:
                return cls.from_dict(response['Item'])
            return None
        except ClientError as e:
            logger.error(f"Error getting registration by ID and u_id: {str(e)}", exc_info=True)
            return None
    
    @classmethod
    async def get_by_u_id(cls, u_id: str) -> Optional['Registration']:
        """
        Get registration by u_id (user ID).
        
        Args:
            u_id: User ID (sort key)
            
        Returns:
            Registration object or None
        """
        table = get_dynamodb_table(cls.TABLE_NAME)
        
        try:
            # Query using u_id as sort key
            # Note: This uses scan since u_id is the sort key, not partition key
            logger.info(f"Searching for registration with u_id: {u_id}")
            
            response = table.scan(
                FilterExpression='u_id = :u_id',
                ExpressionAttributeValues={':u_id': u_id},
                Limit=1
            )
            
            logger.info(f"Scan result: Found {len(response.get('Items', []))} items")
            
            if response['Items']:
                logger.info(f"Found existing registration for u_id: {u_id}")
                return cls.from_dict(response['Items'][0])
            
            logger.info(f"No registration found for u_id: {u_id}")
            return None
        except ClientError as e:
            logger.error(f"ClientError getting registration by u_id: {str(e)}", exc_info=True)
            raise  # Don't return None, raise the error
        except Exception as e:
            logger.error(f"Unexpected error getting registration by u_id: {str(e)}", exc_info=True)
            raise  # Don't return None, raise the error
    
    async def update(self, **kwargs):
        """Update registration fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()
        await self.save()
    
    def __repr__(self) -> str:
        return f"<Registration(id={self.id}, u_id={self.u_id}, type={self.type})>"

