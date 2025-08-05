"""
Logger Agent - Comprehensive Application Tracking and Analytics

This agent tracks all job applications, success rates, and provides detailed analytics.
It maintains a database of applications and generates performance reports.
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ApplicationRecord:
    """Data structure for a job application record."""
    application_id: str
    job_title: str
    company: str
    job_url: str
    application_status: str
    application_time: datetime
    completion_time: Optional[datetime] = None
    error_message: Optional[str] = None
    steps_completed: int = 0
    total_steps: int = 0
    confirmation_received: bool = False
    verification_code_used: bool = False
    resume_uploaded: bool = False
    cover_letter_generated: bool = False
    form_fields_filled: int = 0
    application_source: str = "linkedin"  # linkedin, indeed, etc.

class LoggerAgent:
    """Agent responsible for tracking and logging all job applications."""
    
    def __init__(self, db_path: str = "logs/job_applications.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.active_applications = {}
        self.session_stats = {
            'session_start': datetime.now(),
            'applications_attempted': 0,
            'applications_completed': 0,
            'applications_failed': 0,
            'errors_encountered': 0
        }
        
        print("📊 Logger Agent initialized")
    
    async def initialize(self):
        """Initialize the database and create tables if needed."""
        print("📊 Setting up application tracking database...")
        
        try:
            # Create database connection
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Create tables
            await self.create_tables()
            
            print("✅ Application tracking database ready")
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
    
    async def create_tables(self):
        """Create database tables for application tracking."""
        cursor = self.conn.cursor()
        
        # Main applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                application_id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                job_url TEXT NOT NULL,
                application_status TEXT NOT NULL,
                application_time TIMESTAMP NOT NULL,
                completion_time TIMESTAMP,
                error_message TEXT,
                steps_completed INTEGER DEFAULT 0,
                total_steps INTEGER DEFAULT 0,
                confirmation_received BOOLEAN DEFAULT FALSE,
                verification_code_used BOOLEAN DEFAULT FALSE,
                resume_uploaded BOOLEAN DEFAULT FALSE,
                cover_letter_generated BOOLEAN DEFAULT FALSE,
                form_fields_filled INTEGER DEFAULT 0,
                application_source TEXT DEFAULT 'linkedin'
            )
        ''')
        
        # Application steps tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT NOT NULL,
                step_name TEXT NOT NULL,
                step_status TEXT NOT NULL,
                step_time TIMESTAMP NOT NULL,
                step_duration REAL,
                error_details TEXT,
                FOREIGN KEY (application_id) REFERENCES applications (application_id)
            )
        ''')
        
        # Daily statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                applications_attempted INTEGER DEFAULT 0,
                applications_completed INTEGER DEFAULT 0,
                applications_failed INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                average_completion_time REAL DEFAULT 0.0,
                total_errors INTEGER DEFAULT 0
            )
        ''')
        
        # Error log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                error_time TIMESTAMP NOT NULL,
                stack_trace TEXT,
                context_data TEXT
            )
        ''')
        
        self.conn.commit()
    
    async def start_application(self, application_id: str, job: Dict[str, Any]) -> ApplicationRecord:
        """Start tracking a new job application."""
        print(f"📊 Starting application tracking: {job['title']} at {job['company']}")
        
        # Create application record
        record = ApplicationRecord(
            application_id=application_id,
            job_title=job['title'],
            company=job['company'],
            job_url=job['url'],
            application_status='started',
            application_time=datetime.now(),
            application_source=job.get('source', 'linkedin')
        )
        
        # Store in active applications
        self.active_applications[application_id] = record
        
        # Save to database
        await self.save_application_record(record)
        
        # Log application step
        await self.log_step(application_id, 'application_started', 'success')
        
        # Update session stats
        self.session_stats['applications_attempted'] += 1
        
        return record
    
    async def update_application_status(self, application_id: str, status: str, error_message: str = None):
        """Update the status of an application."""
        if application_id not in self.active_applications:
            return
        
        record = self.active_applications[application_id]
        record.application_status = status
        
        if error_message:
            record.error_message = error_message
        
        if status in ['completed', 'failed', 'timeout']:
            record.completion_time = datetime.now()
            
            # Update session stats
            if status == 'completed':
                self.session_stats['applications_completed'] += 1
            else:
                self.session_stats['applications_failed'] += 1
        
        # Save to database
        await self.save_application_record(record)
        
        print(f"📊 Application {application_id} status: {status}")
    
    async def log_step(self, application_id: str, step_name: str, status: str, 
                      duration: float = None, error_details: str = None):
        """Log a specific step in the application process."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO application_steps 
                (application_id, step_name, step_status, step_time, step_duration, error_details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                application_id,
                step_name,
                status,
                datetime.now(),
                duration,
                error_details
            ))
            self.conn.commit()
            
            # Update record if active
            if application_id in self.active_applications:
                record = self.active_applications[application_id]
                if status == 'success':
                    record.steps_completed += 1
                
                # Update specific flags
                if step_name == 'resume_upload':
                    record.resume_uploaded = (status == 'success')
                elif step_name == 'cover_letter_generation':
                    record.cover_letter_generated = (status == 'success')
                elif step_name == 'verification_code':
                    record.verification_code_used = (status == 'success')
                elif step_name == 'form_field_filled':
                    record.form_fields_filled += 1
                elif step_name == 'confirmation_received':
                    record.confirmation_received = (status == 'success')
            
        except Exception as e:
            print(f"❌ Error logging step: {e}")
    
    async def log_error(self, application_id: str, error_type: str, error_message: str, 
                       stack_trace: str = None, context: Dict[str, Any] = None):
        """Log an error that occurred during application process."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO error_log 
                (application_id, error_type, error_message, error_time, stack_trace, context_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                application_id,
                error_type,
                error_message,
                datetime.now(),
                stack_trace,
                json.dumps(context) if context else None
            ))
            self.conn.commit()
            
            # Update session stats
            self.session_stats['errors_encountered'] += 1
            
            print(f"📊 ❌ Error logged: {error_type} - {error_message}")
            
        except Exception as e:
            print(f"❌ Error saving error log: {e}")
    
    async def save_application_record(self, record: ApplicationRecord):
        """Save application record to database."""
        try:
            cursor = self.conn.cursor()
            
            # Convert dataclass to dict
            data = asdict(record)
            
            # Handle datetime objects
            if data['application_time']:
                data['application_time'] = data['application_time'].isoformat()
            if data['completion_time']:
                data['completion_time'] = data['completion_time'].isoformat()
            
            # Insert or update record
            cursor.execute('''
                INSERT OR REPLACE INTO applications 
                (application_id, job_title, company, job_url, application_status, 
                 application_time, completion_time, error_message, steps_completed, 
                 total_steps, confirmation_received, verification_code_used, 
                 resume_uploaded, cover_letter_generated, form_fields_filled, application_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['application_id'], data['job_title'], data['company'], data['job_url'],
                data['application_status'], data['application_time'], data['completion_time'],
                data['error_message'], data['steps_completed'], data['total_steps'],
                data['confirmation_received'], data['verification_code_used'],
                data['resume_uploaded'], data['cover_letter_generated'],
                data['form_fields_filled'], data['application_source']
            ))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"❌ Error saving application record: {e}")
    
    async def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        session_duration = datetime.now() - self.session_stats['session_start']
        
        success_rate = 0
        if self.session_stats['applications_attempted'] > 0:
            success_rate = (self.session_stats['applications_completed'] / 
                          self.session_stats['applications_attempted']) * 100
        
        return {
            'session_duration': str(session_duration),
            'applications_attempted': self.session_stats['applications_attempted'],
            'applications_completed': self.session_stats['applications_completed'],
            'applications_failed': self.session_stats['applications_failed'],
            'success_rate': round(success_rate, 2),
            'errors_encountered': self.session_stats['errors_encountered'],
            'active_applications': len(self.active_applications)
        }
    
    async def get_daily_stats(self, date: str = None) -> Dict[str, Any]:
        """Get statistics for a specific date."""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT applications_attempted, applications_completed, applications_failed,
                       success_rate, average_completion_time, total_errors
                FROM daily_stats WHERE date = ?
            ''', (date,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                return await self.calculate_daily_stats(date)
                
        except Exception as e:
            print(f"❌ Error getting daily stats: {e}")
            return {}
    
    async def calculate_daily_stats(self, date: str) -> Dict[str, Any]:
        """Calculate and cache daily statistics."""
        try:
            cursor = self.conn.cursor()
            
            # Get applications for the date
            cursor.execute('''
                SELECT COUNT(*) as attempted,
                       SUM(CASE WHEN application_status = 'completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN application_status = 'failed' THEN 1 ELSE 0 END) as failed,
                       AVG(CASE WHEN completion_time IS NOT NULL THEN 
                           (julianday(completion_time) - julianday(application_time)) * 24 * 60 
                           ELSE NULL END) as avg_time
                FROM applications 
                WHERE DATE(application_time) = ?
            ''', (date,))
            
            row = cursor.fetchone()
            
            attempted = row['attempted'] or 0
            completed = row['completed'] or 0
            failed = row['failed'] or 0
            avg_time = row['avg_time'] or 0
            
            success_rate = (completed / attempted * 100) if attempted > 0 else 0
            
            # Get error count for the date
            cursor.execute('''
                SELECT COUNT(*) as error_count
                FROM error_log 
                WHERE DATE(error_time) = ?
            ''', (date,))
            
            error_count = cursor.fetchone()['error_count'] or 0
            
            # Save to daily_stats table
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats 
                (date, applications_attempted, applications_completed, applications_failed,
                 success_rate, average_completion_time, total_errors)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, attempted, completed, failed, success_rate, avg_time, error_count))
            
            self.conn.commit()
            
            return {
                'date': date,
                'applications_attempted': attempted,
                'applications_completed': completed,
                'applications_failed': failed,
                'success_rate': round(success_rate, 2),
                'average_completion_time': round(avg_time, 2),
                'total_errors': error_count
            }
            
        except Exception as e:
            print(f"❌ Error calculating daily stats: {e}")
            return {}
    
    async def get_recent_applications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent applications with their details."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM applications 
                ORDER BY application_time DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"❌ Error getting recent applications: {e}")
            return []
    
    async def get_error_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of errors in the last X days."""
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT error_type, COUNT(*) as count
                FROM error_log 
                WHERE DATE(error_time) >= ?
                GROUP BY error_type
                ORDER BY count DESC
            ''', (since_date,))
            
            error_types = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT COUNT(*) as total_errors
                FROM error_log 
                WHERE DATE(error_time) >= ?
            ''', (since_date,))
            
            total_errors = cursor.fetchone()['total_errors']
            
            return {
                'total_errors': total_errors,
                'error_types': error_types,
                'period_days': days
            }
            
        except Exception as e:
            print(f"❌ Error getting error summary: {e}")
            return {}
    
    async def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        try:
            report_lines = []
            report_lines.append("📊 JOB APPLICATION PERFORMANCE REPORT")
            report_lines.append("=" * 50)
            
            # Session summary
            session = await self.get_session_summary()
            report_lines.append("\n🕒 CURRENT SESSION:")
            report_lines.append(f"   Duration: {session['session_duration']}")
            report_lines.append(f"   Applications Attempted: {session['applications_attempted']}")
            report_lines.append(f"   Applications Completed: {session['applications_completed']}")
            report_lines.append(f"   Success Rate: {session['success_rate']}%")
            report_lines.append(f"   Errors Encountered: {session['errors_encountered']}")
            
            # Today's stats
            today_stats = await self.get_daily_stats()
            if today_stats:
                report_lines.append("\n📅 TODAY'S STATISTICS:")
                report_lines.append(f"   Applications: {today_stats['applications_attempted']}")
                report_lines.append(f"   Completed: {today_stats['applications_completed']}")
                report_lines.append(f"   Success Rate: {today_stats['success_rate']}%")
                report_lines.append(f"   Avg Time: {today_stats['average_completion_time']:.1f} minutes")
            
            # Recent applications
            recent = await self.get_recent_applications(10)
            if recent:
                report_lines.append("\n📋 RECENT APPLICATIONS:")
                for app in recent[:5]:  # Show last 5
                    status_emoji = "✅" if app['application_status'] == 'completed' else "❌"
                    report_lines.append(f"   {status_emoji} {app['job_title']} at {app['company']}")
            
            # Error summary
            errors = await self.get_error_summary(7)
            if errors and errors['total_errors'] > 0:
                report_lines.append("\n⚠️ ERROR SUMMARY (Last 7 days):")
                report_lines.append(f"   Total Errors: {errors['total_errors']}")
                for error_type in errors['error_types'][:3]:  # Top 3 error types
                    report_lines.append(f"   {error_type['error_type']}: {error_type['count']}")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            return f"❌ Error generating report: {e}"
    
    async def export_data(self, format: str = 'json', date_range: int = 30) -> str:
        """Export application data in specified format."""
        try:
            since_date = (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d')
            
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM applications 
                WHERE DATE(application_time) >= ?
                ORDER BY application_time DESC
            ''', (since_date,))
            
            applications = [dict(row) for row in cursor.fetchall()]
            
            if format == 'json':
                return json.dumps(applications, indent=2, default=str)
            elif format == 'csv':
                if not applications:
                    return ""
                
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=applications[0].keys())
                writer.writeheader()
                writer.writerows(applications)
                return output.getvalue()
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return ""
    
    async def cleanup_old_records(self, days: int = 90):
        """Clean up old application records."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor = self.conn.cursor()
            
            # Delete old applications
            cursor.execute('DELETE FROM applications WHERE DATE(application_time) < ?', (cutoff_date,))
            apps_deleted = cursor.rowcount
            
            # Delete old steps
            cursor.execute('DELETE FROM application_steps WHERE DATE(step_time) < ?', (cutoff_date,))
            steps_deleted = cursor.rowcount
            
            # Delete old errors
            cursor.execute('DELETE FROM error_log WHERE DATE(error_time) < ?', (cutoff_date,))
            errors_deleted = cursor.rowcount
            
            self.conn.commit()
            
            print(f"📊 Cleanup completed: {apps_deleted} apps, {steps_deleted} steps, {errors_deleted} errors deleted")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    async def shutdown(self):
        """Shutdown the logger agent and close database connection."""
        print("📊 Generating final session report...")
        
        # Generate final report
        report = await self.generate_performance_report()
        print("\n" + report)
        
        # Save final session stats
        today = datetime.now().strftime('%Y-%m-%d')
        await self.calculate_daily_stats(today)
        
        # Close database connection
        if hasattr(self, 'conn'):
            self.conn.close()
        
        print("📊 Logger Agent shut down")
