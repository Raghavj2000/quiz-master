<template>
  <div class="register-container">
    <form class="register-form" @submit.prevent="handleRegister">
      <h2>Register</h2>

      <div class="input-group">
        <label for="fullname">Full Name</label>
        <input type="text" id="fullname" v-model="fullName" required />
      </div>

      <div class="input-group">
        <label for="email">Username (Email)</label>
        <input type="email" id="email" v-model="email" required />
      </div>

      <div class="input-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>

      <div class="input-group">
        <label for="qualification">Qualification</label>
        <input
          type="text"
          id="qualification"
          v-model="qualification"
          required
        />
      </div>

      <div class="input-group">
        <label for="dob">Date of Birth</label>
        <input type="date" id="dob" v-model="dob" required />
      </div>

      <button type="submit">Register</button>

      <p class="login-link">
        Already have an account?
        <a href="#" @click.prevent="handleLogin">Login here</a>
      </p>
    </form>
  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      fullName: "",
      email: "",
      password: "",
      qualification: "",
      dob: "",
    };
  },
  methods: {
    async handleRegister() {
      // handle registration logic 
  
    try{
      const body = {
        username: this.email,
        password: this.password,
        role: "student",
        full_name: this.fullName,
        qualification: this.qualification,
        dob: this.dob
        
      }
      const response = await axios.post("https://your-api.com/register", body);
      console.log(response.data);
      
    }
    catch(error){
      console.log(error)
    }
    },
    handleLogin() {
      // Navigate to /login using vue-router
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

button:hover {
  background: #37b18e;
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
