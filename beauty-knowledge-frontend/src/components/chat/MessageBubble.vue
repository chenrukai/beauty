<template>
  <div :class="['bubble', role]">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ role: 'user' | 'assistant' }>()
</script>

<style scoped>
.bubble { max-width: 85%; padding: 10px 12px; border-radius: 12px; margin: 8px 0; }
.user { margin-left: auto; background: #d1fae5; }
.assistant { margin-right: auto; background: #fff; border: 1px solid #e5e7eb; }
</style>