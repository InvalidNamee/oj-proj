<template>
  <div class="flex justify-center items-center bg-gray-100 p-4" :style="{ minHeight: 'calc(100vh - 64px)' }">
    <div class="bg-white p-8 rounded-xl shadow-lg text-center max-w-md w-full">
      <h1 class="text-4xl font-bold text-red-500 mb-4">403</h1>
      <h2 class="text-2xl font-semibold mb-2">Forbidden</h2>
      <p class="text-gray-600 mb-6">You do not have permission to access this page.</p>
      <button
        @click="$router.push('/')"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer"
      >
        返回首页
      </button>
    </div>
  </div>
</template>
