<template>
  <div class="settings-overlay" @click.self="$emit('close')">
    <div class="settings-content">
      <h2>Настройки</h2>
      
      <!-- User Profile Section -->
      <div v-if="user" class="settings-group">
        <h3>Профиль</h3>
        <div class="profile-info">
          <p><strong>Имя пользователя:</strong> {{ user.username }}</p>
          <p v-if="user.email"><strong>Email:</strong> {{ user.email }}</p>
        </div>
      </div>

      <div class="settings-group">
        <h3>Эффекты</h3>
        <label>
          <input 
            type="checkbox" 
            :checked="settings.particleEffects"
            @change="$emit('update-settings', 'particleEffects', $event.target.checked)"
          >
          Частицы при попадании
        </label>
        <label>
          <input 
            type="checkbox" 
            :checked="settings.screenShake"
            @change="$emit('update-settings', 'screenShake', $event.target.checked)"
          >
          Тряска экрана
        </label>
      </div>
      <button @click="$emit('close')" class="button">Закрыть</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  props: {
    settings: {
      type: Object,
      required: true
    },
    user: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'update-settings']
}
</script>

