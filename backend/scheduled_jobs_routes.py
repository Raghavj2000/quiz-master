from flask import Blueprint, request, jsonify, render_template_string
from models import db, Score, Quiz, Chapter, Subject, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

scheduled_jobs_bp = Blueprint('scheduled_jobs_bp', __name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'projectaaron11@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'projectaaron1122')

def send_email(to_email, subject, html_content):
    """Send HTML email"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def generate_monthly_report_html(user_id, month_year):
    """Generate HTML content for monthly report"""
    
    # Get user details
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Parse month_year (format: "2024-01")
    try:
        report_date = datetime.strptime(month_year, "%Y-%m")
        start_date = report_date.replace(day=1)
        if report_date.month == 12:
            end_date = report_date.replace(year=report_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = report_date.replace(month=report_date.month + 1, day=1) - timedelta(days=1)
    except:
        return None
    
    # Get monthly quiz data
    monthly_scores = db.session.query(
        Score.id,
        Score.total_scored,
        Score.total_questions,
        Score.timestamp,
        Quiz.name.label('quiz_name'),
        Chapter.name.label('chapter_name'),
        Subject.name.label('subject_name')
    ).join(
        Quiz, Score.quiz_id == Quiz.id
    ).join(
        Chapter, Quiz.chapter_id == Chapter.id
    ).join(
        Subject, Chapter.subject_id == Subject.id
    ).filter(
        Score.user_id == user_id,
        Score.timestamp >= start_date,
        Score.timestamp <= end_date
    ).order_by(
        Score.timestamp.desc()
    ).all()
    
    # Calculate statistics
    total_quizzes = len(monthly_scores)
    total_questions = sum(score.total_questions for score in monthly_scores)
    total_scored = sum(score.total_scored for score in monthly_scores)
    average_score = round((total_scored / total_questions * 100), 2) if total_questions > 0 else 0
    
    # Get subject-wise breakdown
    subject_stats = {}
    for score in monthly_scores:
        subject = score.subject_name
        if subject not in subject_stats:
            subject_stats[subject] = {'quizzes': 0, 'total_scored': 0, 'total_questions': 0}
        subject_stats[subject]['quizzes'] += 1
        subject_stats[subject]['total_scored'] += score.total_scored
        subject_stats[subject]['total_questions'] += score.total_questions
    
    # Calculate subject averages
    for subject in subject_stats:
        stats = subject_stats[subject]
        stats['average'] = round((stats['total_scored'] / stats['total_questions'] * 100), 2) if stats['total_questions'] > 0 else 0
    
    # Get ranking data (position among all users for each quiz)
    quiz_rankings = {}
    for score in monthly_scores:
        quiz_id = score.id
        # Get all scores for this quiz and find user's rank
        all_quiz_scores = db.session.query(
            Score.user_id,
            Score.total_scored,
            Score.total_questions,
            func.rank().over(order_by=desc(Score.total_scored)).label('rank')
        ).filter(
            Score.quiz_id == quiz_id
        ).all()
        
        user_rank = next((s.rank for s in all_quiz_scores if s.user_id == user_id), None)
        if user_rank:
            quiz_rankings[quiz_id] = user_rank
    
    # Generate HTML
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Monthly Quiz Report - {{ month_year }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
            .header h1 { color: #007bff; margin: 0; }
            .user-info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #007bff; color: white; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-card h3 { margin: 0 0 10px 0; font-size: 2em; }
            .stat-card p { margin: 0; opacity: 0.9; }
            .section { margin-bottom: 30px; }
            .section h2 { color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; font-weight: bold; }
            .score-good { color: #28a745; font-weight: bold; }
            .score-average { color: #ffc107; font-weight: bold; }
            .score-poor { color: #dc3545; font-weight: bold; }
            .rank-badge { background: #007bff; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }
            .subject-card { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
            .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Monthly Quiz Report</h1>
                <p>{{ month_year }}</p>
            </div>
            
            <div class="user-info">
                <h3>👤 User Information</h3>
                <p><strong>Name:</strong> {{ user.full_name or user.username }}</p>
                <p><strong>Username:</strong> {{ user.username }}</p>
                <p><strong>Qualification:</strong> {{ user.qualification or 'Not specified' }}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{{ total_quizzes }}</h3>
                    <p>Quizzes Taken</p>
                </div>
                <div class="stat-card">
                    <h3>{{ average_score }}%</h3>
                    <p>Average Score</p>
                </div>
            </div>
            
            {% if subject_stats %}
            <div class="section">
                <h2>📚 Subject-wise Performance</h2>
                {% for subject, stats in subject_stats.items() %}
                <div class="subject-card">
                    <h4>{{ subject }}</h4>
                    <p><strong>Quizzes:</strong> {{ stats.quizzes }} | 
                       <strong>Average:</strong> {{ stats.average }}% | 
                       <strong>Score:</strong> {{ stats.total_scored }}/{{ stats.total_questions }}</p>
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if monthly_scores %}
            <div class="section">
                <h2>📝 Quiz Details</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Subject</th>
                            <th>Chapter</th>
                            <th>Quiz</th>
                            <th>Score</th>
                            <th>Percentage</th>
                            <th>Rank</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for score in monthly_scores %}
                        <tr>
                            <td>{{ score.timestamp.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td>{{ score.subject_name }}</td>
                            <td>{{ score.chapter_name }}</td>
                            <td>{{ score.quiz_name }}</td>
                            <td>{{ score.total_scored }}/{{ score.total_questions }}</td>
                            <td class="{% if (score.total_scored/score.total_questions*100) >= 80 %}score-good{% elif (score.total_scored/score.total_questions*100) >= 60 %}score-average{% else %}score-poor{% endif %}">
                                {{ "%.1f"|format(score.total_scored/score.total_questions*100) }}%
                            </td>
                            <td>
                                {% if score.id in quiz_rankings %}
                                <span class="rank-badge">#{{ quiz_rankings[score.id] }}</span>
                                {% else %}
                                N/A
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            <div class="footer">
                <p>This report was generated automatically on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</p>
                <p>Keep up the great work! 🚀</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, 
                                user=user, 
                                month_year=month_year,
                                total_quizzes=total_quizzes,
                                total_questions=total_questions,
                                total_scored=total_scored,
                                average_score=average_score,
                                subject_stats=subject_stats,
                                monthly_scores=monthly_scores,
                                quiz_rankings=quiz_rankings,
                                datetime=datetime)

@scheduled_jobs_bp.route('/scheduled/generate-monthly-report', methods=['POST'])
@jwt_required()
def generate_monthly_report():
    """
    Generate and send monthly report for a user
    """
    current_user = get_jwt_identity()
    
    # Check if current user is admin
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    month_year = data.get('month_year')  # Format: "2024-01"
    email = data.get('email')
    
    if not user_id or not month_year or not email:
        return jsonify({'error': 'user_id, month_year, and email are required'}), 400
    
    try:
        # Generate HTML report
        html_content = generate_monthly_report_html(user_id, month_year)
        
        if not html_content:
            return jsonify({'error': 'Failed to generate report or user not found'}), 400
        
        # Send email
        subject = f"Monthly Quiz Report - {month_year}"
        email_sent = send_email(email, subject, html_content)
        
        if email_sent:
            return jsonify({
                'message': 'Monthly report generated and sent successfully',
                'user_id': user_id,
                'month_year': month_year,
                'email': email
            }), 200
        else:
            return jsonify({'error': 'Report generated but email sending failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error generating report: {str(e)}'}), 400 