import asyncio
import json
import os
from typing import Optional

try:
    import openai
except Exception:
    openai = None

from .drive_search import DriveSearchTool, SearchRequest
from .llm_parse import parse_nl_to_search

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


async def nl_to_search_via_function_call(nl: str, drive_tool: Optional[DriveSearchTool] = None):
    """Use OpenAI function-calling to translate NL to SearchRequest, then run the Drive search.

    Falls back to `parse_nl_to_search` if OpenAI is not available or errors occur.
    """
    drive_tool = drive_tool or DriveSearchTool()

    if openai and OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        system = (
            "You are an assistant that converts user instructions into a JSON object for searching Google Drive. "
            "Return a JSON object with keys: name, full_text, mime_type, modified_after (ISO datetime), folder_id, page_size. "
            "Use null for missing fields."
        )
        user = nl

        functions = [
            {
                "name": "build_search",
                "description": "Build a drive search JSON",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": ["string", "null"]},
                        "full_text": {"type": ["string", "null"]},
                        "mime_type": {"type": ["string", "null"]},
                        "modified_after": {"type": ["string", "null"], "format": "date-time"},
                        "folder_id": {"type": ["string", "null"]},
                        "page_size": {"type": ["integer", "null"]},
                    },
                    "required": [],
                },
            }
        ]

        try:
            resp = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo-0613",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                functions=functions,
                function_call="auto",
                max_tokens=300,
                temperature=0,
            )

            msg = resp.choices[0].message
            if msg.get("function_call"):
                args_text = msg["function_call"]["arguments"]
                try:
                    args = json.loads(args_text)
                except Exception:
                    args = {}
                # build SearchRequest
                from .drive_search import SearchRequest as SR

                modified_after = None
                if args.get("modified_after"):
                    try:
                        from dateutil import parser

                        modified_after = parser.isoparse(args.get("modified_after"))
                    except Exception:
                        modified_after = None

                sr = SR(
                    name=args.get("name"),
                    full_text=args.get("full_text"),
                    mime_type=args.get("mime_type"),
                    modified_after=modified_after,
                    folder_id=args.get("folder_id"),
                    page_size=int(args.get("page_size") or 20),
                )
                results = await drive_tool.search(sr)
                return results
        except Exception:
            # fall through to heuristic parser
            pass

    # fallback: heuristic parser
    sr = await parse_nl_to_search(nl)
    results = await drive_tool.search(sr)
    return results
