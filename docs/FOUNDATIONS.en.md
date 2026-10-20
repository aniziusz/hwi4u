# Reliable foundations — 0.19.0 TEST

Document ID: HWI4U-FOUNDATIONS · Version: 1 · 2026-10-20

FR-043, FR-045 and FR-047. Candidate changes; production acceptance is separate. No schema change (schema 25), no refresh of TEST data, no inventory uploaded. Existing clients remain pinned until Apply update/restart.

## Device evidence

The device source label and source-selection area show `*` and explain the alternative: enter source text **or** choose one or more device sources. The inline message updates while typing/selecting. Missing both prevents Save and directs focus to evidence in quick and full-window editors. Sources selected only for OS/network/connectivity do not satisfy device evidence. Existing warning-only network/connectivity behavior and verified-assessment requirements are preserved. No duplicate text is required for selected sources. Save/Cancel and existing source history are unchanged.

## Language maintenance

`locales/en.json`, `de.json`, `hu.json` contain 725 migrated messages, including labels, menus, help/tooltips, choices, dialogs, validation/status text and template messages. JSON was chosen over Qt TS/gettext PO to fit existing live widget translation, use the standard library and avoid an additional compiler/runtime dependency. This is not automatic translation, hot reload or a translator GUI.

English entries have stable IDs (`ui.0001` etc.), a **source** lookup alias, editable **text** and translator **context**. Do not renumber IDs or modify source aliases when changing wording. Keep every ID unique and add new IDs without reusing old ones. German/Hungarian entries use the same IDs, text and a SHA-256 of the English display text. Changing English wording marks old translations stale: update the translated wording and hash after review. The loader falls back to current English for absent/empty/stale/incompatible translations. Placeholder names/indices must match exactly. Preserve mnemonic markers (`&`), punctuation and intended markup; existing markup remains application-owned, not user HTML. Current messages use no locale plural forms; do not insert plural arrays into format 1—design a supported plural API first if needed.

Metadata `language`, `name`, `qt_locale` discovers new language-menu options and Qt calendar locale at next startup. Example from the source folder:

```sh
python tools/catalogues.py
python tools/catalogues.py --new-language fr --name Français --qt-locale fr_FR
```

The second command exclusively creates a new incomplete `locales/fr.json`; review/translate its entries, retaining IDs and English hashes. Its empty entries deliberately use English. Read alongside `en.json` for context. A bad locale file is excluded; diagnostics are listed by the checker. A damaged English file leaves literal English labels usable with no catalogue help: restore the released file, then check again. Existing inventories/settings are not changed. Invalid/missing saved language preferences fall back to English. Source files, release hashes and source ZIP include all catalogue JSON, so a wording change requires a new verified release rather than editing immutable installed releases.

Canonical database values and user text remain data, not catalogue IDs; changing language never rewrites records. Keep aligned EN/DE/HU documentation as ordinary separate Markdown files. Verify pending input retention, date locales, shortcuts/mnemonics, placeholders and translated dialogs before release. Compatibility Python exports contain no independently maintained wording.

## Measured validation and safe reuse

Use one focused test after a manageable change; freeze a compatible candidate before the final full regression. Examples from the source folder (choose a **private** evidence directory outside public commits):

```sh
python tools/validate.py --evidence /absolute/private/evidence --pattern test_foundations.py
python tools/validate.py --evidence /absolute/private/evidence
python tools/validate.py --evidence /absolute/private/evidence --fresh
```

Focused results record duration/return code and never satisfy release proof. Full regression records tests run, elapsed seconds, output hash and complete source/test/catalogue/dependency manifests, Python executable/version, actual Qt/module file hashes, OS/architecture, SQLite and an environment digest. Environment values are not stored. A local random key authenticates receipts with HMAC; both receipt and output-log integrity are checked. Source/environment/dependency changes, missing/invalid signatures, changed logs, failures or zero tests cause a fresh run. Inputs are checked again after running. `--fresh` always reruns. The command returns failure if validation fails.

Publication and promotion share private `.runtime/validation` evidence. Reuse requires the same full input fingerprint, not merely the same release version or Git commit. A local pass never substitutes for native platform CI, source-distribution review, database migration/backup validation, the launched TEST-candidate check or explicit production acceptance. No automatic production promotion exists. The exact TEST release is reverified before selecting production. Loss of evidence/key safely causes rerunning (a malformed key causes an explicit error requiring investigation). Old receipts are local records, not an independent backup.

Receipt authentication protects against damaged/edited evidence, not a hostile process with the same user's filesystem privileges and key access. Keep keys/logs private and out of Git/artifacts; do not upload `.runtime`. For recovery, preserve suspicious evidence, choose a new empty private evidence directory and run fresh checks. Do not delete release/data files to bypass validation. Different runner environments deliberately do not share trust or evidence. CI uses measured validation once per candidate; platform smoke and packaging remain separate.

Record initial estimates and actual elapsed durations, failures/retries, external/user waiting and whether full checks ran or valid evidence was reused. Active effort is unknown unless measured separately. Compare like-for-like runs only; do not promise a universal speed-up or interpret account percentages as remaining work time. [Contributor workflow](../CONTRIBUTING.en.md).
