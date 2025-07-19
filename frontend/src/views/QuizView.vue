<template>
    <div class="quiz-view">
        <Navbar />
        
        <div class="quiz-container">
            <!-- Quiz Instructions -->
            <div v-if="!quizStarted && !loading" class="quiz-instructions">
                <div class="instructions-card">
                    <h2>{{ currentQuiz?.name }}</h2>
                    <p class="chapter-info">{{ currentQuiz?.chapter_name }}</p>
                    
                    <div class="quiz-info">
                        <div class="info-item">
                            <span class="label">Duration:</span>
                            <span class="value">{{ formatDuration(currentQuiz?.time_duration) }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Questions:</span>
                            <span class="value">{{ currentQuiz?.questions?.length || 0 }}</span>
                        </div>
                        <div v-if="currentQuiz?.remarks" class="info-item">
                            <span class="label">Notes:</span>
                            <span class="value">{{ currentQuiz.remarks }}</span>
                        </div>
                    </div>
                    
                    <div class="instructions-text">
                        <h3>Instructions:</h3>
                        <ul>
                            <li>Read each question carefully</li>
                            <li>Select the best answer from the options provided</li>
                            <li>You can navigate between questions using the navigation buttons</li>
                            <li>Review your answers before submitting</li>
                            <li>Once submitted, you cannot change your answers</li>
                        </ul>
                    </div>
                    
                    <div v-if="!quizAlreadyTaken" class="start-actions">
                        <button 
                            @click="startQuiz" 
                            class="start-btn primary-btn"
                            :disabled="checkingScore"
                        >
                            {{ checkingScore ? 'Checking...' : 'Start Quiz' }}
                        </button>
                        <button @click="goBack" class="back-btn secondary-btn">
                            Back to Dashboard
                        </button>
                    </div>
                    
                    <!-- Quiz Already Taken Message -->
                    <div v-if="quizAlreadyTaken" class="already-taken-message">
                        <div class="message-card">
                            <h3>Quiz Already Completed</h3>
                            <p>You have already taken this quiz and cannot take it again.</p>
                            <button @click="goBack" class="primary-btn">
                                Back to Dashboard
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="loading-container">
                <div class="loader"></div>
                <p>Loading quiz...</p>
            </div>

            <!-- Quiz Interface -->
            <div v-if="quizStarted && currentQuestion" class="quiz-interface">
                <div class="quiz-header">
                    <div class="quiz-progress">
                        <span class="progress-text">Question {{ currentQuestionIndex + 1 }} of {{ currentQuiz.questions.length }}</span>
                        <div class="progress-bar">
                            <div 
                                class="progress-fill" 
                                :style="{ width: `${((currentQuestionIndex + 1) / currentQuiz.questions.length) * 100}%` }"
                            ></div>
                        </div>
                    </div>
                    
                    <div v-if="timeLimit" class="timer">
                        <span class="timer-text">Time Remaining: {{ formatTime(timeRemaining) }}</span>
                    </div>
                </div>

                <div class="question-container">
                    <h3 class="question-text">{{ currentQuestion.question_statement }}</h3>
                    
                    <div class="options-container">
                        <div 
                            v-for="(option, index) in options" 
                            :key="index"
                            class="option-item"
                            :class="{ 
                                'selected': selectedAnswer === index + 1,
                                'correct': showResults && (index + 1) === getCorrectOptionIndex(currentQuestion),
                                'incorrect': showResults && selectedAnswer === index + 1 && selectedAnswer !== getCorrectOptionIndex(currentQuestion)
                            }"
                            @click="selectAnswer(index + 1)"
                        >
                            <span class="option-label">{{ String.fromCharCode(65 + index) }}</span>
                            <span class="option-text">{{ option }}</span>
                        </div>
                    </div>
                </div>

                <div class="quiz-navigation">
                    <button 
                        @click="previousQuestion" 
                        class="secondary-btn"
                        :disabled="currentQuestionIndex === 0"
                    >
                        Previous
                    </button>
                    
                    <div class="question-indicators">
                        <span 
                            v-for="(question, index) in currentQuiz.questions" 
                            :key="index"
                            class="indicator"
                            :class="{ 
                                'answered': answers[index] !== null,
                                'current': index === currentQuestionIndex
                            }"
                            @click="goToQuestion(index)"
                        >
                            {{ index + 1 }}
                        </span>
                    </div>
                    
                    <button 
                        v-if="currentQuestionIndex < currentQuiz.questions.length - 1"
                        @click="nextQuestion" 
                        class="primary-btn"
                    >
                        Next
                    </button>
                    
                    <button 
                        v-else
                        @click="submitQuiz" 
                        class="primary-btn submit-btn"
                    >
                        Submit Quiz
                    </button>
                </div>
            </div>

            <!-- Results -->
            <div v-if="showResults" class="results-container">
                <div class="results-card">
                    <h2>Quiz Results</h2>
                    <div class="score-display">
                        <div class="score-circle">
                            <span class="score-number">{{ score }}</span>
                            <span class="score-total">/ {{ currentQuiz.questions.length }}</span>
                        </div>
                        <div class="score-percentage">
                            {{ Math.round((score / currentQuiz.questions.length) * 100) }}%
                        </div>
                    </div>
                    
                    <div class="results-summary">
                        <div class="summary-item">
                            <span class="label">Correct Answers:</span>
                            <span class="value correct">{{ score }}</span>
                        </div>
                        <div class="summary-item">
                            <span class="label">Incorrect Answers:</span>
                            <span class="value incorrect">{{ currentQuiz.questions.length - score }}</span>
                        </div>
                    </div>
                    
                    <div class="results-actions">
                        <button @click="goBack" class="primary-btn">
                            Back to Dashboard
                        </button>
                        <button @click="reviewAnswers" class="secondary-btn">
                            Review Answers
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Navbar from '@/components/Navbar.vue';

