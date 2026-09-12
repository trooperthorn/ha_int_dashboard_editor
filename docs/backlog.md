# Backlog

- 2026-09-12 Brand icon: ship `brand/icon.png` for the integrations page.
- 2026-09-12 Repair issue when a registered YAML dashboard cannot be opened
  (missing file, `!secret`), instead of only the listing's problem column.
- 2026-09-12 Detect each file's existing sequence indentation style instead of
  re-indenting to the documented style on first commit.
- 2026-09-12 Send commit records to HA SOC's `ha_soc.ingest_audit` so dashboard
  edits appear in its audit chain.
- 2026-09-12 Card identity for the list matcher is a fixed key list; a
  `custom:decluttering-card` with only `template` and `variables` matches on
  `template`, which merges two cards of the same template edited at once into one
  modification plus one insert. Harmless, but a `variables` comparison would be
  tighter.
- 2026-09-12 Exception translations (quality scale `exception-translations`).
