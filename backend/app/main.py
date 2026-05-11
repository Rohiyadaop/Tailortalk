from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import os

# load .env automatically when the app imports (makes local dev easier)
from dotenv import load_dotenv
load_dotenv()

from .drive_search import DriveSearchTool, SearchRequest, SearchResult
from .llm_parse import parse_nl_to_search
from .agent_search import nl_to_search_via_function_call

app = FastAPI(title="Drive Search Agent - Backend")

# instantiate the Drive search tool. Configure with env vars SERVICE_ACCOUNT_FILE and DRIVE_FOLDER_ID
drive_tool = DriveSearchTool()


@app.post("/search", response_model=List[SearchResult])
async def search(req: SearchRequest):
    """Perform a structured search (JSON payload -> Drive files.list)."""
    try:
        results = await drive_tool.search(req)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class NLRequest(BaseModel):
    query: str


@app.post("/nl_search", response_model=List[SearchResult])
async def nl_search(req: NLRequest):
    """Accept natural language, translate to SearchRequest via LLM, then run Drive search."""
    try:
        sr = await parse_nl_to_search(req.query)
        results = await drive_tool.search(sr)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent_search", response_model=List[SearchResult])
async def agent_search(req: NLRequest):
    """Use function-calling agent to translate NL -> structured query and run Drive search."""
    try:
        results = await nl_to_search_via_function_call(req.query, drive_tool=drive_tool)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
