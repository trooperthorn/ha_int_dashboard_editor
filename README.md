# Dashboard Editor for Home Assistant

![GitHub Release](https://img.shields.io/github/v/release/trooperthorn/ha_int_dashboard_editor?style=for-the-badge)
![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)
![Home Assistant](https://img.shields.io/badge/Home_Assistant-2026.9.0-blue.svg?style=for-the-badge)

Home Assistant's own graphical editor for dashboards that live in YAML files, with
the result written back into those files, `!include` fragments included.

A dashboard in YAML mode cannot be edited in the UI: Home Assistant refuses the save
and the editor never opens. YAML mode is also the only way to share one fragment
(a room's cards, a set of chips, a pop-up) between several dashboards. This
integration keeps the files and gives the editor back:

1. Open. The panel resolves the dashboard's includes and creates a hidden,
   administrator-only scratch copy as an ordinary storage dashboard, then opens it in
   Home Assistant's editor. Card picker, visual card editors, sections, drag and drop,
   view visibility: nothing new to learn.
2. Edit as usual.
3. Preview and commit. The panel lists which files will change and why. Commit writes
   each change into the file that owns it, backs the originals up, refreshes the live
   dashboard, and deletes the scratch copy.

The panel also edits the `lovelace: dashboards:` block so a YAML dashboard can be
added, renamed, or removed without opening `configuration.yaml`. Resources are not
touched; with `resource_mode: storage` they stay under Settings, Dashboards.

Design, rules, security, and operations detail live in [docs/README.md](docs/README.md).

## Installation

1. Add `https://github.com/trooperthorn/ha_int_dashboard_editor` to HACS as a custom
   repository of type Integration, then download Dashboard Editor.
2. Restart Home Assistant.
3. Settings, Devices and services, Add integration, Dashboard Editor. There are no
   settings.
4. The sidebar shows "Dashboard editor" for administrators.

Requirements: Home Assistant 2026.9.0 or later and at least one dashboard declared
with `mode: yaml` under `lovelace: dashboards:`.

## Removal

Remove the integration under Settings, Devices and services. Any scratch dashboard
still open (`edit-<name>`) is an ordinary storage dashboard; delete it under Settings,
Dashboards. Backups under `.storage/dashboard_editor/backups` can be deleted.

## What it refuses

- Dashboards that use `!secret`, `!include_dir_*`, `!env_var`, `!input`, or merge
  keys (`<<`) cannot be opened; the listing says which tag.
- A change to an anchored or aliased node (`&name`, `*name`) is reported and left to
  the file editor; the rest of the commit still lands.
- Included paths must stay inside the configuration directory.

## Example

`dashboards/mobile.yaml`:

```yaml
decluttering_templates: !include shared/templates.yaml
views:
  - title: Garage
    path: garage
    cards: !include shared/rooms/garage.yaml
  - title: Utility Room
    path: utility-room
    cards: []
```

Restricting the Utility Room view to one user in the editor's visibility tab and
committing writes, in that file only:

```yaml
  - title: Utility Room
    path: utility-room
    visible:
      - user: 0123456789abcdef0123456789abcdef
    cards: []
```

Editing a garage card lands in `shared/rooms/garage.yaml`, so every dashboard that
includes it changes together; the preview names the file before anything is written.

## Verification of a release

```bash
gh release download vYYYY.MM.DD.N -R trooperthorn/ha_int_dashboard_editor -p dashboard_editor.zip -p SHA256SUMS
sha256sum --check SHA256SUMS --ignore-missing
gh attestation verify dashboard_editor.zip -R trooperthorn/ha_int_dashboard_editor
```

## License

Apache-2.0.
