<template>
  <div class="card">
    <div class="head">来源 · 文件{{ source.fileId }} · 第{{ source.pageNo }}页</div>
    <div class="body">{{ source.content }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ source: { fileId: number; pageNo: number; content: string } }>()
</script>

<style scoped>
.card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 10px; }
.head { font-size: 12px; color: #6b7280; margin-bottom: 6px; }
.body { font-size: 13px; color: #1f2937; }
</style>