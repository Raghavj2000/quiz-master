import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/login",
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginView.vue"),
      meta: { requiresGuest: true },
    },
    {
      path: "/admin",
      name: "admin",
      component: () => import("../views/AdminView.vue"),
      meta: { requiresAuth: false },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("../views/RegisterView.vue"),
      meta: { requiresGuest: true },
    },
    {
      path: "/about",
      name: "about",
      component: () => import("../views/AboutView.vue"),
    },
    {
      path: "/user-dashboard",
      name: "user-dashboard",
      component: () => import("../views/UserDashboard.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/admin/users",
      name: "admin-users",
      component: () => import("../views/AdminUsersView.vue"),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
});

// **Navigation Guard**
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem("userData");
  const userData = isAuthenticated ? JSON.parse(localStorage.getItem("userData")) : null;
  const isAdmin = userData?.role === "admin";

  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next("/user-dashboard");
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next("/user-dashboard");
  } else {
    next();
  }
});

export default router;
