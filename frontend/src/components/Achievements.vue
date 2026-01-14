<template>
  <div class="achievements">
    <h2>Достижения</h2>
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else class="achievements-list">
      <div 
        v-for="achievement in achievements" 
        :key="achievement.id"
        class="achievement-item"
        :class="{ 'unlocked': isUnlocked(achievement.id) }"
      >
        <div class="achievement-icon">
          <span v-if="achievement.icon">📜</span>
          <span v-else>🏆</span>
        </div>
        <div class="achievement-info">
          <h3>{{ achievement.name }}</h3>
          <p>{{ achievement.description }}</p>
          <div v-if="isUnlocked(achievement.id)" class="unlocked-badge">
            ✓ Разблокировано
          </div>
        </div>
      </div>
      <div v-if="achievements.length === 0" class="no-achievements">
        Пока нет достижений
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAchievements } from '../composables/useApi'

export default {
  name: 'Achievements',
  setup() {
    const { getAchievements, getUserAchievements } = useAchievements()
    const achievements = ref([])
    const userAchievements = ref([])
    const loading = ref(false)

    const loadAchievements = async () => {
      loading.value = true
      try {
        const [allAchievements, userAch] = await Promise.all([
          getAchievements(),
          getUserAchievements()
        ])
        achievements.value = Array.isArray(allAchievements) ? allAchievements : []
        userAchievements.value = Array.isArray(userAch) ? userAch : []
      } catch (error) {
        console.error('Failed to load achievements:', error)
        achievements.value = []
      } finally {
        loading.value = false
      }
    }

    const isUnlocked = (achievementId) => {
      return userAchievements.value.some(ua => ua.achievement?.id === achievementId || ua.achievement === achievementId)
    }

    onMounted(() => {
      loadAchievements()
    })

    return {
      achievements,
      userAchievements,
      loading,
      isUnlocked
    }
  }
}
</script>

<style scoped>
.achievements {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 2rem;
}

.achievements h2 {
  margin-bottom: 1rem;
  font-size: clamp(1.2rem, 3vw, 1.5rem);
}

.achievements-list {
  display: grid;
  gap: 1rem;
}

.achievement-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  align-items: center;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.achievement-item.unlocked {
  opacity: 1;
  background: rgba(0, 255, 136, 0.1);
  border-left: 3px solid #00ff88;
}

.achievement-icon {
  font-size: 2rem;
}

.achievement-info h3 {
  margin-bottom: 0.5rem;
  color: #00ff88;
}

.achievement-info p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.unlocked-badge {
  color: #00ff88;
  font-weight: bold;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.achievement-points {
  color: #ffff44;
  font-weight: bold;
}

.no-achievements {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.6);
}
</style>

