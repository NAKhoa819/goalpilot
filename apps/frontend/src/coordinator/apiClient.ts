import Constants from 'expo-constants';
import { Platform } from 'react-native';

type ExpoExtra = {
  apiBaseUrl?: string;
};

function normalizeHost(host: string): string {
  if (!host) {
    return host;
  }

  return host.replace(/:\d+$/, '');
}

function normalizeBaseUrl(url: string | null | undefined): string | null {
  if (!url) {
    return null;
  }

  const trimmed = url.trim().replace(/\/$/, '');
  return trimmed || null;
}

function extractHost(uri: string | null | undefined): string | null {
  if (!uri) {
    return null;
  }

  const host = normalizeHost(uri.split(':')[0] ?? '');
  return host || null;
}

function getExpoHost(): string | null {
  const expoConfigHost = extractHost(Constants.expoConfig?.hostUri ?? null);
  if (expoConfigHost) {
    return expoConfigHost;
  }

  const expoGoConfig = Constants.expoGoConfig as
    | { debuggerHost?: string; hostUri?: string }
    | null;
  const expoGoHost = extractHost(expoGoConfig?.debuggerHost ?? expoGoConfig?.hostUri ?? null);
  if (expoGoHost) {
    return expoGoHost;
  }

  return extractHost(Constants.linkingUri ?? null);
}

function getConfigApiBaseUrl(): string | null {
  const extra = Constants.expoConfig?.extra as ExpoExtra | undefined;
  return normalizeBaseUrl(extra?.apiBaseUrl);
}

export function getApiBaseUrls(): string[] {
  const candidates: Array<string | null> = [
    getConfigApiBaseUrl(),
    normalizeBaseUrl(process.env.EXPO_PUBLIC_API_URL),
  ];

  const expoHost = getExpoHost();
  if (expoHost) {
    candidates.push(`http://${expoHost}:8000`);
  }

  if (Platform.OS === 'android') {
    candidates.push('http://10.0.2.2:8000');
  }

  candidates.push('http://localhost:8000');

  return [...new Set(candidates.filter((value): value is string => Boolean(value)))];
}

export function getApiBaseUrl(): string {
  const [first] = getApiBaseUrls();
  if (first) {
    return first;
  }

  return 'http://localhost:8000';
}

async function parseJsonResponse(res: Response): Promise<unknown> {
  const rawBody = await res.text();
  if (!rawBody) {
    return null;
  }

  try {
    return JSON.parse(rawBody);
  } catch {
    return { message: rawBody };
  }
}

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrls = getApiBaseUrls();
  let lastNetworkError = 'Unknown network error';

  for (const baseUrl of baseUrls) {
    const url = `${baseUrl}${path}`;
    let res: Response;
    try {
      res = await fetch(url, init);
    } catch (error) {
      lastNetworkError = error instanceof Error ? error.message : 'Unknown network error';
      continue;
    }

    const data = await parseJsonResponse(res);
    if (!res.ok) {
      const message = typeof data === 'object' && data !== null && 'message' in data
        ? String((data as { message?: string }).message ?? '')
        : '';
      throw new Error(message || `Request failed: ${res.status}`);
    }

    return data as T;
  }

  throw new Error(`Cannot reach backend. Tried: ${baseUrls.join(', ')}. Last error: ${lastNetworkError}`);
}
