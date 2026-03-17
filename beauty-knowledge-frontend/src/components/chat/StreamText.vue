<template>
  <div class="stream-text">{{ text }}</div>
</template>

<script setup lang="ts">
defineProps<{ text: string }>()
</script>

<style scoped>
.stream-text { white-space: pre-wrap; line-height: 1.7; }
</style>