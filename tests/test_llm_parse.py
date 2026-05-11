import asyncio
from backend.app.llm_parse import parse_nl_to_search


def test_parse_name_quoted():
    sr = asyncio.run(parse_nl_to_search("Find invoice 'Quarterly Report'"))
    assert sr.name == "Quarterly Report" or sr.full_text is not None


def test_parse_mime_hint():
    sr = asyncio.run(parse_nl_to_search("Show me the latest PDF financial reports"))
    assert sr.mime_type == "application/pdf" or sr.full_text is not None
