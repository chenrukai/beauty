<template>
  <div class="stream-text" v-html="formattedHtml" />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ text: string }>()

function escapeHtml(input: string) {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function linkifyEscaped(input: string) {
  return input.replace(/(https?:\/\/[^\s<]+)/g, (url: string) => {
    const safeUrl = url.replace(/"/g, '%22')
    return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${url}</a>`
  })
}

function isHeadingLine(line: string) {
  return /^(结论|图谱洞察摘要|原理\/原因|原理|原因|关键要点|行动建议|实操建议|注意事项|来源)\s*[：:]/.test(line)
}

function renderLineContent(line: string) {
  return linkifyEscaped(escapeHtml(line))
}

const formattedHtml = computed(() => {
  const raw = String(props.text || '').replace(/\r/g, '')
  if (!raw.trim()) return ''

  const lines = raw.split('\n')
  const parts: string[] = []
  let paragraphLines: string[] = []
  let listItems: string[] = []

  const flushParagraph = () => {
    if (!paragraphLines.length) return
    const content = paragraphLines.map((x) => renderLineContent(x)).join('<br/>')
    parts.push(`<p>${content}</p>`)
    paragraphLines = []
  }

  const flushList = () => {
    if (!listItems.length) return
    parts.push(`<ul>${listItems.map((x) => `<li>${renderLineContent(x)}</li>`).join('')}</ul>`)
    listItems = []
  }

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) {
      flushParagraph()
      flushList()
      continue
    }

    const bulletMatch = trimmed.match(/^([-*•]|\d+[.)])\s+(.+)$/)
    if (bulletMatch) {
      flushParagraph()
      listItems.push(bulletMatch[2])
      continue
    }

    if (isHeadingLine(trimmed)) {
      flushParagraph()
      flushList()
      parts.push(`<h4>${renderLineContent(trimmed)}</h4>`)
      continue
    }

    flushList()
    paragraphLines.push(trimmed)
  }

  flushParagraph()
  flushList()
  return parts.join('')
})
</script>

<style scoped>
.stream-text {
  line-height: 1.82;
  font-size: 15px;
  word-break: break-word;
  color: inherit;
}

.stream-text :deep(h4) {
  margin: 12px 0 8px;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.stream-text :deep(p) {
  margin: 8px 0;
}

.stream-text :deep(ul) {
  margin: 8px 0 10px;
  padding-left: 20px;
}

.stream-text :deep(li) {
  margin: 5px 0;
}

.stream-text :deep(a) {
  color: #0f766e;
  text-decoration: underline;
}

html[data-theme='night'] .stream-text :deep(h4) {
  color: #e8f0ff;
}

html[data-theme='night'] .stream-text :deep(a) {
  color: #7dd3fc;
}

html[data-theme='eye'] .stream-text :deep(a) {
  color: #3f6212;
}
</style>
