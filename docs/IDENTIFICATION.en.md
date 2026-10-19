# Hardware identification fields

Document ID: HWI4U-IDENTIFICATION · Version: 1 · 2026-10-19

HWI4U 0.17.0 / schema 24 — FR-036. Manufacturer, Model and Serial number are optional Unicode text fields. They appear in that order immediately above Location text in the main quick editor. In the expanded editor, the same controls appear above location in the **Hardware & location** tile and corresponding navigation entry. The input controls share the existing Save device/Cancel, language and stale-save safeguards.

Leave unknown values blank; blanks are stored as NULL. Up to 200 printable single-line characters per field. Leading/trailing whitespace is removed, but capitalization, leading zeros and internal spacing are retained. Serial numbers are text, never numbers; an example such as `0007aB` stays exactly that. No global uniqueness is imposed because serials can overlap between manufacturers or be absent. Manufacturer means the recorded manufacturer/brand; Model means a model name or code, separate from the device's descriptive Name and primary Type. Values are user-provided, not verified by the application.

The general device search includes all three fields, even when their list columns are hidden. Columns… can show them; header checkboxes can filter them. Manufacturer and Model can also be grouping levels. Existing column orders, widths, groups and filters are preserved during preference upgrade; the three new columns are appended hidden. JSON/SQL inventory exports include them as device fields; backups/restores retain the exact text. These fields do not alter UUIDs, short IDs, roles, classification or location data.

Migration 024 adds nullable columns and does not infer values from names, earlier invoices or references. Existing records remain blank until explicitly supplied. Run the managed TEST update or normal TEST start: it takes a verified full backup before upgrading schema 23→24, retaining existing records and IDs. Do not apply migration behind a running pinned client, edit released migrations, replace populated databases or point an older release at schema 24. Production remains pinned until explicit acceptance. Rollback requires restoring the verified pre-update full backup into a new directory and using its compatible earlier release; see recovery instructions. Local copies alone are not independent backups.

Verification uses fictional data: previous-schema row/ID preservation and NULL defaults; exact serial round trips; blank/length/control-character validation; backup failure and stale-save rejection; field order in both editors; language changes and search; preservation of old view preferences. Native smoke verifies a leading-zero serial after full backup/restore. Actual full-suite/platform outcomes are recorded in the review; user acceptance remains separate. No real device labels are filled from examples.

[User guide](../GUIDE.en.md) · [List/workspace guide](WORKSPACE.en.md) · [Recovery](RECOVERY.en.md)
