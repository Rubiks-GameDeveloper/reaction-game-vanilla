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

      <KeyboardControls />
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
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import GameHeader from './components/GameHeader.vue'
import DifficultySelection from './components/DifficultySelection.vue'
import GameArea from './components/GameArea.vue'
import GameInfo from './components/GameInfo.vue'
import HighScores from './components/HighScores.vue'
import KeyboardControls from './components/KeyboardControls.vue'
import Settings from './components/Settings.vue'
import AuthModal from './components/AuthModal.vue'
import Achievements from './components/Achievements.vue'
import Friends from './components/Friends.vue'
import { useGame } from './composables/useGame'
import { useSoundManager } from './composables/useSoundManager'
import { useAuth, useGameSessions, useLeaderboard, isAuthenticated, user } from './composables/useApi'

export default {
  name: 'App',
  components: {
    GameHeader,
    DifficultySelection,
    GameArea,
    GameInfo,
    HighScores,
    KeyboardControls,
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

    const soundManager = useSoundManager()
    const { fetchUserProfile, logout: apiLogout } = useAuth()
    const { saveGameSession, loadLatestSession } = useGameSessions()
    const { getLeaderboard } = useLeaderboard()

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

    const handleKeyPress = (e) => {
      if (!e || !e.key) return
      
      switch (e.key.toLowerCase()) {
        case ' ':
          e.preventDefault()
          if (!gameStarted.value && !showDifficultySelection.value) {
            openDifficultySelection()
          }
          break
        case 'm':
          toggleMute()
          break
        case 's':
          toggleSettings()
          break
      }
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
      document.addEventListener('keydown', handleKeyPress)
      
      // Load user profile if authenticated
      if (isAuthenticated.value) {
        await fetchUserProfile()
      }
      
      // Load server leaderboard
      await loadServerLeaderboard()
    })

    onBeforeUnmount(() => {
      cleanupGame()
      document.removeEventListener('keydown', handleKeyPress)
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
      handleAuthSuccess
    }
  }
}
</script>

