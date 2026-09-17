# Vault layout user guide

## Overview

A `VaultLayout` gives applications stable logical directory names while allowing
each user to choose physical directories inside an Obsidian vault.

Current functionality is read-only. It loads, validates, and resolves layout
configuration. It does not move files or rewrite links.

## Install for development

From the repository root:

```bash
python -m pip install -e .
```

The package requires Python 3.14 or later.

## Create a layout manifest

Create `layout.toml` in a user-owned configuration directory:

```toml
schema_version = 1

[directories]
inbox = "00_inbox"
references = "references"
notes = "notes"
lectures = "lectures"
```

Rules:

- keys are logical names used by software;
- values are paths relative to the vault root;
- names and paths must be unique;
- absolute paths are rejected;
- `..` traversal is rejected;
- the manifest should not contain the absolute vault path.

## Load and inspect a layout

```python
from pathlib import Path

from projectkoios.obsidian import load_vault_layout

layout = load_vault_layout(Path("layout.toml"))

for directory in layout.directories:
    print(directory.name, directory.relative_path)
```

Loading does not inspect or modify the vault.

## Resolve a logical directory

Supply the vault root at runtime:

```python
import os
from pathlib import Path

from projectkoios.obsidian import load_vault_layout

layout = load_vault_layout(Path("layout.toml"))
vault_root = Path(os.environ["OBSIDIAN_VAULT_PATH"])
notes_path = layout.resolve(vault_root, "notes")
```

`resolve()` verifies that the result remains beneath `vault_root`. It does not
create the directory.

## Keep deployment configuration separate

A recommended user-owned workspace is:

```text
my-vault-workspace/
├── .env
├── config/
│   ├── profile.toml
│   ├── current-layout.toml
│   ├── target-layout.toml
│   └── migration.toml
├── inventory/
├── templates/
└── migration-reports/
```

Ignore `.env` in Git and place the absolute vault path there. Commit portable
layout manifests, templates, and reviewed reports according to the deployment's
privacy policy.

## Current versus target layouts

Use two manifests while redesigning a vault:

- `current-layout.toml` records the layout observed today;
- `target-layout.toml` records the approved intended layout.

Do not treat a target manifest as permission to move files. A target layout says
where logical collections should live; a migration plan must separately say
which existing paths would move.

## Safe redesign workflow

1. Inventory the vault without modifying it.
2. Record the current logical layout.
3. Design the target layout.
4. Validate both manifests.
5. Generate a proposed migration manifest when planner support exists.
6. Review collisions, links, attachments, aliases, and ignored paths.
7. Approve a specific migration manifest.
8. Run an explicit dry-run.
9. Back up or snapshot the vault.
10. Apply and validate only after all earlier steps pass.

Migration planning and execution are not implemented yet. Until they are, use
this package only for layout design and validation.

## Error handling

`load_vault_layout()` raises `ValueError` for malformed or unsafe manifests and
`KeyError` when an unknown logical directory is requested.

Example:

```python
try:
    path = layout.resolve(vault_root, "unknown")
except KeyError:
    print("The layout has no 'unknown' directory")
```

## Security and privacy

- Do not commit credentials or cloud-provider tokens.
- Avoid committing absolute home-directory paths.
- Treat inventories as potentially sensitive metadata.
- Do not use private vault contents as public test fixtures.
- Review symlinks before migration; they may resolve outside the vault.
- Keep write permission separate from read-only planning whenever possible.
