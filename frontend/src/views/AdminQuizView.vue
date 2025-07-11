<template>
  <Navbar />
  
  <div class="page-container">
    <div class="header-actions">
      <button class="new-quiz-btn" @click="showModal = true">
        <i class="fas fa-plus"></i> New Quiz
      </button>
      <button class="add-question-btn" @click="showQuestionModal = true">
        <i class="fas fa-plus"></i> Add Question
      </button>
    </div>

    <div v-if="loading">
      <Loader :loading="loading" />
    </div>

    <div v-else class="quiz-container">
      <div v-for="quiz in quiz" :key="quiz.id" class="quiz-card">
        <div class="quiz-header">
          <h2>{{ quiz.name }}</h2>
          <span class="chapter-tag">Chapter: {{ quiz.chapter_name }}</span>
        </div>
        
        <div class="quiz-details">
          <p class="remarks">{{ quiz.remarks }}</p>
          <div class="questions-section">
            <h3>Questions:</h3>
            <ul>
              <li v-for="question in quiz.questions" :key="question.id" class="question-item">
                <div class="question-content">
                  <span class="question-text">{{ question.name }}</span>
                  <div class="question-actions">
                    <button class="edit-btn" @click="editQuestion(question)">
                      <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="delete-btn" @click="deleteQuestion(question.id)">
                      <i class="fas fa-trash"></i> Delete
                    </button>
                  </div>
                </div>
              </li>
            </ul>
          </div>
          <div class="quiz-meta">
            <p v-if="quiz.time_duration">Duration: {{ quiz?.time_duration }} minutes</p>
            <p v-if="quiz.date_of_quiz">Date: {{ new Date(quiz.date_of_quiz).toLocaleDateString() }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- New Quiz Modal -->
    <div v-if="showModal" class="modal-overlay" @click="showModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Create New Quiz</h2>
          <button class="close-btn" @click="showModal = false">&times;</button>
        </div>
        <form @submit.prevent="createQuiz" class="quiz-form">
          <div class="form-group">
            <label for="quizName">Quiz Name</label>
            <input 
              type="text" 
              id="quizName" 
              v-model="newQuiz.name" 
              required
              placeholder="Enter quiz name"
            >
          </div>

          <div class="form-group">
            <label for="chapter">Chapter</label>
            <select id="chapter" v-model="newQuiz.chapter_id" required>
              <option value="">Select a chapter</option>
              <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                {{ chapter.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="remarks">Remarks</label>
            <textarea 
              id="remarks" 
              v-model="newQuiz.remarks" 
              placeholder="Enter any remarks"
            ></textarea>
          </div>

          <div class="form-group">
            <label for="duration">Time Duration (minutes)</label>
            <input 
              type="number" 
              id="duration" 
              v-model="newQuiz.time_duration" 
              min="1"
              placeholder="Enter duration in minutes"
            >
          </div>

          <div class="form-group">
            <label for="date">Date of Quiz</label>
            <input 
              type="date" 
              id="date" 
              v-model="newQuiz.date_of_quiz"
            >
          </div>

          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showModal = false">Cancel</button>
            <button type="submit" class="submit-btn">Create Quiz</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Question Modal -->
    <AddQuestionModal 
      :show="showQuestionModal"
      :quizzes="quiz"
      @close="showQuestionModal = false"
      @question-added="handleQuestionAdded"
    />

    <!-- Edit Question Modal -->
    <EditQuestionModal 
      :show="showEditQuestionModal"
      :question="selectedQuestion"
      :quizzes="quiz"
      @close="showEditQuestionModal = false"
      @question-updated="handleQuestionUpdated"
    />
  </div>
</template>

<script>
  import Navbar from "../components/Navbar.vue";
  import AddQuestionModal from "../components/AddQuestionModal.vue";
  import EditQuestionModal from "../components/EditQuestionModal.vue";
  import Loader from "../components/Loader.vue";
  import axios from 'axios';
  export default {
    components: {
      Navbar,
      AddQuestionModal,
      EditQuestionModal,
      Loader,
    },
    data() {
      return {
        quiz:[],
        loading: true,
        showModal: false,
        showQuestionModal: false,
        showEditQuestionModal: false,
        selectedQuestion: {},
        chapters: [],
        newQuiz: {
          name: '',
          chapter_id: '',
          remarks: '',
          time_duration: null,
          date_of_quiz: null
        }
      };
    },
    methods: {
        async fetchQuiz(){
            const userData = JSON.parse(localStorage.getItem("userData"));
            const token = userData?.access_token;
            try{
                const response = await axios.get("http://localhost:5000/quizzes",{
                    headers:{
                        Authorization: `Bearer ${token}`
                    }
                })
                this.quiz = response.data;
                this.loading = false;
            }
            catch(error){
                console.error("Error fetching quiz:", error);
                this.loading = false;
            }
        },
        async fetchChapters() {
            const userData = JSON.parse(localStorage.getItem("userData"));
            const token = userData?.access_token;
            try {
                const response = await axios.get("http://localhost:5000/chapters", {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                this.chapters = response.data;
            } catch (error) {
                console.error("Error fetching chapters:", error);
            }
        },
        async createQuiz() {
            const userData = JSON.parse(localStorage.getItem("userData"));
            const token = userData?.access_token;
            try {
                await axios.post("http://localhost:5000/quiz", this.newQuiz, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                this.showModal = false;
                this.fetchQuiz(); // Refresh the quiz list
                // Reset form
                this.newQuiz = {
                    name: '',
                    chapter_id: '',
                    remarks: '',
                    time_duration: null,
                    date_of_quiz: null
                };
            } catch (error) {
                console.error("Error creating quiz:", error);
            }
        },
        handleQuestionAdded() {
            this.fetchQuiz(); // Refresh the quiz list to show new questions
        },
        editQuestion(question) {
            this.selectedQuestion = question;
            this.showEditQuestionModal = true;
        },
        async deleteQuestion(questionId) {
            if (confirm('Are you sure you want to delete this question?')) {
                const userData = JSON.parse(localStorage.getItem("userData"));
                const token = userData?.access_token;
                try {
                    await axios.delete(`http://localhost:5000/question/${questionId}`, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });
                    this.fetchQuiz(); // Refresh the quiz list
                } catch (error) {
                    console.error("Error deleting question:", error);
                    alert("Error deleting question. Please try again.");
                }
            }
        },
        handleQuestionUpdated() {
            this.fetchQuiz(); // Refresh the quiz list to show updated questions
        }
    },
    mounted() {
        this.fetchQuiz();
        this.fetchChapters();
    },
}
</script>

<style lang="css" scoped>
.page-container {
  padding: 2rem;
}

.header-actions {
  margin-bottom: 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.new-quiz-btn,
.add-question-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.new-quiz-btn:hover,
.add-question-btn:hover {
  background: #45a049;
}

.add-question-btn {
  background: #007bff;
}

.add-question-btn:hover {
  background: #0056b3;
}

.quiz-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.quiz-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  transition: transform 0.2s ease;
}

.quiz-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.quiz-header {
  margin-bottom: 1rem;
}

.quiz-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.chapter-tag {
  display: inline-block;
  background: #e9ecef;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  color: #495057;
  margin-top: 0.5rem;
}

.quiz-details {
  color: #495057;
}

.remarks {
  font-style: italic;
  margin-bottom: 1rem;
  color: #6c757d;
}

.questions-section {
  margin: 1rem 0;
}

.questions-section h3 {
  color: #2c3e50;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.questions-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.questions-section li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.questions-section li:last-child {
  border-bottom: none;
}

.question-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid #e9ecef;
}

.question-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.question-text {
  flex: 1;
  font-size: 0.9rem;
  line-height: 1.4;
}

.question-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.edit-btn,
.delete-btn {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: background-color 0.2s;
}

.edit-btn {
  background: #ffc107;
  color: #212529;
}

.edit-btn:hover {
  background: #e0a800;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.delete-btn:hover {
  background: #c82333;
}

.quiz-meta {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.quiz-meta p {
  margin: 0.25rem 0;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
}

.quiz-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  border: none;
}

.cancel-btn {
  background: #e9ecef;
  color: #495057;
}

.submit-btn {
  background: #4CAF50;
  color: white;
}

.cancel-btn:hover {
  background: #dee2e6;
}

.submit-btn:hover {
  background: #45a049;
}
</style>