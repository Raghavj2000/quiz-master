import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/login", // Redirect root to /login
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginView.vue"),
      meta: { requiresGuest: true }, // Only allow guests
    },
    {
      path: "/admin",
      name: "admin",
      component: () => import("../views/AdminView.vue"),
      meta: { requiresAuth: true }, // Requires authentication
    },
    {
      path: "/register",
      name: "register",
      component: () => import("../views/RegisterView.vue"),
      meta: { requiresGuest: true }, // Only allow guests
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
      meta: { requiresAuth: true }, // Requires authentication
    },
  ],
});

// **Navigation Guard**
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem("userData"); // Check if user is logged in

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if trying to access protected routes without authentication
    next("/login");
  } else if (to.meta.requiresGuest && isAuthenticated) {
    // Redirect to dashboard if already logged in
    next("/user-dashboard");
  } else {
    next(); // Proceed to the requested route
  }
});

export default router;
