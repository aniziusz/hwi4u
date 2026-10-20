# Basic/Details and protected editing — 0.20.0 TEST

Document ID: HWI4U-EDITOR-MODES · Version: 1 · 2026-10-20

FR-050, FR-053, FR-052, FR-044 and FR-046. User selected Basic and Details and left-aligned classic menus. TEST candidate only; production acceptance remains separate. Schema 25 and stored records are unchanged. No new dependency, migration or TEST-data refresh.

## Basic and Details

Every window starts in Basic. Basic shows short ID, name, manufacturer/model, type/group selection, location/structured-location access, current state, physical condition and device evidence. Name and device evidence retain their existing required rules; the other fields can remain unknown. Type group is derived from the chosen type when saved. Generated IDs remain read-only.

Details adds full ID, serial number, roles/model suggestions, purchase/installation/scrapping, software, network identity, interfaces/protocols, lifecycle/warranty, photos and references. Details is available in View mode too, so photos, references and saved text can be inspected without enabling editing. This is the initial field split from the selected preview, not configurable per-user priorities or a new guided-entry wizard. The choice is retained while navigating within that window; a new window/restart starts Basic. Switching never saves, clears or reloads fields. The expanded window retains adaptive tiles, section-tree navigation and selected-branch highlighting. Hidden sections are excluded from the grid; wide desktop space remains available. Main-list search/filter/group/column preferences remain unchanged.

## View versus Edit

Existing records open protected in both quick and full-window views. Choose **Edit device** to enable deliberate changes. Read-only text can still be selected/copied; source browsing, photo viewing and opening manuals/links remain available in Details. Source browsing in View cannot create/revise sources or change assignments. Lifecycle/location editors and attachment mutations require Edit. This is accidental-edit protection, not authentication, database encryption or access control: external database tools and explicit shared-catalogue maintenance remain separate capabilities.

New devices begin editable. After successful Save or Cancel the form returns to View. A failed Save keeps both pending values and Edit mode; validation reveals relevant hidden Details and directs focus to the affected area. Missing device provenance still requires text OR selected device sources. Both editors share the same validation, conflict checks, backups and UUIDs. Changes in another window never silently overwrite an existing draft.

**Save changes** and **Cancel changes** appear once, at bottom-right outside the scrolling form, while editing. The separate Edit device action is near the Basic/Details status. Save/Cancel menu commands use the same operations. Ctrl+S (the platform-standard Command equivalent on macOS) saves only in Edit. Escape invokes Cancel; when a draft exists the explicit Save / Discard / Keep editing confirmation remains. Cancel is not permission to silently lose a draft. Opening, closing and Apply update retain the existing pending-change checks. Deletion still requires its explicit confirmation and verified backup.

Photos/manuals and new source-library entries keep their existing immediate-save semantics: edit-state protection does not make them transactional with the device form. Cancel device changes does not undo an attachment already saved in its dialog or a new source-library entry; pending source assignments save with the device. Existing hints explain those boundaries. Shared type/connection catalogue management remains an explicit Tools workflow with existing confirmations and can affect multiple devices; View is not a database-wide write lock.

## Lifecycle disclosure

In the quick editor, Lifecycle dates is a keyboard-accessible arrow header, collapsed by default like Network identity/Software. Expand it in Details. Hiding preserves dates, sources, warnings and drafts. A textual needs-attention marker on the header and a Basic/Details status hint keep lifecycle warnings discoverable. In the expanded editor the existing lifecycle tile and tree item show the same body, matching its other network/software tiles; no duplicate controls or additional form copies are created.

## Classic menus

File, Edit, View, Tools and Help are grouped on the left; no ribbon. Native macOS may place About/Quit in its application menu as usual.

| Menu | Existing operations |
|---|---|
| File | New device, Save changes, Full backup, Quit |
| Edit | Edit device, Cancel changes, Delete device |
| View | Basic, Details, Find devices, Filters, Columns, Group by, Clear filters, Refresh |
| Tools | Manage types, Manage connection choices, Network connections, Open other client, Language submenu |
| Help | About, User guide, Check local updates |

Save, New, Find, Refresh, Help and Quit use standard Qt platform shortcuts; Edit device uses Ctrl+E and Cancel uses Escape. Full-window editors disable main-list actions because that list belongs to the main window. No unimplemented Excel export or undo/redo action is advertised. Existing update controls and TEST/production labels remain. All new wording is in the external EN/DE/HU catalogues, now 742 entries; language changes preserve drafts, mode and source selections.

## Review and recovery

Apply update in TEST or restart TEST normally. Do not promote until the exact candidate is reviewed. Check a saved device starts protected; enter Edit, change a value, toggle Basic/Details and verify retention, then Save/Cancel. Inspect serial number/purchase dates in Details, lifecycle disclosure and EN/DE/HU menus. Test opening a reference without Edit. Existing immutable 0.19.0 TEST and 0.18.0 production releases remain available; no release directory should be edited in place. [Recovery](RECOVERY.en.md) · [Foundations](FOUNDATIONS.en.md) · [Workspace](WORKSPACE.en.md).
