"""
AWS Bedrock LLM Connector for AI Career Advisor.

This module handles communication with Claude Sonnet model via AWS Bedrock
for generating:
- Career-specific questions
- Career roadmaps
- Profile summaries
"""

from __future__ import annotations
import json
import logging
import re
from typing import Dict, List
from datetime import datetime
import uuid
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from .roadmap_gen_artifacts import build_prompt_highlevel, build_prompt_subtopics, invoke_bedrock_agent, merge_roadmaps

# Import settings from Backend's errorHandler
from ..utils.errorHandler import settings

logger = logging.getLogger(__name__)


class BedrockLLMClient:
    """
    Handles communication with Claude Sonnet model using AWS Bedrock.
    Logs all API requests and LLM responses for debugging & observability.
    """

    def __init__(self):
        """Initialize Bedrock client with settings from Backend configuration."""
        if not settings.DRY_RUN:
            self.client = boto3.client("bedrock-runtime", region_name=settings.BEDROCK_REGION)
        else:
            self.client = None
            logger.info("🧪 DRY_RUN mode enabled - using mock responses")

        self.model_id = settings.BEDROCK_MODEL_ID
        if not self.model_id and not settings.DRY_RUN:
            raise ValueError(" BEDROCK_MODEL_ID is not set in environment")

    # ------------------------------------------------------------
    # Helper: clean and parse model text response
    # ------------------------------------------------------------
    def _extract_and_clean_output(self, parsed: dict) -> str:
        """
        Extract and clean text output from Bedrock response.
        
        Args:
            parsed: Parsed JSON response from Bedrock
            
        Returns:
            Cleaned text output
        """
        text_output = ""
        if "content" in parsed:
            text_output = parsed["content"][0]["text"].strip()
        elif "completion" in parsed:
            text_output = parsed["completion"].strip()
        elif "results" in parsed:
            text_output = parsed["results"][0]["outputText"].strip()

        clean_output = text_output.strip()

        # 🧼 Remove markdown code fences
        if clean_output.startswith("```"):
            clean_output = clean_output.split("\n", 1)[1]
        if clean_output.endswith("```"):
            clean_output = clean_output.rsplit("```", 1)[0]

        # Normalize curly quotes to standard quotes
        clean_output = clean_output.replace(""", '"').replace(""", '"')
        clean_output = clean_output.replace("'", "'").replace("'", "'")

        # 🚨 CRITICAL FIX: Handle escaped single quotes properly
        # Fix double-escaped quotes from AI responses
        clean_output = clean_output.replace("\\'", "'")
        
        # Don't escape single quotes in JSON - they're valid in JSON strings
        # clean_output = clean_output.replace("'", "\\'")  # REMOVED - causes JSON parsing issues

        # 🧽 Collapse multiple spaces but preserve JSON structure
        clean_output = re.sub(r' +', ' ', clean_output).strip()

        # 🚨 CRITICAL FIX: Only escape truly problematic backslashes
        # Don't escape backslashes that are part of valid JSON escapes
        clean_output = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean_output)

        return clean_output

    # ------------------------------------------------------------
    # Question Generation
    # ------------------------------------------------------------
    def generate_questions(self, profile_payload: Dict, max_questions: int = 15) -> Dict:
        """
        Generate intelligent domain-specific career questions.
        
        Args:
            profile_payload: User profile data
            max_questions: Maximum number of questions to generate (default: 15)
            
        Returns:
            Dictionary with "questions" array
            
        Example response:
            {
                "questions": [
                    {"id": "q1", "text": "Do you have experience with...?"},
                    {"id": "q2", "text": "Are you proficient in...?"}
                ]
            }
        """
        if settings.DRY_RUN:
            return self._mock_questions()

        system_instruction = (
            "You are an AI career advisor. "
            "You must return ONLY valid JSON. No markdown, no code blocks, no explanations. "
            "Respond strictly in this format: "
            '{"questions":[{"id":"q1","text":"..."},{"id":"q2","text":"..."}]}'
        )

        prompt = f"""
Given the user registration profile below, generate {max_questions} short, domain-specific questions.
Each question must:
- Be directly related to career goals, skills, interests, or aspirations
- Be clear and short
- Be answerable with: [Yes, No, Agree, Disagree, Not Sure]
- Avoid vague or generic wording

Return ONLY valid JSON in this format:
{{
  "questions": [
    {{"id":"q1","text":"..."}},
    {{"id":"q2","text":"..."}}
  ]
}}

User Profile:
{json.dumps(profile_payload, indent=2)}
"""

        # 🪵 Log the request going to the model
        logger.info(f"🟡 [BedrockLLM] Invoking generate_questions with profile:\n{json.dumps(profile_payload, indent=2)}")

        try:
            resp = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "system": system_instruction,
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    ]
                })
            )

            raw_body = resp["body"].read().decode("utf-8")
            logger.debug(f"🧾 RAW BODY:\n{raw_body}")

            if not raw_body.strip():
                raise RuntimeError(" Model returned an empty response.")

            parsed = json.loads(raw_body)
            clean_output = self._extract_and_clean_output(parsed)
            logger.debug(f"🧼 Cleaned model output:\n{clean_output}")

            # Try to parse the cleaned output directly
            try:
                questions_json = json.loads(clean_output)
            except json.JSONDecodeError as parse_error:
                # If direct parsing fails, try to extract JSON from the text
                logger.warning(f"Direct JSON parsing failed: {parse_error}")
                logger.info("Attempting to extract JSON from response...")
                
                # Look for JSON-like content between curly braces
                json_match = re.search(r'\{.*\}', clean_output, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    logger.debug(f"Extracted JSON text:\n{json_text}")
                    questions_json = json.loads(json_text)
                else:
                    raise RuntimeError(f" Could not extract valid JSON from response: {clean_output}")
            
            logger.info(f" [BedrockLLM] Generated {len(questions_json.get('questions', []))} questions")
            return questions_json

        except (ClientError, BotoCoreError) as e:
            logger.exception(" AWS error invoking Bedrock model")
            raise RuntimeError(f"Error invoking Bedrock model: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cleaned output: {e}")
            raise RuntimeError(f" Model returned malformed JSON. Got:\n{clean_output}") from e
        except Exception as e:
            logger.exception(" Unexpected error during model invocation")
            raise RuntimeError(f"Unexpected error: {e}") from e

    # ------------------------------------------------------------
    # Roadmap Generation with Retry Logic
    # ------------------------------------------------------------
    def generate_roadmap(self, profile_payload: Dict, answers_payload: List[Dict]) -> Dict:
        """
        Generate Exactly 3 career roadmap paths based on user profile + answers.
        Retry once with stricter prompt if first response fails.
        
        Args:
            profile_payload: User profile data
            answers_payload: User answers to generated questions
            
        Returns:
            Dictionary with "careerPaths" array
            
        Example response:
            {
                "careerPaths": [
                    {
                        "title": "Machine Learning Engineer",
                        "description": "...",
                        "timeToAchieve": "6-12 months",
                        "averageSalary": "₹18-20 LPA",
                        "keySkillsRequired": [...],
                        "learningRoadmap": [...],
                        "aiRecommendation": {"reason": "..."}
                    }
                ]
            }
        """
        if settings.DRY_RUN:
            return self._mock_roadmap()
        
        def _call_model(strict: bool = False):
            system_instruction = (
                "You are an AI career advisor. "
                "Using the user profile and their answers, recommend Exactly 3 suitable career paths. "
                "Return ONLY valid JSON in this format:\n"
                '{"careerPaths":[{"title":"...","description":"...","timeToAchieve":"...","averageSalary":"...","keySkillsRequired":["..."],"learningRoadmap":["..."],"aiRecommendation":{"reason":"..."}}]}'
                "When suggesting averageSalary, use the user's demographic or location information from the profile to give a realistic local salary range. If location is not provided, show india salary ranges."

            )
            if strict:
                system_instruction += (
                    " STRICT MODE: No markdown, no explanations, no extra text. "
                    "Return ONLY valid JSON matching exactly the above format."
                    "If the profile contains location, region, country, or demographic information, use it as the basis for salary estimation. show india salary ranges."

                )

            prompt = f"""
User Profile:
{json.dumps(profile_payload, indent=2)}

User Answers:
{json.dumps(answers_payload, indent=2)}

Instructions:
- Analyze interests, domain, and goals.
- Suggest Exactly 3 realistic and meaningful career paths.
- Avoid vague suggestions and duplicates.
- Return structured JSON only.
"""

            logger.info(f"🟡 [BedrockLLM] Invoking generate_roadmap (strict={strict})")

            resp = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 3072,
                    "temperature": 0.7 if not strict else 0.3,
                    "system": system_instruction,
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    ]
                })
            )

            raw_body = resp["body"].read().decode("utf-8")
            logger.debug(f"🧾 RAW BODY (roadmap):\n{raw_body}")

            if not raw_body.strip():
                raise RuntimeError(" Model returned empty response for roadmap generation.")

            parsed = json.loads(raw_body)
            clean_output = self._extract_and_clean_output(parsed)
            logger.debug(f"🧼 Cleaned roadmap output:\n{clean_output}")

            roadmap_json = json.loads(clean_output)
            return roadmap_json

        # First attempt
        try:
            roadmap = _call_model(strict=False)
            logger.info(" [BedrockLLM] Roadmap generated successfully (1st attempt)")
            return roadmap

        # Retry on parse failure or empty output
        except (json.JSONDecodeError, RuntimeError) as first_error:
            logger.warning(f"First roadmap generation attempt failed: {first_error}")
            try:
                logger.info("Retrying roadmap generation in strict mode...")
                roadmap = _call_model(strict=True)
                logger.info(" [BedrockLLM] Roadmap generated successfully on retry")
                return roadmap
            except Exception as retry_error:
                logger.error(f" Retry also failed: {retry_error}")
                raise RuntimeError(
                    f"Roadmap generation failed after retry. First error: {first_error}, Retry error: {retry_error}"
                ) from retry_error

    # ------------------------------------------------------------
    # Complete Roadmap Generation
    # ------------------------------------------------------------

    def complete_roadmap_generation(input_payload):
        logger.info(" Generating high-level roadmap...")
        high_level_prompt = build_prompt_highlevel(input_payload)
        high_level_result = invoke_bedrock_agent(high_level_prompt, "highlevel_roadmap")

        if not high_level_result:
            logger.info(" High-level roadmap generation failed.")
            exit()

        logger.info("\n High-level roadmap generated successfully.")

        logger.info("\nGenerating subtopics JSON separately...")
        subtopics_prompt = build_prompt_subtopics(high_level_result)
        subtopics_result = invoke_bedrock_agent(subtopics_prompt, "subtopics_roadmap")

        if not subtopics_result:
            logger.info("Subtopics generation failed.")
            exit()

        logger.info("\nMerging both JSONs into final roadmap...")
        merged_result = merge_roadmaps(high_level_result, subtopics_result)

        if merged_result:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # merged_path = f"outputs/final_merged_roadmap_{timestamp}.json"
            # with open(merged_path, "w", encoding="utf-8") as f:
            #     json.dump(merged_result, f, indent=2, ensure_ascii=False)
            # logger.info(f" Final merged JSON saved at: {merged_path}")

            # AWS_REGION = "us-east-1"  # change as needed
            # TABLE_NAME = "CareerRoadmaps"

            dynamodb_resource = boto3.resource("dynamodb", region_name="us-east-1")
            table = dynamodb_resource.Table("CareerRoadmaps")
            
            item = {
                "email_id": "sagar.katariya@ex.com",
                "roadmap_id": str(uuid.uuid4()),  # string
                "careerTitle": merged_result.get("careerTitle", "Unknown Career"),  # string
                "created_at": datetime.utcnow().isoformat(),  # timestamp
                "roadmap_data": merged_result  # JSON (map)
            }
            
            table.put_item(Item=item)
            logger.info(f"Inserted item with roadmap_id: {item['roadmap_id']}")
        else:
            logger.info(" Failed to merge roadmap data.")
        

    # ------------------------------------------------------------
    # Profile Summary Generation
    # ------------------------------------------------------------
    def generate_profile_summary(self, profile_payload: Dict) -> Dict:
        """
        Generate a concise 2–5 line profile summary.
        
        Args:
            profile_payload: User profile data
            
        Returns:
            Dictionary with "summary" key
            
        Example response:
            {
                "summary": "John Doe is a Master's student in Computer Science..."
            }
        """
        if settings.DRY_RUN:
            return {
                "summary": "This is a mock profile summary for testing. "
                "The user is exploring career options and skill development."
            }

        system_instruction = (
            "You are an AI career advisor. Create a concise 2–5 line profile summary "
            "that describes who the person is, what they are doing/studying, key skills/interests, "
            "and future goals. "
            "Return ONLY valid JSON: {\"summary\":\"...\"}. No markdown, no code fences."
        )

        prompt = f"""
User Profile (raw fields):
{json.dumps(profile_payload, indent=2)}

Write the summary in 2–5 lines, natural language (not bullet points). Keep it specific and career-focused.
"""
        try:
            logger.info("🟡 [BedrockLLM] Invoking generate_profile_summary")

            resp = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 512,
                    "temperature": 0.6,
                    "system": system_instruction,
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    ]
                })
            )

            raw_body = resp["body"].read().decode("utf-8")
            logger.debug(f"🧾 RAW BODY (summary):\n{raw_body}")

            if not raw_body.strip():
                raise RuntimeError(" Model returned an empty response for profile summary.")

            parsed = json.loads(raw_body)

            # reuse helper
            clean_output = self._extract_and_clean_output(parsed)
            sanitized_output = self._sanitize_summary_text(clean_output)
            logger.debug(f"🧼 Cleaned summary output:\n{clean_output}")

            # Try to parse JSON first
            try:
                obj = json.loads(sanitized_output)
                if "summary" not in obj or not obj["summary"].strip():
                    raise RuntimeError(" Missing 'summary' in model output.")
                logger.info(" [BedrockLLM] Profile summary generated")
                return obj
            except json.JSONDecodeError:
                # If the model returned plain text (rare), wrap it safely
                return {"summary": clean_output}

        except (ClientError, BotoCoreError) as e:
            logger.exception(" AWS error invoking Bedrock model for summary")
            raise RuntimeError(f"Error invoking Bedrock model: {e}") from e
        except Exception as e:
            logger.exception(" Unexpected error during summary generation")
            raise RuntimeError(f"Unexpected error: {e}") from e

    def _sanitize_summary_text(self, text: str) -> str:
        """
        Clean up the profile summary returned by the model.
        
        Args:
            text: Raw text from model
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove code fences if any
        text = text.strip().strip("`")

        # Remove escaped quotes
        text = text.replace('\\"', '"').replace("\\'", "'")

        #  Remove single quotes (')
        text = text.replace("'", "")

        # Remove any leading/trailing quotes
        text = text.strip('"')

        # Remove newlines and collapse spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ------------------------------------------------------------
    # Mock Mode (for local testing)
    # ------------------------------------------------------------
    def _mock_questions(self) -> Dict:
        """
        Return mock questions for testing without AWS calls.
        
        Returns:
            Dictionary with mock questions
        """
        return {
            "questions": [
                {"id": f"q{i+1}", "text": f"Mock question {i+1} for career exploration?"}
                for i in range(15)
            ]
        }
    
    def _mock_roadmap(self) -> Dict:
        """
        Return mock roadmap for testing without AWS calls.
        
        Returns:
            Dictionary with mock career paths
        """
        return {
            "careerPaths": [
                {
                    "title": "Mock Career Path 1",
                    "description": "This is a mock career path for testing the API without AWS calls.",
                    "timeToAchieve": "6-12 months",
                    "averageSalary": "$70,000-100,000 (USA)",
                    "keySkillsRequired": ["Skill 1", "Skill 2", "Skill 3"],
                    "learningRoadmap": ["Step 1: Learn basics", "Step 2: Practice", "Step 3: Build projects"],
                    "aiRecommendation": {"reason": "This is a mock recommendation for testing purposes."}
                },
                {
                    "title": "Mock Career Path 2",
                    "description": "Another mock career path for comprehensive testing.",
                    "timeToAchieve": "12-18 months",
                    "averageSalary": "$80,000-120,000 (USA)",
                    "keySkillsRequired": ["Advanced Skill 1", "Advanced Skill 2"],
                    "learningRoadmap": ["Step 1: Advanced learning", "Step 2: Specialization"],
                    "aiRecommendation": {"reason": "This path builds on your existing skills."}
                },
                {
                    "title": "Mock Career Path 3",
                    "description": "Third mock career option for testing.",
                    "timeToAchieve": "8-14 months",
                    "averageSalary": "$75,000-110,000 (USA)",
                    "keySkillsRequired": ["Core Skill 1", "Core Skill 2", "Core Skill 3"],
                    "learningRoadmap": ["Foundation building", "Practical experience", "Portfolio development"],
                    "aiRecommendation": {"reason": "Balanced approach to career development."}
                }
            ]
        }