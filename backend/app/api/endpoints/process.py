import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.manager import AIAgentManager
from app.sandbox.docker_exec import SandboxExecutionManager

load_dotenv()
router = APIRouter()


class ProcessRequest(BaseModel):
    file_path: str
    data_profile: Dict[str, Any]
    user_preferences: Dict[str, Any]


@router.post("/")
async def process_dataset(request: ProcessRequest):
    """
    Receives dataset profiling info and user preferences, requests Python
    transformation code from the AI agent, and executes it inside the sandbox.
    """
    try:
        # Fetch key from environment configuration
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")

        # Generate transformation script using the Gemini agent
        agent = AIAgentManager(api_key=api_key)
        generated_code = agent.generate_preprocessing_code(
            data_profile=request.data_profile,
            user_preferences=request.user_preferences
        )

        # Securely execute the generated script in the Docker container
        sandbox = SandboxExecutionManager()
        execution_result = sandbox.execute_code(
            generated_code=generated_code,
            file_path=request.file_path
        )

        # Return execution payload to caller
        return {
            "status": "success",
            "generated_code": generated_code,
            "execution_logs": execution_result.get("logs", "Execution completed without log output."),
            "cleaned_file_path": execution_result.get("cleaned_file_path")
        }

    except Exception as e:
        print(f"Error in process_dataset endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))