import "server-only";

export async function apiRead<T>(path: string): Promise<T> {
  const base = process.env.API_BASE_URL ?? "http://localhost:8080";
  const response = await fetch(`${base}${path}`, {
    cache: "no-store",
    signal: AbortSignal.timeout(5000),
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}
