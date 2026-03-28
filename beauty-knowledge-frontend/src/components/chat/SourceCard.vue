<template>
  <div class="card">
    <div class="head">来源 · {{ source.fileName || ('文件' + source.fileId) }} · 第{{ source.pageNo }}页</div>
    <div class="body-wrap">
      <LinkifiedText class="body" :class="{ expanded }" :text="displayText" />
    </div>
    <button v-if="canExpand" class="toggle-btn" type="button" @click="expanded = !expanded">
      {{ expanded ? '收起' : '展开' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import LinkifiedText from '../common/LinkifiedText.vue'

const props = defineProps<{ source: { fileId: number; fileName?: string; pageNo: number; content: string } }>()
const MAX_LEN = 120
const expanded = ref(false)

const normalizedContent = computed(() => sanitizeSourceText(props.source.content || ''))
const canExpand = computed(() => normalizedContent.value.length > MAX_LEN)
const displayText = computed(() => {
  if (expanded.value) return normalizedContent.value
  const content = normalizedContent.value
  return content.length > MAX_LEN ? `${content.slice(0, MAX_LEN)}...` : content
})

function sanitizeSourceText(text: string) {
  return text
    .replace(/\r/g, '')
    .replace(/^#{1,6}\s*/gm, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    .replace(/`+/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}
</script>

<style scoped>
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px;
}

.head {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 6px;
}

.body-wrap {
  display: block;
  width: 100%;
  overflow: hidden;
}

.body {
  font-size: 13px;
  color: #1f2937;
  display: block;
  width: 100%;
  white-space: pre-wrap;
  line-height: 1.5;
  word-break: break-word;
}

.body:not(.expanded) {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.toggle-btn {
  margin-top: 6px;
  padding: 0;
  border: none;
  background: transparent;
  color: #2563eb;
  cursor: pointer;
  font-size: 12px;
}
</style>
