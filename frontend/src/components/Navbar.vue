<template>
  <nav class="navbar_container">
    <ul>
      <li v-for="link in links" :key="link.name">
        <router-link v-if="link.name !== 'Logout'" :to="link.path">
          {{ link.name }}
        </router-link>
        <a v-else href="#" @click.prevent="handleLogout">{{ link.name }}</a>
      </li>
    </ul>
    <div class="heading_container">
      <div class="input_container">
        <input type="text" placeholder="Search" />
      </div>
      <div class="Logged_in_user">
        Welcome, {{ username ? username : "Admin" }}
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "Navbar",
  data() {
    let userData = localStorage.getItem("userData");
    let role = "";
    let full_name = "";

    if (userData) {
      try {
        userData = JSON.parse(userData);
        role = userData.role;
        full_name = userData.full_name;
      } catch (e) {
        console.error("Invalid userData format:", e);
      }
    }

    return {
      username: full_name || "Admin",
      links: role === "admin" 
        ? [
            { name: "Home", path: "/admin" },
            { name: "Summary", path: "/summary" },
            { name: "Quiz", path: "/quiz" },
            { name: "Users", path: "/admin/users" },
            { name: "Logout", path: "" },
          ]
        : [
            { name: "Home", path: "/user-dashboard" },
            { name: "Score", path: "/score" },
            { name: "Summary", path: "/summary" },
            { name: "Logout", path: "" },
          ],
    };
  },
  mounted() {
    const userData = localStorage.getItem("userData");
    if (userData) {
      this.username = JSON.parse(userData).full_name;
    }
  },
  methods: {
    handleLogout() {
      localStorage.removeItem("userData"); // Clear user data
      this.$router.push("/login"); // Redirect to login page
    },
  },
};
</script>

<style scoped>
.navbar_container {
  background-color: #1b263b;
  padding: 1rem 2rem;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
}
.navbar_container ul {
  display: flex;
  list-style: none;
  gap: 1rem;
}
.navbar_container a {
  text-decoration: none;
  color: #fff;
  cursor: pointer;
}
.heading_container {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: center;
}
.heading_container .input_container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 10rem;
}
.heading_container .input_container input {
  width: 100%;
  height: 100%;
  border-radius: 0.5rem;
  padding: 0.5rem 0.3rem;
  border: none;
  outline: none;
}
.heading_container .Logged_in_user {
  color: #fff;
}
</style>