const route = useRoute();
const router = useRouter();

const currentQuiz = ref(null);
const loading = ref(true);
const quizStarted = ref(false);
const currentQuestionIndex = ref(0);
const answers = ref({});
const selectedAnswer = ref(null);
const showResults = ref(false);
const score = ref(0);
const timeRemaining = ref(0);
const timeLimit = ref(null);
const timer = ref(null);
const quizAlreadyTaken = ref(false);
const checkingScore = ref(false);

const currentQuestion = computed(() => {
    if (!currentQuiz.value?.questions) return null;
    return currentQuiz.value.questions[currentQuestionIndex.value];
});

const options = computed(() => {
    if (!currentQuestion.value) return [];
    return [
        currentQuestion.value.option1,
        currentQuestion.value.option2,
        currentQuestion.value.option3,
        currentQuestion.value.option4
    ].filter(option => option); // Remove empty options
});

const getCorrectOptionIndex = (question) => {
    if (!question) return null;
    // correct_option is already the index (1, 2, 3, or 4)
    return question.correct_option;
};

const loadQuiz = async () => {
    const quizData = localStorage.getItem('currentQuiz');
    if (!quizData) {
        router.push('/user-dashboard');
        return;
    }
    
    try {
        currentQuiz.value = JSON.parse(quizData);
        
        // Initialize answers object
        currentQuiz.value.questions.forEach((_, index) => {
            answers.value[index] = null;
        });
        
        // Set up timer if time duration exists
        if (currentQuiz.value.time_duration) {
            timeLimit.value = currentQuiz.value.time_duration * 60; // Convert to seconds
            timeRemaining.value = timeLimit.value;
        }
        
        // Check if user has already taken this quiz
        const hasExistingScore = await checkExistingScore();
        if (hasExistingScore) {
            quizAlreadyTaken.value = true;
        }
        
    } catch (error) {
        console.error('Error loading quiz:', error);
        router.push('/user-dashboard');
    } finally {
        loading.value = false;
    }
};

const startQuiz = async () => {
    checkingScore.value = true;
    
    // Check if user already has a score for this quiz
    const hasExistingScore = await checkExistingScore();
    
    checkingScore.value = false;
    
    if (hasExistingScore) {
        quizAlreadyTaken.value = true;
        return;
    }
    
    quizStarted.value = true;
    if (timeLimit.value) {
        startTimer();
    }
};

const checkExistingScore = async () => {
    try {
        const userData = JSON.parse(localStorage.getItem('userData'));
        const token = userData?.access_token;
        
        if (!token) {
            console.error('No authentication token found');
            return false;
        }
        
        // Get user ID from the JWT token
        let userId = null;
        try {
            userId = userData?.user_id;
        } catch (e) {
            console.error('Could not decode JWT token:', e);
            return false;
        }
        
        if (!userId) {
            console.error('No user ID found in token');
            return false;
        }
        
        // Check if user already has a score for this quiz
        const response = await fetch(`http://localhost:5000/users/${userId}/scores`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const scores = await response.json();
            const existingScore = scores.find(score => score.quiz_id === currentQuiz.value.id);
            
            if (existingScore) {
                console.log('Existing score found:', existingScore);
                return true;
            }
        }
        
        return false;
    } catch (error) {
        console.error('Error checking existing score:', error);
        return false;
    }
};

