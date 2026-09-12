# Design

## The problem

Home Assistant refuses to save a dashboard that is configured in YAML mode:
`LovelaceConfig.async_save` raises "Not supported" for every `lovelace/config/save`
call on it, and the frontend blocks edit mode with the `yaml_unsupported` alert (the
old `?edit=1` hole was closed in 2023.12 by frontend PR 18879). YAML mode is what
makes shared `!include` fragments possible, so an install that uses them loses the
graphical editor. Reproducing Home Assistant's editor is not an option: only the
per-card `getConfigElement()` editor is a public contract, and the view, section,
badge and dashboard editors are internal chunks of the Lovelace panel that move with
every release.

## The round-trip

1. Open. The panel asks the backend to resolve the dashboard: the root file and every
   `!include` are loaded with ruamel.yaml in round-trip mode and flattened to plain
   JSON. The panel then creates an ordinary storage dashboard `edit-<id>` (hidden from
   the sidebar, admin only) through Home Assistant's own `lovelace/dashboards/create`
   and `lovelace/config/save`, and navigates to it in edit mode. The editing experience
   is Home Assistant's, unchanged.
2. Edit. Card picker, visual card editors, sections, drag and drop, view visibility.
3. Preview and commit. The panel reads the scratch copy back with `lovelace/config`
   and sends it to the backend. The reconciler walks the edited JSON and the
   round-trip tree together and mutates the tree in the file that owns each node:
   a change beside an include lands in the parent file, a change inside an included
   fragment lands in the fragment file. Only files with a recorded change are
   dumped, every rewritten file is backed up first, and the write is an atomic
   replace. The panel then forces `lovelace/config` on the live dashboard, which
   re-reads the file by modification time, and deletes the scratch copy.

The backend never touches Lovelace internals beyond reading the registered YAML
dashboards from `hass.data[LOVELACE_DATA]` (mode, file, title, icon).

## Reconcile rules

- Mapping keys present in both sides recurse. Keys added by the editor are appended
  in the owning file. Keys missing from the edited copy are deleted, except keys
  whose original value is `null`: Home Assistant's editor drops null keys, and that
  is not a removal.
- Lists of the same length with pairwise-compatible kinds (map with map, list with
  list, scalar with scalar) reconcile position by position, so a card edited in place
  keeps its `!include` neighbours and their comments.
- Otherwise items are matched in two passes: first an unused original that is deep
  equal (so moved cards keep their `!include` tag), then an unused original of the
  same kind whose identity (card `type` plus the first of `path`, `entity`, `name`,
  `title`, `template`) matches, nearest index first. Unmatched edited items are
  inserted as plain YAML; unmatched originals are removed. The list is rebuilt in
  the owning file in the edited order.
- An `!include` whose target kind matches the edited value recurses into the target
  file. When the kinds differ (a list fragment replaced by one card) the include is
  replaced by the inline value in the parent and the plan carries a warning.
- Anchored or aliased nodes and tagged scalars other than `!include` are never
  modified: a change to one is reported under "blocked" and the rest of the commit
  proceeds. `!secret`, `!include_dir_*`, `!env_var`, `!input` and merge keys make a
  dashboard unsupported for opening at all; the listing says why.
- Multi-line strings are written as literal blocks. Quotes and comments on untouched
  scalars survive because the round-trip objects are reused.
- Every included path is resolved relative to the including file, as Home Assistant
  does, and must stay inside the configuration directory.

## Formatting

The dumper writes mappings at two spaces and sequences with the dash indented two
spaces under the key, the style Home Assistant's documentation uses. A file whose
root is a list is written with the dashes in column 0. A file written in another
style is re-indented on its first commit; nothing else changes.

## The dashboards block

Home Assistant registers YAML dashboards once at startup from `lovelace:
dashboards:`, and the UI's Add dashboard creates storage dashboards only. The
panel edits that block in place, in `configuration.yaml` or in the file it includes
(`lovelace: !include lovelace.yaml`), creates the dashboard file from a template
when asked, and says that a restart is required. Resources are untouched: with
`resource_mode: storage` they stay under Settings, Dashboards, Resources.
