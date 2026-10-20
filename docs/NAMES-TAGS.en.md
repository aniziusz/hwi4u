# Name suggestions and tags

Document ID: HWI4U-NAMES-TAGS · Version: 1 · 2026-10-20

FR-042 and FR-051 · 0.21.0 TEST · schema 26. User-approved rules, 2026-10-20. Production remains 0.18.0. The user accepted 0.20.0 TEST; that does not promote this new candidate or its data. Older guide sections retain their release context; this document is current for names/tags.

## Name suggestions

Choose Edit device for an existing record. In Basic or Details, enter Manufacturer, Model and/or Device type. Name suggestion previews **manufacturer model — device type**, omitting missing parts. No inputs means no suggestion; no manufacturer, model or hardware fact is invented. Choose **Use suggestion** to replace Name in the pending form, then adjust it freely. No existing or populated name changes automatically. Preview changes alone do not make the device dirty. Save changes commits; Cancel changes restores the saved name. Quick and expanded editors use the same controls.

Suggestions retain entered capitalization and Unicode. They collapse spacing, remove nonprinting control/line-break characters from the preview, and fit the existing 100-character limit. Duplicate names use (2), (3), etc.; the base is shortened to fit the suffix. Comparison uses the existing Unicode NFKC/case/whitespace-insensitive name key. The edited device is excluded. Use suggestion recalculates against current saved names; final transaction validation still rejects races. The suffix is a suggestion, never a reserved counter. Names remain descriptive labels, distinct from UUID, random short ID, hostname and serial number. IDs and hostname are never populated or changed by this action. A long preview may be shortened; review it before saving.

## Reusable tags

The optional Tags selector is in Basic and Details, in General in the expanded editor. Choose existing labels or Add tag, tick several labels, and Apply. New labels and assignments stay pending until Save changes; cancelling either the selector or device form discards pending additions. Merely opening the selector creates nothing. A tag is not a device type, functional role, location, state or verified property. No initial vocabulary or automatic assignments are supplied.

Labels accept 1–50 printable Unicode characters on one line. Extra spaces collapse; outer spaces are removed. Display labels use NFC; uniqueness uses NFKC, casefold and collapsed spaces. Existing display capitalization is reused when an equivalent tag exists. Multiple equivalent selections save once. Stable catalogue UUIDs link devices to tags. Unchecking removes only this device's assignment; it does not remove the label or affect other devices. Shared rename, merge and catalogue deletion are deferred. Unused labels remain available. Tag assignment history retains IDs/labels and user_entry/user_reported provenance; it does not certify a factual property. View mode prevents changes. Language switching retains labels and pending selections; stored tags are never translated.

In the left list, enable Tags through View → Columns. Its header filter accepts multiple selections: **any selected tag** matches, combined with **AND** for other columns. Free-text search includes tags even when the column is hidden. The empty-value filter uses the existing Unknown choice: this means no tag assignment, not that a factual property is absent. Tags are not added to grouping in this release. Existing column order/widths/filter settings survive; the new column starts hidden.

## Storage, export and update safety

Schema 26 adds tag_choices, device_tags and immutable device_tag_history. Migration 026 adds no tags to existing devices and preserves UUIDs, short labels, evidence and other properties. Catalogue creation, assignment changes and device edits share one write transaction and checked pre-save backup. Stale tag assignments reject the save and retain the form. CLI/device updates that omit tags preserve existing assignments. Deleting a device retains the catalogue and assignment history and includes tag IDs/history in its deletion snapshot; a verified full backup precedes deletion.

Full backup/restore includes all tag tables. Portable `inventory.py export --directory /new/export/folder` includes catalogue, assignments and history in JSON/SQL; `inventory.py show --device DEVICE_ID` includes tag labels. Add `--db /absolute/private/hardware.sqlite3` before the command, using the selected compatible immutable release's inventory.py. No XLSX or target-specific export is added; FR-048/023/027 remain separate. Never run newer source CLI against an older production schema.

Use managed TEST Apply update or normal TEST start. A running old client stays pinned; the updater performs ordered 25→26 migration under a write reservation, first creating and verifying a full bundle. Lock contention defers safely; finish the blocking transaction and retry. Coding/publication does not migrate the open inventory or refresh TEST from production. Production promotion requires explicit acceptance of the exact tested candidate. To recover, restore the pre-update full bundle into a new directory with compatible 0.20.0/schema-25 code; never downgrade an upgraded database by selecting older code against it. Local snapshots are not independent backups.

## Verification and prerequisites

Existing name policy, identification fields, multi-select header filters, View/Edit protection and managed backups/migrations are confirmed prerequisites in source. No new dependency or infrastructure project is required. Fictional tests cover missing/long/Unicode/duplicate suggestions, explicit application, pending values/languages, normalization/reuse, history, stale assignments, failed-backup atomicity, filtering/search, deletion snapshots, JSON/SQL and full restore, ordered migration, locks and rollback. Current execution evidence and native-platform results are linked from the private project record and pull request; they are separate from user acceptance. The public code, SQL, JSON and this guide can be read offline; dependencies and linked websites are not an offline installation bundle.

[Guide](../GUIDE.en.md) · [Editor modes](EDITOR-MODES.en.md) · [Recovery](RECOVERY.en.md)