const startTimer = () => {
    timer.value = setInterval(() => {
        timeRemaining.value--;
        if (timeRemaining.value <= 0) {
            clearInterval(timer.value);
            submitQuiz();
        }
    }, 1000);
};

const selectAnswer = (answerIndex) => {
    if (showResults.value) return;
    
    selectedAnswer.value = answerIndex;
    answers.value[currentQuestionIndex.value] = answerIndex;
};

const nextQuestion = () => {
    if (currentQuestionIndex.value < currentQuiz.value.questions.length - 1) {
        currentQuestionIndex.value++;
        selectedAnswer.value = answers.value[currentQuestionIndex.value];
    }
};

const previousQuestion = () => {
    if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--;
        selectedAnswer.value = answers.value[currentQuestionIndex.value];
    }
};

const goToQuestion = (index) => {
    currentQuestionIndex.value = index;
    selectedAnswer.value = answers.value[index];
};

const submitQuiz = () => {
    if (timer.value) {
        clearInterval(timer.value);
    }
    
    // Calculate score
    let correctAnswers = 0;
    console.log('Calculating score for quiz:', currentQuiz.value.id);
    console.log('Answers:', answers.value);
    
    currentQuiz.value.questions.forEach((question, index) => {
        // correct_option is already the index (1, 2, 3, or 4)
        const correctOptionIndex = question.correct_option;
        const userAnswer = answers.value[index];
        
        console.log(`Question ${index + 1}: User answered ${userAnswer} (type: ${typeof userAnswer}), Correct is ${correctOptionIndex} (type: ${typeof correctOptionIndex})`);
        
        // Convert both to numbers for comparison
        const userAnswerNum = Number(userAnswer);
        const correctOptionNum = Number(correctOptionIndex);
        
        console.log(`Converted: User answered ${userAnswerNum}, Correct is ${correctOptionNum}`);
        
        if (userAnswerNum === correctOptionNum) {
            correctAnswers++;
            console.log(`✓ Correct!`);
        } else {
            console.log(`✗ Wrong`);
        }
    });
    
    console.log(`Final score: ${correctAnswers}/${currentQuiz.value.questions.length}`);
    score.value = correctAnswers;
    showResults.value = true;
    
    // Send results to backend
    saveResults();
};

const saveResults = async () => {
    try {
        const userData = JSON.parse(localStorage.getItem('userData'));
        const token = userData?.access_token;
        
        if (!token) {
            console.error('No authentication token found');
            return;
        }
        
        // Get user ID from the JWT token or userData
        let userId = null;
        try {
            // Try to decode the JWT token to get user ID
            const tokenPayload = JSON.parse(atob(token.split('.')[1]));
            userId = tokenPayload.id;
        } catch (e) {
            console.error('Could not decode JWT token:', e);
        }
        
        const requestBody = {
            quiz_id: currentQuiz.value.id,
            total_scored: score.value
        };
        
        // Add user_id if we have it
        if (userId) {
            requestBody.user_id = userId;
        }
        
        console.log('Sending score data:', requestBody);
        
        const response = await fetch('http://localhost:5000/score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            console.error('Failed to save results');
            const errorData = await response.json();
            console.error('Error details:', errorData);
        } else {
            console.log('Score saved successfully:', score.value);
        }
    } catch (error) {
        console.error('Error saving results:', error);
    }
};

const reviewAnswers = () => {
    showResults.value = false;
    currentQuestionIndex.value = 0;
    selectedAnswer.value = answers.value[0];
};

const goBack = () => {
    localStorage.removeItem('currentQuiz');
    router.push('/user-dashboard');
};

const formatDuration = (minutes) => {
    if (!minutes) return 'No time limit';
    
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    }
    return `${mins} minutes`;
};

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

onMounted(() => {
    loadQuiz();
});

onUnmounted(() => {
    if (timer.value) {
        clearInterval(timer.value);
    }
});
</script>

<style scoped>
.quiz-view {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.quiz-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

/* Instructions */
.quiz-instructions {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
}

.instructions-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    max-width: 600px;
    width: 100%;
}

