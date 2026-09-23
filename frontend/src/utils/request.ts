/** 后端 4xx 返回的业务错误（如保养到期占用，HTTP 409）。 */
export class ApiError extends Error {
  code: string;
  status: number;
  details?: unknown;

  constructor(message: string, code: string, status: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) }, ...init });
  if (!response.ok) {
    const text = await response.text();
    let code = `HTTP_${response.status}`;
    let message = text;
    let details: unknown;
    try {
      const data = JSON.parse(text) as { code?: string; message?: string };
      details = data;
      if (data.code) code = data.code;
      if (data.message) message = data.message;
    } catch {
      // 非 JSON 错误体时保留原始文本
    }
    throw new ApiError(message, code, response.status, details);
  }
  return response.json() as Promise<T>;
}
