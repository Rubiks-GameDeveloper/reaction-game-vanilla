<template>
  <div class="friends">
    <h2>Друзья</h2>
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else>
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
  name: 'Friends',
  setup() {
    const { getFriends, getFriendRequests, acceptFriendRequest, rejectFriendRequest } = useFriends()
    const friends = ref([])
    const requests = ref([])
    const loading = ref(false)

    const loadFriends = async () => {
      loading.value = true
      try {
        const [friendsData, requestsData] = await Promise.all([
          getFriends(),
          getFriendRequests()
        ])
        friends.value = Array.isArray(friendsData) ? friendsData : []
        requests.value = Array.isArray(requestsData) ? requestsData : []
      } catch (error) {
        console.error('Failed to load friends:', error)
        friends.value = []
        requests.value = []
      } finally {
        loading.value = false
      }
    }

    const acceptRequest = async (requestId) => {
      try {
        await acceptFriendRequest(requestId)
        await loadFriends()
      } catch (error) {
        console.error('Failed to accept request:', error)
      }
    }

    const rejectRequest = async (requestId) => {
      try {
        await rejectFriendRequest(requestId)
        await loadFriends()
      } catch (error) {
        console.error('Failed to reject request:', error)
      }
    }

    const getStatusLabel = (status) => {
      const labels = {
        pending: 'Ожидает',
        accepted: 'Принято',
        rejected: 'Отклонено'
      }
      return labels[status] || status
    }

    onMounted(() => {
      loadFriends()
    })

    return {
      friends,
      requests,
      loading,
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

