<template>
  <div class="linkified-text" v-html="html" />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ text?: string | null }>()

function escapeHtml(input: string) {
  return input
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

const html = computed(() => {
  const raw = String(props.text || '')
  if (!raw) return ''

  const escaped = escapeHtml(raw)
  const urlRegex = /(https?:\/\/[^\s<]+)/g
  return escaped.replace(urlRegex, (url) => {
    const safeUrl = url.replaceAll('"', '%22')
    return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${url}</a>`
  })
})
</script>

<style scoped>
.linkified-text {
  white-space: pre-wrap;
  line-height: 1.7;
  word-break: break-word;
}

.linkified-text :deep(a) {
  color: #0f766e;
  text-decoration: underline;
}
</style>
