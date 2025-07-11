<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>Edit Question</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      
      <form @submit.prevent="updateQuestion" class="question-form">
        <div class="form-group">
          <label for="questionStatement">Question Statement</label>
          <textarea 
            id="questionStatement" 
            v-model="editedQuestion.question_statement" 
            required
            placeholder="Enter the question statement"
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="quizSelect">Select Quiz</label>
          <select id="quizSelect" v-model="editedQuestion.quiz_id" required>
            <option value="">Select a quiz</option>
            <option v-for="quiz in quizzes" :key="quiz.id" :value="quiz.id">
              {{ quiz.name }} ({{ quiz.chapter_name }})
            </option>
          </select>
        </div>

        <div class="options-section">
          <h3>Options</h3>
          
          <div class="form-group">
            <label for="option1">Option 1</label>
            <input 
              type="text" 
              id="option1" 
              v-model="editedQuestion.option1" 
              required
              placeholder="Enter option 1"
            >
          </div>

          <div class="form-group">
            <label for="option2">Option 2</label>
            <input 
              type="text" 
              id="option2" 
              v-model="editedQuestion.option2" 
              required
              placeholder="Enter option 2"
            >
          </div>

          <div class="form-group">
            <label for="option3">Option 3</label>
            <input 
              type="text" 
              id="option3" 
              v-model="editedQuestion.option3" 
              required
              placeholder="Enter option 3"
            >
          </div>

          <div class="form-group">
            <label for="option4">Option 4</label>
            <input 
              type="text" 
              id="option4" 
              v-model="editedQuestion.option4" 
              required
              placeholder="Enter option 4"
            >
          </div>
        </div>

        <div class="form-group">
          <label for="correctOption">Correct Option</label>
          <select id="correctOption" v-model="editedQuestion.correct_option" required>
            <option value="">Select correct option</option>
            <option value="1">Option 1</option>
            <option value="2">Option 2</option>
            <option value="3">Option 3</option>
            <option value="4">Option 4</option>
          </select>
        </div>

        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="closeModal">Cancel</button>
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? 'Updating...' : 'Update Question' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'EditQuestionModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    question: {
      type: Object,
      default: () => ({})
    },
    quizzes: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      loading: false,
      editedQuestion: {
        question_statement: '',
        quiz_id: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: ''
      }
    };
  },
  watch: {
    question: {
      handler(newQuestion) {
        if (newQuestion && Object.keys(newQuestion).length > 0) {
          this.editedQuestion = {
            question_statement: newQuestion.question_statement || '',
            quiz_id: newQuestion.quiz_id || '',
            option1: newQuestion.option1 || '',
            option2: newQuestion.option2 || '',
            option3: newQuestion.option3 || '',
            option4: newQuestion.option4 || '',
            correct_option: newQuestion.correct_option ? newQuestion.correct_option.toString() : ''
          };
        }
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    async updateQuestion() {
      this.loading = true;
      const userData = JSON.parse(localStorage.getItem("userData"));
      const token = userData?.access_token;
      
      try {
        await axios.post(`http://localhost:5000/question/${this.question.id}`, this.editedQuestion, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        this.$emit('question-updated');
        this.closeModal();
      } catch (error) {
        console.error("Error updating question:", error);
        alert("Error updating question. Please try again.");
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
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

.question-form {
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
  resize: vertical;
  min-height: 80px;
}

.options-section {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  background: #f8f9fa;
}

.options-section h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
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
  background: #28a745;
  color: white;
}

.submit-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.cancel-btn:hover {
  background: #dee2e6;
}

.submit-btn:hover:not(:disabled) {
  background: #218838;
}
</style> 