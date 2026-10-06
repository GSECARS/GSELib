# SPDX-License-Identifier: MIT

from gselib.deps import available, require

if available("logbook"):
    from gselib.logbook.logbook import Logbook

__all__ = ["Logbook"]


def add_logbook_subparser(subparsers) -> None:
    """Registers the logbook subcommand on the given subparsers."""
    if not available("logbook"):
        return

    logbook = subparsers.add_parser("logbook", help="logbook operations via Google Docs")
    logbook.add_argument("--doc-id", metavar="ID", help="Google Doc ID (or set LOGBOOK_DOCUMENT_ID in .env)")
    logbook.add_argument("--env", default=".env", metavar="FILE", help="path to .env file (default: .env)")

    commands = logbook.add_subparsers(dest="logbook_command", metavar="command", required=True)

    create = commands.add_parser("create", help="create a new logbook document")
    create.add_argument("title", help="title for the new Google Doc")

    append = commands.add_parser("append", help="append a timestamped entry")
    append.add_argument("text", help="message to append")

    save = commands.add_parser("save", help="export the logbook to a local file")
    save.add_argument("path", help="output path (.pdf, .docx, .txt, or .md)")

    share = commands.add_parser("share", help="share the logbook with a user")
    share.add_argument("email", help="recipient email address")
    share.add_argument("--role", choices=["editor", "viewer", "commenter"], default="editor", help="permission role (default: editor)")


@require("logbook")
def run_logbook_command(args) -> None:
    """Dispatches a parsed logbook command to the appropriate handler."""
    from gselib.logbook.logbook import Logbook

    logbook = Logbook(
        document_id=args.doc_id if args.logbook_command != "create" else None,
        env_file=args.env,
        create_title=args.title if args.logbook_command == "create" else None,
    )

    if args.logbook_command == "create":
        print(f"Created logbook '{args.title}' with document ID: {logbook.document_id}")
    elif args.logbook_command == "append":
        logbook.append(args.text)
    elif args.logbook_command == "save":
        logbook.save(args.path)
    elif args.logbook_command == "share":
        role_map = {"editor": "writer", "viewer": "reader", "commenter": "commenter"}
        logbook.share(args.email, role_map[args.role])
