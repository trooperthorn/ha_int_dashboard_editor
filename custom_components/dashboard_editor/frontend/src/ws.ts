/** Typed wrappers over hass.callWS for the editor's commands and the lovelace commands it drives. */

export interface HomeAssistant {
  callWS<T>(msg: Record<string, unknown>): Promise<T>;
  user?: { id: string; is_admin?: boolean };
}

export interface YamlDashboard {
  id: string;
  url_path: string;
  title: string;
  icon: string | null;
  file: string;
  scratch_url_path: string;
  includes: string[];
  supported: boolean;
  problem: string | null;
}

export interface Listing {
  dashboards: YamlDashboard[];
  resource_mode: string | null;
  config_dir: string;
}

export interface Change {
  file: string;
  path: string;
  kind: string;
  detail: string;
}

export interface Plan {
  changes: Change[];
  files: string[];
  warnings: string[];
  blocked: string[];
}

export interface CommitResult extends Plan {
  written: string[];
  backup: string | null;
}

export interface ConfigEntry {
  url_path: string;
  mode?: string;
  title?: string;
  icon?: string;
  show_in_sidebar?: boolean;
  require_admin?: boolean;
  filename?: string;
}

export interface DashboardsConfig {
  file: string;
  writable: boolean;
  problem: string | null;
  mode?: string | null;
  entries: ConfigEntry[];
}

export interface StorageDashboard {
  id: string;
  url_path: string;
  title: string;
  mode: string;
}

export type DashboardConfig = Record<string, unknown>;

export const listDashboards = (hass: HomeAssistant) => hass.callWS<Listing>({ type: "dashboard_editor/list" });

export const resolveDashboard = (hass: HomeAssistant, dashboard_id: string) =>
  hass.callWS<{ config: DashboardConfig; files: string[] }>({ type: "dashboard_editor/resolve", dashboard_id });

export const planCommit = (hass: HomeAssistant, dashboard_id: string, config: DashboardConfig) =>
  hass.callWS<Plan>({ type: "dashboard_editor/plan", dashboard_id, config });

export const commit = (hass: HomeAssistant, dashboard_id: string, config: DashboardConfig) =>
  hass.callWS<CommitResult>({ type: "dashboard_editor/commit", dashboard_id, config });

export const getDashboardsConfig = (hass: HomeAssistant) =>
  hass.callWS<DashboardsConfig>({ type: "dashboard_editor/config/get" });

export const setDashboardsConfig = (hass: HomeAssistant, entry: ConfigEntry & { create_file: boolean }) =>
  hass.callWS<{ created: boolean; file_created: boolean; restart_required: boolean }>({
    type: "dashboard_editor/config/set",
    ...entry,
  });

export const removeDashboardsConfig = (hass: HomeAssistant, url_path: string) =>
  hass.callWS<{ restart_required: boolean }>({ type: "dashboard_editor/config/remove", url_path });

// Home Assistant's own dashboard commands; the scratch copy is an ordinary storage dashboard.
export const listStorageDashboards = (hass: HomeAssistant) =>
  hass.callWS<StorageDashboard[]>({ type: "lovelace/dashboards/list" });

export const createStorageDashboard = (hass: HomeAssistant, url_path: string, title: string, icon: string | null) =>
  hass.callWS<StorageDashboard>({
    type: "lovelace/dashboards/create",
    url_path,
    title,
    icon: icon ?? "mdi:pencil-box-outline",
    show_in_sidebar: false,
    require_admin: true,
  });

export const deleteStorageDashboard = (hass: HomeAssistant, dashboard_id: string) =>
  hass.callWS<null>({ type: "lovelace/dashboards/delete", dashboard_id });

export const saveStorageConfig = (hass: HomeAssistant, url_path: string, config: DashboardConfig) =>
  hass.callWS<null>({ type: "lovelace/config/save", url_path, config });

export const loadConfig = (hass: HomeAssistant, url_path: string) =>
  hass.callWS<DashboardConfig>({ type: "lovelace/config", url_path, force: true });
