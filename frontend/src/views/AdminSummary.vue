<template>
  <div class="admin-summary">
    <Navbar />
    <div class="summary-container">
      <h1>Admin Summary Dashboard</h1>
      
      <div class="chart-section">
        <h2>Subject Top Scores</h2>
        <div class="chart-container">
          <canvas ref="subjectTopScoresChart"></canvas>
        </div>
        <div v-if="loading" class="loading">
          <Loader />
        </div>
        <div v-if="error" class="error">
          {{ error }}
        </div>
      </div>

      <div class="chart-section">
        <h2>Subject User Attempts</h2>
        <div class="chart-container">
          <canvas ref="subjectUserAttemptsChart"></canvas>
        </div>
        <div v-if="loadingAttempts" class="loading">
          <Loader />
        </div>
        <div v-if="errorAttempts" class="error">
          {{ errorAttempts }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import Loader from '../components/Loader.vue';
import axios from 'axios';
import { Chart, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

export default {
  components: {
    Navbar,
    Loader
  },
  data() {
    return {
      loading: true,
      loadingAttempts: true,
      error: null,
      errorAttempts: null,
      subjectTopScores: [],
      subjectUserAttempts: [],
      chart: null,
      pieChart: null
    };
  },
  methods: {
    async fetchSubjectTopScores() {
      try {
        this.loading = true;
        this.error = null;
        
        const userData = JSON.parse(localStorage.getItem("userData"));
        const token = userData?.access_token;
        
        if (!token) {
          throw new Error('No authentication token found');
        }

        const response = await axios.get('http://localhost:5000/summary/admin/subject-top-scores', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        this.subjectTopScores = response.data.subject_top_scores;
        this.createChart();
      } catch (error) {
        console.error('Error fetching subject top scores:', error);
        this.error = error.response?.data?.error || 'Failed to fetch subject top scores';
      } finally {
        this.loading = false;
      }
    },

    async fetchSubjectUserAttempts() {
      try {
        this.loadingAttempts = true;
        this.errorAttempts = null;
        
        const userData = JSON.parse(localStorage.getItem("userData"));
        const token = userData?.access_token;
        
        if (!token) {
          throw new Error('No authentication token found');
        }

        const response = await axios.get('http://localhost:5000/summary/admin/subject-user-attempts', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        this.subjectUserAttempts = response.data.subject_user_attempts;
        this.createPieChart();
      } catch (error) {
        console.error('Error fetching subject user attempts:', error);
        this.errorAttempts = error.response?.data?.error || 'Failed to fetch subject user attempts';
      } finally {
        this.loadingAttempts = false;
      }
    },

    createChart() {
      if (this.chart) {
        this.chart.destroy();
      }

      const ctx = this.$refs.subjectTopScoresChart;
      if (!ctx) return;

      const labels = this.subjectTopScores.map(item => item.subject_name);
      const scores = this.subjectTopScores.map(item => item.top_score);
      const percentages = this.subjectTopScores.map(item => item.percentage || 0);
      const users = this.subjectTopScores.map(item => item.full_name);

      this.chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Top Score',
              data: scores,
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1,
              yAxisID: 'y',
              barThickness: 30,
              maxBarThickness: 40
            },
            {
              label: 'Percentage (%)',
              data: percentages,
              backgroundColor: 'rgba(255, 99, 132, 0.8)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1,
              yAxisID: 'y1',
              type: 'line'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Subject Top Scores and Percentages',
              font: {
                size: 16
              }
            },
            tooltip: {
              callbacks: {
                afterBody: function(context) {
                  const dataIndex = context[0].dataIndex;
                  const user = users[dataIndex];
                  return `Top Student: ${user}`;
                }
              }
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Subjects'
              }
            },
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: {
                display: true,
                text: 'Score'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: {
                display: true,
                text: 'Percentage (%)'
              },
              grid: {
                drawOnChartArea: false,
              },
              max: 100
            }
          }
        }
      });
    },

    createPieChart() {
      if (this.pieChart) {
        this.pieChart.destroy();
      }

      const ctx = this.$refs.subjectUserAttemptsChart;
      if (!ctx) return;

      const labels = this.subjectUserAttempts.map(item => item.subject_name);
      const data = this.subjectUserAttempts.map(item => item.unique_users);

      // Generate colors for each subject
      const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)'
      ];

      this.pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: colors.slice(0, labels.length),
            borderColor: colors.slice(0, labels.length).map(color => color.replace('0.8', '1')),
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Distribution of User Attempts by Subject',
              font: {
                size: 16
              }
            },
            legend: {
              position: 'bottom',
              labels: {
                padding: 20,
                usePointStyle: true
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || '';
                  const value = context.parsed;
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${value} users (${percentage}%)`;
                }
              }
            }
          }
        }
      });
    }
  },
  mounted() {
    this.fetchSubjectTopScores();
    this.fetchSubjectUserAttempts();
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
    if (this.pieChart) {
      this.pieChart.destroy();
    }
  }
};
</script>

<style scoped>
.admin-summary {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.summary-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.summary-container h1 {
  text-align: center;
  color: white;
  margin-bottom: 2rem;
  font-size: 2.5rem;
  font-weight: 700;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.chart-section h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.chart-container {
  position: relative;
  height: 400px;
  margin-bottom: 1rem;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.error {
  color: #dc3545;
  text-align: center;
  padding: 1rem;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin-top: 1rem;
}
</style>