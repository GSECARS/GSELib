# SPDX-License-Identifier: MIT

import pytest

pytest.importorskip("requests")

from unittest.mock import MagicMock, patch

from gselib.cloud.nextcloud.client import NextcloudClient


@pytest.fixture
def client() -> NextcloudClient:
    return NextcloudClient("https://cloud.example.com", "admin", "secret")


def _ocs(data, statuscode: int = 100) -> MagicMock:
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {"ocs": {"meta": {"statuscode": statuscode, "message": "OK"}, "data": data}}
    return mock


class TestNextcloudClientShare:
    def test_share_local_user(self, client: NextcloudClient) -> None:
        """Share with a local username sets share_type_user and the correct recipient."""
        with patch("requests.request", return_value=_ocs({"id": 1, "share_with": "alice"})) as mock:
            result = client.share("/data", "alice")
        assert result["id"] == 1
        call_data = mock.call_args.kwargs["data"]
        assert call_data["shareType"] == NextcloudClient.share_type_user
        assert call_data["shareWith"] == "alice"

    def test_share_federated_user(self, client: NextcloudClient) -> None:
        """Share with an address containing @ sets share_type_federated."""
        with patch("requests.request", return_value=_ocs({"id": 2, "share_with": "bob@other.org"})) as mock:
            client.share("/data", "bob@other.org")
        assert mock.call_args.kwargs["data"]["shareType"] == NextcloudClient.share_type_federated

    def test_share_default_permissions(self, client: NextcloudClient) -> None:
        """Share without explicit permissions defaults to perm_read."""
        with patch("requests.request", return_value=_ocs({"id": 1})) as mock:
            client.share("/data", "alice")
        assert mock.call_args.kwargs["data"]["permissions"] == NextcloudClient.perm_read

    def test_share_custom_permissions(self, client: NextcloudClient) -> None:
        """Share passes through a custom permission bitmask unchanged."""
        with patch("requests.request", return_value=_ocs({"id": 1})) as mock:
            client.share("/data", "alice", NextcloudClient.perm_all)
        assert mock.call_args.kwargs["data"]["permissions"] == NextcloudClient.perm_all

    def test_share_with_many_list(self, client: NextcloudClient) -> None:
        """share_with_many issues one share request per recipient and returns all results."""
        responses = [_ocs({"id": 1, "share_with": "alice"}), _ocs({"id": 2, "share_with": "bob"})]
        with patch("requests.request", side_effect=responses):
            results = client.share_with_many("/data", ["alice", "bob"])
        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[1]["id"] == 2

    def test_share_with_many_single_string(self, client: NextcloudClient) -> None:
        """share_with_many accepts a bare string and wraps it in a single-item list."""
        with patch("requests.request", return_value=_ocs({"id": 1, "share_with": "alice"})):
            results = client.share_with_many("/data", "alice")
        assert len(results) == 1
        assert results[0]["share_with"] == "alice"


class TestNextcloudClientShares:
    def test_list_shares(self, client: NextcloudClient) -> None:
        """list_shares returns all shares when no path filter is given."""
        shares = [{"id": 1, "path": "/data"}, {"id": 2, "path": "/other"}]
        with patch("requests.request", return_value=_ocs(shares)):
            result = client.list_shares()
        assert result == shares

    def test_list_shares_with_path(self, client: NextcloudClient) -> None:
        """list_shares appends a ?path= query parameter when a path is given."""
        with patch("requests.request", return_value=_ocs([])) as mock:
            client.list_shares(path="/data")
        url = mock.call_args.args[1]
        assert "?path=/data" in url

    def test_list_shares_without_path(self, client: NextcloudClient) -> None:
        """list_shares omits the query string entirely when no path is given."""
        with patch("requests.request", return_value=_ocs([])) as mock:
            client.list_shares()
        url = mock.call_args.args[1]
        assert "?" not in url

    def test_delete_share(self, client: NextcloudClient) -> None:
        """delete_share issues a DELETE request to the share's endpoint by ID."""
        with patch("requests.request", return_value=_ocs({})) as mock:
            client.delete_share(5)
        assert mock.call_args.args[0] == "DELETE"
        assert mock.call_args.args[1].endswith("/5")


class TestNextcloudClientErrors:
    def test_ocs_error_raises_runtime_error(self, client: NextcloudClient) -> None:
        """A non-100/200 OCS statuscode raises RuntimeError containing the code."""
        with patch("requests.request", return_value=_ocs({}, statuscode=404)):
            with pytest.raises(RuntimeError, match="404"):
                client.list_shares()

    def test_http_error_propagates(self, client: NextcloudClient) -> None:
        """An HTTP-level error from raise_for_status propagates unchanged."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500")
        with patch("requests.request", return_value=mock_response):
            with pytest.raises(Exception, match="HTTP 500"):
                client.list_shares()

    def test_ocs_200_is_success(self, client: NextcloudClient) -> None:
        """OCS statuscode 200 is treated as success alongside 100."""
        with patch("requests.request", return_value=_ocs([{"id": 1}], statuscode=200)):
            result = client.list_shares()
        assert result == [{"id": 1}]
