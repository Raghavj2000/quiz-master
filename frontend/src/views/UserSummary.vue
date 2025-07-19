<template>
   <Navbar />
   <div class="user-summary">
     <div class="container">
       <h1>My Quiz Summary</h1>
       
       <div v-if="loading" class="loading">
         <p>Loading your quiz summary...</p>
       </div>
       
       <div v-else-if="error" class="error">
         <p>{{ error }}</p>
       </div>
       
       <div v-else class="summary-content">
        
        <div class="bar_line_chart_container">
          
            <div class="subject_header">
                <h2>Subject-wise Quiz Summary</h2>
                <div class="chart-container">
                    <canvas ref="subjectChartCanvas"></canvas>
                </div>
            </div>
        </div>
        <div class="pie_chart_container">
            <div class="montly_header">
                <h2>Monthly Quiz Summary</h2>
                <div class="chart-container">
                    <canvas ref="monthlyChartCanvas"></canvas>
                </div>
            </div>
        </div>
         
       </div>
     </div>
   </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import Navbar from '@/components/Navbar.vue';

// Register Chart.js components
Chart.register(...registerables);

const API_BASE_URL = 'http://localhost:5000';

const loading = ref(true);
const error = ref(null);
const subjectSummary = ref([]);
const totalSubjectsWithQuizzes = ref(0);
const subjectChartCanvas = ref(null);
const monthlyChartCanvas = ref(null);
let subjectChart = null;
let monthlyChart = null;
const monthlySummary = ref([]);
const totalMonthsWithQuizzes = ref(0);

const totalSubjects = computed(() => totalSubjectsWithQuizzes.value);
const totalQuizzes = computed(() => {
  return subjectSummary.value.reduce((total, subject) => total + subject.quiz_count, 0);
});

const createSubjectChart = () => {
  console.log('Creating chart...');
  console.log('Canvas ref:', subjectChartCanvas.value);
  console.log('Subject summary:', subjectSummary.value);
  
  if (!subjectChartCanvas.value) {
    console.log('Canvas not found, retrying...');
    setTimeout(createSubjectChart, 100);
    return;
  }
  
  if (subjectSummary.value.length === 0) {
    console.log('No subject data available');
    return;
  }

  // Destroy existing chart if it exists
  if (subjectChart) {
    subjectChart.destroy();
  }

  const ctx = subjectChartCanvas.value.getContext('2d');
  console.log('Canvas context:', ctx);
  
  const labels = subjectSummary.value.map(subject => subject.subject_name);
  const data = subjectSummary.value.map(subject => subject.quiz_count);
  
  console.log('Chart labels:', labels);
  console.log('Chart data:', data);

  try {
    subjectChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Number of Quizzes',
          data: data,
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(255, 107, 107, 0.8)',
            'rgba(255, 193, 7, 0.8)',
            'rgba(40, 167, 69, 0.8)',
            'rgba(23, 162, 184, 0.8)'
          ],
          borderColor: [
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)',
            'rgba(255, 107, 107, 1)',
            'rgba(255, 193, 7, 1)',
            'rgba(40, 167, 69, 1)',
            'rgba(23, 162, 184, 1)'
          ],
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
          barThickness: 40,
          maxBarThickness: 50
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: '#333',
              font: {
                size: 14,
                weight: 'bold'
              }
            }
          },
          title: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              color: '#333',
              font: {
                size: 12
              }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            }
          },
          x: {
            ticks: {
              color: '#333',
              font: {
                size: 12
              }
            },
            grid: {
              display: false
            }
          }
        },
        elements: {
          bar: {
            categoryPercentage: 0.6,
            barPercentage: 0.8
          }
        }
      }
    });
    console.log('Chart created successfully:', subjectChart);
  } catch (error) {
    console.error('Error creating chart:', error);
  }
};

