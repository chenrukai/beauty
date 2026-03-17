<template>
  <router-view />
</template>

<style>
:root {
  --bg: #f5f4ef;
  --ink: #1f2937;
  --brand: #0f766e;
  --accent: #ef4444;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: radial-gradient(circle at 20% 20%, #fff8ea 0%, #f5f4ef 45%, #eef3f2 100%);
}
</style>