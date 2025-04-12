<template>
  <div class="login-container">
    <div style="position: absolute; right: 0; top: 0"></div>
    <form class="login-form" @submit.prevent="handleLogin">
      <h2>Login</h2>

      <div class="input-group">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="email" @blur="validateEmail" />
        <p v-if="emailError" class="error-message">{{ emailError }}</p>
      </div>

      <div class="input-group">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          v-model="password"
          @blur="validatePassword"
        />
        <p v-if="passwordError" class="error-message">{{ passwordError }}</p>
      </div>

      <button type="submit" :disabled="!isFormValid">Login</button>

      <p class="register-link">
        Don't have an account?
        <a href="/register" @click.prevent="handleRegister">Register here</a>
      </p>
    </form>
  </div>
</template>

<script>
import Loader from "@/components/Loader.vue";
import axios from "axios";
import { useToast } from "vue-toast-notification";

export default {
  components: { Loader },
  data() {
    return {
      email: "",
      password: "",
      emailError: "",
      passwordError: "",
      loading: false,
    };
  },
  computed: {
    isFormValid() {
      return (
        this.email !== "" &&
        this.password !== "" &&
        !this.emailError &&
        !this.passwordError
      );
    },
  },
  methods: {
    validateEmail() {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!this.email) {
        this.emailError = "Email is required.";
      } else if (!emailRegex.test(this.email)) {
        this.emailError = "Please enter a valid email.";
      } else {
        this.emailError = "";
      }
    },
    validatePassword() {
      if (!this.password) {
        this.passwordError = "Password is required.";
      } else if (this.password.length < 6) {
        this.passwordError = "Password must be at least 6 characters.";
      } else {
        this.passwordError = "";
      }
    },
    async handleLogin() {
      this.validateEmail();
      this.validatePassword();

      if (!this.isFormValid) return;

      const $toast = useToast();
      this.loading = true;

      const body = {
        username: this.email,
        password: this.password,
      };

      try {
        const response = await axios.post("http://127.0.0.1:5000/logi", body);

        if (response?.data?.statusCode === "200") {
          $toast.success("Login successful!", { position: "top-right" });
          localStorage.setItem("userData", JSON.stringify(response?.data));
          this.$router.push("/user-dashboard");
        } else {
          $toast.error("Login failed!", { position: "top-right" });
        }
      } catch (error) {
        console.error(error);
        $toast.error("Login failed!", { position: "top-right" });
      } finally {
        this.loading = false;
        this.email = "";
        this.password = "";
      }
    },
    handleRegister() {
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

button:disabled {
  background: #ccc;
  cursor: not-allowed;
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

.error-message {
  color: red;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
</style>
