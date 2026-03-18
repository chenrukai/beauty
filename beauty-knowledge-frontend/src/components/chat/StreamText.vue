<template>
  <LinkifiedText :text="text" />
</template>

<script setup lang="ts">
import LinkifiedText from '../common/LinkifiedText.vue'

defineProps<{ text: string }>()
</script>
