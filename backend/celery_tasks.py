from celery import shared_task
from models import db, User
from datetime import datetime
import uuid
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template_string
from sqlalchemy import func, desc
from datetime import timedelta

# Import export tasks to ensure they're registered
import export_tasks

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'projectaaron11@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'xypc lhco tpoq bvza')

def send_email(to_email, subject, html_content):
    """Send HTML email"""
    try:
        print(f"Attempting to send email to: {to_email}")
        print(f"Using SMTP: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"Username: {SMTP_USERNAME}")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print("TLS started successfully")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("Login successful")
            server.send_message(msg)
            print("Message sent successfully")
        
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication failed: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error: {str(e)}")
        return False
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def generate_monthly_report_html(user_id, month_year):
    """Generate HTML content for monthly report"""
    
    print(f"🔍 generate_monthly_report_html called for user_id: {user_id}, month_year: {month_year}")
    
    # Get user details
    user = User.query.get(user_id)
    if not user:
        print(f"❌ User {user_id} not found")
        return None
    
    print(f"✅ User found: {user.username}")
    
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
    from models import Score, Quiz, Chapter, Subject
    
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
    total_questions = sum(score.total_questions or 0 for score in monthly_scores)
    total_scored = sum(score.total_scored or 0 for score in monthly_scores)
    average_score = round((total_scored / total_questions * 100), 2) if total_questions > 0 else 0
    
    print(f"📊 Found {total_quizzes} quizzes for user {user_id} in {month_year}")
    print(f"📊 Date range: {start_date} to {end_date}")
    print(f"📊 Total questions: {total_questions}, Total scored: {total_scored}")
    
    # Get subject-wise breakdown
    subject_stats = {}
    for score in monthly_scores:
        subject = score.subject_name
        if subject not in subject_stats:
            subject_stats[subject] = {'quizzes': 0, 'total_scored': 0, 'total_questions': 0}
        subject_stats[subject]['quizzes'] += 1
        subject_stats[subject]['total_scored'] += score.total_scored or 0
        subject_stats[subject]['total_questions'] += score.total_questions or 0
    
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
                            <td>{{ score.total_scored or 0 }}/{{ score.total_questions or 0 }}</td>
                            <td class="{% if score.total_questions and score.total_questions > 0 and (score.total_scored or 0)/(score.total_questions)*100 >= 80 %}score-good{% elif score.total_questions and score.total_questions > 0 and (score.total_scored or 0)/(score.total_questions)*100 >= 60 %}score-average{% else %}score-poor{% endif %}">
                                {% if score.total_questions and score.total_questions > 0 %}
                                    {{ "%.1f"|format((score.total_scored or 0)/(score.total_questions)*100) }}%
                                {% else %}
                                    0.0%
                                {% endif %}
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

@shared_task(bind=True)
def generate_user_report(self, user_id, month_year):
    """Generate monthly report for a specific user"""
    try:
        print(f"Generating report for user {user_id} for {month_year}")
        
        # Generate HTML report
        html_content = generate_monthly_report_html(user_id, month_year)
        
        if not html_content:
            print(f"No report content generated for user {user_id}")
            return f"No report generated for user {user_id}"
        
        print(f"Report generated successfully for user {user_id}")
        return {
            'user_id': user_id,
            'month_year': month_year,
            'html_content': html_content,
            'status': 'generated'
        }
    except Exception as e:
        print(f"Error generating report for user {user_id}: {str(e)}")
        raise

@shared_task(bind=True)
def send_report_email(self, user_id, month_year, html_content):
    """Send email with report for a specific user"""
    try:
        print(f"Sending email for user {user_id} for {month_year}")
        
        # Get user email
        user = User.query.get(user_id)
        if not user:
            print(f"User {user_id} not found")
            return f"User {user_id} not found"
        
        email = user.username  # Assuming username is email
        subject = f"Monthly Quiz Report - {month_year}"
        
        # Send email
        email_sent = send_email(email, subject, html_content)
        
        if email_sent:
            print(f"Email sent successfully to {email}")
            return {
                'user_id': user_id,
                'email': email,
                'month_year': month_year,
                'status': 'sent'
            }
        else:
            print(f"Failed to send email to {email}")
            return {
                'user_id': user_id,
                'email': email,
                'month_year': month_year,
                'status': 'failed'
            }
    except Exception as e:
        print(f"Error sending email for user {user_id}: {str(e)}")
        raise

@shared_task(bind=True)
def process_all_reports(self, month_year=None):
    """Process reports for all users"""
    try:
        # If month_year is not provided (called from scheduler), use current month
        if month_year is None:
            today = datetime.now()
            current_month = today.month
            current_year = today.year
            
            month_year = f"{current_year}-{current_month:02d}"
            print(f"Auto-detected month_year: {month_year} (current month)")
        
        print(f"Starting report generation for all users for {month_year}")
        
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users")
        
        results = []
        total_users = len(users)
        
        for i, user in enumerate(users, 1):
            try:
                print(f"Processing user {user.id} ({user.username}) - {i}/{total_users}")
                
                # Update task progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i,
                        'total': total_users,
                        'status': f'Processing user {user.username} ({i}/{total_users})'
                    }
                )
                
                # Generate report
                report_result = generate_user_report(user.id, month_year)
                
                if isinstance(report_result, dict) and report_result.get('html_content'):
                    # Send email
                    email_result = send_report_email(user.id, month_year, report_result['html_content'])
                    results.append({
                        'user_id': user.id,
                        'username': user.username,
                        'report_status': 'generated',
                        'email_status': email_result.get('status', 'unknown'),
                        'success': True
                    })
                    print(f"✅ Successfully processed user {user.username}")
                else:
                    results.append({
                        'user_id': user.id,
                        'username': user.username,
                        'report_status': 'failed',
                        'email_status': 'not_attempted',
                        'success': False,
                        'error': 'No report content generated'
                    })
                    print(f"❌ Failed to generate report for user {user.username}")
                    
            except Exception as e:
                print(f"Error processing user {user.id}: {str(e)}")
                results.append({
                    'user_id': user.id,
                    'username': user.username if user else 'unknown',
                    'report_status': 'error',
                    'email_status': 'not_attempted',
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate summary
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        print(f"Completed processing {len(results)} users")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        
        return {
            'message': f'Completed report generation for {len(users)} users',
            'summary': {
                'total_users': total_users,
                'successful': successful,
                'failed': failed,
                'success_rate': round((successful / total_users) * 100, 2) if total_users > 0 else 0
            },
            'results': results,
            'month_year': month_year
        }
    except Exception as e:
        print(f"Error processing all reports: {str(e)}")
        raise

@shared_task(bind=True)
def generate_and_send_user_report(self, user_id, month_year):
    """Generate and send report for a single user in one task"""
    try:
        print(f"Starting report generation and email for user {user_id} for {month_year}")
        
        # Get user details
        user = User.query.get(user_id)
        if not user:
            return {
                'user_id': user_id,
                'success': False,
                'error': 'User not found'
            }
        
        # Generate report
        html_content = generate_monthly_report_html(user_id, month_year)
        
        if not html_content:
            return {
                'user_id': user_id,
                'username': user.username,
                'success': False,
                'error': 'No report content generated'
            }
        
        # Send email
        email = user.username  # Assuming username is email
        subject = f"Monthly Quiz Report - {month_year}"
        email_sent = send_email(email, subject, html_content)
        
        if email_sent:
            print(f"✅ Successfully generated and sent report to {email}")
            return {
                'user_id': user_id,
                'username': user.username,
                'email': email,
                'month_year': month_year,
                'success': True,
                'status': 'Report generated and email sent successfully'
            }
        else:
            print(f"❌ Report generated but email failed for {email}")
            return {
                'user_id': user_id,
                'username': user.username,
                'email': email,
                'month_year': month_year,
                'success': False,
                'status': 'Report generated but email sending failed',
                'html_content': html_content  # Return HTML content for manual sending
            }
            
    except Exception as e:
        print(f"Error in generate_and_send_user_report for user {user_id}: {str(e)}")
        return {
            'user_id': user_id,
            'success': False,
            'error': str(e)
        }



@shared_task(bind=True)
def send_daily_quiz_reminders(self):
    """Send daily reminders about new quizzes to users"""
    try:
        print("Starting daily quiz reminders...")
        
        # Get today's date
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        # Find quizzes created today
        from models import Quiz, Chapter, Subject
        
        new_quizzes = db.session.query(
            Quiz.id,
            Quiz.name,
            Chapter.name.label('chapter_name'),
            Subject.name.label('subject_name')
        ).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Subject, Chapter.subject_id == Subject.id
        ).filter(
            Quiz.created_at >= start_of_day,
            Quiz.created_at <= end_of_day
        ).all()
        
        if not new_quizzes:
            print("No new quizzes found today")
            return {
                'status': 'SUCCESS',
                'message': 'No new quizzes found today',
                'quizzes_count': 0
            }
        
        print(f"Found {len(new_quizzes)} new quizzes today")
        
        # Get all users (excluding admins)
        users = User.query.filter(User.role != 'admin').all()
        
        # Prepare reminder message
        quiz_list = "\n".join([
            f"• {quiz.name} ({quiz.subject_name} - {quiz.chapter_name})"
            for quiz in new_quizzes
        ])
        
        reminder_message = f"""🎯 Daily Quiz Reminder

Good evening! {len(new_quizzes)} new quiz{'s' if len(new_quizzes) > 1 else ''} {'have' if len(new_quizzes) > 1 else 'has'} been added today:

{quiz_list}

Best regards,
Quiz Master Team"""
        
        # Send reminders
        success_count = 0
        failure_count = 0
        
        for user in users:
            try:
                email = user.username
                subject = f"Daily Quiz Reminder - {len(new_quizzes)} New Quiz{'s' if len(new_quizzes) > 1 else ''} Available"
                
                email_sent = send_email(email, subject, reminder_message)
                
                if email_sent:
                    success_count += 1
                    print(f"✅ Reminder sent to {user.username}")
                else:
                    failure_count += 1
                    print(f"❌ Failed to send reminder to {user.username}")
                    
            except Exception as e:
                failure_count += 1
                print(f"❌ Error sending reminder to {user.username}: {str(e)}")
        
        print(f"Daily reminders completed: {success_count} successful, {failure_count} failed")
        
        return {
            'status': 'SUCCESS',
            'message': f'Daily reminders sent to {len(users)} users',
            'quizzes_count': len(new_quizzes),
            'success_count': success_count,
            'failure_count': failure_count,
            'total_users': len(users)
        }
        
    except Exception as e:
        print(f"Error in daily quiz reminders: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e),
            'message': 'Daily reminders failed'
        } 
        