<template>
   <nav class="navbar_container">
   
      <ul>
        <li v-for="link in links" :key="link.name">
          <router-link :to="link.path">
            {{ link.name }}
          </router-link>
        </li>
    </ul>
    <div class="heading_container">
        <div class="input_container">
            <input type="text" placeholder="Search">
        </div>
        <div class="Logged_in_user">
            Welcome Admin
        </div>
    </div>
   
   </nav>
  </template>
  
  <script>
  export default {
    name: "Navbar",
    data() {
      return {
        links: [
          {
            name: "Home",
            path: "/",
          },
          {
            name: "Quiz",
            path: "/quiz",
          },
          {
            name: "Summary",
            path: "/summary",
          },
          {
            name: "Logout",
            path: "",
          }
        ],
      };
    },
  };
  </script>
  
  
  <style scoped>
  .navbar_container{
    background-color: #1b263b;
    padding: 1rem 2rem;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1rem;
  }
  .navbar_container ul{
    display: flex;
    list-style: none;
    gap: 1rem;
    
  }
  .navbar_container a{
    text-decoration: none;
    color: #fff;
  }
  .heading_container{
    display: flex;
    gap: 1rem;
    align-items: center;
    justify-content: center;
  }
  .heading_container .input_container{
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 10rem;
    
  }
  .heading_container .input_container input{
    width: 100%;
    height: 100%;
    border-radius: 0.5rem;
    padding: 0.5rem 0.3rem;
    border: none;
    outline: none;
  }
  .heading_container .Logged_in_user{
    color: #fff;
  }
  

  </style>
