<template>
  <div class="game-container">
    <GameHeader 
      :game-started="gameStarted"
      :show-difficulty-selection="showDifficultySelection"
      :sound-enabled="settings.soundEnabled"
      :is-authenticated="isAuthenticated"
      :user="user"
      @start-game="openDifficultySelection"
      @toggle-settings="toggleSettings"
      @toggle-mute="toggleMute"
      @show-auth="showAuthModal = true"
      @logout="handleLogout"
      @go-home="goHome"
      @show-profile="showMyProfile"
    />

    <div class="game-content">
      <DifficultySelection
        v-if="showDifficultySelection"
        @select-difficulty="selectDifficulty"
      />

      <GameArea
        v-if="showGameArea"
        :targets="targets"
        @hit-target="hitTarget"
      />

      <GameInfo
        v-if="showGameInfo"
        :score="score"
        :time-left="timeLeft"
        :reaction-time="currentReactionTime"
        @exit-game="exitGame"
      />

      <!-- Внутри <div class="game-content"> -->
      <div v-if="!showGameArea && !showDifficultySelection" class="game-menu">
      <!-- Вкладки появляются только для авторизованных пользователей -->
        <div v-if="isAuthenticated" class="tabs">
          <button 
            :class="{ active: activeTab === 'scores' }" 
            @click="activeTab = 'scores'"
          >Рекорды</button>
          <button 
            :class="{ active: activeTab === 'achievements' }" 
            @click="activeTab = 'achievements'"
          > Достижения </button>
          <button 
            :class="{ active: activeTab === 'friends' }" 
            @click="activeTab = 'friends'"
          > Друзья </button>
        </div>

      <!-- Контент вкладок -->
      <HighScores 
        v-if="activeTab === 'scores'"
        :high-scores="highScores" 
        :server-leaderboard="serverLeaderboard"
        :loading-leaderboard="loadingLeaderboard"
      />

      <Achievements 
        v-if="isAuthenticated && activeTab === 'achievements'" 
      />

      <Friends 
        v-if="isAuthenticated && activeTab === 'friends'" 
      />
    </div>
    </div>

    <Settings
      v-if="showSettings"
      :settings="settings"
      :user="user"
      @close="toggleSettings"
      @update-settings="updateSettings"
    />

    <AuthModal
      :show="showAuthModal"
      @close="showAuthModal = false"
      @success="handleAuthSuccess"
    />

    <!-- User Profile Modal -->
    <div v-if="showUserProfileModal && userProfileData" class="modal-overlay" @click.self="closeUserProfile">
      <div class="modal-content profile-modal">
        <button class="close-btn" @click="closeUserProfile">&times;</button>
        
        <div v-if="loadingUserProfile" class="loading">Загрузка профиля...</div>
        <div v-else class="profile-details">
          <div class="profile-header">
            <div class="header-info">
              <h2>{{ userProfileData.username }}</h2>
              <p class="date">На сайте с: {{ formatDate(userProfileData.date_joined) }}</p>
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-item">
              <span class="label">Игр сыграно</span>
              <span class="value">{{ userProfileData.games_played }}</span>
            </div>
            <div class="stat-item">
              <span class="label">Средняя реакция</span>
              <span class="value">{{ userProfileData.avg_reaction_time ? Math.round(userProfileData.avg_reaction_time) + ' мс' : '-' }}</span>
            </div>
          </div>

          <h4>Лучшие результаты</h4>
          <div class="high-scores-list">
            <div v-for="(score, diff) in userProfileData.high_scores" :key="diff" class="score-row">
              <span class="diff-label">{{ translateDifficulty(diff) }}:</span>
              <span class="score-value">{{ score }}</span>
            </div>
            <div v-if="Object.keys(userProfileData.high_scores || {}).length === 0">Нет рекордов</div>
          </div>

          <h4>Достижения</h4>
          <div class="achievements-list">
            <div v-for="ach in userProfileData.achievements" :key="ach.id" class="achievement-badge" :title="ach.description">
              <span>🏆 {{ ach.name }}</span>
            </div>
            <div v-if="!userProfileData.achievements?.length">Нет достижений</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import GameHeader from './components/GameHeader.vue'
