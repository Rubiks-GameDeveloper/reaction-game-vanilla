<template>
  <div class="settings-overlay" @click.self="$emit('close')">
    <div class="settings-content">
      <h2>Настройки</h2>
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
    }
  },
  emits: ['close', 'update-settings']
}
</script>

