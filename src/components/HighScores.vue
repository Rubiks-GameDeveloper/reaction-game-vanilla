<template>
  <div class="high-scores">
    <h2>Рекорды:</h2>
    <div v-if="loadingLeaderboard" class="loading">Загрузка...</div>
    <div v-else class="scores-list">
      <!-- Server leaderboard -->
      <div v-if="serverLeaderboard && serverLeaderboard.length > 0" class="server-scores">
        <h3>Глобальная таблица лидеров</h3>
        <div 
          v-for="(entry, index) in serverLeaderboard" 
          :key="'server-' + entry.id"
          class="score-item server-item"
        >
          <span class="rank">{{ entry.rank || index + 1 }}.</span>
          <span class="username">{{ entry.username }}</span>
          <span class="difficulty">{{ getDifficultyLabel(entry.difficulty) }}</span>
          <span class="points">{{ entry.score }} очков</span>
          <span v-if="entry.avg_reaction_time" class="reaction-time">
            {{ Math.round(entry.avg_reaction_time) }}мс
          </span>
        </div>
      </div>

      <!-- Local high scores -->
      <div v-if="highScores && highScores.length > 0" class="local-scores">
        <h3>Локальные рекорды</h3>
        <div 
          v-for="(score, index) in highScores" 
          :key="'local-' + index"
          class="score-item"
        >
          <span class="rank">{{ index + 1 }}.</span>
          <span class="difficulty">{{ getDifficultyLabel(score.name) }}</span>
          <span class="points">{{ score.score }} очков</span>
          <span class="reaction-time">{{ score.avgReactionTime }}мс</span>
        </div>
      </div>

      <div v-if="(!highScores || highScores.length === 0) && (!serverLeaderboard || serverLeaderboard.length === 0)" class="score-item">
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
    },
    serverLeaderboard: {
      type: Array,
      default: () => []
    },
    loadingLeaderboard: {
      type: Boolean,
      default: false
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

