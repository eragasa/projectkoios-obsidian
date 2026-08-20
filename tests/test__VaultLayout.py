from pathlib import Path

import pytest
from projectkoios.obsidian import (
    VaultDirectory,
    VaultLayout,
    load_vault_layout,
)


def test__load_vault_layout__loads_named_relative_directories(
    tmp_path: Path,
) -> None:
    config = tmp_path / "layout.toml"
    config.write_text(
        """
schema_version = 1

[directories]
references = "03_references"
notes = "04_notes"
""".strip(),
        encoding="utf-8",
    )

    layout = load_vault_layout(config)

    assert layout.schema_version == 1
    assert layout.directory("references").relative_path.as_posix() == (
        "03_references"
    )
    assert layout.resolve(tmp_path, "notes") == tmp_path / "04_notes"


def test__vault_directory__rejects_absolute_paths() -> None:
    with pytest.raises(ValueError, match="relative"):
        VaultDirectory.create("notes", "/private/notes")


def test__vault_directory__rejects_parent_traversal() -> None:
    with pytest.raises(ValueError, match="traverse"):
        VaultDirectory.create("notes", "../notes")


def test__vault_layout__rejects_duplicate_destination_paths() -> None:
    with pytest.raises(ValueError, match="paths must be unique"):
        VaultLayout(
            schema_version=1,
            directories=(
                VaultDirectory.create("notes", "notes"),
                VaultDirectory.create("knowledge", "notes"),
            ),
        )


def test__load_vault_layout__rejects_missing_directory_table(
    tmp_path: Path,
) -> None:
    config = tmp_path / "layout.toml"
    config.write_text("schema_version = 1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="directories"):
        load_vault_layout(config)
