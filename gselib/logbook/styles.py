# SPDX-License-Identifier: MIT


def heading_style(start_index: int, end_index: int) -> dict:
    return {
        "updateParagraphStyle": {
            "range": {"startIndex": start_index, "endIndex": end_index},
            "paragraphStyle": {"namedStyleType": "HEADING_1"},
            "fields": "namedStyleType",
        }
    }


def timestamp_style(start_index: int, end_index: int) -> dict:
    return {
        "updateTextStyle": {
            "range": {"startIndex": start_index, "endIndex": end_index},
            "textStyle": {"bold": True, "foregroundColor": {"color": {"rgbColor": {"red": 0.2, "green": 0.2, "blue": 0.2}}}},
            "fields": "bold,foregroundColor",
        }
    }


def entry_style(start_index: int, end_index: int) -> dict:
    return {
        "updateParagraphStyle": {
            "range": {"startIndex": start_index, "endIndex": end_index},
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "fields": "namedStyleType",
        }
    }


def apply_logbook_template(docs, document_id: str, title: str) -> None:
    """Apply heading style to the document title on a freshly created logbook."""
    requests = [
        {"insertText": {"location": {"index": 1}, "text": f"{title}\n"}},
        heading_style(1, len(title) + 1),
    ]
    docs.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
