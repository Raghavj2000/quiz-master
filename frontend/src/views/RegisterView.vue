<template>
  <Loader v-if="loading" />
  <div class="register-container">
    <form class="register-form" @submit.prevent="handleRegister">
      <h2>Register</h2>

      <!-- Full Name -->
      <div class="input-group">
        <label for="fullname">Full Name</label>
        <input 
          type="text" 
          id="fullname" 
          v-model="fullName" 
          @blur="validateFullName" 
          @focus="clearError('fullName')" 
          required 
        />
        <p v-if="errors.fullName" class="error">{{ errors.fullName }}</p>
      </div>

      <!-- Email -->
      <div class="input-group">
        <label for="email">Username (Email)</label>
        <input 
          type="email" 
          id="email" 
          v-model="email" 
          @blur="validateEmail" 
          @focus="clearError('email')" 
          required 
        />
        <p v-if="errors.email" class="error">{{ errors.email }}</p>
      </div>

      <!-- Password -->
      <div class="input-group">
        <label for="password">Password</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          @blur="validatePassword" 
          @focus="clearError('password')" 
          required 
        />
        <p v-if="errors.password" class="error">{{ errors.password }}</p>
      </div>

      <!-- Qualification -->
      <div class="input-group">
        <label for="qualification">Qualification</label>
        <input 
          type="text" 
          id="qualification" 
          v-model="qualification" 
          @blur="validateQualification" 
          @focus="clearError('qualification')" 
          required 
        />
        <p v-if="errors.qualification" class="error">{{ errors.qualification }}</p>
      </div>

      <!-- Date of Birth -->
      <div class="input-group">
        <label for="dob">Date of Birth</label>
        <input 
          type="date" 
          id="dob" 
          v-model="dob" 
          @blur="validateDob" 
          @focus="clearError('dob')" 
          required 
        />
        <p v-if="errors.dob" class="error">{{ errors.dob }}</p>
      </div>

      <!-- Register Button -->
      <button type="submit" :disabled="!isFormValid">Register</button>

      <p class="login-link">
        Already have an account?
        <a href="#" @click.prevent="handleLogin">Login here</a>
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
      loading: false,
      fullName: "",
      email: "",
      password: "",
      qualification: "",
      dob: "",
      errors: {},
    };
  },

  computed: {
    isFormValid() {
      return Object.values(this.errors).every((error) => error === "");
    },
  },

  methods: {
    clearError(field) {
      this.errors[field] = "";
    },

    validateFullName() {
      this.errors.fullName = this.fullName.length >= 3 ? "" : "Full Name must be at least 3 characters.";
    },

    validateEmail() {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      this.errors.email = emailPattern.test(this.email) ? "" : "Invalid email format.";
    },

    validatePassword() {
      this.errors.password = this.password.length >= 6 ? "" : "Password must be at least 6 characters.";
    },

    validateQualification() {
      this.errors.qualification = this.qualification ? "" : "Qualification is required.";
    },

    validateDob() {
      this.errors.dob = this.dob ? "" : "Date of Birth is required.";
    },

    async handleRegister() {
      const $toast = useToast();

      // Validate before submitting
      this.validateFullName();
      this.validateEmail();
      this.validatePassword();
      this.validateQualification();
      this.validateDob();

      if (!this.isFormValid) {
        $toast.error("Please fix form errors before submitting.", { position: "top-right" });
        return;
      }

      this.loading = true;
      try {
        const body = {
          username: this.email,
          password: this.password,
          role: "student",
          full_name: this.fullName,
          qualification: this.qualification,
          dob: this.dob,
        };

        const response = await axios.post("http://127.0.0.1:5000/register", body);
        if (response?.data?.statusCode === "200") {
          $toast.success("Registration successful!", { position: "top-right" });

          // Reset fields
          this.fullName = "";
          this.email = "";
          this.password = "";
          this.qualification = "";
          this.dob = "";
          this.errors = {};

          this.$router.push("/login");
        } else {
          $toast.error("Registration failed!", { position: "top-right" });
        }
      } catch (error) {
        console.error("Registration failed:", error);
        $toast.error("Registration failed!", { position: "top-right" });
      } finally {
        this.loading = false;
      }
    },

    handleLogin() {
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #43cea2, #185a9d);
}

.register-form {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  width: 400px;
  text-align: center;
}

.register-form h2 {
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
  border-color: #43cea2;
}

button {
  width: 100%;
  padding: 0.7rem;
  border: none;
  background: #43cea2;
  color: #fff;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background: #37b18e;
}

.error {
  color: red;
  font-size: 0.8rem;
  margin-top: 0.3rem;
}

.login-link {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #555;
}

.login-link a {
  color: #43cea2;
  text-decoration: none;
  font-weight: bold;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
