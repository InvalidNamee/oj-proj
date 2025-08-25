<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import { useRouter, useRoute } from "vue-router";
import { useUserStore } from "@/stores/user";

const groups = ref([]);
const total = ref(0);
const page = ref(1);
const perPage = ref(10);
const keyword = ref("");
const selected = ref([]); // 已选组
const batchMode = ref(false);

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const fetchGroups = async () => {
  const res = await axios.get("/api/groups", {
    params: {
      course_id: userStore.currentCourseId,
      page: page.value,
      per_page: perPage.value,
      keyword: keyword.value || undefined,
    },
  });
  groups.value = res.data.groups || [];
  total.value = res.data.total || 0;
};

// 改变路由参数以便能返回同一状态
const updateRoute = () => {
  router.replace({
    path: "/groups",
    query: {
      page: page.value,
      per_page: perPage.value,
      keyword: keyword.value || undefined,
    },
  });
};

watch([page, perPage, keyword], () => {
  if (keyword.value) {
    page.value = 1; // 搜索时重置页码
  }
  updateRoute();
  fetchGroups();
});

// 初始加载时从路由恢复参数
onMounted(() => {
  page.value = Number(route.query.page) || 1;
  perPage.value = Number(route.query.per_page) || 10;
  keyword.value = route.query.keyword || "";
  fetchGroups();
});

const goDetail = (id) => {
  router.push(`/groups/${id}`);
};

const goEdit = (id) => {
  router.push(`/groups/${id}/edit`);
};

const deleteOne = async (id) => {
  if (!confirm("确认删除该组？")) return;
  await axios.delete("/api/groups", { data: { group_ids: [id] } });
  fetchGroups();
};

const deleteBatch = async () => {
  if (!confirm(`确认删除选中的 ${selected.value.length} 个组？`)) return;
  await axios.delete("/api/groups", { data: { group_ids: selected.value } });
  selected.value = [];
  batchMode.value = false;
  fetchGroups();
};
</script>

<template>
  <div class="p-6">
    <h2 class="text-xl font-bold mb-2">分组列表</h2>
    <!-- 搜索栏 -->
    <div class="flex justify-between items-center mb-2">
      <!-- 左侧搜索框 -->
      <div class="flex items-center space-x-2">
        <input type="text" v-model="keyword" placeholder="按组名搜索"
          class="border border-gray-500 rounded px-2 py-1 w-64" />
        <button class="px-4 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded"
          @click="page = 1; updateRoute(); fetchGroups();">
          搜索
        </button>
      </div>

      <!-- 右侧操作按钮 -->
      <div class="flex items-center space-x-2">
        <button class="px-4 py-1 bg-gray-500 hover:bg-gray-600 text-white rounded"
          @click="batchMode = !batchMode; selected = []">
          {{ batchMode ? "取消" : "选择" }}
        </button>
        <button v-if="batchMode" class="px-4 py-1 bg-red-500 hover:bg-red-600 text-white rounded"
          @click="deleteBatch">
          批量删除
        </button>
      </div>
    </div>


    <div class="bg-white shadow rounded-lg overflow-hidden">
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-700">
          <tr>
            <th class="p-3" v-if="batchMode">
              <input type="checkbox" :checked="selected.length === groups.length"
                @change="selected = $event.target.checked ? groups.map(g => g.id) : []" />
            </th>
            <th class="p-3">ID</th>
            <th class="p-3">组名</th>
            <th class="p-3">所属课程</th>
            <th class="p-3">学生数</th>
            <th class="p-3">题单数</th>
            <th class="p-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in groups" :key="g.id" class="hover:bg-gray-50 transition">
            <td class="p-3" v-if="batchMode">
              <input type="checkbox" v-model="selected" :value="g.id" />
            </td>
            <td class="p-3">{{ g.id }}</td>
            <td class="p-3 text-blue-600 hover:underline cursor-pointer" @click="goDetail(g.id)">
              {{ g.name }}
            </td>
            <td class="p-3">{{ g.course.name }}</td>
            <td class="p-3">{{ g.student_cnt }}</td>
            <td class="p-3">{{ g.problemset_cnt }}</td>
            <td class="p-3 space-x-3">
              <template v-if="userStore.usertype !== 'student'">
                <button class="text-blue-500 hover:underline" @click.stop="goEdit(g.id)">
                  编辑
                </button>
                <button class="text-red-500 hover:underline" @click.stop="deleteOne(g.id)">
                  删除
                </button>
              </template>
            </td>
          </tr>
          <tr v-if="groups.length === 0">
            <td :colspan="batchMode ? 7 : 6" class="p-3 text-center text-gray-400">
              暂无分组
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="flex justify-center mt-4 space-x-2">
      <button class="px-3 py-1 border rounded" :disabled="page === 1" @click="page--">
        上一页
      </button>
      <span>第 {{ page }} / {{ Math.ceil(total / perPage) }} 页</span>
      <button class="px-3 py-1 border rounded" :disabled="page >= Math.ceil(total / perPage)" @click="page++">
        下一页
      </button>
    </div>
  </div>
</template>
