# Security

## Trust boundary

Every command needs an administrator session; Home Assistant's `require_admin`
decorator enforces it before the handler runs. An administrator can already edit
any file through the File editor or Terminal apps, so the integration adds no
capability, only a safer path to one.

## What the backend writes

- Dashboard files that the registered YAML dashboards name, and the files they
  include. Included paths are resolved relative to the including file and refused
  when they resolve outside the configuration directory, including through `..`
  and symlinks.
- The `lovelace: dashboards:` block in `configuration.yaml` or the file it includes,
  and a new dashboard file from a fixed template when asked. File names must be
  relative, end in `.yaml`, and stay inside the configuration directory.
- Backups under `.storage/dashboard_editor/backups/<timestamp>/`, the last 20 sets.

Writes are atomic replaces of whole files. No other file is read or written; in
particular `secrets.yaml` is never opened, because `!secret` makes a dashboard
unsupported instead of being resolved.

## What the scratch copy exposes

The scratch dashboard is a storage dashboard visible to administrators only
(`require_admin: true`, hidden from the sidebar). It holds the resolved dashboard
while editing and is deleted on commit or discard. A dashboard left open survives a
restart as an ordinary hidden storage dashboard until it is committed or discarded.

## Not defended against

A hostile administrator, or a hostile process with write access to the
configuration directory. The integration does not sign or verify files.
