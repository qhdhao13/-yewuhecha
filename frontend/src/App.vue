<template>
  <el-container class="app-container">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-content">
        <h1 class="app-title">合规审查知识库系统</h1>
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          router
          class="header-menu"
        >
          <el-menu-item index="/regulations">
            <el-icon><Document /></el-icon>
            <span>制度文件</span>
          </el-menu-item>
          <el-menu-item index="/documents">
            <el-icon><Files /></el-icon>
            <span>员工文档</span>
          </el-menu-item>
          <el-menu-item index="/reviews">
            <el-icon><Search /></el-icon>
            <span>合规审查</span>
          </el-menu-item>
          <el-menu-item index="/annotations">
            <el-icon><EditPen /></el-icon>
            <span>标注管理</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Files, Search, EditPen } from '@element-plus/icons-vue'

const route = useRoute()

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  height: 64px;
  line-height: 64px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 24px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.app-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-title::before {
  content: '📋';
  font-size: 24px;
}

.header-menu {
  background-color: transparent;
  border: none;
}

.header-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 2px solid transparent;
  font-weight: 500;
  transition: all 0.3s ease;
  margin: 0 4px;
}

.header-menu :deep(.el-menu-item:hover) {
  color: white;
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}

.header-menu :deep(.el-menu-item.is-active) {
  color: white;
  background-color: rgba(255, 255, 255, 0.2);
  border-bottom-color: white;
  border-radius: 4px 4px 0 0;
}

.app-main {
  padding: 24px;
  background: linear-gradient(to bottom, #f8f9fa 0%, #ffffff 100%);
  min-height: calc(100vh - 64px);
  flex: 1;
  overflow-y: auto;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #303133;
}

#app {
  height: 100vh;
  overflow: hidden;
}

/* 优化滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

