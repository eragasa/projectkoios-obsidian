from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class VaultDirectory:
    name: str
    relative_path: PurePosixPath

    @classmethod
    def create(cls, name: str, relative_path: str) -> VaultDirectory:
        return cls(name=name, relative_path=PurePosixPath(relative_path))

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("vault directory name must be non-empty")
        if self.relative_path.is_absolute():
            raise ValueError("vault directory paths must be relative")
        if self.relative_path == PurePosixPath("."):
            raise ValueError("vault directory paths must not be empty")
        if ".." in self.relative_path.parts:
            raise ValueError("vault directory paths cannot traverse parents")


@dataclass(frozen=True)
class VaultLayout:
    schema_version: int
    directories: tuple[VaultDirectory, ...]

    def __post_init__(self) -> None:
        if self.schema_version <= 0:
            raise ValueError("schema_version must be positive")

        names = tuple(directory.name for directory in self.directories)
        if len(names) != len(set(names)):
            raise ValueError("vault directory names must be unique")

        paths = tuple(directory.relative_path for directory in self.directories)
        if len(paths) != len(set(paths)):
            raise ValueError("vault directory paths must be unique")

    def directory(self, name: str) -> VaultDirectory:
        for directory in self.directories:
            if directory.name == name:
                return directory
        raise KeyError(name)

    def resolve(self, vault_root: Path, name: str) -> Path:
        root = vault_root.expanduser().resolve()
        path = (root / self.directory(name).relative_path).resolve()
        if not path.is_relative_to(root):
            raise ValueError("resolved vault directory escapes the vault root")
        return path


def load_vault_layout(path: Path) -> VaultLayout:
    with path.open("rb") as stream:
        values = tomllib.load(stream)

    schema_version = values.get("schema_version")
    directories = values.get("directories")

    if not isinstance(schema_version, int):
        raise ValueError("layout schema_version must be an integer")
    if not isinstance(directories, dict):
        raise ValueError("layout directories must be a table")

    parsed_directories: list[VaultDirectory] = []
    for name, relative_path in directories.items():
        if not isinstance(name, str) or not isinstance(relative_path, str):
            raise ValueError("layout directory entries must be strings")
        parsed_directories.append(VaultDirectory.create(name, relative_path))

    return VaultLayout(
        schema_version=schema_version,
        directories=tuple(parsed_directories),
    )
