<template>
  <div class="game-container">
    <GameHeader 
      :game-started="gameStarted"
      :show-difficulty-selection="showDifficultySelection"
      :sound-enabled="settings.soundEnabled"
      @start-game="openDifficultySelection"
      @toggle-settings="toggleSettings"
      @toggle-mute="toggleMute"
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

      <HighScores :high-scores="highScores" />

      <KeyboardControls />
    </div>

    <Settings
      v-if="showSettings"
      :settings="settings"
      @close="toggleSettings"
      @update-settings="updateSettings"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import GameHeader from './components/GameHeader.vue'
import DifficultySelection from './components/DifficultySelection.vue'
import GameArea from './components/GameArea.vue'
import GameInfo from './components/GameInfo.vue'
import HighScores from './components/HighScores.vue'
import KeyboardControls from './components/KeyboardControls.vue'
import Settings from './components/Settings.vue'
import { useGame } from './composables/useGame'
import { useSoundManager } from './composables/useSoundManager'

export default {
  name: 'App',
  components: {
    GameHeader,
    DifficultySelection,
    GameArea,
    GameInfo,
    HighScores,
    KeyboardControls,
    Settings
  },
  setup() {
    const showDifficultySelection = ref(false)
    const showSettings = ref(false)
    const showGameArea = ref(false)
    const showGameInfo = ref(false)
    const currentReactionTime = ref(null)

    const soundManager = useSoundManager()

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
        setTimeout(() => {
          currentReactionTime.value = null
        }, 2000)
      }
    }

    const exitGame = () => {
      endGameLogic()
      showGameArea.value = false
      showGameInfo.value = false
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

    const handleKeyPress = (e) => {
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

    onMounted(() => {
      loadHighScores()
      loadSettings()
      document.addEventListener('keydown', handleKeyPress)
    })

    onBeforeUnmount(() => {
      cleanupGame()
      document.removeEventListener('keydown', handleKeyPress)
    })

    return {
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
      openDifficultySelection,
      selectDifficulty,
      startGame,
      hitTarget,
      exitGame,
      toggleSettings,
      toggleMute,
      updateSettings
    }
  }
}
</script>

