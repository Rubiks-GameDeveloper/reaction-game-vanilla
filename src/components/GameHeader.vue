<template>
  <div class="game-header">
    <h1>Игра на реакцию</h1>
    <div class="controls">
      <button 
        v-if="!gameStarted && !showDifficultySelection" 
        @click="$emit('start-game')" 
        class="button"
      >
        Начать игру
      </button>
      <button @click="$emit('toggle-settings')" class="button">Настройки</button>
      <button 
        v-if="gameStarted || showDifficultySelection"
        @click="$emit('toggle-mute')" 
        class="button"
      >
        {{ soundEnabled ? '🔊' : '🔇' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GameHeader',
  props: {
    gameStarted: {
      type: Boolean,
      required: true
    },
    showDifficultySelection: {
      type: Boolean,
      required: true
    },
    soundEnabled: {
      type: Boolean,
      required: true
    }
  },
  emits: ['start-game', 'toggle-settings', 'toggle-mute']
}
</script>

