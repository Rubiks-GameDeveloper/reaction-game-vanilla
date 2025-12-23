<template>
  <div class="difficulty-selection">
    <h2>Выберите уровень сложности</h2>
    <div class="difficulty-options">
      <button 
        class="difficulty-button" 
        @click="$emit('select-difficulty', 'easy')"
      >
        <h3>Легкий</h3>
        <p>Большие цели (60-80px)</p>
        <p>3 секунды на реакцию</p>
        <p>60 секунд игры</p>
      </button>
      <button 
        class="difficulty-button" 
        @click="$emit('select-difficulty', 'medium')"
      >
        <h3>Средний</h3>
        <p>Средние цели (40-60px)</p>
        <p>2 секунды на реакцию</p>
        <p>45 секунд игры</p>
      </button>
      <button 
        class="difficulty-button" 
        @click="$emit('select-difficulty', 'hard')"
      >
        <h3>Сложный</h3>
        <p>Маленькие цели (30-50px)</p>
        <p>1.5 секунды на реакцию</p>
        <p>30 секунд игры</p>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DifficultySelection',
  emits: ['select-difficulty']
}
</script>

