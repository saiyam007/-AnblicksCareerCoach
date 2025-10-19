"""
DynamoDB connection management and database utilities.
Handles connection setup, table management, and database operations.
"""

from typing import Optional
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from .errorHandler import settings, get_logger


logger = get_logger(__name__)


# ============================================================================
# DynamoDB Connection Management
# ============================================================================

class DynamoDBConnection:
    """
    Singleton class for DynamoDB connection management.
    
    Provides a single instance of DynamoDB connection that can be reused
    throughout the application.
    """
    
    _instance = None
    _dynamodb = None
    _table = None
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(DynamoDBConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize DynamoDB connection if not already initialized."""
        if self._dynamodb is None:
            self._initialize_connection()
    
    def _initialize_connection(self):
        """
        Initialize DynamoDB connection with AWS credentials.
        
        Supports both local DynamoDB (for development) and AWS DynamoDB (for production).
        """
        try:
            # Configure boto3 session
            # Use DYNAMODB_REGION for DynamoDB connections (Users table in us-east-1)
            session_config = {
                'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
                'region_name': settings.DYNAMODB_REGION  # Use DynamoDB-specific region
            }

            # Network timeout configuration to avoid hanging health checks
            boto_config = Config(
                connect_timeout=2,
                read_timeout=2,
                retries={"max_attempts": 1, "mode": "standard"}
            )
            
            # Add endpoint URL for local DynamoDB
            if settings.DYNAMODB_ENDPOINT_URL:
                self._dynamodb = boto3.resource(
                    'dynamodb',
                    endpoint_url=settings.DYNAMODB_ENDPOINT_URL,
                    config=boto_config,
                    **session_config
                )
                logger.info(f"Connected to local DynamoDB at {settings.DYNAMODB_ENDPOINT_URL}")
            else:
                self._dynamodb = boto3.resource('dynamodb', config=boto_config, **session_config)
                logger.info(f"Connected to AWS DynamoDB in {settings.AWS_REGION}")
            
            self._table = self._dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
            logger.info(f"Using DynamoDB table: {settings.DYNAMODB_TABLE_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB connection: {str(e)}", exc_info=True)
            raise
    
    @property
    def table(self):
        """
        Get DynamoDB table resource.
        
        Returns:
            DynamoDB Table resource
        """
        if self._table is None:
            self._initialize_connection()
        return self._table
    
    @property
    def dynamodb(self):
        """
        Get DynamoDB resource.
        
        Returns:
            DynamoDB resource
        """
        if self._dynamodb is None:
            self._initialize_connection()
        return self._dynamodb
    
    def reset_connection(self):
        """
        Reset the connection (useful for testing or reconnecting).
        """
        self._dynamodb = None
        self._table = None
        logger.info("DynamoDB connection reset")


# Global DynamoDB connection instance
db_connection = DynamoDBConnection()


# ============================================================================
# Database Helper Functions
# ============================================================================

def get_dynamodb_table(table_name: Optional[str] = None):
    """
    Get DynamoDB table instance.
    
    This is the main function to use when you need access to the DynamoDB table.
    
    Args:
        table_name: Optional table name. If not provided, uses settings.DYNAMODB_TABLE_NAME
    
    Returns:
        DynamoDB Table resource
        
    Example:
        table = get_dynamodb_table()  # Gets career-coach-users
        table = get_dynamodb_table('career_coach_data')  # Gets specific table
        response = table.get_item(Key={'id': user_id})
    """
    if table_name:
        # Get specific table by name
        return db_connection.dynamodb.Table(table_name)
    return db_connection.table


def get_dynamodb_resource():
    """
    Get boto3 DynamoDB resource.
    
    Returns:
        DynamoDB resource for accessing tables
    """
    return db_connection.dynamodb


# ============================================================================
# Database Initialization
# ============================================================================

async def init_db() -> None:
    """
    Initialize DynamoDB table (create if not exists).
    
    Creates the users table with appropriate Global Secondary Indexes (GSIs)
    for querying by email and Google ID.
    
    Note: In production, use CloudFormation or Terraform for table creation.
    This is only for development/testing.
    
    Raises:
        ClientError: If table creation fails
    """
    try:
        dynamodb = db_connection.dynamodb
        
        # Check if table exists
        try:
            table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
            table.load()
            logger.info(f"DynamoDB table '{settings.DYNAMODB_TABLE_NAME}' already exists")
            return
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise
        
        # Create table with GSIs
        logger.info(f"Creating DynamoDB table: {settings.DYNAMODB_TABLE_NAME}")
        
        table = dynamodb.create_table(
            TableName=settings.DYNAMODB_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'},
                {'AttributeName': 'google_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'google-id-index',
                    'KeySchema': [
                        {'AttributeName': 'google_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        logger.info(f"DynamoDB table '{settings.DYNAMODB_TABLE_NAME}' created successfully")
        
        # Log table details
        table_description = table.meta.client.describe_table(
            TableName=settings.DYNAMODB_TABLE_NAME
        )
        logger.info(f"Table status: {table_description['Table']['TableStatus']}")
        logger.info(f"GSIs created: {len(table_description['Table'].get('GlobalSecondaryIndexes', []))}")
        
    except Exception as e:
        logger.error(f"Error initializing DynamoDB: {str(e)}", exc_info=True)
        raise


async def close_db() -> None:
    """
    Close DynamoDB connections.
    
    Should be called on application shutdown to properly clean up resources.
    Note: boto3 connections are stateless, so this is mainly for logging
    and future extensibility.
    """
    logger.info("Closing DynamoDB connections")
    # boto3 DynamoDB connections are stateless, no explicit close needed
    # This function is here for compatibility and future enhancements
    logger.info("DynamoDB connections closed")


async def reset_db() -> None:
    """Deprecated: not used by runtime; kept for compatibility in tests."""
    db_connection.reset_connection()
    logger.info("Database connection reset")


# ============================================================================
# Database Health Check
# ============================================================================

async def check_db_health() -> dict:
    """
    Check DynamoDB connection health without blocking the event loop.
    Uses a short timeout to avoid hanging the health endpoint.
    """
    import asyncio

    def describe_table_sync():
        table = get_dynamodb_table()
        return table.meta.client.describe_table(
            TableName=settings.DYNAMODB_TABLE_NAME
        )

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(describe_table_sync),
            timeout=3
        )

        table_info = response['Table']

        return {
            'status': 'connected',
            'table_name': settings.DYNAMODB_TABLE_NAME,
            'table_status': table_info.get('TableStatus'),
            'item_count': table_info.get('ItemCount', 0),
            'table_size_bytes': table_info.get('TableSizeBytes', 0),
            'region': settings.AWS_REGION,
            'endpoint': settings.DYNAMODB_ENDPOINT_URL or 'AWS DynamoDB'
        }

    except asyncio.TimeoutError:
        logger.warning("Database health check timed out")
        return {
            'status': 'disconnected',
            'error': 'timeout',
            'table_name': settings.DYNAMODB_TABLE_NAME,
            'region': settings.AWS_REGION
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return {
            'status': 'disconnected',
            'error': str(e),
            'table_name': settings.DYNAMODB_TABLE_NAME,
            'region': settings.AWS_REGION
        }


# ============================================================================
# FastAPI Dependency
# ============================================================================

async def get_db():
    """
    FastAPI dependency for getting DynamoDB table.
    
    This can be used with Depends() in FastAPI route handlers.
    
    Yields:
        DynamoDB Table resource
        
    Example:
        @app.get("/users")
        async def get_users(db = Depends(get_db)):
            response = db.scan()
            return response['Items']
    """
    yield get_dynamodb_table()


# ============================================================================
# Utility Functions
# ============================================================================

def table_exists(table_name: Optional[str] = None) -> bool:
    """Deprecated: prefer IaC/console for table introspection."""
    table_name = table_name or settings.DYNAMODB_TABLE_NAME
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(table_name)
        table.load()
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        raise


async def delete_table(table_name: Optional[str] = None) -> bool:
    """Deprecated: destructive admin utility; do not use in app runtime."""
    table_name = table_name or settings.DYNAMODB_TABLE_NAME
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(table_name)
        table.delete()
        logger.warning(f"Table '{table_name}' deleted!")
        return True
    except Exception as e:
        logger.error(f"Error deleting table: {str(e)}", exc_info=True)
        return False


def list_tables() -> list:
    """Deprecated: admin utility; not used in application code."""
    try:
        dynamodb = get_dynamodb_resource()
        tables = [table.name for table in dynamodb.tables.all()]
        return tables
    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}", exc_info=True)
        return []

