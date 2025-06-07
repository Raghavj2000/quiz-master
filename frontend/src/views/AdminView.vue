<template>
  <div class="admin_container">
    <Navbar />
    <div v-if="loading">
      <Loader :loading="loading" />
    </div>
    <div v-else>
      <button class="add-subject-button" @click="showAddSubjectPopup = true">
        <span class="plus-icon">+</span> Add Subject
      </button>
    </div>
    <div class="subjects-grid">
      <div v-for="subject in subjects" :key="subject.id" class="subject-card">
        <div class="card-header">
          <h3>{{ subject.name }}</h3>
        </div>
        <div class="card-body">
          <p class="description">{{ subject.description }}</p>
          <div class="chapters">
            <h4>Chapters ({{ subject?.chapters?.length }})</h4>
            <ul>
              <li v-for="chapter in subject.chapters" :key="chapter.id" class="chapter-item">
                <span class="chapter-name">{{ chapter.name }}</span>
                <div class="chapter-actions">
                  <button class="action-button primary" @click="editChapter(chapter)">Edit</button>
                  <button class="action-button danger" @click="deleteChapter(chapter.id)">Delete</button>
                </div>
              </li>
            </ul>
            <button class="add-chapter-button" @click="openAddChapterPopup(subject)">
              <span class="plus-icon">+</span> Add Chapter
            </button>
          </div>
        </div>
      </div>
    </div>
    <Popup
      v-model="showAddSubjectPopup"
      title="Add New Subject"
      @confirm="handleAddSubject"
    >
      <form @submit.prevent="handleAddSubject" class="add-subject-form">
        <div class="form-group">
          <label for="subjectName">Subject Name</label>
          <input
            type="text"
            id="subjectName"
            v-model="newSubject.name"
            required
            placeholder="Enter subject name"
          />
        </div>
        <div class="form-group">
          <label for="subjectDescription">Description</label>
          <textarea
            id="subjectDescription"
            v-model="newSubject.description"
            required
            placeholder="Enter subject description"
            rows="3"
          ></textarea>
        </div>
      </form>
    </Popup>

    <Popup
      v-model="showAddChapterPopup"
      title="Add New Chapter"
      @confirm="handleAddChapter"
    >
      <form @submit.prevent="handleAddChapter" class="add-subject-form">
        <div class="form-group">
          <label for="chapterName">Chapter Name</label>
          <input
            type="text"
            id="chapterName"
            v-model="newChapter.name"
            required
            placeholder="Enter chapter name"
          />
        </div>
        <div class="form-group">
          <label for="chapterDescription">Description</label>
          <textarea
            id="chapterDescription"
            v-model="newChapter.description"
            required
            placeholder="Enter chapter description"
            rows="3"
          ></textarea>
        </div>
      </form>
    </Popup>
  </div>
</template>

<script>
import Navbar from "../components/Navbar.vue";
import { useToast } from "vue-toast-notification";
import axios from "axios";
import Loader from "../components/Loader.vue";
import Popup from "../components/Popup.vue";

export default {
  components: {
    Navbar,
    Loader,
    Popup
  },
  data() {
    return {
      subjects: [],
      showAddSubjectPopup: false,
      showAddChapterPopup: false,
      newSubject: {
        name: '',
        description: ''
      },
      newChapter: {
        name: '',
        subjectId: null,
        description: ''
      },
      loading: true,
      token: localStorage.getItem('token') || ''
    };
  },
  methods: {
    async fetchSubjects() {
      const $toast = useToast();
      const userData = JSON.parse(localStorage.getItem("userData"));
      const token = userData?.access_token;
      this.loading = true;
      try {
        const response = await axios.get("http://192.168.0.105:5000/subjects", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.subjects = response.data;
      } catch (error) {
        $toast.error("Error fetching subjects");
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    },
    async handleAddSubject() {
      const $toast = useToast();
      const userData = JSON.parse(localStorage.getItem("userData"));
      const token = userData?.access_token;
      
      try {
        const response = await axios.post(
          "http://192.168.0.105:5000/subject",
          this.newSubject,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        
      
        this.showAddSubjectPopup = false;
        this.newSubject = { name: '', description: '' };
        this.fetchSubjects();
        $toast.success("Subject added successfully");
      } catch (error) {
        $toast.error("Error adding subject");
        console.error('Error:', error);
      }
    },
    editChapter(chapter) {
      // Convert Proxy object to plain object to access properties
      const chapterData = {
        id: chapter.id,
        name: chapter.name
      };
      console.log('Chapter data:', chapterData);
    },
    async deleteChapter(chapterId) {
      console.log('Chapter ID:', chapterId);
    },
    openAddChapterPopup(subject) {
      this.newChapter = {
        name: '',
        subjectId: subject.id
      };
      this.showAddChapterPopup = true;
    },
    async handleAddChapter() {
      const $toast = useToast();
      const userData = JSON.parse(localStorage.getItem("userData"));
      const token = userData?.access_token;
      
      try {
        const response = await axios.post(
          `http://192.168.0.105:5000/chapter`,
          { 
            name: this.newChapter.name,
            description: this.newChapter.description,
            subject_id: this.newChapter.subjectId
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        
        this.showAddChapterPopup = false;
        this.newChapter = { name: '', description: '', subjectId: null };
        this.fetchSubjects();
        $toast.success("Chapter added successfully");
      } catch (error) {
        $toast.error("Error adding chapter");
        console.error('Error:', error);
      }
    },
  },
  mounted() {
    this.fetchSubjects();
  },
};
</script>

<style scoped>
.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.subject-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s;
}

.subject-card:hover {
  transform: translateY(-5px);
}

.card-header {
  background: #f8f9fa;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.card-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.card-body {
  padding: 15px;
}

.description {
  color: #666;
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.chapters {
  margin-top: 10px;
}

.chapters h4 {
  margin: 0 0 10px 0;
  color: #444;
  font-size: 1rem;
}

.chapters ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.chapter-item {
  padding: 10px 0;
  color: #666;
  font-size: 0.9rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.chapter-item:last-child {
  border-bottom: none;
}

.chapter-name {
  flex: 1;
}

.chapter-actions {
  display: flex;
  gap: 8px;
}

.action-button {
  padding: 0.5rem 1rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.action-button:hover {
  transform: scale(1.03);
}

.action-button.primary {
  background-color: #6e8efb;
  color: white;
}

.action-button.primary:hover {
  background-color: #5b74e8;
}

.action-button.danger {
  background-color: #e74c3c;
  color: white;
}

.action-button.danger:hover {
  background-color: #c0392b;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  justify-content: flex-end;
}

.add-subject-button {
  margin: 20px;
  padding: 10px 20px;
  background-color: #6e8efb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s, transform 0.2s;
}

.add-subject-button:hover {
  background-color: #5b74e8;
  transform: translateY(-2px);
}

.plus-icon {
  font-size: 1.2em;
  font-weight: bold;
}

.add-subject-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6e8efb;
  box-shadow: 0 0 0 2px rgba(110, 142, 251, 0.2);
}

.add-chapter-button {
  width: 100%;
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #f8f9fa;
  color: #6e8efb;
  border: 1px dashed #6e8efb;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.add-chapter-button:hover {
  background-color: #6e8efb;
  color: white;
  border-style: solid;
}

.add-chapter-button .plus-icon {
  font-size: 1.1em;
}
</style>
