<template>
  <div class="login-container">
    <form class="login-form" @submit.prevent="handleLogin">
      <h2>Login</h2>
      <div class="input-group">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div class="input-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
      <p class="register-link">
        Don't have an account?
        <a href="/register" @click.prevent="handleRegister">Register here</a>
      </p>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: "",
      password: "",
    };
  },
  methods: {
    handleLogin() {
      // handle login logic
      alert(`Email: ${this.email}, Password: ${this.password}`);
    },
    handleRegister() {
      // redirect or show register form
      this.$router.push("/register");
    },
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #6e8efb, #a777e3);
}

.login-form {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  width: 400px;
  text-align: center;
}

.login-form h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.input-group {
  margin-bottom: 1rem;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
}

.input-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
}

.input-group input:focus {
  border-color: #6e8efb;
}

button {
  width: 100%;
  padding: 0.7rem;
  border: none;
  background: #6e8efb;
  color: #fff;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

button:hover {
  background: #5b74e8;
}

.register-link {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #555;
}

.register-link a {
  color: #6e8efb;
  text-decoration: none;
  font-weight: bold;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
