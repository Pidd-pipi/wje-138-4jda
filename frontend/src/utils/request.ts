export type ApiError = Error & { data?: { detail?: string } };

export async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) }, ...init });
  if (!response.ok) {
    const text = await response.text();
    let data: { detail?: string } | undefined;
    try { data = JSON.parse(text); } catch { data = undefined; }
    const error = new Error(data?.detail ?? text) as ApiError;
    error.data = data;
    throw error;
  }
  return response.json() as Promise<T>;
}
