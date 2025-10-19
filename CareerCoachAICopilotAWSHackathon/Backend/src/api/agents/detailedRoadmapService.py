import os
import json
import boto3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from ..utils.errorHandler import get_logger, settings

logger = get_logger(__name__)

class DetailedRoadmapService:
    """Service for generating detailed roadmaps using Bedrock Agent."""
    
    def __init__(self):
        # Use the provided Bedrock Agent configuration
        self.region = settings.BEDROCK_REGION
        self.agent_id = settings.BEDROCK_DETAILED_ROADMAP_AGENT_ID
        self.agent_alias_id = settings.BEDROCK_DETAILED_ROADMAP_AGENT_ALIAS_ID
        self.session_id = str(uuid.uuid4())  # Generate new UUID for each session
        
        # Initialize Bedrock Agent client
        self.client = boto3.client(
            "bedrock-agent-runtime",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        logger.info("DetailedRoadmapService initialized with Bedrock Agent")
    
    def build_prompt_highlevel(self, payload: Dict[str, Any]) -> str:
        """Prompt for high-level roadmap generation with verified course links."""
        return f"""
        You are an expert AI career roadmap generator.

        Here is the input career profile JSON:
        {json.dumps(payload, indent=2)}

        Generate a **high-level learning roadmap** divided into these phases:
        1. Beginner
        2. Intermediate
        3. Advanced
        4. Capstone Projects

        For each phase, include:
        - Short description of what to learn
        - Duration (weeks or months)
        - 2-3 verified and real resource links only from these domains:
            - https://www.coursera.org
            - https://www.udemy.com
            - https://www.youtube.com
            - https://www.tensorflow.org
            - https://www.python.org
        - Do NOT include links from:
            - edx.org 
            - outside the listed domains
        - official documentation sites (e.g., tensorflow.org, python.org)
        - **DO NOT invent or fabricate links.**
        - If no valid link is known, leave the resources list empty.
        - Do NOT use homepage or search result pages (e.g., coursera.org/, youtube.com/).
        - All URLs you provide will be validated against allowed domains. Invalid or dead links will be removed automatically.

        
        Key outcomes
        - For Capstone Projects:
          - Provide 2-3 project ideas with duration and brief description.

        Output strictly in valid JSON with this structure::
        {{
          "careerTitle": "<title>",
          "highLevelRoadmap": [
            {{
              "phase": "Beginner",
              "duration": "3 months",
              "topics": ["..."],
              "resources": [<Link Title>: "https://..."],
              "outcomes": ["..."]
            }},
            {{
              "phase": "Intermediate",
              ...
            }}
          ],
          "capstoneProjects": [ ... ]
        }}

        Important:
        - Return only real, existing URLs from the trusted domains listed above.
        - Do not make up fake links or use placeholder URLs.
        - If unsure, leave the list empty.
        - Return strictly valid JSON only, with no extra text or commentary.
        """
    
    def build_prompt_subtopics(self, high_level_json: Dict[str, Any]) -> str:
        """Prompt to generate subtopics separately for each topic."""
        return f"""
        You are an educational content planner AI.

        Below is a JSON representing a career learning roadmap:
        {json.dumps(high_level_json, indent=2)}

        For each topic under each phase, generate **4–5 detailed subtopics**.

        Output JSON in this format:
        {{
          "subtopicsBreakdown": [
            {{
              "phase": "<phase name>",
              "topics": [
                {{
                  "topic": "<original topic>",
                  "subtopics": ["subtopic1", "subtopic2", "subtopic3", "subtopic4"]
                }}
              ]
            }}
          ]
        }}

        Ensure valid JSON only.
        """
    
    def invoke_bedrock_agent(self, prompt: str, filename_prefix: str) -> Optional[Dict[str, Any]]:
        """Invoke Bedrock Agent and return parsed JSON."""
        try:
            logger.info(f"Invoking Bedrock Agent for: {filename_prefix}")
            
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                inputText=prompt,
                sessionId=self.session_id,
            )

            collected = []
            for event in response.get("completion", []):
                if "chunk" in event:
                    chunk = event["chunk"]
                    if "bytes" in chunk:
                        collected.append(chunk["bytes"].decode("utf-8"))
                    elif "text" in chunk:
                        collected.append(chunk["text"])

            final_text = "".join(collected).strip()
            
            try:
                parsed = json.loads(final_text)
                logger.info(f"Bedrock Agent response parsed successfully for: {filename_prefix}")
                return parsed
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from Bedrock Agent for {filename_prefix}: {e}")
                logger.debug(f"Raw response: {final_text}")
                return None
                
        except Exception as e:
            logger.error(f"Bedrock Agent error for {filename_prefix}: {e}")
            return None
    
    def merge_roadmaps(self, high_level: Dict[str, Any], subtopics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Merge subtopics into the high-level roadmap."""
        if not high_level or not subtopics:
            logger.error("Missing data for merging.")
            return None

        merged = {
            "careerTitle": high_level.get("careerTitle"),
            "highLevelRoadmap": [],
            "capstoneProjects": high_level.get("capstoneProjects", [])
        }

        # Create subtopic mapping
        subtopic_map = {}
        for phase in subtopics.get("subtopicsBreakdown", []):
            phase_name = phase["phase"]
            subtopic_map[phase_name] = {}
            for topic_data in phase.get("topics", []):
                topic_name = topic_data["topic"]
                subtopic_map[phase_name][topic_name] = topic_data.get("subtopics", [])

        # Merge phases
        for phase in high_level.get("highLevelRoadmap", []):
            merged_phase = {
                "phase": phase["phase"],
                "duration": phase.get("duration"),
                "resources": phase.get("resources", []),
                "outcomes": phase.get("outcomes", []),
                "topics": []
            }

            for topic in phase.get("topics", []):
                # Get subtopics for this topic in this phase
                sub_list = subtopic_map.get(phase["phase"], {}).get(topic, [])
                merged_phase["topics"].append({
                    "topic": topic,
                    "subtopics": sub_list,
                    "isCompleted": False,
                    "totalQuestions": 5,  # Default number of questions per topic
                    "correctAnswers": 0,
                    "score": 0.0
                })

            merged["highLevelRoadmap"].append(merged_phase)

        logger.info("Roadmaps merged successfully")
        return merged
    
    def update_topic_progress(self, roadmap_data: Dict[str, Any], topic_name: str, correct_answers: int, total_questions: int) -> Dict[str, Any]:
        """
        Update progress for a specific topic in the roadmap.
        
        Args:
            roadmap_data: The complete roadmap data
            topic_name: Name of the topic to update
            correct_answers: Number of correct answers
            total_questions: Total number of questions
            
        Returns:
            Updated roadmap data
        """
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0.0
        is_completed = score >= 60.0  # 60% threshold for completion
        
        # Update the topic in all phases
        for phase in roadmap_data.get("highLevelRoadmap", []):
            for topic in phase.get("topics", []):
                if topic["topic"] == topic_name:
                    topic["correctAnswers"] = correct_answers
                    topic["totalQuestions"] = total_questions
                    topic["score"] = round(score, 2)
                    topic["isCompleted"] = True
                    logger.info(f"Updated progress for topic '{topic_name}': {correct_answers}/{total_questions} ({score:.1f}%)")
                    break
        
        return roadmap_data
    
    def generate_detailed_roadmap(self, input_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate complete detailed roadmap using two-phase approach."""
        try:
            logger.info(f"Starting detailed roadmap generation for: {input_payload.get('title', 'Unknown')}")
            
            # Phase 1: Generate high-level roadmap
            logger.info("Phase 1: Generating high-level roadmap...")
            high_level_prompt = self.build_prompt_highlevel(input_payload)
            high_level_result = self.invoke_bedrock_agent(high_level_prompt, "highlevel_roadmap")
            
            if not high_level_result:
                logger.error("High-level roadmap generation failed.")
                return None
            
            logger.info("High-level roadmap generated successfully.")
            
            # Phase 2: Generate subtopics
            logger.info("Phase 2: Generating subtopics...")
            subtopics_prompt = self.build_prompt_subtopics(high_level_result)
            subtopics_result = self.invoke_bedrock_agent(subtopics_prompt, "subtopics_roadmap")
            
            if not subtopics_result:
                logger.warning("Subtopics generation failed, using high-level only.")
                return high_level_result
            
            logger.info("Subtopics generated successfully.")
            
            # Phase 3: Merge results
            logger.info("Phase 3: Merging roadmaps...")
            merged_result = self.merge_roadmaps(high_level_result, subtopics_result)
            
            if merged_result:
                logger.info("Detailed roadmap generation completed successfully!")
                return merged_result
            else:
                logger.warning("Merging failed, returning high-level result.")
                return high_level_result
                
        except Exception as e:
            logger.error(f"Unexpected error in detailed roadmap generation: {e}")
            return None

# Singleton instance
_detailed_roadmap_service = None

def get_detailed_roadmap_service() -> DetailedRoadmapService:
    """Get singleton instance of DetailedRoadmapService."""
    global _detailed_roadmap_service
    if _detailed_roadmap_service is None:
        _detailed_roadmap_service = DetailedRoadmapService()
    return _detailed_roadmap_service
