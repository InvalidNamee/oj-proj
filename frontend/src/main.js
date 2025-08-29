import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import axios from 'axios'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { useUserStore } from './stores/user.js'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

axios.defaults.baseURL = 'http://121.249.151.214'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.mount('#app')

const userStore = useUserStore()
if (userStore.accessToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${userStore.accessToken}`
}

axios.interceptors.response.use(
  res => res,
  async err => {
    const userStore = useUserStore();
    const originalRequest = err.config;

    // 如果是刷新请求自身失败，不再重试，直接登出
    if (originalRequest.url === '/api/auth/refresh') {
      userStore.clearUser();
      router.push('/login');
      return Promise.reject(err);
    }

    const status = err.response?.status;

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      if (userStore.refreshToken) {
        try {
          const res = await axios.post('/api/auth/refresh', {}, {
            headers: { Authorization: `Bearer ${userStore.refreshToken}` }
          });
          userStore.accessToken = res.data.access_token;
          axios.defaults.headers.common['Authorization'] = `Bearer ${userStore.accessToken}`;
          originalRequest.headers['Authorization'] = `Bearer ${userStore.accessToken}`;
          return axios(originalRequest); // 重试原请求
        } catch {
          userStore.clearUser();
          router.push('/login');
        }
      } else {
        userStore.clearUser();
        router.push('/login');
      }
    } else if (status === 403) {
      router.push('/403');
    } else if (status === 404) {
      router.push('/404');
    }

    return Promise.reject(err);
  }
);