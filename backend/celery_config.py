from celery.schedules import crontab

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/1"
timezone = "Asia/Kolkata"
enable_utc = False
broker_connection_retry_on_startup = True

# Task configuration
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
task_track_started = True
task_time_limit = 30 * 60  # 30 minutes
task_soft_time_limit = 25 * 60  # 25 minutes

# Worker configuration
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_pool = 'solo'  # For Windows
worker_concurrency = 1  # Single worker process

# Beat schedule configuration
beat_schedule = {
    'daily-quiz-reminders': {
        'task': 'celery_tasks.send_daily_quiz_reminders',
        'schedule': crontab(hour=21, minute=51),  # 9:51 PM daily
        'options': {'expires': 3600}
    },
    'monthly-report-generation': {
        'task': 'celery_tasks.process_all_reports',
        'schedule': crontab(day_of_month=26, hour=18, minute=3),  # 1st day of every month at 8:00 AM
        'args': (),  # No arguments - will auto-detect previous month
        'options': {'expires': 3600 * 24}  # 24 hours expiry
    },
}

# Beat configuration
beat_schedule_filename = 'celerybeat-schedule'
beat_sync_every = 1
