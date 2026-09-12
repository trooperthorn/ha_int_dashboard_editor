# Operations

## Test gate

The Home Assistant harness imports `fcntl`, so the suite runs in WSL Ubuntu with
Python 3.14, never on the Windows host:

```bash
wsl -e bash -lc 'cd /mnt/c/Users/<you>/repos/ha_int_dashboard_editor && ~/socvenv/bin/python -m pytest tests -q'
```

Venv: `python3.14 -m venv ~/socvenv && ~/socvenv/bin/pip install -r requirements_test.txt`.
The harness pin 0.13.364 installs core 2026.9.1; CI asserts that version. The full
gate is `ruff check`, `mypy --python-version 3.14 custom_components/dashboard_editor/`,
`pytest tests`, the frontend bundle drift check, and
`python scripts/build_release_artifacts.py --validate-only`.

## Frontend

`custom_components/dashboard_editor/frontend` is a Lit panel built with rollup:

```bash
cd custom_components/dashboard_editor/frontend && npm ci && npm run build
```

`dist/dashboard-editor-panel.js` is committed; CI rebuilds it and fails on drift.
The integration serves it at `/api/panel_custom/dashboard_editor` with a content
hash as the cache token and registers the sidebar entry "Dashboard editor" for
administrators.

## Release path

A merge to `main` is the release. `release.yml` reruns the test and validate
workflows, validates the manifest version, builds the deterministic
`dashboard_editor.zip`, generates the SPDX SBOM and checksums, attests both, and
publishes an immutable tag and release. `prepare-release.yml` runs after every
Release run on `main` and opens the CalVer bump PR when the component changed since
the last release; it needs the repository variable `RELEASE_AUTOMATION_CLIENT_ID`
and the secret `RELEASE_AUTOMATION_PRIVATE_KEY` of the release GitHub App.

Verification of a release:

```bash
gh release download vYYYY.MM.DD.N -R trooperthorn/ha_int_dashboard_editor -p dashboard_editor.zip -p SHA256SUMS
sha256sum --check SHA256SUMS --ignore-missing
gh attestation verify dashboard_editor.zip -R trooperthorn/ha_int_dashboard_editor
```

## Branch protection

`main` requires, with strict status checks: `pytest (Python 3.14)`, `Frontend bundle
matches source`, `HACS validation`, `hassfest (manifest sanity)`, `CodeQL (python)`,
`CodeQL (javascript-typescript)`, `Python static security checks`, `Frontend
dependency audit`; conversation resolution; admins included; no force pushes.

## Runtime knobs

None. Backups keep the last 20 commit sets under
`.storage/dashboard_editor/backups/`; older sets are removed on the next commit.

## Troubleshooting

- "is not a YAML dashboard": the id is not registered in `lovelace: dashboards:`
  with `mode: yaml`, or Home Assistant was not restarted after adding it.
- "uses !secret, which the editor does not resolve": the dashboard cannot be opened.
  Replace the secret with a literal in the dashboard, or leave that dashboard to the
  file editor.
- "anchored or aliased node changed": the commit wrote everything else; make that one
  edit in the file. Anchors are left alone so an alias elsewhere keeps its meaning.
- The live dashboard still shows the old version after a commit: choose Refresh from
  its three-dot menu. The file is re-read when its modification time moves; a
  network file system with coarse timestamps can lag.
- A scratch dashboard `edit-<id>` remains after a browser crash: open the panel and
  choose Discard, or Continue editing and then Commit.
- The panel does not appear in the sidebar: the bundle is missing (HACS download
  incomplete); the Core log says "Frontend bundle missing".