const createMonthlyChart = () => {
  console.log('Creating monthly chart...');
  console.log('Monthly canvas ref:', monthlyChartCanvas.value);
  console.log('Monthly summary:', monthlySummary.value);
  
  if (!monthlyChartCanvas.value) {
    console.log('Monthly canvas not found, retrying...');
    setTimeout(createMonthlyChart, 100);
    return;
  }
  
  if (monthlySummary.value.length === 0) {
    console.log('No monthly data available');
    return;
  }

  // Destroy existing chart if it exists
  if (monthlyChart) {
    monthlyChart.destroy();
  }

  const ctx = monthlyChartCanvas.value.getContext('2d');
  console.log('Monthly canvas context:', ctx);
  
  const labels = monthlySummary.value.map(item => {
    const [year, month] = item.month.split('-');
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return `${monthNames[parseInt(month) - 1]} ${year}`;
  });
  const data = monthlySummary.value.map(item => item.quiz_count);
  
  console.log('Monthly chart labels:', labels);
  console.log('Monthly chart data:', data);

  try {
    monthlyChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(255, 107, 107, 0.8)',
            'rgba(255, 193, 7, 0.8)',
            'rgba(40, 167, 69, 0.8)',
            'rgba(23, 162, 184, 0.8)',
            'rgba(220, 53, 69, 0.8)',
            'rgba(40, 167, 69, 0.8)',
            'rgba(255, 193, 7, 0.8)',
            'rgba(23, 162, 184, 0.8)',
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)'
          ],
          borderColor: [
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)',
            'rgba(255, 107, 107, 1)',
            'rgba(255, 193, 7, 1)',
            'rgba(40, 167, 69, 1)',
            'rgba(23, 162, 184, 1)',
            'rgba(220, 53, 69, 1)',
            'rgba(40, 167, 69, 1)',
            'rgba(255, 193, 7, 1)',
            'rgba(23, 162, 184, 1)',
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)'
          ],
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
            labels: {
              color: '#333',
              font: {
                size: 12,
                weight: 'bold'
              },
              padding: 20
            }
          },
          title: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return `${label}: ${value} quizzes (${percentage}%)`;
              }
            }
          }
        }
      }
    });
    console.log('Monthly chart created successfully:', monthlyChart);
  } catch (error) {
    console.error('Error creating monthly chart:', error);
  }
};

const fetchUserSubjectSummary = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const userData = JSON.parse(localStorage.getItem('userData'));
    const token = userData?.access_token;
    const userId = userData?.user_id;
    
    console.log('User data:', userData);
    console.log('Token:', token);
    console.log('User ID:', userId);
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    if (!userId) {
      throw new Error('User ID not found');
    }
    
    const response = await fetch(`${API_BASE_URL}/summary/user/${userId}/subject-quizzes`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to fetch summary: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Subject summary data:', data);
    
    subjectSummary.value = data.subject_summary || [];
    totalSubjectsWithQuizzes.value = data.total_subjects_with_quizzes || 0;
    
    console.log('Updated subject summary:', subjectSummary.value);
    
    // Create chart after data is loaded with a small delay to ensure DOM is ready
    await nextTick();
    setTimeout(() => {
      createSubjectChart();
    }, 200);
    
  } catch (err) {
    console.error('Error fetching user subject summary:', err);
    error.value = err.message || 'Failed to load quiz summary';
  } finally {
    loading.value = false;
  }
};

const fetchUserMonthlySummary = async () => {
  try {
    const userData = JSON.parse(localStorage.getItem('userData'));
    const token = userData?.access_token;
    const userId = userData?.user_id;
    
    console.log('Fetching monthly summary for user:', userId);
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    if (!userId) {
      throw new Error('User ID not found');
    }
    
    const response = await fetch(`${API_BASE_URL}/summary/user/${userId}/monthly-quizzes`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to fetch monthly summary: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Monthly summary data:', data);
    
    monthlySummary.value = data.monthly_summary || [];
    totalMonthsWithQuizzes.value = data.total_months_with_quizzes || 0;
    
    console.log('Updated monthly summary:', monthlySummary.value);
    
    // Create monthly chart after data is loaded
    await nextTick();
    setTimeout(() => {
      createMonthlyChart();
    }, 200);
    
  } catch (err) {
    console.error('Error fetching user monthly summary:', err);
    // Don't set error state for monthly data, just log it
  }
};

onMounted(() => {
  console.log('Component mounted');
  fetchUserSubjectSummary();
  fetchUserMonthlySummary(); // Fetch monthly summary on mount
  
  // Fallback chart creation after a longer delay
  setTimeout(() => {
    if (subjectSummary.value.length > 0 && !subjectChart) {
      console.log('Fallback subject chart creation');
      createSubjectChart();
    }
    if (monthlySummary.value.length > 0 && !monthlyChart) {
      console.log('Fallback monthly chart creation');
      createMonthlyChart();
    }
  }, 1000);
});
</script>

<style scoped>
.user-summary {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

h1 {
  text-align: center;
  color: white;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  font-weight: 700;
}

.loading, .error {
  text-align: center;
  color: white;
  font-size: 1.2rem;
  margin-top: 3rem;
}

.error {
  color: #ff6b6b;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.bar_line_chart_container, .pie_chart_container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.subject_header, .montly_header {
  margin-bottom: 1.5rem;
}

.subject_header h2, .montly_header h2 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.8rem;
  font-weight: 600;
}

.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.summary-card h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  font-weight: 600;
}

.no-data {
  text-align: center;
  color: #666;
  font-size: 1.1rem;
  padding: 2rem;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.subject-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border-left: 4px solid #667eea;
  transition: transform 0.2s ease;
}

.subject-item:hover {
  transform: translateY(-2px);
}

.subject-item h3 {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.quiz-count {
  color: #667eea;
  font-weight: 500;
  margin: 0;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  color: #666;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  font-weight: 500;
}

.stat-number {
  color: #667eea;
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
}

@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .subjects-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-stats {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>