import DifficultySelection from './components/DifficultySelection.vue'
import GameArea from './components/GameArea.vue'
import GameInfo from './components/GameInfo.vue'
import HighScores from './components/HighScores.vue'
import Settings from './components/Settings.vue'
import AuthModal from './components/AuthModal.vue'
import Achievements from './components/Achievements.vue'
import Friends from './components/Friends.vue'
import { useGame } from './composables/useGame'
import { useSoundManager } from './composables/useSoundManager'
import { useAuth, useGameSessions, useLeaderboard, useFriends, isAuthenticated, user } from './composables/useApi'

export default {
  name: 'App',
  components: {
    GameHeader,
    DifficultySelection,
    GameArea,
    GameInfo,
    HighScores,
    Settings,
    AuthModal,
    Achievements,
    Friends
  },
  setup() {
    const activeTab = ref('scores');
    const showDifficultySelection = ref(false)
    const showSettings = ref(false)
    const showGameArea = ref(false)
    const showGameInfo = ref(false)
    const currentReactionTime = ref(null)
    const showAuthModal = ref(false)
    const serverLeaderboard = ref([])
    const loadingLeaderboard = ref(false)
    const showUserProfileModal = ref(false)
    const userProfileData = ref(null)
    const loadingUserProfile = ref(false)

    const soundManager = useSoundManager()
    const { fetchUserProfile, logout: apiLogout } = useAuth()
    const { saveGameSession, loadLatestSession } = useGameSessions()
    const { getLeaderboard } = useLeaderboard()
    const { getFriendProfile } = useFriends()

    const {
      gameStarted,
      score,
      timeLeft,
      targets,
      reactionTimes,
      highScores,
      settings,
      difficultyLevels,
      startGame: startGameLogic,
      hitTarget: hitTargetLogic,
      endGame: endGameLogic,
      cleanup: cleanupGame,
      loadHighScores,
      loadSettings,
      saveSettings,
      addHighScore
    } = useGame(soundManager)

    const openDifficultySelection = () => {
      showDifficultySelection.value = true
    }

    const selectDifficulty = (difficulty) => {
      settings.value.difficulty = difficulty
      startGame()
    }

    const startGame = () => {
      startGameLogic()
      showDifficultySelection.value = false
      showGameArea.value = true
      showGameInfo.value = true
    }

    const hitTarget = (target) => {
      const reactionTime = hitTargetLogic(target)
      if (reactionTime) {
        currentReactionTime.value = reactionTime
        // Time reaction will stay until next hit or game ends
      }
    }

    const exitGame = async () => {
      // Save game session to backend if authenticated
      if (isAuthenticated.value && gameStarted.value) {
        try {
          await saveGameSession({
            gameState: {},
            score: score.value,
            difficulty: settings.value.difficulty,
            timePlayed: difficultyLevels[settings.value.difficulty].gameTime - timeLeft.value,
            isCompleted: timeLeft.value <= 0,
            reactionTimes: reactionTimes.value
          })
          // Reload leaderboard after saving
          await loadServerLeaderboard()
        } catch (error) {
          console.error('Failed to save game session:', error)
        }
      }

      endGameLogic()
      showGameArea.value = false
      showGameInfo.value = false
      currentReactionTime.value = null
    }

    const toggleSettings = () => {
      showSettings.value = !showSettings.value
    }

    const toggleMute = () => {
      settings.value.soundEnabled = !settings.value.soundEnabled
      saveSettings()
      
      if (settings.value.soundEnabled) {
        soundManager.setMuted(false)
        if (gameStarted.value) {
          soundManager.startBackgroundMusic()
        }
      } else {
        soundManager.setMuted(true)
        soundManager.pauseBackgroundMusic()
      }
    }

    const updateSettings = (key, value) => {
      settings.value[key] = value
      saveSettings()
    }

    const loadServerLeaderboard = async () => {
      loadingLeaderboard.value = true
      try {
        const data = await getLeaderboard(null, 10)
        serverLeaderboard.value = Array.isArray(data) ? data : []
      } catch (error) {
        console.error('Failed to load leaderboard:', error)
        serverLeaderboard.value = []
      } finally {
        loadingLeaderboard.value = false
      }
    }

    const handleLogout = () => {
      apiLogout()
      showAuthModal.value = false
      serverLeaderboard.value = []
      // Возвращаем пользователя в главное меню (вкладка "Рекорды")
      activeTab.value = 'scores'
    }

    const handleAuthSuccess = async () => {
      await fetchUserProfile()
      await loadServerLeaderboard()
    }

    const goHome = () => {
      if (gameStarted.value || showGameArea.value || showDifficultySelection.value) {
        exitGame()
      }
      activeTab.value = 'scores'
      showDifficultySelection.value = false
      showGameArea.value = false
      showGameInfo.value = false
    }

    const showMyProfile = async () => {
      if (!isAuthenticated.value || !user.value) return
      
      showUserProfileModal.value = true
      loadingUserProfile.value = true
      userProfileData.value = null
      
      try {
        const data = await getFriendProfile(user.value.id)
        userProfileData.value = data
      } catch (e) {
        console.error('Failed to load profile:', e)
        showUserProfileModal.value = false
      } finally {
        loadingUserProfile.value = false
      }
    }

    const closeUserProfile = () => {
      showUserProfileModal.value = false
      userProfileData.value = null
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('ru-RU')
    }

    const translateDifficulty = (diff) => {
      const map = { 'easy': 'Легкий', 'medium': 'Средний', 'hard': 'Сложный' }
      return map[diff] || diff
    }

    // Watch for automatic game end (when timer reaches 0)
    watch(gameStarted, async (newValue) => {
      if (!newValue && (showGameArea.value || showGameInfo.value)) {
        // Save game session if authenticated
        if (isAuthenticated.value) {
          try {
            await saveGameSession({
              gameState: {},
              score: score.value,
              difficulty: settings.value.difficulty,
              timePlayed: difficultyLevels[settings.value.difficulty].gameTime,
              isCompleted: true,
              reactionTimes: reactionTimes.value
            })
            await loadServerLeaderboard()
          } catch (error) {
            console.error('Failed to save game session:', error)
          }
        }
        
        // Game ended automatically, hide game UI
        showGameArea.value = false
        showGameInfo.value = false
        currentReactionTime.value = null
      }
    })

    onMounted(async () => {
      loadHighScores()
      loadSettings()
      
      // Load user profile if authenticated
      if (isAuthenticated.value) {
        await fetchUserProfile()
      }
      
      // Load server leaderboard
      await loadServerLeaderboard()
    })

    onBeforeUnmount(() => {
      cleanupGame()
    })

    return {
      activeTab,
      gameStarted,
      score,
      timeLeft,
      targets,
      reactionTimes,
      highScores,
      settings,
      showDifficultySelection,
      showSettings,
      showGameArea,
      showGameInfo,
      currentReactionTime,
      showAuthModal,
      isAuthenticated,
      user,
      serverLeaderboard,
      loadingLeaderboard,
      openDifficultySelection,
      selectDifficulty,
      startGame,
      hitTarget,
      exitGame,
      toggleSettings,
      toggleMute,
      updateSettings,
      handleLogout,
      handleAuthSuccess,
      goHome,
      showMyProfile,
      showUserProfileModal,
      userProfileData,
      loadingUserProfile,
      closeUserProfile,
      formatDate,
      translateDifficulty
    }
  }
}
</script>

