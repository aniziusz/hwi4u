# Backup and recovery

Document ID: HWI4U-RECOVERY · Version: 1 · 2026-10-18

Private data is in your chosen workspace, outside Git. GitHub protects versioned source only; it is not an inventory backup. Keep an independent backup of the whole private workspace (database, photos/, manuals/, sources/, .runtime/, preferences and source snapshot) and a normal Git clone/bundle of the source. A same-disk backup is not independent protection. Use a consistent filesystem snapshot or close writers before copying the whole workspace; do not copy a live SQLite file casually. Normal coding does not require closing the app.

In the client, Full backup creates a checked portable ZIP with database, all referenced managed files and MANIFEST.json hashes; automatic .sqlite3 snapshots contain database metadata only. Keep the source commit/release identifier alongside each backup. Retain old runtime releases: SQLite migrations cannot generally be reversed simply by selecting older code.

To inspect a portable ZIP without overwriting anything:

```sh
python tools/verify_bundle.py /path/backup.zip /new/empty/restore-directory
python inventory.py --db /new/empty/restore-directory/hardware.sqlite3 check
```

The verifier rejects missing/extra/unsafe members or changed hashes and extracts only into a new directory. The second command requires a matching schema (this source expects 21); for older snapshots use the matching source/runtime first, then the managed updater on a disposable copy. Do not change user_version to bypass compatibility. A portable ZIP is data, not a pre-initialized manage.py workspace.

For normal recovery, restore a consistent whole-workspace backup to a NEW path, preserving its source/runtime/marker files, and run `python manage.py run --workspace /new/restored/workspace`. It uses that workspace's pinned production release. Verify inventory check and full-backup hashes on the restored copy before resuming work. Do not overwrite your original workspace. If only a portable data ZIP remains, retain the verified extraction and matching source, and plan an explicit data adoption/migration step; automatic ZIP-to-workspace adoption is not supplied in this release.

For failed source publication, production remains on its prior pointer. Fix the source, rerun tests and publish again. Resolve actual database transactions before retrying a busy migration; never kill another editor or disable integrity checks. A failed migration rolls back and retains its pre-update full backup. Restoring the complete matched data/runtime snapshot is safer than trying old code against a newer schema. [Setup](../README.en.md) · [Development](../CONTRIBUTING.en.md)
