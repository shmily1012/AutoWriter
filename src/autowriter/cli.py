"""Command line interface for AutoWriter prototype."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from textwrap import indent

from .services import AutoWriterService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lightweight AutoWriter project manager")
    parser.add_argument("--root", type=Path, default=Path.home() / ".autowriter", help="Storage root directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-project", help="Create a new project")
    create.add_argument("name")
    create.add_argument("author")
    create.add_argument("--description", default="")

    list_projects = subparsers.add_parser("list", help="List projects")

    show = subparsers.add_parser("show", help="Show a single project")
    show.add_argument("project_id")

    add_character = subparsers.add_parser("add-character", help="Add a character")
    add_character.add_argument("project_id")
    add_character.add_argument("name")
    add_character.add_argument("--bio", default="")
    add_character.add_argument("--tags", nargs="*", default=[])

    add_chapter = subparsers.add_parser("add-chapter", help="Add a chapter entry")
    add_chapter.add_argument("project_id")
    add_chapter.add_argument("index", type=int)
    add_chapter.add_argument("title")
    add_chapter.add_argument("--outline", default="")
    add_chapter.add_argument("--content", default="")

    add_foreshadow = subparsers.add_parser("add-foreshadow", help="Track a foreshadow/clue")
    add_foreshadow.add_argument("project_id")
    add_foreshadow.add_argument("description")
    add_foreshadow.add_argument("--status", default="planned")
    add_foreshadow.add_argument("--first-chapter-id")
    add_foreshadow.add_argument("--resolve-chapter-id")

    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging verbosity (default: WARNING)",
    )

    return parser


def _print_project(project) -> None:
    print(f"{project.name} ({project.id})")
    print(f"Author: {project.author}")
    if project.description:
        print(project.description)
    print(f"Characters: {len(project.characters)} | Settings: {len(project.settings)} | Chapters: {len(project.chapters)} | Foreshadows: {len(project.foreshadows)}")

    if project.characters:
        print("\nCharacters:")
        for char in project.characters:
            tag_str = ", ".join(char.tags)
            print(f"- {char.name} ({char.id}) [{tag_str}]")
            if char.bio:
                print(indent(char.bio, "  "))

    if project.chapters:
        print("\nChapters:")
        for chapter in sorted(project.chapters, key=lambda c: c.index):
            print(f"- #{chapter.index} {chapter.title} ({chapter.id})")
            if chapter.outline:
                print(indent(f"Outline: {chapter.outline}", "  "))
            if chapter.content:
                preview = (chapter.content[:120] + "...") if len(chapter.content) > 120 else chapter.content
                print(indent(preview, "  "))

    if project.foreshadows:
        print("\nForeshadows:")
        for clue in project.foreshadows:
            print(f"- {clue.description} [{clue.status}] ({clue.id})")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    service = AutoWriterService(args.root)

    if args.command == "create-project":
        project = service.create_project(args.name, args.author, args.description)
        print(f"Created project {project.name} with id {project.id}")
        return 0

    if args.command == "list":
        for project in service.list_projects():
            print(f"- {project.name} ({project.id})")
        return 0

    if args.command == "show":
        project = service.get_project(args.project_id)
        _print_project(project)
        return 0

    if args.command == "add-character":
        character = service.add_character(args.project_id, args.name, args.bio, tags=args.tags)
        print(f"Added character {character.name} ({character.id})")
        return 0

    if args.command == "add-chapter":
        chapter = service.add_chapter(args.project_id, args.index, args.title, args.outline, args.content)
        print(f"Added chapter #{chapter.index} {chapter.title} ({chapter.id})")
        return 0

    if args.command == "add-foreshadow":
        clue = service.add_foreshadow(
            args.project_id,
            args.description,
            status=args.status,
            first_chapter_id=args.first_chapter_id,
            resolve_chapter_id=args.resolve_chapter_id,
        )
        print(f"Tracked foreshadow {clue.description} ({clue.id})")
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
