# Vault layout architecture

## Status

Implemented foundation. Layout loading, validation, and safe path resolution are
available. Inventory, migration planning, link rewriting, and migration
execution remain planned.

## Purpose

`projectkoios-obsidian` provides reusable, configurable Obsidian vault
management. It defines generic layout and safety contracts without prescribing
a user's directory names, absolute vault path, templates, or content model.

A deployment supplies its own layout manifest and vault root:

```text
projectkoios-obsidian          deployment workspace
(reusable software)            (user-owned configuration)
          |                                  |
          +----------> resolved layout <-----+
                              |
                              v
                       Obsidian vault
```

## Architectural boundary

The package owns:

- validated logical directory names and relative paths;
- loading versioned layout manifests;
- resolving configured paths beneath a vault root;
- reusable inventory and migration contracts when implemented;
- validation before any future filesystem mutation;
- explicit separation of planning and execution.

The package does not own:

- a particular user's vault root or directory names;
- personal note templates or naming conventions;
- source ingestion, retrieval, or semantic processing;
- application-specific bibliography or lecture layouts;
- implicit file movement;
- migration without review and approval.

## Current components

### `VaultConfiguration`

Holds an optional runtime vault path. The path is a deployment concern and is
not embedded in a reusable `VaultLayout`.

### `VaultService`

Reports whether a configured vault path exists. It does not create or modify a
vault.

### `VaultDirectory`

Maps a logical name to one portable relative path. It rejects:

- empty logical names;
- absolute paths;
- empty paths;
- parent traversal.

### `VaultLayout`

Contains a schema version and an immutable sequence of `VaultDirectory`
objects. Logical names and destination paths must each be unique.

`VaultLayout.resolve()` combines a runtime vault root with a logical directory
and verifies that the result remains beneath the vault root. Existing symlinks
that resolve outside the root are rejected.

### `load_vault_layout()`

Loads and validates a TOML manifest. Loading is read-only and has no filesystem
side effects beyond reading the manifest.

## Manifest contract

```toml
schema_version = 1

[directories]
references = "references"
notes = "notes"
lectures = "lectures"
```

Directory keys are stable logical names used by applications. Values are
portable relative paths interpreted beneath a separately configured vault root.
Changing a physical directory does not require changing every application that
uses its logical name.

The version-1 manifest deliberately excludes:

- an absolute vault root;
- move or delete instructions;
- overwrite policy;
- link-rewrite policy;
- user content.

Those concerns belong to deployment configuration or future migration
contracts.

## Deployment boundary

A recommended deployment workspace contains:

```text
vault-workspace/
├── config/
│   ├── profile.toml
│   ├── current-layout.toml
│   ├── target-layout.toml
│   └── migration.toml
├── inventory/
├── templates/
└── migration-reports/
```

The reusable package does not load that entire profile format yet. It loads the
individual layout manifests. Profile and migration-control schemas remain
application-level contracts until promoted into this package.

## Read and write paths

The current implementation has only a read path:

```text
TOML manifest
    -> tomllib
    -> VaultDirectory objects
    -> VaultLayout validation
    -> safe path resolution
```

The planned write path is deliberately longer:

```text
current inventory
    -> target VaultLayout
    -> proposed migration manifest
    -> collision validation
    -> link-impact analysis
    -> human approval
    -> explicit apply
    -> post-migration validation report
```

No migration executor should accept a target layout alone. It must consume an
approved, source-specific migration manifest.

## Safety invariants

1. Layout manifests never require an absolute vault path.
2. Resolved directories remain beneath the configured vault root.
3. Loading, resolving, and validating a layout never modify a vault.
4. Migration planning and execution are separate operations.
5. Future migration execution defaults to dry-run.
6. Existing files are never overwritten silently.
7. Every proposed move records source, destination, reason, and status.
8. Link rewriting is planned and validated before filesystem changes.
9. User-authored content is never treated as regenerable layout output.
10. A deployment can review a migration plan without running mutation code.

## Extension direction

Planned generic contracts include:

- `VaultInventory`
- `VaultInventoryEntry`
- `VaultMigrationPlan`
- `VaultMove`
- `VaultLinkImpact`
- `VaultMigrationValidator`
- `VaultMigrationExecutor`
- `VaultMigrationReport`

These types should remain independent of any one vault layout. Execution must be
an explicit capability; validation and planning must remain usable without it.

## Testing

Reusable tests use temporary directories and synthetic notes. Private vaults
may be used for local acceptance testing but are not package fixtures.

Required migration tests will include:

- dry-run causes no filesystem mutations;
- traversal and symlink escape are rejected;
- collisions prevent approval;
- moves preserve bytes;
- link rewrites are explicit and reversible;
- interrupted execution can be diagnosed from a report;
- human-owned files are never overwritten implicitly.
