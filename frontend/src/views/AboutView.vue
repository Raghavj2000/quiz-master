<template>
  <div class="about-container">
    <div class="about-content">
      <h1>About Our Platform</h1>
      <p>
        Welcome to our platform! We are committed to providing a seamless and
        secure experience for users who want to manage their accounts, access
        personalized dashboards, and interact with our services.
      </p>
      <p>
        Our mission is to empower users through technology by offering intuitive
        interfaces, real-time insights, and a responsive support system. Whether
        you're a new user or a returning member, we aim to deliver the best
        possible experience every time.
      </p>
      <h2>Key Features</h2>
      <ul>
        <li>🔒 Secure Login & Authentication</li>
        <li>📊 Personalized User Dashboard</li>
        <li>⚡ Fast and Responsive Interface</li>
        <li>💬 Real-time Notifications and Updates</li>
        <li>📱 Mobile-friendly Design</li>
      </ul>
      <p>
        We're constantly working on new features and improvements. Your feedback
        helps us grow, so don’t hesitate to reach out with suggestions or
        questions.
      </p>
      <p>Thank you for being a part of our Project!</p>

      <!-- Back to Login Button -->
      <button @click="goBack" class="back-button">← Back to Login</button>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    goBack() {
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.about-container {
  display: flex;
  justify-content: center;
  padding: 3rem 1rem;
  background-color: #f9f9f9;
  min-height: 100vh;
}

.about-content {
  max-width: 800px;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.about-content h1 {
  color: #333;
  margin-bottom: 1rem;
}

.about-content h2 {
  margin-top: 2rem;
  color: #555;
}

.about-content p {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.about-content ul {
  list-style: none;
  padding-left: 0;
}

.about-content li {
  margin: 0.5rem 0;
  font-weight: 500;
  color: #444;
}

.back-button {
  margin-top: 2rem;
  padding: 0.7rem 1.2rem;
  background-color: #6e8efb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s ease;
}

.back-button:hover {
  background-color: #5b74e8;
}
</style>
