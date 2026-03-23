<template>
  <div class="card">
    <div class="head">来源 · {{ source.fileName || ('文件' + source.fileId) }} · 第{{ source.pageNo }}页</div>
    <div class="body-wrap">
      <LinkifiedText class="body" :text="displayText" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import LinkifiedText from '../common/LinkifiedText.vue'

const props = defineProps<{ source: { fileId: number; fileName?: string; pageNo: number; content: string } }>()
const MAX_LEN = 15

const normalizedContent = computed(() => sanitizeSourceText(props.source.content || ''))
const displayText = computed(() => {
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
