<template>
  <div class="game-area">
    <div
      v-for="target in targets"
      :key="target.id"
      :data-target-id="target.id"
      class="target"
      :class="{ 'hit': target.hit }"
      :style="{
        width: target.size + 'px',
        height: target.size + 'px',
        left: target.left,
        top: target.top,
        background: 'radial-gradient(circle, ' + target.colors.start + ' 0%, ' + target.colors.end + ' 100%)'
      }"
      @click="$emit('hit-target', target)"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'GameArea',
  props: {
    targets: {
      type: Array,
      required: true
    }
  },
  emits: ['hit-target']
}
</script>