<style scoped>
/* Profile Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
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
  transition: color 0.3s;
}

.close-btn:hover {
  color: #fff;
}

.profile-header {
  margin-bottom: 30px;
}

.header-info h2 {
  color: #00ff88;
  margin: 0 0 10px 0;
}

.bio {
  font-style: italic;
  color: #aaa;
  margin: 5px 0;
}

.date {
  font-size: 0.9em;
  color: #888;
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
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat-item .label {
  display: block;
  font-size: 0.85em;
  color: #888;
  margin-bottom: 5px;
}

.stat-item .value {
  display: block;
  font-size: 1.4em;
  font-weight: bold;
  color: #00ff88;
}

.profile-details h4 {
  color: #00ff88;
  margin: 20px 0 10px 0;
}

.high-scores-list,
.achievements-list {
  background: rgba(255, 255, 255, 0.03);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.score-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.score-row:last-child {
  border: none;
}

.diff-label {
  color: #aaa;
}

.score-value {
  color: #00ff88;
  font-weight: bold;
}

.achievement-badge {
  display: inline-block;
  background: rgba(255, 215, 0, 0.1);
  color: #ffd700;
  padding: 6px 12px;
  border-radius: 6px;
  margin: 4px;
  font-size: 0.9em;
  border: 1px solid rgba(255, 215, 0, 0.3);
}

.loading {
  text-align: center;
  padding: 40px;
  color: #00ff88;
  font-size: 1.1em;
}
</style>
