<template>
  <el-select
    :model-value="theme.mode"
    class="theme-switch"
    size="small"
    @change="onChange"
  >
    <el-option label="日间模式" value="day" />
    <el-option label="夜间模式" value="night" />
    <el-option label="护眼模式" value="eye" />
  </el-select>
</template>

<script setup lang="ts">
import { useThemeStore, type ThemeMode } from '../../stores/theme'

const theme = useThemeStore()

function onChange(v: string) {
  theme.setMode(v as ThemeMode)
}
</script>

<style scoped>
.theme-switch {
  width: 116px;
}
</style>
