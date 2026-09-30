# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field

import requests
from requests.auth import HTTPBasicAuth


@dataclass
class NextcloudClient:
    share_type_user = 0
    share_type_federated = 6

    perm_read = 1
    perm_update = 2
    perm_create = 4
    perm_delete = 8
    perm_share = 16
    perm_all = 31

    base_url: str
    user: str
    password: str
    _auth: HTTPBasicAuth = field(init=False, repr=False, compare=False)
    _headers: dict = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self._auth = HTTPBasicAuth(self.user, self.password)
        self._headers = {"OCS-APIREQUEST": "true", "Accept": "application/json"}

    def _request(self, method: str, path: str, data: dict = None) -> dict | list:
        """Executes an OCS API request and returns the data payload."""
        response = requests.request(method, f"{self.base_url}{path}", data=data, auth=self._auth, headers=self._headers, timeout=30)
        response.raise_for_status()
        body = response.json()
        meta = body.get("ocs", {}).get("meta", {})
        if meta.get("statuscode") not in (100, 200):
            raise RuntimeError(f"OCS {meta.get('statuscode')}: {meta.get('message')}")
        return body["ocs"]["data"]

    def share(self, path: str, recipient: str, permissions: int = perm_read) -> dict:
        """Shares a Nextcloud path with a single user or federated address."""
        share_type = self.share_type_federated if "@" in recipient else self.share_type_user
        return self._request(
            "POST", "/ocs/v2.php/apps/files_sharing/api/v1/shares", {"path": path, "shareType": share_type, "shareWith": recipient, "permissions": permissions}
        )

    def share_with_many(self, path: str, recipients: str | list[str], permissions: int = perm_read) -> list[dict]:
        """Shares a Nextcloud path with one or more users or federated addresses."""
        if isinstance(recipients, str):
            recipients = [recipients]
        return [self.share(path, r, permissions) for r in recipients]

    def list_shares(self, path: str = None) -> list:
        """Returns all shares, optionally filtered by path."""
        params = f"?path={path}" if path else ""
        return self._request("GET", f"/ocs/v2.php/apps/files_sharing/api/v1/shares{params}")

    def delete_share(self, share_id: int) -> None:
        """Deletes a share by its ID."""
        self._request("DELETE", f"/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}")
