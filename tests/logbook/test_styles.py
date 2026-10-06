# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock

from gselib.logbook.styles import apply_logbook_template, entry_style, heading_style, timestamp_style


class TestHeadingStyle:
    def test_range(self) -> None:
        """heading_style sets the correct start and end index."""
        result = heading_style(1, 10)
        r = result["updateParagraphStyle"]["range"]
        assert r["startIndex"] == 1
        assert r["endIndex"] == 10

    def test_named_style_type(self) -> None:
        """heading_style applies HEADING_1."""
        result = heading_style(1, 10)
        style = result["updateParagraphStyle"]["paragraphStyle"]
        assert style["namedStyleType"] == "HEADING_1"


class TestTimestampStyle:
    def test_range(self) -> None:
        """timestamp_style sets the correct start and end index."""
        result = timestamp_style(5, 25)
        r = result["updateTextStyle"]["range"]
        assert r["startIndex"] == 5
        assert r["endIndex"] == 25

    def test_bold(self) -> None:
        """timestamp_style makes the text bold."""
        result = timestamp_style(5, 25)
        assert result["updateTextStyle"]["textStyle"]["bold"] is True

    def test_fields_include_bold(self) -> None:
        """timestamp_style declares bold in the fields mask."""
        result = timestamp_style(5, 25)
        assert "bold" in result["updateTextStyle"]["fields"]


class TestEntryStyle:
    def test_range(self) -> None:
        """entry_style sets the correct start and end index."""
        result = entry_style(10, 40)
        r = result["updateParagraphStyle"]["range"]
        assert r["startIndex"] == 10
        assert r["endIndex"] == 40

    def test_named_style_type(self) -> None:
        """entry_style applies NORMAL_TEXT."""
        result = entry_style(10, 40)
        style = result["updateParagraphStyle"]["paragraphStyle"]
        assert style["namedStyleType"] == "NORMAL_TEXT"


class TestApplyLogbookTemplate:
    def test_inserts_title_text(self) -> None:
        """apply_logbook_template inserts the title at index 1."""
        docs = MagicMock()
        apply_logbook_template(docs, "doc-id", "My Logbook")
        body = docs.documents().batchUpdate.call_args.kwargs["body"]
        insert = next(r for r in body["requests"] if "insertText" in r)
        assert "My Logbook" in insert["insertText"]["text"]
        assert insert["insertText"]["location"]["index"] == 1

    def test_applies_heading_style(self) -> None:
        """apply_logbook_template styles the title as HEADING_1."""
        docs = MagicMock()
        apply_logbook_template(docs, "doc-id", "My Logbook")
        body = docs.documents().batchUpdate.call_args.kwargs["body"]
        style = next(r for r in body["requests"] if "updateParagraphStyle" in r)
        assert style["updateParagraphStyle"]["paragraphStyle"]["namedStyleType"] == "HEADING_1"

    def test_targets_correct_document(self) -> None:
        """apply_logbook_template passes the document_id to batchUpdate."""
        docs = MagicMock()
        apply_logbook_template(docs, "doc-id", "Title")
        assert docs.documents().batchUpdate.call_args.kwargs["documentId"] == "doc-id"
