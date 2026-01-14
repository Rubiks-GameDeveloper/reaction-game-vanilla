<template>
  <div class="friends-container">
    <h2>Друзья</h2>

    <!-- Tabs Navigation -->
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'friends' }" 
        @click="activeTab = 'friends'"
      >Мои друзья</button>
      <button 
        :class="{ active: activeTab === 'search' }" 
        @click="activeTab = 'search'"
      >Поиск</button>
      <button 
        :class="{ active: activeTab === 'incoming' }" 
        @click="activeTab = 'incoming'"
      >Входящие <span v-if="incomingRequests.length" class="badge">{{ incomingRequests.length }}</span></button>
      <button 
        :class="{ active: activeTab === 'sent' }" 
        @click="activeTab = 'sent'"
      >Исходящие</button>
      <button 
        :class="{ active: activeTab === 'archive' }" 
        @click="activeTab = 'archive'"
      >Архив</button>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else class="tab-content">
      
      <!-- TAB: FRIENDS -->
      <div v-if="activeTab === 'friends'" class="friends-list">
        <h3>Список друзей</h3>
        <div v-if="friends.length > 0" class="list-grid">
          <div v-for="friend in friends" :key="friend.id" class="friend-card" @click="openProfile(friend)">
            <div class="info">
              <span class="username">{{ friend.username }}</span>
              <span class="status-text">Нажмите для просмотра профиля</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">У вас пока нет друзей. Найдите их во вкладке "Поиск"!</div>
      </div>

      <!-- TAB: INCOMING REQUESTS -->
      <div v-if="activeTab === 'incoming'" class="requests-list">
        <h3>Входящие запросы</h3>
        <div v-if="incomingRequests.length > 0" class="list-grid">
          <div v-for="req in incomingRequests" :key="req.id" class="request-card">
            <div class="info">
              <span class="username">{{ req.from_username }}</span>
              <span class="date">{{ formatDate(req.created_at) }}</span>
            </div>
            <div class="actions">
              <button @click="handleAccept(req.id)" class="btn-accept">Принять</button>
              <button @click="handleReject(req.id)" class="btn-reject">Отклонить</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">Нет новых запросов.</div>
      </div>

      <!-- TAB: SENT REQUESTS -->
      <div v-if="activeTab === 'sent'" class="requests-list">
        <h3>Отправленные запросы</h3>
        <div v-if="sentRequests.length > 0" class="list-grid">
          <div v-for="req in sentRequests" :key="req.id" class="request-card">
            <div class="info">
              <span class="username">{{ req.to_username }}</span>
              <span class="status-text">Ожидает подтверждения</span>
            </div>
            <div class="actions">
              <button @click="handleCancel(req.id)" class="btn-cancel">Отменить</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">Нет отправленных запросов.</div>
      </div>

       <!-- TAB: ARCHIVE -->
      <div v-if="activeTab === 'archive'" class="requests-list">
        <h3>Архив запросов</h3>
        <div v-if="archivedRequests.length > 0" class="list-grid">
          <div v-for="req in archivedRequests" :key="req.id" class="request-card archive-card">
            <div class="info">
              <!-- Show who was the other party -->
              <span class="username">
                {{ req.from_username === currentUser?.username ? req.to_username : req.from_username }}
              </span>
              <span class="status-badge rejected">Отклонено</span>
            </div>
            <div class="meta">
              {{ req.from_username === currentUser?.username ? 'Исходящий' : 'Входящий' }}
            </div>
          </div>
        </div>
        <div v-else class="empty-state">Архив пуст.</div>
      </div>

      <!-- TAB: SEARCH -->
      <div v-if="activeTab === 'search'" class="search-section">
        <h3>Поиск игроков</h3>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Введите имя пользователя..." 
          class="search-input"
          @input="handleSearchInput"
        >
        
        <div v-if="isSearching" class="loading-small">Поиск...</div>
        
        <div v-if="searchResults.length > 0" class="search-results">
          <div v-for="user in searchResults" :key="user.id" class="result-card">
            <span class="username">{{ user.username }}</span>
            <button @click="handleSendRequest(user.username)" class="btn-add">Добавить</button>
          </div>
        </div>
        <div v-else-if="searchQuery.length >= 2 && !isSearching" class="empty-search">
           Пользователи не найдены
        </div>
      </div>

    </div>

    <!-- FRIEND PROFILE MODAL -->
    <div v-if="showProfileModal && selectedFriend" class="modal-overlay" @click.self="closeProfile">
      <div class="modal-content profile-modal">
        <button class="close-btn" @click="closeProfile">&times;</button>
        
        <div v-if="loadingProfile" class="loading">Загрузка профиля...</div>
        <div v-else class="profile-details">
          <div class="profile-header">
            <div class="header-info">
              <h2>{{ selectedFriend.username }}</h2>
              <p class="date">На сайте с: {{ formatDate(selectedFriend.date_joined) }}</p>
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-item">
              <span class="label">Игр сыграно</span>
              <span class="value">{{ selectedFriend.games_played }}</span>
            </div>
            <div class="stat-item">
              <span class="label">Средняя реакция</span>
              <span class="value">{{ selectedFriend.avg_reaction_time ? Math.round(selectedFriend.avg_reaction_time) + ' мс' : '-' }}</span>
            </div>
          </div>

          <h4>Лучшие результаты</h4>
          <div class="high-scores-list">
             <div v-for="(score, diff) in selectedFriend.high_scores" :key="diff" class="score-row">
               <span class="diff-label">{{ translateDifficulty(diff) }}:</span>
               <span class="score-value">{{ score }}</span>
             </div>
             <div v-if="Object.keys(selectedFriend.high_scores).length === 0">Нет рекордов</div>
          </div>

          <h4>Достижения</h4>
          <div class="achievements-list">
            <div v-for="ach in selectedFriend.achievements" :key="ach.id" class="achievement-badge" :title="ach.description">
              <span>🏆 {{ ach.name }}</span>
            </div>
            <div v-if="!selectedFriend.achievements?.length">Нет достижений</div>
          </div>
        </div>
      </div>
    </div>

    <!-- NOTIFICATIONS -->
    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>

  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useFriends, useAuth } from '../composables/useApi'

