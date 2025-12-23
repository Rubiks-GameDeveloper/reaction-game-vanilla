<template>
  <div class="high-scores">
    <h2>Рекорды:</h2>
    <div class="scores-list">
      <div 
        v-for="(score, index) in highScores" 
        :key="index"
        class="score-item"
      >
        <span class="rank">{{ index + 1 }}.</span>
        <span class="difficulty">{{ getDifficultyLabel(score.name) }}</span>
        <span class="points">{{ score.score }} очков</span>
        <span class="reaction-time">{{ score.avgReactionTime }}мс</span>
      </div>
      <div v-if="highScores.length === 0" class="score-item">
        <span>Пока нет рекордов</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HighScores',
  props: {
    highScores: {
      type: Array,
      required: true
    }
  },
  methods: {
    getDifficultyLabel(difficulty) {
      const labels = {
        easy: 'Легкий',
        medium: 'Средний',
        hard: 'Сложный'
      }
      return labels[difficulty] || difficulty
    }
  }
}
</script>

