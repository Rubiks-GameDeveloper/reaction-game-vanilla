<template>
  <div class="high-scores">
    <h2>Рекорды:</h2>
    <div v-if="loadingLeaderboard" class="loading">Загрузка...</div>
    <div v-else class="scores-list">
      <!-- Server leaderboard -->
      <div v-if="serverLeaderboard && serverLeaderboard.length > 0" class="scores-section">
        <h3>Глобальная таблица лидеров</h3>
        <div class="score-grid header">
          <span>№</span>
          <span>Игрок</span>
          <span>Уровень</span>
          <span>Очки</span>
          <span>Реакция</span>
          <span>Дата</span>
        </div>
        <div 
          v-for="(entry, index) in serverLeaderboard" 
          :key="'server-' + entry.id"
          class="score-grid item server-item"
        >
          <span class="rank">{{ entry.rank || index + 1 }}</span>
          <span class="username">{{ entry.username }}</span>
          <span class="difficulty">{{ getDifficultyLabel(entry.difficulty) }}</span>
          <span class="points">{{ entry.score }}</span>
          <span class="reaction-time">{{ Math.round(entry.avg_reaction_time) }}мс</span>
          <span class="date">{{ formatDate(entry.date_achieved) }}</span>
        </div>
      </div>

      <!-- Локальные рекорды -->
      <div v-if="highScores && highScores.length > 0" class="scores-section">
        <h3>Ваши локальные рекорды</h3>
        <div class="score-grid local-header">
          <span>№</span>
          <span>Уровень</span>
          <span>Очки</span>
          <span>Реакция</span>
        </div>
        <div 
          v-for="(score, index) in highScores" 
          :key="'local-' + index"
          class="score-grid item"
        >
          <span class="rank">{{ index + 1 }}</span>
          <span class="difficulty">{{ getDifficultyLabel(score.name) }}</span>
          <span class="points">{{ score.score }}</span>
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
  props: ['highScores', 'serverLeaderboard', 'loadingLeaderboard'],
  methods: {
    getDifficultyLabel(d) {
      return {easy:'Легкий', medium:'Средний', hard:'Сложный'}[d] || d;
    },
    formatDate(dateStr) {
      if (!dateStr) return '-';
      const d = new Date(dateStr);
      return d.toLocaleDateString('ru-RU', {day:'2-digit', month:'2-digit'});
    }
  }
}
</script>

