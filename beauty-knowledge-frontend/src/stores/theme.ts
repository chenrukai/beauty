import { defineStore } from 'pinia'

export type ThemeMode = 'day' | 'night' | 'eye'

const THEME_KEY = 'beauty_theme_mode'
const DEFAULT_MODE: ThemeMode = 'day'

function normalizeThemeMode(raw?: string | null): ThemeMode {
  if (raw === 'day' || raw === 'night' || raw === 'eye') {
    return raw
  }
  return DEFAULT_MODE
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: DEFAULT_MODE as ThemeMode
  }),
  actions: {
    initTheme() {
      const saved = typeof window !== 'undefined' ? window.localStorage.getItem(THEME_KEY) : null
      this.mode = normalizeThemeMode(saved)
      this.applyTheme()
    },
    setMode(mode: ThemeMode) {
      this.mode = normalizeThemeMode(mode)
      this.applyTheme()
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(THEME_KEY, this.mode)
      }
    },
    applyTheme() {
      if (typeof document === 'undefined') return
      const root = document.documentElement
      root.setAttribute('data-theme', this.mode)
      root.style.colorScheme = this.mode === 'night' ? 'dark' : 'light'
    }
  }
})
