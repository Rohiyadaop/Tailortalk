from pydantic import BaseModel
from typing import List, Optional
import datetime
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build


class SearchRequest(BaseModel):
    name: Optional[str] = None
    full_text: Optional[str] = None
    mime_type: Optional[str] = None
    modified_after: Optional[datetime.datetime] = None
    folder_id: Optional[str] = None
    page_size: int = 20


class SearchResult(BaseModel):
    id: str
    name: str
    mimeType: Optional[str] = None
    webViewLink: Optional[str] = None
    modifiedTime: Optional[str] = None


class DriveSearchTool:
    def __init__(self, service_account_file: Optional[str] = None, folder_id: Optional[str] = None):
        # service_account_file: path to service account JSON
        self.service_account_file = service_account_file or os.environ.get("SERVICE_ACCOUNT_FILE")
        self.folder_id = folder_id or os.environ.get("DRIVE_FOLDER_ID")
        self._service = None

    def _get_service(self):
        if self._service:
            return self._service
        if not self.service_account_file:
            raise RuntimeError("Service account file not configured. Set SERVICE_ACCOUNT_FILE env var or pass path.")
        creds = service_account.Credentials.from_service_account_file(self.service_account_file, scopes=["https://www.googleapis.com/auth/drive.readonly"])
        service = build("drive", "v3", credentials=creds, cache_discovery=False)
        self._service = service
        return service

    async def search(self, req: SearchRequest) -> List[SearchResult]:
        """Perform a Drive files().list using a constructed `q` parameter.

        Supports searching by name (contains), fullText, mimeType, modifiedTime, and optionally limiting to a folder.
        """
        service = self._get_service()

        q_parts = []
        if req.name:
            # escape single quotes in the user input
            safe_name = req.name.replace("'", "\\'")
            q_parts.append(f"name contains '{safe_name}'")
        if req.full_text:
            safe_full = req.full_text.replace("'", "\\'")
            q_parts.append(f"fullText contains '{safe_full}'")
        if req.mime_type:
            q_parts.append(f"mimeType = '{req.mime_type}'")
        # modified_after is datetime
        if req.modified_after:
            iso = req.modified_after.astimezone(datetime.timezone.utc).isoformat()
            q_parts.append(f"modifiedTime > '{iso}'")
        # restrict to folder if provided (request overrides default)
        folder = req.folder_id or self.folder_id
        if folder:
            q_parts.append(f"'{folder}' in parents")

        q = " and ".join(q_parts) if q_parts else None

        results: List[SearchResult] = []
        page_token = None
        while True:
            params = {
                "pageSize": req.page_size,
                "fields": "nextPageToken, files(id, name, mimeType, webViewLink, modifiedTime)",
                "supportsAllDrives": True,
                "includeItemsFromAllDrives": True,
            }
            if q:
                params["q"] = q
            if page_token:
                params["pageToken"] = page_token

            resp = service.files().list(**params).execute()
            for f in resp.get("files", []):
                results.append(SearchResult(
                    id=f.get("id"),
                    name=f.get("name"),
                    mimeType=f.get("mimeType"),
                    webViewLink=f.get("webViewLink"),
                    modifiedTime=f.get("modifiedTime"),
                ))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        return results
