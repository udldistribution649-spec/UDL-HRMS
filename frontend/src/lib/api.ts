
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export function getAccessToken(): string | null {
  return sessionStorage.getItem('hrms_access_token')
}

export function saveAccessToken(token: string): void {
  sessionStorage.setItem('hrms_access_token', token)
}

export function clearAccessToken(): void {
  sessionStorage.removeItem('hrms_access_token')
}

export async function login(
  username: string,
  password: string,
): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || 'Login failed')
  }

  saveAccessToken(data.access_token)
  return data as LoginResponse
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAccessToken()

  const headers = new Headers(options.headers)

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(
      typeof data.detail === 'string'
        ? data.detail
        : `Request failed (${response.status})`,
    )
  }

  return data as T
}
