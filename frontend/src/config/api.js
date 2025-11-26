const trimTrailingSlash = (value = "") => value.replace(/\/+$/, "");
const ensureLeadingSlash = (value = "") =>
  value.startsWith("/") ? value : `/${value}`;

const inferApiBase = () => {
  const fallbackPort = process.env.REACT_APP_API_PORT || "8000";

  if (typeof window !== "undefined" && window.location) {
    const { protocol, hostname } = window.location;

    // Default to backend on same host but configurable port
    return `${protocol}//${hostname}:${fallbackPort}`;
  }

  return `http://localhost:${fallbackPort}`;
};

const swapProtocol = (url, toSecure) => {
  if (url.startsWith("https://") || url.startsWith("http://")) {
    const withoutProtocol = url.replace(/^https?:\/\//i, "");
    return `${toSecure ? "wss" : "ws"}://${withoutProtocol}`;
  }

  return url;
};

export const getApiBaseUrl = () => {
  const fromEnv = process.env.REACT_APP_API_BASE_URL?.trim();
  if (fromEnv) {
    return trimTrailingSlash(fromEnv);
  }

  return trimTrailingSlash(inferApiBase());
};

export const getWsBaseUrl = () => {
  const fromEnv = process.env.REACT_APP_WS_BASE_URL?.trim();
  if (fromEnv) {
    return trimTrailingSlash(fromEnv);
  }

  const apiBase = getApiBaseUrl();
  const secure = apiBase.startsWith("https://");
  return trimTrailingSlash(swapProtocol(apiBase, secure));
};

export const buildApiUrl = (path = "/") =>
  `${getApiBaseUrl()}${ensureLeadingSlash(path)}`;

export const buildWsUrl = (path = "/") =>
  `${getWsBaseUrl()}${ensureLeadingSlash(path)}`;
