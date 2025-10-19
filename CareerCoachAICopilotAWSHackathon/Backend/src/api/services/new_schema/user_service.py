"""
New User Service for normalized users table.

Handles core user management with clean separation from profile data.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import uuid

from ...utils.database import get_dynamodb_table
from ...utils.errorHandler import get_logger
from ...models.new_schema.user_model import NewUser, AuthProvider, UserStatus, UserRole

logger = get_logger(__name__)


class NewUserService:
    """
    Service for managing users in the normalized users table.
    
    Handles core user management:
    - User creation and updates
    - Authentication data management
    - Account status management
    - No career-specific data (handled by UserProfileService)
    """
    
    def __init__(self):
        """Initialize the service with users table."""
        self.table = get_dynamodb_table('users')
        logger.info("NewUserService initialized with users table")
    
    def create_user(self, user_data: Dict[str, Any]) -> NewUser:
        """
        Create a new user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            NewUser: Created user object
            
        Raises:
            Exception: If user creation fails
        """
        try:
            # Generate unique ID if not provided
            if 'id' not in user_data:
                user_data['id'] = str(uuid.uuid4())
            
            # Set timestamps
            user_data['created_at'] = datetime.utcnow().isoformat()
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Create user object
            user = NewUser(**user_data)
            
            # Save to DynamoDB
            self.table.put_item(Item=user.to_dict())
            
            logger.info(f"Created new user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user(self, email: str) -> Optional[NewUser]:
        """
        Get user by email.
        
        Args:
            email: User email address
            
        Returns:
            NewUser or None if not found
        """
        try:
            response = self.table.get_item(
                Key={'email': email}
            )
            
            if 'Item' in response:
                user = NewUser.from_dict(response['Item'])
                logger.info(f"Retrieved user: {email}")
                return user
            else:
                logger.info(f"User not found: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user {email}: {e}")
            raise
    
    def create_or_update_user(self, user_data: Dict[str, Any]) -> NewUser:
        """
        Create or update a user (alias for create_user for compatibility).
        
        Args:
            user_data: User data dictionary
            
        Returns:
            NewUser: Created user object
        """
        return self.create_user(user_data)
    
    def get_user_by_google_id(self, google_id: str) -> Optional[NewUser]:
        """
        Get user by Google ID using GSI.
        
        Args:
            google_id: Google user ID
            
        Returns:
            NewUser or None if not found
        """
        try:
            response = self.table.query(
                IndexName='google-id-index',
                KeyConditionExpression='google_id = :google_id',
                ExpressionAttributeValues={':google_id': google_id}
            )
            
            if response['Items']:
                user = NewUser.from_dict(response['Items'][0])
                logger.info(f"Retrieved user by Google ID: {google_id}")
                return user
            else:
                logger.info(f"User not found with Google ID: {google_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by Google ID {google_id}: {e}")
            raise
    
    def update_user(self, email: str, updates: Dict[str, Any]) -> Optional[NewUser]:
        """
        Update user data.
        
        Args:
            email: User email address
            updates: Dictionary of fields to update
            
        Returns:
            Updated NewUser or None if not found
        """
        try:
            # Add updated timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Build update expression
            update_expression = 'SET '
            expression_attribute_names = {}
            expression_attribute_values = {}
            
            for key, value in updates.items():
                update_expression += f'#{key} = :{key}, '
                expression_attribute_names[f'#{key}'] = key
                expression_attribute_values[f':{key}'] = value
            
            # Remove trailing comma
            update_expression = update_expression.rstrip(', ')
            
            response = self.table.update_item(
                Key={'email': email},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            if 'Attributes' in response:
                updated_user = NewUser.from_dict(response['Attributes'])
                logger.info(f"Updated user: {email}")
                return updated_user
            else:
                logger.warning(f"User not found for update: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating user {email}: {e}")
            raise
    
    def update_last_login(self, email: str) -> bool:
        """
        Update user's last login timestamp.
        
        Args:
            email: User email address
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.table.update_item(
                Key={'email': email},
                UpdateExpression='SET last_login_at = :login_time, updated_at = :update_time',
                ExpressionAttributeValues={
                    ':login_time': datetime.utcnow().isoformat(),
                    ':update_time': datetime.utcnow().isoformat()
                },
                ReturnValues='UPDATED_NEW'
            )
            
            if 'Attributes' in response:
                logger.info(f"Updated last login for user: {email}")
                return True
            else:
                logger.warning(f"User not found for login update: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating last login for {email}: {e}")
            return False
    
    def verify_email(self, email: str) -> bool:
        """
        Mark user's email as verified.
        
        Args:
            email: User email address
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.table.update_item(
                Key={'email': email},
                UpdateExpression='SET is_verified = :verified, email_verified_at = :verify_time, updated_at = :update_time',
                ExpressionAttributeValues={
                    ':verified': True,
                    ':verify_time': datetime.utcnow().isoformat(),
                    ':update_time': datetime.utcnow().isoformat()
                },
                ReturnValues='UPDATED_NEW'
            )
            
            if 'Attributes' in response:
                logger.info(f"Email verified for user: {email}")
                return True
            else:
                logger.warning(f"User not found for email verification: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying email for {email}: {e}")
            return False
    
    def deactivate_user(self, email: str) -> bool:
        """
        Deactivate user account.
        
        Args:
            email: User email address
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.table.update_item(
                Key={'email': email},
                UpdateExpression='SET is_active = :active, #status = :status, updated_at = :update_time',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':active': False,
                    ':status': UserStatus.INACTIVE.value,
                    ':update_time': datetime.utcnow().isoformat()
                },
                ReturnValues='UPDATED_NEW'
            )
            
            if 'Attributes' in response:
                logger.info(f"Deactivated user: {email}")
                return True
            else:
                logger.warning(f"User not found for deactivation: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error deactivating user {email}: {e}")
            return False
    
    def suspend_user(self, email: str) -> bool:
        """
        Suspend user account.
        
        Args:
            email: User email address
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.table.update_item(
                Key={'email': email},
                UpdateExpression='SET is_active = :active, #status = :status, updated_at = :update_time',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':active': False,
                    ':status': UserStatus.SUSPENDED.value,
                    ':update_time': datetime.utcnow().isoformat()
                },
                ReturnValues='UPDATED_NEW'
            )
            
            if 'Attributes' in response:
                logger.info(f"Suspended user: {email}")
                return True
            else:
                logger.warning(f"User not found for suspension: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error suspending user {email}: {e}")
            return False
    
    def soft_delete_user(self, email: str) -> bool:
        """
        Soft delete user account.
        
        Args:
            email: User email address
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.table.update_item(
                Key={'email': email},
                UpdateExpression='SET is_active = :active, #status = :status, deleted_at = :delete_time, updated_at = :update_time',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':active': False,
                    ':status': UserStatus.DELETED.value,
                    ':delete_time': datetime.utcnow().isoformat(),
                    ':update_time': datetime.utcnow().isoformat()
                },
                ReturnValues='UPDATED_NEW'
            )
            
            if 'Attributes' in response:
                logger.info(f"Soft deleted user: {email}")
                return True
            else:
                logger.warning(f"User not found for deletion: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error soft deleting user {email}: {e}")
            return False
    
    def list_users(self, limit: int = 100, last_evaluated_key: Optional[Dict] = None) -> Dict[str, Any]:
        """
        List users with pagination.
        
        Args:
            limit: Maximum number of users to return
            last_evaluated_key: Pagination token
            
        Returns:
            Dictionary with users list and pagination info
        """
        try:
            scan_kwargs = {
                'Limit': limit
            }
            
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
            
            response = self.table.scan(**scan_kwargs)
            
            users = [NewUser.from_dict(item) for item in response.get('Items', [])]
            
            result = {
                'users': users,
                'count': len(users),
                'total_count': response.get('Count', 0),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
            logger.info(f"Listed {len(users)} users")
            return result
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise
    
    def user_exists(self, email: str) -> bool:
        """
        Check if user exists.
        
        Args:
            email: User email address
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            response = self.table.get_item(
                Key={'email': email},
                ProjectionExpression='email'
            )
            
            return 'Item' in response
            
        except Exception as e:
            logger.error(f"Error checking if user exists {email}: {e}")
            return False
    
    def get_user_summary(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user summary for API responses.
        
        Args:
            email: User email address
            
        Returns:
            User summary dictionary or None
        """
        user = self.get_user(email)
        if not user:
            return None
        
        return {
            'email': user.email,
            'id': user.id,
            'auth_provider': user.auth_provider,
            'full_name': user.full_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_picture_url': user.profile_picture_url,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'status': user.status,
            'role': user.role,
            'created_at': user.created_at,
            'last_login_at': user.last_login_at
        }


# Dependency injection
_new_user_service: Optional[NewUserService] = None


def get_new_user_service() -> NewUserService:
    """
    Get or create NewUserService instance (singleton pattern).
    
    Returns:
        NewUserService instance
    """
    global _new_user_service
    if _new_user_service is None:
        _new_user_service = NewUserService()
    return _new_user_service
