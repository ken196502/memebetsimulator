// API configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : '/api'  // 使用代理，不要硬编码端口

// Helper function for making API requests
export async function apiRequest(
  endpoint: string, 
  options: RequestInit = {}
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }
  
  const response = await fetch(url, defaultOptions)
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  const contentType = response.headers.get('content-type')
  if (!contentType || !contentType.includes('application/json')) {
    throw new Error('Response is not JSON')
  }
  
  return response
}

// Specific API functions
export async function checkRequiredConfigs() {
  const response = await apiRequest('/config/check-required')
  return response.json()
}

export async function getXueqiuCookie() {
  const response = await apiRequest('/config/xueqiu-cookie')
  return response.json()
}

export async function saveXueqiuCookie(cookieValue: string, description: string = '雪球API访问Cookie') {
  const response = await apiRequest('/config/xueqiu-cookie', {
    method: 'POST',
    body: JSON.stringify({
      key: 'xueqiu_cookie',
      value: cookieValue,
      description: description
    }),
  })
  return response.json()
}

// Pump.fun API functions
export async function getPumpFunCookie() {
  const response = await apiRequest('/config/pump-fun-cookie')
  return response.json()
}

export async function savePumpFunCookie(cookieValue: string, description: string = 'Pump.fun API访问Cookie') {
  const response = await apiRequest('/config/pump-fun-cookie', {
    method: 'POST',
    body: JSON.stringify({
      key: 'pump_fun_cookie',
      value: cookieValue,
      description: description
    }),
  })
  return response.json()
}

export async function testPumpFunConnection() {
  const response = await apiRequest('/config/pump-fun-test')
  return response.json()
}

export async function getPumpFunCoins(limit: number = 50, offset: number = 0) {
  const response = await apiRequest(`/pump/coins?limit=${limit}&offset=${offset}`)
  return response.json()
}

export async function getPumpFunTrendingCoins(limit: number = 20) {
  const response = await apiRequest(`/pump/trending?limit=${limit}`)
  return response.json()
}

export async function getPumpFunNewCoins(limit: number = 20) {
  const response = await apiRequest(`/pump/new?limit=${limit}`)
  return response.json()
}

export async function getPumpFunCoinDetail(mintAddress: string) {
  const response = await apiRequest(`/pump/coins/${mintAddress}`)
  return response.json()
}

export async function searchPumpFunCoins(query: string, limit: number = 20) {
  const response = await apiRequest(`/pump/search?q=${encodeURIComponent(query)}&limit=${limit}`)
  return response.json()
}