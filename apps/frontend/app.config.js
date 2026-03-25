const fs = require("fs");
const path = require("path");

const rootEnvPath = path.resolve(__dirname, "../../.env");

if (fs.existsSync(rootEnvPath)) {
  const envLines = fs.readFileSync(rootEnvPath, "utf8").split(/\r?\n/);

  for (const line of envLines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }

    const separatorIndex = trimmed.indexOf("=");
    if (separatorIndex <= 0) {
      continue;
    }

    const key = trimmed.slice(0, separatorIndex).trim();
    const value = trimmed.slice(separatorIndex + 1).trim();

    if (!(key in process.env)) {
      process.env[key] = value;
    }
  }
}

const appConfig = require("./app.json");

module.exports = {
  ...appConfig,
  expo: {
    ...appConfig.expo,
    extra: {
      ...(appConfig.expo?.extra ?? {}),
      apiBaseUrl: process.env.EXPO_PUBLIC_API_URL || "",
    },
  },
};
