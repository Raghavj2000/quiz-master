import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import "vue-toast-notification/dist/theme-sugar.css"; // Import toast styles
import VueToast from "vue-toast-notification";

const app = createApp(App)
app.use(VueToast);
app.use(router)

app.mount('#app')
