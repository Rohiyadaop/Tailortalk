from fastapi.testclient import TestClient

from backend.app import main


def test_search_endpoint_monkeypatch(monkeypatch):
    class DummyTool:
        async def search(self, req):
            return [{
                "id": "1",
                "name": "Mock.pdf",
                "mimeType": "application/pdf",
                "webViewLink": "https://example.com/mock",
                "modifiedTime": "2026-01-01T00:00:00Z",
            }]

    monkeypatch.setattr(main, "drive_tool", DummyTool())
    client = TestClient(main.app)
    resp = client.post("/search", json={"name": "Mock"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Mock.pdf"
