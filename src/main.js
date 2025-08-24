import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { basicSetup } from 'codemirror'
import VueCodemirror from 'vue-codemirror'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import axios from 'axios'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { useUserStore } from './stores/user.js'

axios.defaults.baseURL = 'http://121.249.151.214:5000'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)
app.use(VueCodemirror, {
  // optional default global options
  autofocus: true,
  disabled: false,
  indentWithTab: true,
  tabSize: 4,
  placeholder: 'Code goes here...',
  extensions: [basicSetup]
  // ...
})

app.mount('#app')

axios.interceptors.request.use(config => {
  const userStore = useUserStore();
  if (config.url && config.url.includes('/api/auth/refresh')) {
    if (userStore.refreshToken) {
      config.headers.Authorization = 'Bearer ' + userStore.refreshToken;
    }
  } else {
    if (userStore.accessToken) {
      config.headers.Authorization = 'Bearer ' + userStore.accessToken;
    }
  }
  return config;
}, error => Promise.reject(error));