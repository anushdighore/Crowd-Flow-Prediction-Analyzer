import { getApiBaseUrl, buildWsUrl } from "./api";

describe("api config helpers", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it("prefers REACT_APP_API_BASE_URL when provided", () => {
    process.env.REACT_APP_API_BASE_URL = "https://api.example.com";
    expect(getApiBaseUrl()).toBe("https://api.example.com");
  });

  it("derives secure websocket url from https base", () => {
    process.env.REACT_APP_API_BASE_URL = "https://api.example.com";
    delete process.env.REACT_APP_WS_BASE_URL;
    expect(buildWsUrl("/ws/count")).toBe("wss://api.example.com/ws/count");
  });
});
