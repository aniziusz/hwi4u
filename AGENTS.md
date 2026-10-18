# HWI4U contributor guidance

Read README.en.md, GUIDE.en.md and CONTRIBUTING.en.md before changes. Keep matching English, German and Hungarian document IDs, versions and dates aligned. Keep substantive procedures in local editable documents, not only an issue or chat.

Use disposable fictional data and a private workspace outside the source tree. Never open a user's inventory from tests or commit private database files, attachments, credentials or backups. Run tools/check_distribution.py on staged content; inspect actual content and history as well.

Preserve UUIDs, unknown values, evidence revisions and connection histories. Never infer actual device configuration from a type/capability. Use supported stores and managed ordered migrations with verified full backups and rollback checks. Do not rewrite released migrations.

Publish changes to TEST first and keep production pinned until deliberate acceptance of the exact tested candidate. Do not refresh TEST datasets or merge test records into production implicitly. Code edits do not require closing a running pinned client. Run relevant tests and the full suite before publication; test real platform behavior before claiming Windows/mobile support.
