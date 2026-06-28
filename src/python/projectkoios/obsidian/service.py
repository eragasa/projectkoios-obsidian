from pathlib import Path

from projectkoios.obsidian.config import VaultConfiguration


class VaultService:
    def __init__(self, configuration: VaultConfiguration) -> None:
        self.configuration = configuration

    @property
    def path(self) -> Path | None:
        return self.configuration.path

    def is_configured(self) -> bool:
        return self.path is not None

    def exists(self) -> bool:
        if self.path is None:
            return False

        return self.path.exists() and self.path.is_dir()
