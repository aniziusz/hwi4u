# Model suggestions and lifecycle dates

Document ID: HWI4U-LIFECYCLE · Version: 1 · 2026-10-19

FR-037/038/039 · Source 0.18.0 · Schema 25 · TEST first. Production requires deliberate acceptance of the tested release. Model profiles start empty; no private inventory, online model catalogue or automatic scraping is bundled. Existing fields, IDs, sources and classifications are not inferred or changed by migration.

## Six distinct properties

Open **Lifecycle dates** in quick editing or its own tile in the expanded editor. Unknown properties are listed as Unknown. Double-click a property or use Add/Edit. Use Remove to stage removal; **Save device** commits the complete form, Cancel changes restores its saved state. Source-library creation remains immediate, as before. Lifecycle assignments and edits are pending with the parent form. Each edit/clear retains a lifecycle history snapshot; exports include this history, though no dedicated history browser is provided.

- Market release: the manufacturer's launch of this exact model/variant, not merely a component or announcement.
- Firmware security-support end: provider, product and firmware version/support track, e.g. BIOS/UEFI or an SSD's firmware.
- OS security-support end: provider, installed OS/distribution and version/support track. A distribution's base OS is not a substitute for its own support policy.
- Hardware service-support end: explicit repair/replacement/parts/service promise and region.
- Production end: when manufacturing the applicable model/variant ends. It is not end of sales or support.
- Warranty expiry: individual device/purchase/contract, not a shared model date.

Multiple observations are supported for each property, including multiple installed software items and conflicting statements. Supply provider/product, version where applicable, variant/region/scope, sources, actual observation/access date, verification status and notes. Unknown remains absent, never today's date. The date editor's default is not saved unless you explicitly use an observation. Model release/production requires manufacturer and exact model in Provider/Product; software support requires provider/product/version; hardware service and warranty require an explicit scope. No fixed warranty length or support term is inferred. If a vendor supplies one OS/firmware image, use the relevant records with the same evidence without inventing separate deadlines.

Dates support exact day with calendar, month (`2025-06`), quarter (`2025-Q2`) and year (`2025`). Select the matching precision. A quarterly source is not turned into an invented launch day. A verified observation requires a real observation date and selected sources whose library entries are verified and dated; verification of the source is not automatically verification of applicability to the owned device. Unverified observations can be retained with warnings and no source. Websites need network access; preserve relevant source text or import a PDF in Sources for offline evidence. No claim that every external reference has been saved locally.

## Purchase-date check

Earliest purchase is **market release minus one calendar year**, inclusive; February 29 clamps to February 28 in the preceding non-leap year. An exact release 2025-06-15 allows purchase from 2024-06-15. Quarter/month/year dates use intervals: subtract one calendar year from both boundaries; dates before the earliest boundary fail, dates inside the uncertain boundary warn, dates at/after the latest boundary pass this check. For `2014-Q2`, before 2013-04-01 fails, 2013-04-01 through 2013-06-29 warns, from 2013-06-30 passes. This does not assert that an early sale happened.

Hard blocking requires verified, matching release evidence. Differing release intervals, unverified evidence, missing dates or a provider/product mismatch against the device manufacturer/model warn instead of inventing certainty. Only market release affects this rule; purchases after production/support end remain allowed. Dates are never automatically corrected. Existing historical violations remain editable for unrelated changes; new/changed purchase dates, release records or manufacturer/model must pass the confirmed rule. Always review the visible warnings. Exact provider/model comparison is case-insensitive and normalizes Unicode/spacing, but does not guess aliases or regional applicability.

## Reusable model profiles and classification

1. Enter manufacturer/model and review the device's type/group, roles and lifecycle dates using evidence. Select source references in the device Sources and evidence section.
2. Choose **Model suggestions… → Save current values as model profile…**. Enter explicit variant/region/hardware revision and evidence/applicability notes. The shared model library saves immediately with a full backup; it is not undone by cancelling the device form. An existing selected variant can be saved as a new immutable revision with confirmation. Old profiles/sources remain; existing devices are not changed.
3. For another exact manufacturer/model, open Model suggestions. Choose the applicable variant; review group, type, roles, dates, source IDs and notes; tick the review confirmation and Apply suggestion. Multiple variants are never silently chosen.
4. Apply changes only the pending form. It replaces the primary type/group, roles and non-warranty lifecycle snapshot, retains this device's warranty and merges device source assignments. Review and Save device, or Cancel changes. A stale revision/model mismatch is rejected. Current use is not established by advertised capabilities: save only reviewed role suggestions, and verify actual device use separately.

No fuzzy matching, automatic alias selection, online lookup, background synchronization or automatic device-wide profile updates. Manual classification and software configuration remain available. Catalogue revisions do not retrospectively alter dates copied into devices. Individual serials, warranty and installed software settings are never shared by a profile. If applicability is unclear, cancel and investigate. Type names remain one primary classification; roles remain multiple selections.

## Upgrade, validation and recovery

Use managed TEST Apply update or normal TEST start. The launcher verifies the immutable release and full backup before transactional migration 24→25; older supported schemas use the ordered chain. Coding does not require closing a pinned running client; a lock defers migration safely. Never replace a live database or run migration behind an old client. New tables are device_lifecycle, device_lifecycle_history and model_profiles. JSON/SQL exports and verified full bundles preserve records, profiles, sources and histories; separate managed files remain included in full bundles. Recovery: restore a pre-update full bundle into a new directory with compatible older software; never point older software at schema 25. See [Recovery](RECOVERY.en.md). Local snapshots are not independent backup copies; include documentation and data in an independently stored backup.

Automated checks use disposable fictional records: exact/partial/leap tolerance, unknown/conflicting/model-mismatched evidence, required software/scope metadata, verified-source checks, stale saves, backup failure, profile revisions/variants, explicit review/Cancel, warranty retention, schema-24 migration preservation, deletion history and portable export/restore. Native platform results and user acceptance must be recorded separately; source availability is not physical-platform qualification. [User guide](../GUIDE.en.md).
