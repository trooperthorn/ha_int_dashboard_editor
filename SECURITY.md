# Security Policy

## Reporting a vulnerability

Do not open a public issue containing exploit details, credentials, private
addresses, or logs. Use GitHub's private vulnerability-reporting feature for
this repository. If private reporting is unavailable, open a minimal issue
asking the maintainer to establish a private channel; omit technical details.

Include the affected version/commit, prerequisites, impact, a minimal
reproduction, and suggested remediation. Remove tokens, usernames, and private
network details.

## Response targets

These are project targets, not an SLA: acknowledge critical/high reports in
three business days, establish severity and containment in seven, and publish
a coordinated fix/advisory as soon as safely validated. Lower-severity issues
are prioritized by exploitability and impact.

## Supported version

Only the latest published release and the default branch receive security
fixes. Operators should update Home Assistant promptly and retain a tested
rollback/backup.

## Security boundaries

Dashboard Editor writes dashboard YAML files and the `lovelace: dashboards:`
block inside the Home Assistant configuration directory, on behalf of an
administrator session only. Every path is confined to that directory. It does
not read `secrets.yaml`; a dashboard that uses `!secret` is refused. It does
not defend against a hostile administrator or a process that already has write
access to the configuration directory. docs/security.md carries the full model.
