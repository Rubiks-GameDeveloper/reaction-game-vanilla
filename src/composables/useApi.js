/**
 * API client for backend communication
 */
import { ref } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Reactive state for authentication
const isAuthenticated = ref(false)
const user = ref(null)
const accessToken = ref(localStorage.getItem('access_token'))
const refreshToken = ref(localStorage.getItem('refresh_token'))

// Check if user is authenticated on load
if (accessToken.value) {
  isAuthenticated.value = true
}

/**
 * Make API request with authentication
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  // Add auth token if available
  if (accessToken.value) {
    headers['Authorization'] = `Bearer ${accessToken.value}`
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    // Handle token refresh on 401
    if (response.status === 401 && refreshToken.value) {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        // Retry request with new token
        headers['Authorization'] = `Bearer ${accessToken.value}`
        return fetch(url, {
          ...options,
          headers,
        }).then(res => res.json())
      }
    }

    if (!response.ok) {
      let errorData
      try {
        errorData = await response.json()
      } catch {
        errorData = { detail: `HTTP ${response.status}: ${response.statusText}` }
      }
      
      // Handle validation errors from Django REST Framework
      if (errorData.password || errorData.email || errorData.username || errorData.non_field_errors) {
        const errorMessages = []
        if (errorData.password) {
          const passwordErrors = Array.isArray(errorData.password) ? errorData.password : [errorData.password]
          errorMessages.push(...passwordErrors)
        }
        if (errorData.email) {
          const emailErrors = Array.isArray(errorData.email) ? errorData.email : [errorData.email]
          errorMessages.push(...emailErrors)
        }
        if (errorData.username) {
          const usernameErrors = Array.isArray(errorData.username) ? errorData.username : [errorData.username]
          errorMessages.push(...usernameErrors)
        }
        if (errorData.non_field_errors) {
          const nonFieldErrors = Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors : [errorData.non_field_errors]
          errorMessages.push(...nonFieldErrors)
        }
        throw new Error(errorMessages.join('; ') || 'Ошибка валидации')
      }
      
      throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('API Request Error:', error)
    throw error
  }
}

/**
 * Refresh access token
 */
async function refreshAccessToken() {
  if (!refreshToken.value) return false

  try {
    const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken.value }),
    })

    if (response.ok) {
      const data = await response.json()
      accessToken.value = data.access
      localStorage.setItem('access_token', data.access)
      return true
    }
  } catch (error) {
    console.error('Token refresh error:', error)
    logout()
  }

  return false
}

/**
 * Authentication methods
 */
export const useAuth = () => {
  const register = async (username, email, password, password2) => {
    try {
      const requestData = {
        username,
        email,
        password,
        password2,
      }
      
      console.log('Registering user:', { username, email, password: '***', password2: '***' })
      
      const data = await apiRequest('/auth/register/', {
        method: 'POST',
        body: JSON.stringify(requestData),
      })

      if (data.tokens) {
        accessToken.value = data.tokens.access
        refreshToken.value = data.tokens.refresh
        localStorage.setItem('access_token', data.tokens.access)
        localStorage.setItem('refresh_token', data.tokens.refresh)
        isAuthenticated.value = true
        user.value = data.user
      }

      return data
    } catch (error) {
      throw error
    }
  }

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      accessToken.value = data.access
      refreshToken.value = data.refresh
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      isAuthenticated.value = true

      // Fetch user profile
      await fetchUserProfile()

      return data
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  const fetchUserProfile = async () => {
    try {
      const data = await apiRequest('/auth/profile/')
      user.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      return null
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const data = await apiRequest('/auth/profile/', {
        method: 'PUT',
        body: JSON.stringify(profileData),
      })
      user.value = data
      return data
    } catch (error) {
      throw error
    }
  }

  return {
    register,
    login,
    logout,
    fetchUserProfile,
    updateProfile,
    isAuthenticated,
    user,
  }
}

/**
 * Game session methods
 */
export const useGameSessions = () => {
  const saveGameSession = async (gameData) => {
    try {
      const data = await apiRequest('/games/sessions/', {
        method: 'POST',
        body: JSON.stringify({
          game_state: gameData.gameState || {},
          score: gameData.score,
          difficulty: gameData.difficulty,
          time_played: gameData.timePlayed,
          is_completed: gameData.isCompleted,
          reaction_times: gameData.reactionTimes || [],
        }),
      })
      return data
    } catch (error) {
      console.error('Failed to save game session:', error)
      throw error
    }
  }

  const loadLatestSession = async () => {
    try {
      const data = await apiRequest('/games/sessions/latest/')
      return data
    } catch (error) {
      if (error.message.includes('404')) {
        return null
      }
      throw error
    }
  }

  const getGameSessions = async () => {
    try {
      const data = await apiRequest('/games/sessions/')
      return data.results || data
    } catch (error) {
      throw error
    }
  }

  return {
    saveGameSession,
    loadLatestSession,
    getGameSessions,
  }
}

/**
 * Leaderboard methods
 */
export const useLeaderboard = () => {
  const getLeaderboard = async (difficulty = null, limit = 20) => {
    try {
      let endpoint = '/games/leaderboard/'
      if (limit) {
        endpoint = `/games/leaderboard/top/?limit=${limit}`
        if (difficulty) {
          endpoint += `&difficulty=${difficulty}`
        }
      } else if (difficulty) {
        endpoint += `?difficulty=${difficulty}`
      }

      const data = await apiRequest(endpoint)
      return data.results || data
    } catch (error) {
      throw error
    }
  }

  return {
    getLeaderboard,
  }
}

/**
 * Achievements methods
 */
export const useAchievements = () => {
  const getAchievements = async () => {
    try {
      const data = await apiRequest('/games/achievements/')
      return data.results || data
    } catch (error) {
      throw error
    }
  }

  const getUserAchievements = async () => {
    try {
      const data = await apiRequest('/games/user-achievements/')
      return data.results || data
    } catch (error) {
      throw error
    }
  }

  return {
    getAchievements,
    getUserAchievements,
  }
}

/**
 * Friends methods
 */
export const useFriends = () => {
  const getFriends = async () => {
    try {
      const data = await apiRequest('/games/friends/friends/')
      return data
    } catch (error) {
      throw error
    }
  }

  const getFriendRequests = async () => {
    try {
      const data = await apiRequest('/games/friends/')
      return data.results || data
    } catch (error) {
      throw error
    }
  }

  const sendFriendRequest = async (userId) => {
    try {
      const data = await apiRequest('/games/friends/', {
        method: 'POST',
        body: JSON.stringify({ to_user: userId }),
      })
      return data
    } catch (error) {
      throw error
    }
  }

  const acceptFriendRequest = async (requestId) => {
    try {
      const data = await apiRequest(`/games/friends/${requestId}/accept/`, {
        method: 'POST',
      })
      return data
    } catch (error) {
      throw error
    }
  }

  const rejectFriendRequest = async (requestId) => {
    try {
      const data = await apiRequest(`/games/friends/${requestId}/reject/`, {
        method: 'POST',
      })
      return data
    } catch (error) {
      throw error
    }
  }

  return {
    getFriends,
    getFriendRequests,
    sendFriendRequest,
    acceptFriendRequest,
    rejectFriendRequest,
  }
}

// Export API request function for custom requests
export { apiRequest, isAuthenticated, user }

