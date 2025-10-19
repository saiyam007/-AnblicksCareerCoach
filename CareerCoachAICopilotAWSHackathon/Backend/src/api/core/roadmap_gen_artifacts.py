import os
import json
import boto3
import uuid
from dotenv import load_dotenv
from datetime import datetime

# ---------------------------------------------------------
# PROMPT BUILDERS
# ---------------------------------------------------------
def build_prompt_highlevel(payload):
    """Prompt for high-level roadmap generation."""
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
    - 2–3 resource links (Coursera, YouTube, or official docs) with link title
    - Key outcomes

    For Capstone Projects:
    - Provide 2–3 project ideas with duration and brief description.

    Output JSON structure:
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

    Return strictly valid JSON only.
    """

def build_prompt_subtopics(high_level_json):
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

# ---------------------------------------------------------
# INVOKE AGENT
# ---------------------------------------------------------
def invoke_bedrock_agent(prompt, filename_prefix):
    """Invoke Bedrock Agent and save JSON output."""
    response = client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        inputText=prompt,
        sessionId=SESSION_ID,
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("outputs", exist_ok=True)
    json_path = f"outputs/{filename_prefix}_{timestamp}.json"
    raw_path = f"outputs/{filename_prefix}_raw_{timestamp}.txt"

    try:
        parsed = json.loads(final_text)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        return parsed
    except json.JSONDecodeError:
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(final_text)
        return None

# ---------------------------------------------------------
# MERGE FUNCTION
# ---------------------------------------------------------
def merge_roadmaps(high_level, subtopics):
    """Merge subtopics into the high-level roadmap."""
    if not high_level or not subtopics:
        return None

    merged = {
        "careerTitle": high_level.get("careerTitle"),
        "highLevelRoadmap": [],
        "capstoneProjects": high_level.get("capstoneProjects", [])
    }

    subtopic_map = {
        phase["phase"]: {t["topic"]: t["subtopics"] for t in phase["topics"]}
        for phase in subtopics.get("subtopicsBreakdown", [])
    }

    for phase in high_level.get("highLevelRoadmap", []):
        merged_phase = {
            "phase": phase["phase"],
            "duration": phase.get("duration"),
            "resources": phase.get("resources", []),
            "outcomes": phase.get("outcomes", []),
            "topics": []
        }

        for topic in phase.get("topics", []):
            sub_list = subtopic_map.get(phase["phase"], {}).get(topic, [])
            merged_phase["topics"].append({
                "topic": topic,
                "subtopics": sub_list
            })

        merged["highLevelRoadmap"].append(merged_phase)

    return merged