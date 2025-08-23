import { defineStore } from 'pinia';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

export const useUserStore = defineStore('user', {
  state: () => ({
    id: '',
    uid: '',
    username: '',
    usertype: '',
    accessToken: '',
    refreshToken: '',
    courses: [], // 新增 courses
    currentCourseId: null
  }),
  actions: {
    setUser(user, accessToken, refreshToken) {
      this.id = user.id;
      this.uid = user.uid;
      this.username = user.username;
      this.usertype = user.usertype;
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      this.courses = user.courses || []; // 存 courses
      this.currentCourseId = user.usertype === 'admin' ? null : (user.courses.length > 0 ? user.courses[0].id : null); // 设置当前课程
    },

    setCurrentCourse(courseId) {
      this.currentCourseId = courseId
    },

    clearUser() {
      this.id = '';
      this.uid = '';
      this.username = '';
      this.usertype = '';
      this.accessToken = '';
      this.refreshToken = '';
      this.courses = [];
    },

    async logout() {
      try {
        if (this.accessToken) {
          await axios.post('/api/auth/logout');
          console.log('Logout API successful');
        }
      } catch (error) {
        console.error('Logout API failed:', error);
      } finally {
        this.clearUser();
      }
    },
  },
  persist: true // 启用 pinia-plugin-persistedstate
});