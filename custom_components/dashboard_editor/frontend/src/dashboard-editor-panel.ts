import { LitElement, html, css, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import {
  type HomeAssistant,
  type YamlDashboard,
  type Listing,
  type Plan,
  type CommitResult,
  type DashboardsConfig,
  type ConfigEntry,
  type StorageDashboard,
  listDashboards,
  resolveDashboard,
  planCommit,
  commit,
  getDashboardsConfig,
  setDashboardsConfig,
  removeDashboardsConfig,
  listStorageDashboards,
  createStorageDashboard,
  deleteStorageDashboard,
  saveStorageConfig,
  loadConfig,
} from "./ws";

/**
 * The Dashboard editor panel.
 *
 * The backend only reads and writes YAML files. The scratch copy a person edits
 * is an ordinary storage dashboard created and deleted here through Home
 * Assistant's own lovelace commands, so the editing experience is Home
 * Assistant's, unchanged. Flow and rules: docs/design.md in the repository.
 */

const navigate = (path: string) => {
  history.pushState(null, "", path);
  window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
};

const KIND_LABEL: Record<string, string> = {
  set: "changed",
  add: "added",
  delete: "removed",
  insert: "card added",
  remove: "card removed",
  replace: "replaced",
  reorder: "reordered",
  resize: "list rebuilt",
  include_dropped: "include replaced by inline value",
};

type EntryDraft = ConfigEntry & { create_file: boolean; isNew?: boolean };

@customElement("dashboard-editor-panel")
export class DashboardEditorPanel extends LitElement {
  static styles = css`
    :host {
      display: block;
      background: var(--primary-background-color);
      color: var(--primary-text-color);
      min-height: 100vh;
    }
    .page {
      max-width: 1100px;
      margin: 0 auto;
      padding: 20px clamp(14px, 2vw, 24px) 40px;
    }
    h1 {
      font-size: 22px;
      font-weight: 500;
      margin: 0 0 4px;
    }
    h2 {
      font-size: 16px;
      font-weight: 500;
      margin: 28px 0 10px;
    }
    .muted {
      color: var(--secondary-text-color);
      font-size: 13px;
    }
    .card {
      background: var(--card-background-color, #fff);
      border-radius: var(--ha-card-border-radius, 12px);
      border: 1px solid var(--divider-color);
      padding: 14px 16px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th {
      text-align: left;
      font-weight: 500;
      color: var(--secondary-text-color);
      font-size: 12px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      padding: 6px 8px;
      border-bottom: 1px solid var(--divider-color);
    }
    td {
      padding: 8px;
      border-bottom: 1px solid var(--divider-color);
      vertical-align: top;
    }
    tr:last-child td {
      border-bottom: 0;
    }
    code {
      font-family: var(--ha-font-family-code, monospace);
      font-size: 12.5px;
    }
    .actions {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
    button {
      font: inherit;
      font-size: 13px;
      padding: 6px 12px;
      border-radius: 8px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color, #fff);
      color: var(--primary-text-color);
      cursor: pointer;
    }
    button.primary {
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      border-color: var(--primary-color);
    }
    button.danger {
      color: var(--error-color);
    }
    button:disabled {
      opacity: 0.5;
      cursor: default;
    }
    .pill {
      display: inline-block;
      font-size: 12px;
      padding: 1px 8px;
      border-radius: 10px;
      background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.06);
    }
    .pill.open {
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
    }
    .alert {
      border-left: 3px solid var(--error-color);
      padding: 8px 12px;
      margin: 10px 0;
      background: rgba(var(--rgb-error-color, 219, 68, 55), 0.08);
      font-size: 13px;
      white-space: pre-wrap;
    }
    .notice {
      border-left: 3px solid var(--warning-color, #ffa600);
      padding: 8px 12px;
      margin: 10px 0;
      background: rgba(var(--rgb-warning-color, 255, 166, 0), 0.08);
      font-size: 13px;
    }
    .plan {
      margin-top: 12px;
      border-top: 1px solid var(--divider-color);
      padding-top: 10px;
    }
    .plan ul {
      margin: 6px 0 0;
      padding-left: 18px;
      font-size: 13px;
    }
    input[type="text"],
    select {
      font: inherit;
      font-size: 13px;
      padding: 4px 6px;
      border-radius: 6px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color, #fff);
      color: var(--primary-text-color);
      width: 100%;
      box-sizing: border-box;
    }
    label.inline {
      display: inline-flex;
      gap: 4px;
      align-items: center;
      font-size: 13px;
      white-space: nowrap;
    }
  `;

  @property({ attribute: false }) hass!: HomeAssistant;

  @state() private _listing: Listing | null = null;
  @state() private _scratch: Map<string, StorageDashboard> = new Map();
  @state() private _plans: Map<string, Plan | CommitResult> = new Map();
  @state() private _busy: string | null = null;
  @state() private _error: string | null = null;
  @state() private _message: string | null = null;
  @state() private _config: DashboardsConfig | null = null;
  @state() private _drafts: EntryDraft[] = [];
  @state() private _restartNeeded = false;

  connectedCallback() {
    super.connectedCallback();
    void this._refresh();
  }

  private async _refresh() {
    this._error = null;
    try {
      const [listing, storage, config] = await Promise.all([
        listDashboards(this.hass),
        listStorageDashboards(this.hass),
        getDashboardsConfig(this.hass),
      ]);
      this._listing = listing;
      const scratch = new Map<string, StorageDashboard>();
      for (const d of storage) {
        const owner = listing.dashboards.find((y) => y.scratch_url_path === d.url_path);
        if (owner) scratch.set(owner.id, d);
      }
      this._scratch = scratch;
      this._config = config;
      this._drafts = config.entries.map((e) => ({ ...e, create_file: false }));
    } catch (err) {
      this._error = errorText(err);
    }
  }

  private async _run(id: string, work: () => Promise<void>) {
    this._busy = id;
    this._error = null;
    this._message = null;
    try {
      await work();
    } catch (err) {
      this._error = errorText(err);
    } finally {
      this._busy = null;
    }
  }

  private _open(d: YamlDashboard) {
    return this._run(d.id, async () => {
      const resolved = await resolveDashboard(this.hass, d.id);
      let scratch = this._scratch.get(d.id);
      if (!scratch) {
        scratch = await createStorageDashboard(this.hass, d.scratch_url_path, `Editing ${d.title}`, d.icon);
      }
      await saveStorageConfig(this.hass, d.scratch_url_path, resolved.config);
      await this._refresh();
      navigate(`/${d.scratch_url_path}/0?edit=1`);
    });
  }

  private _preview(d: YamlDashboard) {
    return this._run(d.id, async () => {
      const config = await loadConfig(this.hass, d.scratch_url_path);
      const plan = await planCommit(this.hass, d.id, config);
      this._plans = new Map(this._plans).set(d.id, plan);
    });
  }

  private _commit(d: YamlDashboard) {
    return this._run(d.id, async () => {
      const config = await loadConfig(this.hass, d.scratch_url_path);
      const result = await commit(this.hass, d.id, config);
      this._plans = new Map(this._plans).set(d.id, result);
      await loadConfig(this.hass, d.url_path);
      const scratch = this._scratch.get(d.id);
      if (scratch && result.blocked.length === 0) {
        await deleteStorageDashboard(this.hass, scratch.id);
      }
      this._message =
        result.written.length === 0
          ? `Nothing to write for ${d.title}; the files already match.`
          : `Wrote ${result.written.join(", ")} for ${d.title}. Backup in ${result.backup}. Open the dashboard and choose Refresh if it still shows the old version.`;
      await this._refresh();
    });
  }

  private _discard(d: YamlDashboard) {
    return this._run(d.id, async () => {
      const scratch = this._scratch.get(d.id);
      if (scratch) await deleteStorageDashboard(this.hass, scratch.id);
      const plans = new Map(this._plans);
      plans.delete(d.id);
      this._plans = plans;
      await this._refresh();
    });
  }

  private _renderDashboards() {
    const l = this._listing;
    if (!l) return html`<p class="muted">Loading…</p>`;
    if (l.dashboards.length === 0) {
      return html`<p class="muted">
        No YAML-mode dashboards are registered. Add one in the block below and restart Home Assistant.
      </p>`;
    }
    return html`
      <table>
        <tr>
          <th>Dashboard</th>
          <th>File</th>
          <th>State</th>
          <th></th>
        </tr>
        ${l.dashboards.map((d) => this._renderRow(d))}
      </table>
    `;
  }

  private _renderRow(d: YamlDashboard) {
    const scratch = this._scratch.get(d.id);
    const busy = this._busy === d.id;
    const plan = this._plans.get(d.id);
    return html`
      <tr>
        <td>
          <strong>${d.title}</strong><br />
          <span class="muted">/${d.url_path}</span>
        </td>
        <td>
          <code>${d.file}</code>
          ${d.includes.length
            ? html`<br /><span class="muted">${d.includes.length} included file${d.includes.length === 1 ? "" : "s"}</span>`
            : nothing}
          ${d.problem ? html`<div class="alert">${d.problem}</div>` : nothing}
        </td>
        <td>
          ${scratch
            ? html`<span class="pill open">editing</span><br /><span class="muted">/${d.scratch_url_path}</span>`
            : html`<span class="pill">on disk</span>`}
        </td>
        <td>
          <div class="actions">
            ${scratch
              ? html`
                  <button ?disabled=${busy} @click=${() => navigate(`/${d.scratch_url_path}/0?edit=1`)}>
                    Continue editing
                  </button>
                  <button ?disabled=${busy} @click=${() => this._preview(d)}>Preview changes</button>
                  <button class="primary" ?disabled=${busy} @click=${() => this._commit(d)}>Commit</button>
                  <button class="danger" ?disabled=${busy} @click=${() => this._discard(d)}>Discard</button>
                `
              : html`
                  <button class="primary" ?disabled=${busy || !d.supported} @click=${() => this._open(d)}>
                    ${busy ? "Opening…" : "Open in editor"}
                  </button>
                `}
          </div>
          ${plan ? this._renderPlan(plan) : nothing}
        </td>
      </tr>
    `;
  }

  private _renderPlan(plan: Plan | CommitResult) {
    const written = (plan as CommitResult).written;
    return html`
      <div class="plan">
        ${written
          ? html`<strong>${written.length ? `Written: ${written.join(", ")}` : "Nothing was written."}</strong>`
          : plan.changes.length
            ? html`<strong>${plan.files.length} file${plan.files.length === 1 ? "" : "s"} will change</strong>`
            : html`<strong>No changes.</strong>`}
        ${plan.changes.length
          ? html`<ul>
              ${plan.changes.map(
                (c) => html`<li><code>${c.file}</code> ${c.path}: ${KIND_LABEL[c.kind] ?? c.kind}${c.detail ? ` (${c.detail})` : ""}</li>`,
              )}
            </ul>`
          : nothing}
        ${plan.warnings.map((w) => html`<div class="notice">${w}</div>`)}
        ${plan.blocked.length
          ? html`<div class="alert">Not written, edit the file directly:\n${plan.blocked.join("\n")}</div>`
          : nothing}
      </div>
    `;
  }

  private _draftChanged(index: number, patch: Partial<EntryDraft>) {
    this._drafts = this._drafts.map((d, i) => (i === index ? { ...d, ...patch } : d));
  }

  private _addDraft() {
    this._drafts = [
      ...this._drafts,
      { url_path: "", title: "", icon: "mdi:view-dashboard", show_in_sidebar: true, require_admin: false, filename: "dashboards/", create_file: true, isNew: true },
    ];
  }

  private _saveDraft(index: number) {
    const d = this._drafts[index];
    return this._run(`cfg-${index}`, async () => {
      await setDashboardsConfig(this.hass, {
        url_path: d.url_path.trim(),
        title: d.title || null as unknown as string,
        icon: d.icon || null as unknown as string,
        show_in_sidebar: d.show_in_sidebar ?? true,
        require_admin: d.require_admin ?? false,
        filename: (d.filename ?? "").trim(),
        create_file: d.create_file,
      });
      this._restartNeeded = true;
      await this._refresh();
    });
  }

  private _removeDraft(index: number) {
    const d = this._drafts[index];
    if (d.isNew) {
      this._drafts = this._drafts.filter((_, i) => i !== index);
      return;
    }
    if (!window.confirm(`Remove ${d.url_path} from the dashboards block? The file stays on disk.`)) return;
    return this._run(`cfg-${index}`, async () => {
      await removeDashboardsConfig(this.hass, d.url_path);
      this._restartNeeded = true;
      await this._refresh();
    });
  }

  private _renderConfig() {
    const c = this._config;
    if (!c) return nothing;
    return html`
      <p class="muted">
        The <code>lovelace: dashboards:</code> block in <code>${c.file}</code>.
        ${c.mode ? html`Top-level mode <code>${c.mode}</code>.` : nothing}
        Resources stay in ${this._listing?.resource_mode ?? "storage"} mode and are managed under Settings, Dashboards.
        Home Assistant reads this block at startup, so every change here needs a restart.
      </p>
      ${c.problem ? html`<div class="alert">${c.problem}</div>` : nothing}
      ${this._restartNeeded
        ? html`<div class="notice">Restart Home Assistant to register the changed dashboards.</div>`
        : nothing}
      <table>
        <tr>
          <th style="width:18%">URL</th>
          <th style="width:18%">Title</th>
          <th style="width:16%">Icon</th>
          <th style="width:24%">File</th>
          <th>Flags</th>
          <th></th>
        </tr>
        ${this._drafts.map((d, i) => this._renderDraft(d, i))}
      </table>
      <div class="actions" style="margin-top:10px">
        <button ?disabled=${!c.writable} @click=${() => this._addDraft()}>Add YAML dashboard</button>
      </div>
    `;
  }

  private _renderDraft(d: EntryDraft, i: number) {
    const busy = this._busy === `cfg-${i}`;
    const writable = this._config?.writable ?? false;
    return html`
      <tr>
        <td>
          ${d.isNew
            ? html`<input type="text" placeholder="garage-dashboard" .value=${d.url_path} @input=${(e: Event) => this._draftChanged(i, { url_path: (e.target as HTMLInputElement).value })} />`
            : html`<code>${d.url_path}</code>`}
        </td>
        <td><input type="text" .value=${d.title ?? ""} @input=${(e: Event) => this._draftChanged(i, { title: (e.target as HTMLInputElement).value })} /></td>
        <td><input type="text" .value=${d.icon ?? ""} @input=${(e: Event) => this._draftChanged(i, { icon: (e.target as HTMLInputElement).value })} /></td>
        <td>
          <input type="text" .value=${d.filename ?? ""} @input=${(e: Event) => this._draftChanged(i, { filename: (e.target as HTMLInputElement).value })} />
          <label class="inline"><input type="checkbox" .checked=${d.create_file} @change=${(e: Event) => this._draftChanged(i, { create_file: (e.target as HTMLInputElement).checked })} /> create if missing</label>
        </td>
        <td>
          <label class="inline"><input type="checkbox" .checked=${d.show_in_sidebar ?? true} @change=${(e: Event) => this._draftChanged(i, { show_in_sidebar: (e.target as HTMLInputElement).checked })} /> sidebar</label><br />
          <label class="inline"><input type="checkbox" .checked=${d.require_admin ?? false} @change=${(e: Event) => this._draftChanged(i, { require_admin: (e.target as HTMLInputElement).checked })} /> admin only</label>
        </td>
        <td>
          <div class="actions">
            <button class="primary" ?disabled=${busy || !writable} @click=${() => this._saveDraft(i)}>Save</button>
            <button class="danger" ?disabled=${busy || !writable} @click=${() => this._removeDraft(i)}>${d.isNew ? "Cancel" : "Remove"}</button>
          </div>
        </td>
      </tr>
    `;
  }

  render() {
    return html`
      <div class="page">
        <h1>Dashboard editor</h1>
        <p class="muted">
          Open a YAML-mode dashboard in Home Assistant's own editor, then commit the result back into the
          files it was assembled from, <code>!include</code> fragments included. A commit backs up every file
          it rewrites under <code>.storage/dashboard_editor/backups</code>.
        </p>
        ${this._error ? html`<div class="alert">${this._error}</div>` : nothing}
        ${this._message ? html`<div class="notice">${this._message}</div>` : nothing}
        <h2>YAML dashboards</h2>
        <div class="card">${this._renderDashboards()}</div>
        <h2>Dashboards block</h2>
        <div class="card">${this._renderConfig()}</div>
      </div>
    `;
  }
}

function errorText(err: unknown): string {
  const e = err as { message?: string; code?: string };
  return e?.message ?? e?.code ?? String(err);
}
