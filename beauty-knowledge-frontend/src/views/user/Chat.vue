<template>
  <div class="chat-page">
    <aside class="left">
      <el-button type="primary" @click="newSession" plain>新会话</el-button>
      <el-scrollbar height="calc(100vh - 150px)">
        <div
          v-for="s in chat.sessionList"
          :key="s.id"
          class="session"
          :class="{ active: chat.currentSessionId === s.id }"
          @click="openSession(s.id)"
        >
          <span class="title">{{ s.title }}</span>
          <el-button text type="danger" size="small" @click.stop="removeSession(s.id)">删除</el-button>
        </div>
      </el-scrollbar>
    </aside>
    <section class="right">
      <div class="messages">
        <MessageBubble v-for="(m, idx) in chat.messages" :key="idx" :role="m.role">
          <StreamText :text="m.content" />
          <div v-if="m.sources?.length" class="sources">
            <SourceCard v-for="(s, i) in m.sources" :key="i" :source="s" />
          </div>
        </MessageBubble>
      </div>
      <div class="ask">
        <el-input v-model="question" type="textarea" :rows="3" placeholder="请输入问题..." />
        <el-button type="primary" :loading="chat.isStreaming" @click="ask">发送</el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import MessageBubble from '../../components/chat/MessageBubble.vue'
import StreamText from '../../components/chat/StreamText.vue'
import SourceCard from '../../components/chat/SourceCard.vue'
import { useChatStore } from '../../stores/chat'

const chat = useChatStore()
const question = ref('')

onMounted(() => {
  chat.fetchSessions()
})

async function ask() {
  const q = question.value.trim()
  if (!q) return
  await chat.streamAsk(q)
  question.value = ''
}

function newSession() {
  chat.currentSessionId = null
  chat.messages = []
}

function openSession(id: number) {
  chat.fetchMessages(id)
}

async function removeSession(id: number) {
  await ElMessageBox.confirm('确定删除这个会话吗？', '提示', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await chat.deleteSession(id)
}
</script>

<style scoped>
.chat-page { display: grid; grid-template-columns: 260px 1fr; gap: 12px; min-height: calc(100vh - 80px); }
.left { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px; }
.session { padding: 8px; cursor: pointer; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.session:hover { background: #f3f4f6; }
.session.active { background: #e5f3ff; }
.title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.right { display: grid; grid-template-rows: 1fr auto; background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; }
.messages { padding: 12px; overflow: auto; }
.ask { border-top: 1px solid #e5e7eb; padding: 12px; display: grid; gap: 8px; }
.sources { margin-top: 8px; display: grid; gap: 8px; }
@media (max-width: 900px) { .chat-page { grid-template-columns: 1fr; } }
</style>
