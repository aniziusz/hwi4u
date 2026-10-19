# User guide

Document ID: HWI4U-GUIDE · Version: 7 · 2026-10-19

[FR-037/038/039 · 0.18.0 TEST · Lifecycle / Lebenszyklus / Életciklus](docs/LIFECYCLE.en.md)

[FR-036 · Manufacturer / Model / Serial number · 0.18.0 TEST](docs/IDENTIFICATION.en.md)

Current 0.18.0 list controls, roles and expanded layout supersede the older descriptions below. Read [the current workspace guide](docs/WORKSPACE.en.md). FR-034 duplicates the existing search and adds no separate implementation.

Start with README and initialize a new private workspace. Open production with manage.py run, TEST with manage.py test. TEST is a separate data copy; edits never synchronize automatically. Refresh TEST from production only deliberately: manage.py refresh-test opens a confirmation dialog and retains older datasets. Avoid opening multiple editors of the same record; stale saves are rejected.

New device: enter a unique descriptive name and evidence notes or selected device sources. UUID and two-letter/five-digit short label generate on save. Names accept Unicode, max 100 characters; case and extra whitespace do not distinguish duplicates. Choose a type to derive its group. Current state means hardware lifecycle, not live online status. Unknown optional dates stay unchecked; use calendars for known dates. Location text is optional single-line Unicode text <=200 characters. Guided location adds reusable addresses/buildings/floors/rooms and device-specific placement; see the location guide. Price/currency must be supplied together. Purchased at is a seller/place of purchase, not device location; spelling suggestions never silently change it.

Save device commits its form with a checked pre-save database-only snapshot. Cancel changes restores the saved form. The unsaved dialog explicitly offers Save changes, Discard unsaved changes or Keep editing. Discard does not delete saved data. Delete device confirms destructive record removal with a full snapshot; IDs/history remain reserved and other devices are preserved. Connection-linked devices/ports must first be explicitly disconnected by removing their connection records. Assembly management is available through CLI; no assembly/fact GUI editor is supplied.

Expand Network identity for optional hostname and actual interface labels, MAC and multiple IPv4/IPv6 addresses. This does not configure DNS/DHCP or discover network settings. Software, Connection interfaces and Communication protocols also expand. Record supported versus in-use separately; capabilities do not prove a currently connected link. Missing unverified sources warn; verified assessments need appropriate evidence/date. A vendor's latest firmware is not proof of the installed version. No field is auto-filled from a device type as verified fact.

Network connections connects two saved ports on different devices, with medium, planned/observed/retired state, optional rate and sources. It saves immediately with history; it is not a live network map. Multiple links and wireless associations can be documented. Source references can be reused across sections; library creation/revision saves immediately, while assignments save with the parent form. Revisions preserve old source IDs/content. Existing free-text evidence is retained. Opening external sources is explicit; no automatic downloads. Local PDFs/photos are managed separately from SQLite.

The device search includes location, IDs, software and network identities. Group/type list filters accept substring typing; choose a result to apply, or All groups/types to reset. Closed dropdown/date/number controls ignore wheel edits and scroll the enclosing form. Open lists/calendars and deliberate keyboard edits remain available. Hover help and Info/About explain fields, data paths and versions. Language switching preserves pending device values and never translates stored user data.

Full backup creates a verified ZIP containing database and referenced photos/manuals/source files. Automatic database-only snapshots omit files. Follow recovery instructions and keep an independent copy. Apply update restarts into a tested candidate with Save/Discard/Keep editing protections; Abort postpones a notice without discarding data. Code publication is separate from production acceptance. No synchronization with KeePass, OPNsense or Home Assistant is implemented; roadmap items do not establish readiness.

[Setup](README.en.md) · [Recovery](docs/RECOVERY.en.md) · [CLI](docs/CLI.en.md)

[FR-025 · Guided location / Standort / Helyadat](docs/LOCATIONS.en.md)

[FR-028 · FR-012 · FR-029](docs/DESKTOP.en.md)


[FR-030/031/032/033/035 · 0.18.0 · TEST](docs/WORKSPACE.en.md)
