"""
Overlord Agent - System Monitor and Recovery

This agent monitors all other agents and handles stuck states, timeouts,
and system recovery. It's the "overseer" that ensures the system keeps running.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Set
from dataclasses import dataclass

@dataclass
class ApplicationStatus:
    """Track status of individual applications."""
    application_id: str
    start_time: datetime
    last_activity: datetime
    current_agent: str
    status: str = "ACTIVE"

class OverlordAgent:
    """Overlord agent that monitors and recovers from stuck states."""
    
    def __init__(self):
        self.active_applications: Dict[str, ApplicationStatus] = {}
        self.monitoring = False
        self.timeout_threshold = timedelta(minutes=2)  # 2 minute timeout
        
        print("🔮 Overlord Agent initialized")
    
    async def initialize(self):
        """Initialize the overlord agent."""
        print("🔮 Overlord monitoring system ready")
    
    async def register_application(self, application_id: str):
        """Register a new application for monitoring."""
        now = datetime.now()
        self.active_applications[application_id] = ApplicationStatus(
            application_id=application_id,
            start_time=now,
            last_activity=now,
            current_agent="starting"
        )
        print(f"🔮 Overlord: Registered application {application_id}")
    
    async def unregister_application(self, application_id: str):
        """Unregister a completed application."""
        if application_id in self.active_applications:
            del self.active_applications[application_id]
            print(f"🔮 Overlord: Unregistered application {application_id}")
    
    async def update_activity(self, application_id: str, current_agent: str):
        """Update the last activity time for an application."""
        if application_id in self.active_applications:
            self.active_applications[application_id].last_activity = datetime.now()
            self.active_applications[application_id].current_agent = current_agent
    
    async def monitor_session(self, session_id: str):
        """Monitor a complete session for stuck states."""
        print(f"🔮 Overlord: Starting monitoring for session {session_id}")
        self.monitoring = True
        
        try:
            while self.monitoring:
                await self.check_for_stuck_applications()
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except asyncio.CancelledError:
            print(f"🔮 Overlord: Monitoring cancelled for session {session_id}")
            self.monitoring = False
    
    async def check_for_stuck_applications(self):
        """Check for applications that have been stuck too long."""
        now = datetime.now()
        stuck_applications = []
        
        for app_id, status in self.active_applications.items():
            if now - status.last_activity > self.timeout_threshold:
                stuck_applications.append(app_id)
        
        for app_id in stuck_applications:
            await self.handle_stuck_application(app_id)
    
    async def handle_stuck_application(self, application_id: str):
        """Handle a stuck application - attempt recovery."""
        print(f"⚠️  Overlord: Application {application_id} appears stuck!")
        status = self.active_applications.get(application_id)
        
        if not status:
            return
        
        stuck_duration = datetime.now() - status.last_activity
        print(f"⏰ Stuck for {stuck_duration.total_seconds():.0f} seconds")
        print(f"🔧 Last agent: {status.current_agent}")
        
        # Recovery actions
        if stuck_duration.total_seconds() < 180:  # Less than 3 minutes
            print("🔄 Attempting soft recovery...")
            await self.soft_recovery(application_id)
        else:
            print("🛑 Attempting hard recovery (skip application)...")
            await self.hard_recovery(application_id)
    
    async def soft_recovery(self, application_id: str):
        """Attempt soft recovery - refresh page, retry action."""
        print(f"🔄 Overlord: Soft recovery for {application_id}")
        # This would signal other agents to retry their current action
        # For now, just update the activity to give it more time
        if application_id in self.active_applications:
            self.active_applications[application_id].last_activity = datetime.now()
    
    async def hard_recovery(self, application_id: str):
        """Hard recovery - skip this application and move on."""
        print(f"🛑 Overlord: Hard recovery for {application_id} - skipping application")
        # Mark as failed and remove from monitoring
        if application_id in self.active_applications:
            self.active_applications[application_id].status = "FAILED_TIMEOUT"
            await self.unregister_application(application_id)
    
    def get_system_status(self) -> Dict:
        """Get current system status."""
        return {
            'monitoring': self.monitoring,
            'active_applications': len(self.active_applications),
            'applications': {
                app_id: {
                    'start_time': status.start_time.isoformat(),
                    'last_activity': status.last_activity.isoformat(),
                    'current_agent': status.current_agent,
                    'status': status.status,
                    'duration': (datetime.now() - status.start_time).total_seconds()
                }
                for app_id, status in self.active_applications.items()
            }
        }
    
    async def shutdown(self):
        """Shutdown the overlord agent."""
        self.monitoring = False
        print("🔮 Overlord agent shut down")
