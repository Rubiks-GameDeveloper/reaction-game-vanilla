<template>
  <div class="game-header">
    <h1 class="clickable-title" @click="$emit('go-home')">Игра на реакцию</h1>
    <div class="controls">
      <div v-if="isAuthenticated && user" class="user-info">
        <span class="username clickable-username" @click="$emit('show-profile')">{{ user.username }}</span>
      </div>
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
      <button 
        v-if="!isAuthenticated"
        @click="$emit('show-auth')" 
        class="button"
      >
        Войти
      </button>
      <button 
        v-if="isAuthenticated"
        @click="$emit('logout')" 
        class="button"
      >
        Выйти
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
    },
    isAuthenticated: {
      type: Boolean,
      default: false
    },
    user: {
      type: Object,
      default: null
    }
  },
  emits: ['start-game', 'toggle-settings', 'toggle-mute', 'show-auth', 'logout', 'go-home', 'show-profile']
}
</script>

<style scoped>
.clickable-title {
  cursor: pointer;
  transition: color 0.3s ease;
}

.clickable-title:hover {
  color: #00ff88;
}

.clickable-username {
  cursor: pointer;
  transition: color 0.3s ease;
}

.clickable-username:hover {
  color: #00ff88;
  text-decoration: underline;
}
</style>