.instructions-card h2 {
    color: #2c3e50;
    text-align: center;
    margin-bottom: 0.5rem;
}

.chapter-info {
    text-align: center;
    color: #667eea;
    font-weight: 600;
    margin-bottom: 2rem;
}

.quiz-info {
    margin-bottom: 2rem;
}

.info-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.info-item:last-child {
    border-bottom: none;
}

.info-item .label {
    color: #666;
    font-weight: 500;
}

.info-item .value {
    color: #2c3e50;
    font-weight: 600;
}

.instructions-text h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

.instructions-text ul {
    color: #666;
    line-height: 1.6;
}

.instructions-text li {
    margin-bottom: 0.5rem;
}

.start-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 2rem;
}

.already-taken-message {
    margin-top: 2rem;
}

.message-card {
    background: rgba(231, 76, 60, 0.1);
    border: 2px solid #e74c3c;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
}

.message-card h3 {
    color: #e74c3c;
    margin-bottom: 1rem;
}

.message-card p {
    color: #666;
    margin-bottom: 1.5rem;
}

.start-btn {
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
}

.back-btn {
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
}

/* Loading */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    color: white;
}

.loader {
    width: 50px;
    height: 50px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-top: 5px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Quiz Interface */
.quiz-interface {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.quiz-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid rgba(0, 0, 0, 0.05);
}

.quiz-progress {
    flex: 1;
}

.progress-text {
    display: block;
    color: #2c3e50;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    transition: width 0.3s ease;
}

.timer {
    background: #e74c3c;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 600;
}

/* Question */
.question-container {
    margin-bottom: 2rem;
}

.question-text {
    color: #2c3e50;
    font-size: 1.3rem;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.options-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.option-item {
    display: flex;
    align-items: center;
    padding: 1rem;
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.option-item:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
}

.option-item.selected {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.1);
}

.option-item.correct {
    border-color: #27ae60;
    background: rgba(39, 174, 96, 0.1);
}

.option-item.incorrect {
    border-color: #e74c3c;
    background: rgba(231, 76, 60, 0.1);
}

.option-label {
    background: #667eea;
    color: white;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    margin-right: 1rem;
    flex-shrink: 0;
}

.option-item.correct .option-label {
    background: #27ae60;
}

.option-item.incorrect .option-label {
    background: #e74c3c;
}

.option-text {
    color: #2c3e50;
    font-size: 1.1rem;
    flex: 1;
}

/* Navigation */
.quiz-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid rgba(0, 0, 0, 0.05);
}

.question-indicators {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
}

.indicator {
    width: 35px;
    height: 35px;
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.indicator:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.1);
}

.indicator.answered {
    background: #667eea;
    color: white;
    border-color: #667eea;
}

.indicator.current {
    border-color: #e74c3c;
    background: #e74c3c;
    color: white;
}

.submit-btn {
    background: #e74c3c;
}

.submit-btn:hover {
    background: #c0392b;
}

/* Results */
.results-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
}

.results-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 3rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    text-align: center;
    max-width: 500px;
    width: 100%;
}

.results-card h2 {
    color: #2c3e50;
    margin-bottom: 2rem;
}

.score-display {
    margin-bottom: 2rem;
}

.score-circle {
    display: inline-block;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
}

.score-number {
    font-size: 2.5rem;
    font-weight: 700;
}

.score-total {
    font-size: 1rem;
    opacity: 0.8;
}

.score-percentage {
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
}

.results-summary {
    margin-bottom: 2rem;
}

.summary-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
}

.summary-item .label {
    color: #666;
}

.summary-item .value.correct {
    color: #27ae60;
    font-weight: 600;
}

.summary-item .value.incorrect {
    color: #e74c3c;
    font-weight: 600;
}

.results-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

/* Button Styles */
.primary-btn, .secondary-btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.primary-btn {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

.primary-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #5a6fd8, #6a4190);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.primary-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.secondary-btn {
    background: rgba(255, 255, 255, 0.9);
    color: #667eea;
    border: 2px solid #667eea;
}

.secondary-btn:hover:not(:disabled) {
    background: #667eea;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.secondary-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* Responsive */
@media (max-width: 768px) {
    .quiz-container {
        padding: 1rem;
    }
    
    .quiz-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }
    
    .quiz-navigation {
        flex-direction: column;
        gap: 1rem;
    }
    
    .question-indicators {
        order: -1;
    }
    
    .start-actions {
        flex-direction: column;
    }
}
</style> 