export default {
  setup() {
    const { 
      getFriends, getIncomingRequests, getSentRequests, getArchivedRequests,
      searchUsers, sendFriendRequest, acceptFriendRequest, rejectFriendRequest, cancelFriendRequest,
      getFriendProfile 
    } = useFriends()
    
    const { user: currentUser } = useAuth()

    const activeTab = ref('friends')
    const loading = ref(false)
    
    // Lists
    const friends = ref([])
    const incomingRequests = ref([])
    const sentRequests = ref([])
    const archivedRequests = ref([])
    
    // Search
    const searchQuery = ref('')
    const searchResults = ref([])
    const isSearching = ref(false)
    let searchTimeout = null

    // Profile Modal
    const showProfileModal = ref(false)
    const selectedFriend = ref(null)
    const loadingProfile = ref(false)

    // Notification
    const notification = ref(null)

    const showNotification = (msg, type = 'success') => {
      notification.value = { message: msg, type }
      setTimeout(() => notification.value = null, 3000)
    }

    const loadAllData = async () => {
      loading.value = true
      try {
        const [f, i, s, a] = await Promise.all([
           getFriends(),
           getIncomingRequests(),
           getSentRequests(),
           getArchivedRequests()
        ])
        friends.value = f || []
        incomingRequests.value = i || []
        sentRequests.value = s || []
        archivedRequests.value = a || []
      } catch (e) {
        console.error(e)
        showNotification('Ошибка загрузки данных', 'error')
      } finally {
        loading.value = false
      }
    }

    // Call loadAllData whenever tab changes to keep fresh, or just on mount
    // Better to refresh when switching TABS to relevant data, but loadAll covers everything simple.
    
    watch(activeTab, () => {
       if (activeTab.value !== 'search') {
          loadAllData()
       }
    })

    const handleSearchInput = () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      if (searchQuery.value.length < 2) {
        searchResults.value = []
        return
      }
      
      isSearching.value = true
      searchTimeout = setTimeout(async () => {
        try {
          const res = await searchUsers(searchQuery.value)
          searchResults.value = res || []
        } catch (e) {
          console.error(e)
        } finally {
          isSearching.value = false
        }
      }, 500) // Debounce 500ms
    }

    const handleSendRequest = async (username) => {
      try {
        await sendFriendRequest(username)
        showNotification(`Запрос отправлен пользователю ${username}`)
        // Remove from search results to prevent double send
        searchResults.value = searchResults.value.filter(u => u.username !== username)
        // Refresh sent list silently
        getSentRequests().then(res => sentRequests.value = res)
      } catch (e) {
        showNotification(e.message || 'Ошибка отправки запроса', 'error')
      }
    }

    const handleAccept = async (id) => {
      try {
        await acceptFriendRequest(id)
        showNotification('Заявка принята!')
        loadAllData()
      } catch (e) {
        showNotification('Ошибка принятия заявки', 'error')
      }
    }

    const handleReject = async (id) => {
      try {
        await rejectFriendRequest(id)
        showNotification('Заявка отклонена')
        loadAllData()
      } catch (e) {
        showNotification('Ошибка отклонения', 'error')
      }
    }

    const handleCancel = async (id) => {
      try {
        await cancelFriendRequest(id)
        showNotification('Заявка отменена')
        loadAllData()
      } catch (e) {
        showNotification('Ошибка отмены', 'error')
      }
    }

    const openProfile = async (friend) => {
      selectedFriend.value = null
      showProfileModal.value = true
      loadingProfile.value = true
      try {
        // friend object from list has some basics, but we fetch full profile for stats
        // friend.id is user ID from serializer
        const data = await getFriendProfile(friend.id)
        selectedFriend.value = data
      } catch (e) {
        showNotification('Не удалось загрузить профиль', 'error')
        showProfileModal.value = false
      } finally {
        loadingProfile.value = false
      }
    }

    const closeProfile = () => {
      showProfileModal.value = false
      selectedFriend.value = null
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('ru-RU')
    }

    const translateDifficulty = (diff) => {
      const map = { 'easy': 'Легкий', 'medium': 'Средний', 'hard': 'Сложный' }
      return map[diff] || diff
    }

    onMounted(() => {
      loadAllData()
    })

    return {
      activeTab,
      friends, incomingRequests, sentRequests, archivedRequests,
      loading, currentUser,
      searchQuery, searchResults, isSearching, handleSearchInput,
      handleSendRequest, handleAccept, handleReject, handleCancel,
      showProfileModal, selectedFriend, loadingProfile, openProfile, closeProfile,
      notification, formatDate, translateDifficulty
    }
  }
}
</script>

