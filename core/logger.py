"""
Application Logger - Comprehensive Logging System

Logs all job applications, errors, and system events for tracking and analysis.
"""

import asyncio
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class ApplicationLogger:
    """Comprehensive logging system for job applications."""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Log files
        self.applications_file = self.log_dir / "applications.yaml"
        self.errors_file = self.log_dir / "errors.json"
        self.system_file = self.log_dir / "system.log"
        
        print("📋 Application Logger initialized")
    
    async def log_application(self, job: Dict[str, Any], status: str, details: Dict[str, Any] = None):
        """Log a job application attempt."""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'job_title': job.get('title', 'Unknown'),
                'company': job.get('company', 'Unknown'),
                'url': job.get('url', ''),
                'site': job.get('site', 'unknown'),
                'status': status,
                'details': details or {}
            }
            
            # Load existing logs
            applications = []
            if self.applications_file.exists():
                with open(self.applications_file, 'r') as f:
                    applications = yaml.safe_load(f) or []
            
            # Add new entry
            applications.append(log_entry)
            
            # Save updated logs
            with open(self.applications_file, 'w') as f:
                yaml.dump(applications, f, default_flow_style=False, sort_keys=False)
            
            # Also log to console
            status_emoji = {
                'SUCCESS': '✅',
                'FAILED': '❌',
                'ERROR': '💥',
                'NAVIGATION_FAILED': '🧭',
                'INCOMPLETE': '⚠️'
            }.get(status, '📝')
            
            print(f"{status_emoji} {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} - {status}")
            
        except Exception as e:
            print(f"❌ Error logging application: {e}")
    
    async def log_error(self, component: str, error_message: str, details: Dict[str, Any] = None):
        """Log system errors."""
        try:
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'component': component,
                'error': error_message,
                'details': details or {}
            }
            
            # Load existing errors
            errors = []
            if self.errors_file.exists():
                with open(self.errors_file, 'r') as f:
                    errors = json.load(f)
            
            # Add new error
            errors.append(error_entry)
            
            # Keep only last 1000 errors
            errors = errors[-1000:]
            
            # Save updated errors
            with open(self.errors_file, 'w') as f:
                json.dump(errors, f, indent=2)
            
            print(f"💥 ERROR in {component}: {error_message}")
            
        except Exception as e:
            print(f"❌ Error logging error: {e}")
    
    async def log_system_event(self, event: str, details: str = ""):
        """Log system events."""
        try:
            timestamp = datetime.now().isoformat()
            log_line = f"[{timestamp}] {event}: {details}\n"
            
            with open(self.system_file, 'a') as f:
                f.write(log_line)
            
        except Exception as e:
            print(f"❌ Error logging system event: {e}")
    
    async def get_application_stats(self) -> Dict[str, Any]:
        """Get application statistics."""
        try:
            if not self.applications_file.exists():
                return {'total': 0, 'successful': 0, 'failed': 0, 'success_rate': 0}
            
            with open(self.applications_file, 'r') as f:
                applications = yaml.safe_load(f) or []
            
            total = len(applications)
            successful = len([app for app in applications if app.get('status') == 'SUCCESS'])
            failed = total - successful
            success_rate = (successful / total * 100) if total > 0 else 0
            
            return {
                'total': total,
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {'total': 0, 'successful': 0, 'failed': 0, 'success_rate': 0}
    
    async def get_recent_applications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent applications."""
        try:
            if not self.applications_file.exists():
                return []
            
            with open(self.applications_file, 'r') as f:
                applications = yaml.safe_load(f) or []
            
            # Return most recent applications
            return applications[-limit:]
            
        except Exception as e:
            print(f"❌ Error getting recent applications: {e}")
            return []
