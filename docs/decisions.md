# Decisions

## 2026-09-12, round-trip through a storage dashboard instead of an own editor

Alternatives: rebuild Home Assistant's dashboard editor in a custom panel (rejected;
only the per-card `getConfigElement()` is public, the rest is internal and moves
every release), or go back to storage mode with flattened files (rejected; the three
dashboards would grow from 4,014 to 9,167 lines and every shared block would exist
three times). The scratch storage dashboard uses only public lovelace commands and
gives the unchanged Home Assistant editor.

## 2026-09-12, ruamel.yaml round-trip, not the core loader

Home Assistant's loader (annotatedyaml) resolves `!include` while loading and keeps
only file and line on nodes; it has no dumper that preserves comments. ruamel.yaml
in round-trip mode keeps comments, quotes, key order, anchors and unknown tags, and
the `!include` tag is registered as a class so it survives a dump verbatim. Pinned
exactly because core does not constrain it.

## 2026-09-12, anchors are read but never written

`tablet.yaml` uses anchors for shared user lists and card rows. Writing through an
alias would change every site at once, and writing one site only would need to
break the alias. Both are surprises, so a change to an anchored node is reported as
blocked and left to the file editor; everything else in the commit still lands.

## 2026-09-12, `!secret` makes a dashboard unsupported

Resolving a secret would copy its value into the scratch storage dashboard, where
any administrator's browser would download it. Refusing is cheaper than a leak.

## 2026-09-12, a separate integration, not a view in HA SOC

The editor writes files under the configuration directory, which is outside HA
SOC's security scope, and needs no Supervisor or app. HA SOC can record commits
through its audit ingest later.

## 2026-09-12, one service object in hass.data, not entry.runtime_data

The editor has no per-entry state: the single config entry exists so the panel can
be added and removed from the UI, and the websocket commands must answer whether or
not that entry is loaded. `hass.data[DOMAIN]` holds the one stateless service for the
whole Home Assistant run, which is the cross-entry singleton case the runtime-data
rule allows; the scanner's three `hass-data-domain` findings are that choice.
