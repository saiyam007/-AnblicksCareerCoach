"""
DynamoDB Client for Users Table Management.

This client handles operations on the 'Users' table from Backend_2,
which uses a composite key (email + recordId) schema.

Separate from Backend's main database.py to avoid conflicts.
"""

import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError
from typing import Dict, Optional

# Import settings from Backend's errorHandler
from ..utils.errorHandler import settings, get_logger

logger = get_logger(__name__)


class DynamoDBUsersClient:
    """
    DynamoDB client for interacting with the `Users` table.
    
    This table uses a composite key schema:
    - Partition Key: email
    - Sort Key: recordId (usually "PROFILE#LATEST")
    
    Operations:
    - Stores basic user info
    - Updates profile_summary
    - Fetches user profile by email
    - Delete user profile
    """

    def __init__(self, table_name: str = "Users", region_name: Optional[str] = None):
        """
        Initialize DynamoDB client for Users table.
        
        Args:
            table_name: Name of the DynamoDB table (default: "Users")
            region_name: AWS region (default: from settings.DYNAMODB_REGION)
        """
        self.region = region_name or settings.DYNAMODB_REGION
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
        
        logger.info(f" DynamoDB Users Client initialized for table '{table_name}' in region '{self.region}'")

    # ------------------------------------------------------------
    # Create / Update user basic info
    # ------------------------------------------------------------
    def upsert_user_profile(self, user_data: Dict) -> None:
        """
        Insert or update user basic info in the Users table.
        
        Ensures `recordId` is present for the table's key schema.
        If an existing record exists, it will be overwritten cleanly.
        
        Args:
            user_data: Dictionary containing user profile data
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            #  Add default recordId if not provided
            if "recordId" not in user_data or not user_data["recordId"]:
                user_data["recordId"] = "PROFILE#LATEST"

            user_data["updatedAt"] = datetime.utcnow().isoformat()

            #  Optional: enforce partition+sort key existence
            #   This ensures no accidental insert without proper keys
            self.table.put_item(
                Item=user_data,
                ConditionExpression="attribute_not_exists(email) OR attribute_exists(recordId)"
            )

            logger.info(f" [DynamoDB] Upserted profile for {user_data.get('email')}")

        except ClientError as e:
            # NOTE: ConditionalCheckFailedException means the item already exists
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.info(f"[DynamoDB] Item already exists — updating existing record for {user_data.get('email')}")
                self.table.put_item(Item=user_data)  # overwrite existing
            else:
                logger.error(f" Failed to upsert user profile: {e}")
                raise RuntimeError(f"Error saving user profile for {user_data.get('email')}: {e}")

    # ------------------------------------------------------------
    # Update profile summary only
    # ------------------------------------------------------------
    def update_profile_summary(self, email: str, profile_summary: str) -> None:
        """
        Update only the profile_summary field for an existing user.
        
        Handles tables with composite key (email + recordId).
        
        Args:
            email: User's email address
            profile_summary: AI-generated profile summary text
            
        Raises:
            RuntimeError: If user doesn't exist or update fails
        """
        try:
            self.table.update_item(
                Key={
                    "email": email,
                    "recordId": "PROFILE#LATEST"  #  Required for composite key schema
                },
                UpdateExpression="SET profile_summary = :s, updatedAt = :u",
                ExpressionAttributeValues={
                    ":s": profile_summary,
                    ":u": datetime.utcnow().isoformat()
                },
                ConditionExpression="attribute_exists(email) AND attribute_exists(recordId)"
            )
            logger.info(f" [DynamoDB] Updated profile_summary for {email}")

        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning(f"[DynamoDB] Tried to update non-existing user: {email}")
            else:
                logger.error(f" Failed to update profile_summary for {email}: {e}")
            raise RuntimeError(f"Error updating profile_summary for {email}: {e}")

    # ------------------------------------------------------------
    # Get user profile by email
    # ------------------------------------------------------------
    def get_user_profile(self, email: str) -> Optional[Dict]:
        """
        Retrieve a user profile by email and fixed recordId.
        
        Args:
            email: User's email address
            
        Returns:
            User profile dictionary or None if not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            resp = self.table.get_item(
                Key={
                    "email": email,
                    "recordId": "PROFILE#LATEST"  # 👈 required for composite key
                }
            )
            item = resp.get("Item")
            if not item:
                logger.warning(f"[DynamoDB] No user profile found for {email}")
            return item
        except ClientError as e:
            logger.error(f" Failed to fetch user profile: {e}")
            raise RuntimeError(f"Error fetching user profile: {e}")

    # ------------------------------------------------------------
    # Delete user profile (Optional)
    # ------------------------------------------------------------
    def delete_user_profile(self, email: str) -> None:
        """
        Delete a user profile (optional helper).
        
        Args:
            email: User's email address
            
        Raises:
            RuntimeError: If user doesn't exist or delete fails
        """
        try:
            self.table.delete_item(
                Key={
                    "email": email,
                    "recordId": "PROFILE#LATEST"
                },
                ConditionExpression="attribute_exists(email)"  # Ensures record exists
            )
            logger.info(f"[DynamoDB] Deleted profile for {email}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning(f"Tried to delete non-existing user: {email}")
            else:
                logger.error(f" Failed to delete user profile for {email}: {e}")
            raise RuntimeError(f"Error deleting user profile for {email}: {e}")

    # ------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------
    def list_all_profiles(self, limit: int = 100) -> list:
        """
        List all user profiles (for admin/debugging).
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of user profile dictionaries
        """
        try:
            response = self.table.scan(Limit=limit)
            items = response.get("Items", [])
            logger.info(f" [DynamoDB] Retrieved {len(items)} user profiles")
            return items
        except ClientError as e:
            logger.error(f" Failed to list profiles: {e}")
            raise RuntimeError(f"Error listing user profiles: {e}")

    def table_exists(self) -> bool:
        """
        Check if the Users table exists.
        
        Returns:
            True if table exists, False otherwise
        """
        try:
            self.table.load()
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return False
            raise