<style scoped>
.friends-container {
  background: rgba(0, 0, 0, 0.4);
  padding: 20px;
  border-radius: 12px;
  color: #fff;
  min-height: 400px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tabs button {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 20px;
  transition: all 0.3s;
}

.tabs button.active {
  background: #00ff88;
  color: #000;
  border-color: #00ff88;
  font-weight: bold;
}

.badge {
  background: #ff4444;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.8em;
  margin-left: 5px;
}

.list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.friend-card, .request-card {
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: transform 0.2s;
}

.friend-card {
  cursor: pointer;
}
.friend-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background: #333;
}

.info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.username {
  font-weight: bold;
  font-size: 1.1em;
  color: #00ff88;
}

.status-text {
  font-size: 0.85em;
  color: rgba(255, 255, 255, 0.5);
}

.date {
  font-size: 0.8em;
  color: #888;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-accept, .btn-reject, .btn-cancel, .btn-add {
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: opacity 0.2s;
}

.btn-accept, .btn-add {
  background: #00ff88;
  color: black;
}

.btn-reject, .btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-accept:hover, .btn-add:hover {
  opacity: 0.9;
}
.btn-reject:hover, .btn-cancel:hover {
  background: rgba(255, 255, 255, 0.2);
}

.archive-card {
  opacity: 0.7;
}

.status-badge.rejected {
  color: #ff4444;
  font-size: 0.9em;
}

.meta {
  font-size: 0.8em;
  color: #666;
}

.search-input {
  width: 100%;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: white;
  font-size: 1em;
  margin-bottom: 20px;
}

.search-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.result-card {
  background: rgba(255, 255, 255, 0.05);
  padding: 10px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.empty-state, .empty-search {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.4);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: #222;
  padding: 30px;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  position: relative;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 24px;
  color: #888;
  cursor: pointer;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #00ff88;
}

.header-info h2 {
  color: #00ff88;
  margin: 0;
}

.bio {
  font-style: italic;
  color: #aaa;
  margin: 5px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 25px;
}

.stat-item {
  background: rgba(0, 255, 136, 0.05);
  padding: 10px;
  border-radius: 8px;
  text-align: center;
}

.stat-item .label {
  display: block;
  font-size: 0.85em;
  color: #888;
}

.stat-item .value {
  display: block;
  font-size: 1.2em;
  font-weight: bold;
  color: #fff;
}

.high-scores-list, .achievements-list {
  background: rgba(255, 255, 255, 0.03);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.score-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.score-row:last-child {
  border: none;
}

.achievement-badge {
  display: inline-block;
  background: rgba(255, 215, 0, 0.1);
  color: #ffd700;
  padding: 4px 8px;
  border-radius: 4px;
  margin: 4px;
  font-size: 0.9em;
}

.notification {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  animation: slideUp 0.3s ease;
  z-index: 2000;
}

.notification.success {
  background: #00ff88;
  color: black;
}

.notification.error {
  background: #ff4444;
  color: white;
}

@keyframes slideUp {
  from { transform: translate(-50%, 20px); opacity: 0; }
  to { transform: translate(-50%, 0); opacity: 1; }
}
</style>
