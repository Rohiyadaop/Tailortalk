import os
import json
from typing import Optional
from .drive_search import SearchRequest

try:
    import openai
except Exception:
    openai = None


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


async def parse_nl_to_search(nl: str) -> SearchRequest:
    """Use OpenAI to translate natural language into a SearchRequest JSON.

    If OpenAI is not configured, fall back to a simple heuristic parser.
    """
    text = None
    if openai and OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        # Use ChatCompletion (gpt-3.5-turbo) to translate instruction into JSON
        system = (
            "You are a helpful assistant. Translate the user's instruction into a JSON object with keys: "
            "name, full_text, mime_type, modified_after (ISO datetime), folder_id, page_size. "
            "Return only valid JSON. If a field is not present, set it to null."
        )
        user = f"Instruction: {nl}"
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                max_tokens=300,
                temperature=0,
            )
            text = resp.choices[0].message.content.strip()
        except Exception as e:
            # Likely quota or API error — fall back to heuristic parser below
            text = None
        # attempt to parse JSON from text
        try:
            if text:
                data = json.loads(text)
            else:
                data = {}
        except Exception:
            # best-effort: find first { ... }
            try:
                start = text.find("{") if text else -1
                end = text.rfind("}") if text else -1
                if start != -1 and end != -1:
                    data = json.loads(text[start:end+1])
                else:
                    data = {}
            except Exception:
                data = {}
    else:
        # fallback heuristic: very simple parsing
        data = {}
        data["name"] = None
        data["full_text"] = None
        data["mime_type"] = None
        data["modified_after"] = None
        data["folder_id"] = None
        data["page_size"] = 20
        # crude heuristics
        nl_low = nl.lower()
        if "pdf" in nl_low or "pdf" in nl:
            data["mime_type"] = "application/pdf"
        if "sheet" in nl_low or "spreadsheet" in nl_low:
            data["mime_type"] = "application/vnd.google-apps.spreadsheet"
        # pick a quoted phrase as name
        import re
        m = re.search(r"'([^']+)'|\"([^\"]+)\"", nl)
        if m:
            data["name"] = m.group(1) or m.group(2)
        else:
            # if contains the word report or invoice, set full_text
            if "report" in nl_low or "invoice" in nl_low:
                data["full_text"] = nl
    # normalize into SearchRequest
    # handle datetime parsing
    modified_after = None
    if data.get("modified_after"):
        from dateutil import parser
        try:
            modified_after = parser.isoparse(data.get("modified_after"))
        except Exception:
            modified_after = None
    sr = SearchRequest(
        name=data.get("name"),
        full_text=data.get("full_text"),
        mime_type=data.get("mime_type"),
        modified_after=modified_after,
        folder_id=data.get("folder_id"),
        page_size=int(data.get("page_size") or 20),
    )
    return sr
