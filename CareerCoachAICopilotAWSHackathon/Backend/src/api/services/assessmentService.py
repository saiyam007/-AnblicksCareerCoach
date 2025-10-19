"""
Assessment Service

Handles assessment question generation and answer evaluation using AWS Bedrock Agent.
"""
import os
import json
import boto3
import uuid
from typing import Dict, Any, Optional, List
from ..utils.errorHandler import get_logger ,settings

logger = get_logger(__name__)


class AssessmentService:
    """Service for generating assessment questions and evaluating answers using Bedrock Agent."""
    
    def __init__(self):
        # Bedrock Agent configuration for assessment
        self.region = settings.BEDROCK_REGION
        self.agent_id = settings.BEDROCK_ASSESSMENT_AGENT_ID
        self.agent_alias_id = settings.BEDROCK_ASSESSMENT_AGENT_ALIAS_ID
        self.session_id = str(uuid.uuid4())
        
        # Initialize Bedrock Agent client
        self.client = boto3.client(
            "bedrock-agent-runtime",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        logger.info("AssessmentService initialized with Bedrock Agent")
    
    def _invoke_bedrock_agent(self, prompt: str) -> str:
        """
        Invoke AWS Bedrock Agent Runtime with the given prompt and return response text.
        
        Args:
            prompt: The prompt to send to the Bedrock Agent
            
        Returns:
            str: The response text from the Bedrock Agent
            
        Raises:
            Exception: If Bedrock Agent invocation fails
        """
        try:
            logger.info("Invoking Bedrock Agent for assessment")
            
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=self.session_id,
                inputText=prompt
            )
            
            # Collect response chunks
            chunks = []
            for event in response.get("completion", []):
                if "chunk" in event:
                    chunk = event["chunk"]
                    if "bytes" in chunk:
                        chunks.append(chunk["bytes"].decode("utf-8"))
                    elif "text" in chunk:
                        chunks.append(chunk["text"])
            
            output = "".join(chunks)
            logger.info("Bedrock Agent response received successfully")
            return output
            
        except Exception as e:
            logger.error(f"Bedrock Agent error: {e}")
            raise
    
    def generate_questions(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate Exactly 5 assessment questions for a given skill.
        
        Args:
            profile_data: User profile data containing name, career_goal, skill, and experience
            
        Returns:
            List[Dict[str, Any]]: List of Exactly 5  assessment questions
            
        Raises:
            Exception: If question generation fails
        """
        try:
            logger.info(f"Generating assessment questions for skill: {profile_data.get('skill')}")
            
            prompt = f"""
Generate Exactly 5  assessment questions for:
Skill: {profile_data.get('skill')}
User: {profile_data.get('name', 'Anonymous')}
Career Goal: {profile_data.get('career_goal')}
Experience: {profile_data.get('experience', 'N/A')}

Rules:
- Total questions: Exactly 5 
- 70% → "difficulty": "Medium"
- 30% → "difficulty": "Hard"
- Exactly 1 theoretical question (no options, any difficulty)
- 1 scenario-based question (2–4 lines, reasoning-based)
- Remaining 2-4 questions → MCQ with 4 options (A–D)
- Each question must match the given skill exactly
- Avoid duplication or overly simple questions
- Focus on applied, practical knowledge

Response Format Rules (STRICT):
- Return only valid JSON array (no text outside JSON).
- No text, explanations, markdown, or code fences outside the JSON
- No trailing commas.
"""
            
            result = self._invoke_bedrock_agent(prompt)
            
            # Parse JSON response
            questions = json.loads(result)
            
            if not isinstance(questions, list):
                raise ValueError("Bedrock Agent did not return a list of questions")
            
            if len(questions) != 5 :
                logger.warning(f"Expected 5 questions, got {len(questions)}")
            
            logger.info(f"Generated {len(questions)} assessment questions successfully")
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bedrock Agent response as JSON: {e}")
            raise ValueError(f"Invalid JSON response from Bedrock Agent: {e}")
        except Exception as e:
            logger.error(f"Error generating assessment questions: {e}")
            raise
    
    def evaluate_answers(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate user's assessment responses and generate scores.
        
        Args:
            responses: List of user responses to assessment questions
            
        Returns:
            Dict[str, Any]: Evaluation results with scores and summary
            
        Raises:
            Exception: If evaluation fails
        """
        try:
            logger.info(f"Evaluating assessment responses for {len(responses)} questions")
            
            skill = responses[0].get('skill', 'Unknown')
            responses_json = json.dumps(responses, indent=2)
            
            prompt = f"""
Now, based on the following assessment responses for skill: "{skill}",
evaluate the user's performance and return a **strict JSON object** that includes:

- "Skill": the skill name
- "Total_Questions": number of questions
- "Correct_Answers": number of correct answers
- "Intermidiate_score": percentage correct among Medium
- "Advanced_score": percentage correct among Hard
- "theory_question_score": percentage correct among theoretical
- "Overall": total percentage correct
- "Summary": short list (2–5 bullet points, no long sentences)

Do not include any explanation, text, markdown, or prefix before/after the JSON.

Here are the responses (in JSON format):
{responses_json}

Return only valid JSON strictly following this format:
{{
  "Skill": "Employee Engagement",
  "Total_Questions": 5,
  "Correct_Answers": 3,
  "Intermidiate_score": "75%",
  "Advanced_score": "60%",
  "theory_question_score": "80%",
  "Overall": "72%",
  "Summary": [
    "Good understanding of engagement strategies and employee motivation.",
    "Needs improvement in advanced techniques and data-driven approaches."
  ]
}}
"""
            
            result = self._invoke_bedrock_agent(prompt)
            
            # Parse JSON response
            evaluation = json.loads(result)
            
            if not isinstance(evaluation, dict):
                raise ValueError("Bedrock Agent did not return a dictionary")
            
            # Validate required fields
            required_fields = ["Skill", "Total_Questions", "Correct_Answers", "Intermidiate_score", 
                             "Advanced_score", "theory_question_score", "Overall", "Summary"]
            for field in required_fields:
                if field not in evaluation:
                    raise ValueError(f"Missing required field in evaluation result: {field}")
            
            logger.info(f"Assessment evaluation completed successfully")
            return evaluation
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bedrock Agent response as JSON: {e}")
            raise ValueError(f"Invalid JSON response from Bedrock Agent: {e}")
        except Exception as e:
            logger.error(f"Error evaluating assessment answers: {e}")
            raise


# ============================================================================
# Dependency Injection
# ============================================================================

_assessment_service: Optional[AssessmentService] = None


def get_assessment_service() -> AssessmentService:
    """
    Get or create AssessmentService instance (singleton pattern).
    
    Returns:
        AssessmentService instance
    """
    global _assessment_service
    if _assessment_service is None:
        _assessment_service = AssessmentService()
    return _assessment_service

