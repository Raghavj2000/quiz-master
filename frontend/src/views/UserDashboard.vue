<template>
    <div class="user-dashboard">
        <Navbar />
        
        <div class="dashboard-container">
            <div class="dashboard-header">
                <h1>Welcome to Quiz Master</h1>
                <p>Select a quiz to start testing your knowledge</p>
            </div>

            <!-- Tab Navigation -->
            <div class="tab-navigation">
                <button 
                    @click="activeTab = 'quizzes'" 
                    :class="['tab-button', { active: activeTab === 'quizzes' }]"
                >
                    Available Quiz
                </button>
                <button 
                    @click="activeTab = 'history'" 
                    :class="['tab-button', { active: activeTab === 'history' }]"
                >
                    My Quiz History
                </button>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="loading-container">
                <div class="loader"></div>
                <p>Loading quizzes...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="error-container">
                <div class="error-message">
                    <h3>Oops! Something went wrong</h3>
                    <p>{{ error }}</p>
                    <button @click="fetchQuizzes" class="primary-btn">
                        Try Again
                    </button>
                </div>
            </div>

            <!-- Quiz List -->
            <div v-else-if="activeTab === 'quizzes'" class="quiz-grid">
                <div v-if="quizzes.length === 0" class="no-quizzes">
                    <h3>No quizzes available</h3>
                    <p>Check back later for new quizzes!</p>
                </div>
                
                <div 
                    v-for="quiz in quizzes" 
                    :key="quiz.id" 
                    class="quiz-card"
                >
                    <div class="quiz-header">
                        <h3>{{ quiz.name }}</h3>
                        <span class="chapter-badge">{{ quiz.chapter_name }}</span>
                    </div>
                    
                    <div class="quiz-details">
                        <div class="detail-item">
                            <span class="label">Duration:</span>
                            <span class="value">{{ formatDuration(quiz.time_duration) }}</span>
                        </div>
                        
                        <div v-if="quiz.date_of_quiz" class="detail-item">
                            <span class="label">Date:</span>
                            <span class="value">{{ formatDate(quiz.date_of_quiz) }}</span>
                        </div>
                        
                        <div v-if="quiz.remarks" class="detail-item">
                            <span class="label">Notes:</span>
                            <span class="value">{{ quiz.remarks }}</span>
                        </div>
                        
                        <div class="detail-item">
                            <span class="label">Questions:</span>
                            <span class="value">{{ quiz.questions.length }}</span>
                        </div>
                    </div>
                    
                    <div class="quiz-actions">
                        <button 
                            @click="startQuiz(quiz)" 
                            class="primary-btn"
                            :disabled="quiz.questions.length === 0"
                        >
                            {{ quiz.questions.length === 0 ? 'No Questions Available' : 'Start Quiz' }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Quiz History -->
            <div v-else-if="activeTab === 'history'" class="history-container">
                <div v-if="myScores.length === 0" class="no-history">
                    <h3>No quiz history yet</h3>
                    <p>Complete your first quiz to see your results here!</p>
                </div>
                
                <div v-else class="score-grid">
                    <div 
                        v-for="score in myScores" 
                        :key="score.id" 
                        class="score-card"
                    >
                        <div class="score-header">
                            <h3>{{ score.quiz_name || `Quiz ${score.quiz_id}` || 'Unknown Quiz' }}</h3>
                            <span class="score-badge" :class="getScoreClass(score.percentage)">
                                {{ score.percentage }}%
                            </span>
                        </div>
                        
                        <div class="score-details">
                            <div class="detail-item">
                                <span class="label">Score:</span>
                                <span class="value">{{ score.total_scored }}/{{ score.total_questions || '?' }}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="label">Date:</span>
                                <span class="value">{{ formatDateTime(score.timestamp) }}</span>
                            </div>
                        </div>
                        
                        <div class="score-progress">
                            <div class="progress-bar">
                                <div 
                                    class="progress-fill" 
                                    :style="{ width: `${score.percentage || 0}%` }"
                                    :class="getScoreClass(score.percentage || 0)"
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Navbar from '@/components/Navbar.vue';

const router = useRouter();
const quizzes = ref([]);
const myScores = ref([]);
const loading = ref(true);
const error = ref(null);
const activeTab = ref('quizzes'); // 'quizzes' or 'history'

const API_BASE_URL = 'http://localhost:5000';

const fetchQuizzes = async () => {
    loading.value = true;
    error.value = null;
    
    try {
        console.log('Fetching quizzes from:', `${API_BASE_URL}/quizzes`);
        
        const response = await fetch(`${API_BASE_URL}/quizzes`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Response error text:', errorText);
            throw new Error(`Failed to fetch quizzes: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Quizzes loaded:', data);
        quizzes.value = data;
    } catch (err) {
        console.error('Error fetching quizzes:', err);
        error.value = err.message || 'Failed to load quizzes';
    } finally {
        loading.value = false;
    }
};

const fetchMyScores = async () => {
    try {
        const userData = JSON.parse(localStorage.getItem('userData'));
        const token = userData?.access_token;
        
        if (!token) {
            throw new Error('No authentication token found');
        }

        const response = await fetch(`${API_BASE_URL}/my-scores`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch scores: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Scores data received:', data);
        console.log('First score details:', data[0] ? {
            id: data[0].id,
            quiz_id: data[0].quiz_id,
            total_scored: data[0].total_scored,
            total_questions: data[0].total_questions,
            percentage: data[0].percentage,
            timestamp: data[0].timestamp
        } : 'No scores');
        
        // Map scores with additional data from quizzes
        if (data.length > 0) {
            console.log('Mapping scores with quiz data...');
            const scoresWithData = data.map((score) => {
                // Find the quiz in our existing quizzes array
                const quiz = quizzes.value.find(q => q.id === score.quiz_id);
                return {
                    ...score,
                    quiz_name: quiz ? quiz.name : `Quiz ${score.quiz_id}`,
                    total_questions: score.total_questions || (quiz ? quiz.questions.length : null)
                };
            });
            
            myScores.value = scoresWithData;
        } else {
            myScores.value = data;
        }
    } catch (err) {
        console.error('Error fetching scores:', err);
        // Don't set error for scores, just log it
    }
};

const startQuiz = (quiz) => {
    if (quiz.questions.length === 0) {
        return;
    }
    
    // Store quiz data in localStorage for the quiz session
    localStorage.setItem('currentQuiz', JSON.stringify(quiz));
    
    // Navigate to quiz page (you'll need to create this route)
    router.push(`/quiz/${quiz.id}`);
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

const formatDate = (dateString) => {
    if (!dateString) return 'No date set';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return 'Unknown';
    
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const getScoreClass = (percentage) => {
    if (percentage >= 80) return 'excellent';
    if (percentage >= 60) return 'good';
    if (percentage >= 40) return 'average';
    return 'poor';
};

onMounted(async () => {
    console.log('UserDashboard mounted, fetching quizzes...');
    
    // Test if backend is reachable
    fetch(`${API_BASE_URL}/test`)
        .then(response => response.json())
        .then(data => console.log('Backend test response:', data))
        .catch(err => console.error('Backend test failed:', err));
    
    // Check quiz count
    fetch(`${API_BASE_URL}/quiz-count`)
        .then(response => response.json())
        .then(data => console.log('Quiz count:', data))
        .catch(err => console.error('Quiz count failed:', err));
    
    // Fetch quizzes first, then scores
    await fetchQuizzes();
    await fetchMyScores();
});
</script>

<style scoped>
.user-dashboard {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.dashboard-header {
    text-align: center;
    margin-bottom: 3rem;
    color: white;
}

.dashboard-header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}

.dashboard-header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

.tab-navigation {
    display: flex;
    justify-content: center;
    margin-bottom: 2rem;
    gap: 1rem;
}

.tab-button {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    font-size: 1rem;
}

.tab-button:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
}

.tab-button.active {
    background: white;
    color: #667eea;
    border-color: white;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    color: white;
}

.loading-container p {
    margin-top: 1rem;
    font-size: 1.1rem;
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

.error-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
}

.error-message {
    text-align: center;
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.error-message h3 {
    color: #e74c3c;
    margin-bottom: 1rem;
}

.error-message p {
    color: #666;
    margin-bottom: 1.5rem;
}

.quiz-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.quiz-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.quiz-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.quiz-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.quiz-header h3 {
    color: #2c3e50;
    font-size: 1.3rem;
    font-weight: 600;
    margin: 0;
    flex: 1;
}

.chapter-badge {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    white-space: nowrap;
    margin-left: 0.5rem;
}

.quiz-details {
    margin-bottom: 1.5rem;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.detail-item:last-child {
    border-bottom: none;
}

.detail-item .label {
    color: #666;
    font-weight: 500;
}

.detail-item .value {
    color: #2c3e50;
    font-weight: 600;
}

.quiz-actions {
    display: flex;
    justify-content: center;
}

.no-quizzes {
    grid-column: 1 / -1;
    text-align: center;
    background: rgba(255, 255, 255, 0.95);
    padding: 3rem;
    border-radius: 16px;
    color: #666;
}

.no-quizzes h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

/* History Styles */
.history-container {
    margin-top: 2rem;
}

.no-history {
    text-align: center;
    background: rgba(255, 255, 255, 0.95);
    padding: 3rem;
    border-radius: 16px;
    color: #666;
}

.no-history h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

.score-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
}

.score-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.score-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.score-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.score-header h3 {
    color: #2c3e50;
    font-size: 1.3rem;
    font-weight: 600;
    margin: 0;
    flex: 1;
}

.score-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    white-space: nowrap;
    margin-left: 0.5rem;
}

.score-badge.excellent {
    background: #27ae60;
    color: white;
}

.score-badge.good {
    background: #f39c12;
    color: white;
}

.score-badge.average {
    background: #e67e22;
    color: white;
}

.score-badge.poor {
    background: #e74c3c;
    color: white;
}

.score-details {
    margin-bottom: 1.5rem;
}

.score-progress {
    margin-top: 1rem;
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
    transition: width 0.3s ease;
}

.progress-fill.excellent {
    background: #27ae60;
}

.progress-fill.good {
    background: #f39c12;
}

.progress-fill.average {
    background: #e67e22;
}

.progress-fill.poor {
    background: #e74c3c;
}

/* Button Styles */
.primary-btn {
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

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard-container {
        padding: 1rem;
    }
    
    .dashboard-header h1 {
        font-size: 2rem;
    }
    
    .tab-navigation {
        flex-direction: column;
        align-items: center;
    }
    
    .tab-button {
        width: 100%;
        max-width: 300px;
    }
    
    .quiz-grid,
    .score-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .quiz-card,
    .score-card {
        padding: 1rem;
    }
    
    .quiz-header,
    .score-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .chapter-badge,
    .score-badge {
        margin-left: 0;
        margin-top: 0.5rem;
    }
}
</style>