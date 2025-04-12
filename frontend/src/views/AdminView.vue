<template>
  <div class="admin_container">
    <Navbar />

    <div v-if="loading">
      <Loader :loading="loading" />
    </div>

    <div v-else class="table-container">
      <h2>Registered Users</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Full Name</th>
            <th>Username</th>
            <th>Date of Birth</th>
            <th>Qualification</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.full_name }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.dob }}</td>
            <td>{{ user.qualification }}</td>
            <td>{{ user.role }}</td>
            <td>
              <BaseButton type="danger" @click="deleteUser(user.id)"
                >Delete</BaseButton
              >
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import Navbar from "../components/Navbar.vue";
import Loader from "../components/Loader.vue";
import BaseButton from "../components/BaseButton.vue";
import { useToast } from "vue-toast-notification";
import axios from "axios";

export default {
  components: {
    Navbar,
    Loader,
    BaseButton,
  },
  data() {
    return {
      loading: true,
      users: [],
    };
  },
  methods: {
    async fetchUsers() {
      const $toast = useToast();
      try {
        this.loading = true;
        const userData = JSON.parse(localStorage.getItem("userData"));
        const token = userData?.access_token;

        const response = await axios.get("http://127.0.0.1:5000/admin/users", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status !== 200) throw new Error("Fetch failed");

        this.users = response?.data;
        $toast.success("Users fetched successfully", { position: "top-right" });
      } catch (error) {
        console.error("Error fetching users:", error);
        useToast().error("An error occurred while fetching users", {
          position: "top-right",
        });
      } finally {
        this.loading = false;
      }
    },

    async deleteUser(userId) {
      const $toast = useToast();

      try {
        const userData = JSON.parse(localStorage.getItem("userData"));
        const token = userData?.access_token;

        await axios.delete(`http://127.0.0.1:5000/admin/user/${userId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        this.users = this.users.filter((user) => user.id !== userId);
        $toast.success("User deleted successfully", { position: "top-right" });
      } catch (error) {
        console.error("Error deleting user:", error);
        $toast.error("An error occurred while deleting user", {
          position: "top-right",
        });
      } finally {
      }
    },
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>

<style scoped>
.admin_container {
  min-height: 100dvh;
  background-color: white;
}

.table-container {
  margin-top: 20px;
  overflow-x: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

table {
  border-collapse: collapse;
  width: 100%;
  border: 1px solid #ddd;
  background-color: #f9f9f9;
}

th,
td {
  text-align: left;
  padding: 12px;
  border: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
  font-weight: 600;
}

.loader-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 70vh;
}
</style>
