# Celery Report Generation System

## Overview
This system provides asynchronous report generation and email sending for quiz users using Celery and Redis.

## Features
- ✅ **Asynchronous Processing** - Reports generated in background
- ✅ **Progress Tracking** - Real-time progress updates
- ✅ **Error Handling** - Comprehensive error handling and logging
- ✅ **Email Integration** - HTML email reports with beautiful styling
- ✅ **Task Monitoring** - Check task status and results
- ✅ **Batch Processing** - Process reports for all users
- ✅ **Single User Processing** - Generate reports for individual users

## Setup

### 1. Install Dependencies
```bash
pip install celery redis
```

### 2. Start Redis Server
```bash
# Windows (if using WSL or Redis for Windows)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

### 3. Start Celery Worker
```bash
cd backend
celery -A celery_config worker --loglevel=info
```

### 4. Start Flask App
```bash
python app.py
```

## API Endpoints

### 1. Generate Reports for All Users
```http
POST /scheduled/generate-all-monthly-reports
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "month_year": "2024-12"
}
```

**Response:**
```json
{
  "message": "Report generation started for all users",
  "task_id": "abc123-def456",
  "month_year": "2024-12",
  "status": "PENDING"
}
```

### 2. Generate Report for Single User
```http
POST /scheduled/generate-user-report
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "user_id": 1,
  "month_year": "2024-12"
}
```

### 3. Check Task Status
```http
GET /scheduled/task-status/<task_id>
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "state": "SUCCESS",
  "current": 10,
  "total": 10,
  "status": "Completed processing 10 users",
  "result": {
    "message": "Completed report generation for 10 users",
    "summary": {
      "total_users": 10,
      "successful": 8,
      "failed": 2,
      "success_rate": 80.0
    },
    "results": [...]
  }
}
```

### 4. Get Report Summary
```http
GET /scheduled/report-summary
Authorization: Bearer <admin_token>
```

## Celery Tasks

### 1. `process_all_reports(month_year)`
- Processes reports for all users
- Shows progress updates
- Returns summary statistics

### 2. `generate_user_report(user_id, month_year)`
- Generates HTML report for a single user
- Returns report content

### 3. `send_report_email(user_id, month_year, html_content)`
- Sends email with report
- Returns email status

### 4. `generate_and_send_user_report(user_id, month_year)`
- Combines report generation and email sending
- Single task for complete workflow

## Email Configuration

Set these environment variables:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Report Content

Each monthly report includes:
- 📊 User information and statistics
- 📚 Subject-wise performance breakdown
- 📝 Detailed quiz results with rankings
- 🎯 Performance insights and recommendations
- 📧 Professional HTML email styling

## Task States

- **PENDING** - Task is queued
- **PROGRESS** - Task is running (with progress updates)
- **SUCCESS** - Task completed successfully
- **FAILURE** - Task failed with error

## Error Handling

The system handles:
- ✅ Database connection issues
- ✅ SMTP authentication errors
- ✅ Missing user data
- ✅ Invalid month/year formats
- ✅ Network connectivity issues

## Monitoring

### Celery Logs
Monitor Celery worker logs for:
- Task execution progress
- Error messages
- Email sending status
- Performance metrics

### Task Results
Check task results for:
- Success/failure counts
- Individual user status
- Email delivery confirmation
- Error details

## Production Considerations

1. **Database Connection Pooling** - Configure proper connection limits
2. **Email Rate Limiting** - Implement delays between emails
3. **Task Retry Logic** - Add retry mechanisms for failed tasks
4. **Monitoring** - Use Flower for Celery monitoring
5. **Logging** - Implement structured logging
6. **Security** - Secure SMTP credentials

## Troubleshooting

### Common Issues

1. **Tasks stuck in PENDING**
   - Check if Celery worker is running
   - Verify Redis connection
   - Check for circular imports

2. **Email sending fails**
   - Verify SMTP credentials
   - Check Gmail app password
   - Test SMTP connection

3. **Database errors**
   - Ensure Flask app context
   - Check database connection
   - Verify model imports

### Windows-Specific Issues

The system is configured for Windows with:
- `worker_pool='solo'` - Avoids multiprocessing issues
- `worker_concurrency=1` - Single worker process
- Proper app context handling

## Example Usage

### Generate Reports for All Users
```bash
curl -X POST http://localhost:5000/scheduled/generate-all-monthly-reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_token>" \
  -d '{"month_year": "2024-12"}'
```

### Check Progress
```bash
curl -X GET http://localhost:5000/scheduled/task-status/<task_id> \
  -H "Authorization: Bearer <admin_token>"
```

This system provides a robust, scalable solution for generating and sending monthly quiz reports to all users asynchronously. 