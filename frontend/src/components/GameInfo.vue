<template>
  <div class="game-info">
    <div class="game-controls">
      <div class="game-buttons">
        <button @click="$emit('exit-game')" class="control-button">Выйти</button>
      </div>
    </div>
    <div class="score">Счёт: {{ score }}</div>
    <div class="timer">Время: {{ timeLeft }}</div>
    <div v-if="reactionTime" class="reaction-time">
      Время реакции: {{ reactionTime }}мс
    </div>
  </div>
</template>

<script>
export default {
  name: 'GameInfo',
  props: {
    score: {
      type: Number,
      required: true
    },
    timeLeft: {
      type: Number,
      required: true
    },
    reactionTime: {
      type: Number,
      default: null
    }
  },
  emits: ['exit-game']
}
</script>

