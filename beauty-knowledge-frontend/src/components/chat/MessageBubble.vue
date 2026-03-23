<template>
  <div :class="['bubble', role]">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ role: 'user' | 'assistant' }>()
</script>

<style scoped>
.bubble {
  max-width: 85%;
  padding: 10px 12px;
  border-radius: 12px;
  margin: 8px 0;
  color: var(--bubble-text, #1f2937);
}

.user {
  margin-left: auto;
  background: var(--bubble-user-bg, #d1fae5);
  color: var(--bubble-user-text, #0f172a);
}

.assistant {
  margin-right: auto;
  background: var(--bubble-assistant-bg, #ffffff);
  border: 1px solid var(--bubble-assistant-border, #e5e7eb);
  color: var(--bubble-assistant-text, #1f2937);
}

html[data-theme='night'] .bubble {
  --bubble-user-bg: #2d4e68;
  --bubble-user-text: #eef6ff;
  --bubble-assistant-bg: #1f2d40;
  --bubble-assistant-border: #35506e;
  --bubble-assistant-text: #e7f0ff;
}

html[data-theme='eye'] .bubble {
  --bubble-user-bg: #d9f0c7;
  --bubble-user-text: #243127;
  --bubble-assistant-bg: #f4f7df;
  --bubble-assistant-border: #ccd7b2;
  --bubble-assistant-text: #243127;
}
</style>
