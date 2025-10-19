import boto3
import time

# Initialize DynamoDB
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

def create_table_if_not_exists(params):
    table_name = params["TableName"]
    try:
        existing = dynamodb.describe_table(TableName=table_name)
        print(f"⚠️ Table '{table_name}' already exists — skipping creation.")
        return
    except dynamodb.exceptions.ResourceNotFoundException:
        pass

    print(f"🚀 Creating table: {table_name}")
    dynamodb.create_table(**params)
    # Wait until ACTIVE
    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName=table_name)
    print(f"✅ Table '{table_name}' created and active.")

# ---------- TABLE DEFINITIONS ---------- #

tables = [
    # assessments
    {
        "TableName": "assessments",
        "AttributeDefinitions": [
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "assessment_id", "AttributeType": "S"},
            {"AttributeName": "skill_name", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
            {"AttributeName": "completed_at", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "email", "KeyType": "HASH"},
            {"AttributeName": "assessment_id", "KeyType": "RANGE"}
        ],
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        },
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "skill-index",
                "KeySchema": [
                    {"AttributeName": "skill_name", "KeyType": "HASH"},
                    {"AttributeName": "created_at", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            },
            {
                "IndexName": "status-index",
                "KeySchema": [
                    {"AttributeName": "status", "KeyType": "HASH"},
                    {"AttributeName": "completed_at", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }
        ]
    },

    # roadmaps
    {
        "TableName": "roadmaps",
        "AttributeDefinitions": [
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "roadmap_id", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
            {"AttributeName": "updated_at", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "email", "KeyType": "HASH"},
            {"AttributeName": "roadmap_id", "KeyType": "RANGE"}
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "status-index",
                "KeySchema": [
                    {"AttributeName": "status", "KeyType": "HASH"},
                    {"AttributeName": "updated_at", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }
        ]
    },

    # user_journey
    {
        "TableName": "user_journey",
        "AttributeDefinitions": [
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "journey_id", "AttributeType": "S"},
            {"AttributeName": "is_active", "AttributeType": "S"},
            {"AttributeName": "updated_at", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "email", "KeyType": "HASH"},
            {"AttributeName": "journey_id", "KeyType": "RANGE"}
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "active-journeys-index",
                "KeySchema": [
                    {"AttributeName": "is_active", "KeyType": "HASH"},
                    {"AttributeName": "updated_at", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }
        ]
    },

    # user_profiles
    {
        "TableName": "user_profiles",
        "AttributeDefinitions": [
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "profile_version", "AttributeType": "S"},
            {"AttributeName": "is_current", "AttributeType": "S"},
            {"AttributeName": "updated_at", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "email", "KeyType": "HASH"},
            {"AttributeName": "profile_version", "KeyType": "RANGE"}
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "current-profiles-index",
                "KeySchema": [
                    {"AttributeName": "is_current", "KeyType": "HASH"},
                    {"AttributeName": "updated_at", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }
        ]
    },

    # users
    {
        "TableName": "users",
        "AttributeDefinitions": [
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "google_id", "AttributeType": "S"}
        ],
        "KeySchema": [
            {"AttributeName": "email", "KeyType": "HASH"}
        ],
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "google-id-index",
                "KeySchema": [
                    {"AttributeName": "google_id", "KeyType": "HASH"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }
        ]
    }
]

# ---------- CREATE TABLES ---------- #

if __name__ == "__main__":
    for t in tables:
        create_table_if_not_exists(t)
    print("🎯 All tables processed.")
