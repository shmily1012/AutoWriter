from pathlib import Path

from autowriter.services import AutoWriterService


def test_project_lifecycle(tmp_path: Path):
    service = AutoWriterService(tmp_path)

    project = service.create_project("My Novel", "Author", "A test project")
    assert project.name == "My Novel"

    loaded = service.get_project(project.id)
    assert loaded.author == "Author"

    character = service.add_character(project.id, "Hero", bio="Protagonist")
    assert character.name == "Hero"

    chapter = service.add_chapter(project.id, 1, "Opening", outline="Intro", content="Once upon a time")
    assert chapter.index == 1

    updated = service.update_chapter(project.id, chapter.id, content="Expanded content")
    assert updated.content == "Expanded content"

    clue = service.add_foreshadow(project.id, "Mysterious key", status="hinted", first_chapter_id=chapter.id)
    assert clue.status == "hinted"

    projects = service.list_projects()
    assert len(projects) == 1
    assert projects[0].id == project.id
