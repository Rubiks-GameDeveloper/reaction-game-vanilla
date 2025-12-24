<template>
  <div class="friends">
    <h2>Друзья</h2>
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else>
      <!-- Форма поиска друзей -->
      <div class="search-box">
        <h3>Найти друга</h3>
        <div class="search-form">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Введите никнейм или email..."
            @keyup.enter="handleSearch"
            class="search-input"
          />
          <button 
            @click="handleSearch" 
            class="button search-button"
            :disabled="isSearching"
          >
            <span v-if="!isSearching">Найти и добавить</span>
            <span v-else>Поиск...</span>
          </button>
        </div>
        <p v-if="searchError" class="error-text">{{ searchError }}</p>
        <p v-if="searchSuccess" class="success-text">{{ searchSuccess }}</p>
      </div>

      <!-- Список друзей -->
      <div class="friends-section">
        <h3>Мои друзья</h3>
        <div v-if="friends.length > 0" class="friends-list">
          <div 
            v-for="friend in friends" 
            :key="friend.id"
            class="friend-item"
          >
            <div class="friend-avatar">
              <span v-if="friend.profile?.avatar">👤</span>
              <span v-else>👤</span>
            </div>
            <div class="friend-info">
              <strong>{{ friend.username }}</strong>
              <p v-if="friend.profile?.bio">{{ friend.profile.bio }}</p>
            </div>
          </div>
        </div>
        <div v-else class="no-friends">
          У вас пока нет друзей
        </div>
      </div>

      <!-- Запросы на дружбу -->
      <div class="requests-section">
        <h3>Запросы на дружбу</h3>
        <div v-if="requests.length > 0" class="requests-list">
          <div 
            v-for="request in requests" 
            :key="request.id"
            class="request-item"
          >
            <div class="request-info">
              <strong>{{ request.from_username || request.to_username }}</strong>
              <span class="request-status">{{ getStatusLabel(request.status) }}</span>
            </div>
            <div v-if="request.status === 'pending' && request.to_username" class="request-actions">
              <button @click="acceptRequest(request.id)" class="button small">Принять</button>
              <button @click="rejectRequest(request.id)" class="button small">Отклонить</button>
            </div>
          </div>
        </div>
        <div v-else class="no-requests">
          Нет запросов на дружбу
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useFriends } from '../composables/useApi'

export default {
  setup() {
    const { getFriends, getFriendRequests, sendFriendRequest, acceptFriendRequest, rejectFriendRequest } = useFriends()
    
    // Переменные для состояния
    const friends = ref([])
    const requests = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const isSearching = ref(false)
    const searchError = ref('')
    const searchSuccess = ref('')

    // Загрузка друзей
    const loadFriends = async () => {
      try {
        const data = await getFriends()
        friends.value = Array.isArray(data) ? data : []
      } catch (error) {
        console.error('Failed to load friends:', error)
      }
    }

    // Загрузка запросов на дружбу
    const loadFriendRequests = async () => {
      try {
        const data = await getFriendRequests()
        requests.value = Array.isArray(data) ? data : []
        console.log('Loaded friend requests:', requests.value)
      } catch (error) {
        console.error('Failed to load friend requests:', error)
      }
    }

    // Поиск и отправка запроса на дружбу
    const handleSearch = async () => {
      if (!searchQuery.value.trim()) return
      
      isSearching.value = true
      searchError.value = ''
      searchSuccess.value = ''
      
      try {
        console.log('Searching for friend:', searchQuery.value.trim())
        await sendFriendRequest(searchQuery.value.trim())
        searchSuccess.value = 'Запрос на дружбу отправлен!'
        searchQuery.value = ''
        // Обновляем список запросов после отправки
        await loadFriendRequests()
      } catch (err) {
        console.error('Search error:', err)
        searchError.value = err.message || 'Пользователь не найден или произошла ошибка'
      } finally {
        isSearching.value = false
      }
    }

    // Принятие запроса на дружбу
    const acceptRequest = async (requestId) => {
      try {
        await acceptFriendRequest(requestId)
        // Обновляем оба списка после изменения статуса
        await loadFriends()
        await loadFriendRequests()
      } catch (error) {
        console.error('Failed to accept request:', error)
      }
    }

    // Отклонение запроса на дружбу
    const rejectRequest = async (requestId) => {
      try {
        await rejectFriendRequest(requestId)
        // Обновляем список запросов после отклонения
        await loadFriendRequests()
      } catch (error) {
        console.error('Failed to reject request:', error)
      }
    }

    // Получение текста статуса
    const getStatusLabel = (status) => {
      const labels = {
        pending: 'Ожидает',
        accepted: 'Принято',
        rejected: 'Отклонено'
      }
      return labels[status] || status
    }

    // Загрузка данных при монтировании компонента
    onMounted(async () => {
      loading.value = true
      await Promise.all([
        loadFriends(),
        loadFriendRequests()
      ])
      loading.value = false
    })

    return { 
      friends,
      requests,
      loading,
      searchQuery, 
      handleSearch, 
      isSearching, 
      searchError, 
      searchSuccess,
      acceptRequest,
      rejectRequest,
      getStatusLabel
    }
  }
}
</script>

<style scoped>
.friends {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 2rem;
}

.friends h2 {
  margin-bottom: 1rem;
  font-size: clamp(1.2rem, 3vw, 1.5rem);
}

.friends-section, .requests-section {
  margin-bottom: 2rem;
}

.friends-section h3, .requests-section h3 {
  margin-bottom: 1rem;
  color: #00ff88;
  font-size: clamp(1rem, 2.5vw, 1.2rem);
}

.friends-list, .requests-list {
  display: grid;
  gap: 1rem;
}

.friend-item, .request-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  align-items: center;
}

.friend-avatar {
  font-size: 2rem;
}

.friend-info strong {
  color: #00ff88;
  display: block;
  margin-bottom: 0.5rem;
}

.friend-info p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.request-status {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.request-actions {
  display: flex;
  gap: 0.5rem;
}

.button.small {
  padding: 0.3rem 0.6rem;
  font-size: 0.9rem;
}

.no-friends, .no-requests {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.6);
}
</style>

