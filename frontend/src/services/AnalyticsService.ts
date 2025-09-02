// Temporary Analytics Service - to be replaced with generated client
const BASE_URL = 'http://localhost:8000/api/v1'

interface RequestOptions {
  days?: number
  limit?: number
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

export const AnalyticsService = {
  async getAnalyticsOverview(options: RequestOptions = {}) {
    const { days = 30 } = options
    const response = await fetch(`${BASE_URL}/analytics/overview?days=${days}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      throw new Error('Failed to fetch analytics overview')
    }
    return response.json()
  },

  async getResponseTrends(options: RequestOptions = {}) {
    const { days = 30 } = options
    const response = await fetch(`${BASE_URL}/analytics/response-trends?days=${days}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      throw new Error('Failed to fetch response trends')
    }
    return response.json()
  },

  async getSentimentAnalysis(options: RequestOptions = {}) {
    const { days = 30 } = options
    const response = await fetch(`${BASE_URL}/analytics/sentiment-analysis?days=${days}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      throw new Error('Failed to fetch sentiment analysis')
    }
    return response.json()
  },

  async getSurveyPerformance() {
    const response = await fetch(`${BASE_URL}/analytics/survey-performance`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      throw new Error('Failed to fetch survey performance')
    }
    return response.json()
  },

  async getRecentFeedback(options: RequestOptions = {}) {
    const { limit = 10 } = options
    const response = await fetch(`${BASE_URL}/analytics/recent-feedback?limit=${limit}`, {
      headers: getAuthHeaders(),
    })
    if (!response.ok) {
      throw new Error('Failed to fetch recent feedback')
    }
    return response.json()
  },

  async analyzeText(text: string) {
    const response = await fetch(`${BASE_URL}/analytics/analyze-text`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ text }),
    })
    if (!response.ok) {
      throw new Error('Failed to analyze text')
    }
    return response.json()
  },
}
