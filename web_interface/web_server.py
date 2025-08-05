"""
Web Server for AutoApply AI - Connects the web interface to the orchestrator

This server provides:
- Static file serving for the web interface
- WebSocket communication for real-time updates
- REST API endpoints for system control
- Integration with the existing JobApplicationOrchestrator
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from aiohttp import web, WSMsgType
import aiohttp_cors
from orchestrator import JobApplicationOrchestrator

class WebSocketManager:
    """Manages WebSocket connections and broadcasts updates."""
    
    def __init__(self):
        self.connections: List[web.WebSocketResponse] = []
    
    async def add_connection(self, ws: web.WebSocketResponse):
        """Add a new WebSocket connection."""
        self.connections.append(ws)
        print(f"✅ WebSocket connection added. Total connections: {len(self.connections)}")
    
    async def remove_connection(self, ws: web.WebSocketResponse):
        """Remove a WebSocket connection."""
        if ws in self.connections:
            self.connections.remove(ws)
            print(f"❌ WebSocket connection removed. Total connections: {len(self.connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        if not self.connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for ws in self.connections:
            try:
                await ws.send_str(message_str)
            except Exception as e:
                print(f"❌ Failed to send message to client: {e}")
                disconnected.append(ws)
        
        # Remove disconnected clients
        for ws in disconnected:
            await self.remove_connection(ws)

class WebOrchestrator(JobApplicationOrchestrator):
    """Extended orchestrator that integrates with the web interface."""
    
    def __init__(self, websocket_manager: WebSocketManager):
        super().__init__()
        self.ws_manager = websocket_manager
        self.current_job_index = 0
        self.search_params = {}
        self.settings = {
            'delayBetweenJobs': 60,
            'maxPerHour': 10,
            'enableEmail': True,
            'enableCoverLetter': True
        }
    
    async def broadcast_log(self, message: str, level: str = 'info'):
        """Broadcast a log message to all connected clients."""
        await self.ws_manager.broadcast({
            'type': 'log',
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        })
    
    async def broadcast_job_found(self, job: Dict[str, Any]):
        """Broadcast when a new job is found."""
        await self.ws_manager.broadcast({
            'type': 'job_found',
            'job': job
        })
    
    async def broadcast_job_update(self, job: Dict[str, Any]):
        """Broadcast when a job status is updated."""
        await self.ws_manager.broadcast({
            'type': 'job_update',
            'job': job
        })
    
    async def broadcast_progress(self, percentage: float):
        """Broadcast progress update."""
        await self.ws_manager.broadcast({
            'type': 'progress',
            'percentage': percentage
        })
    
    async def broadcast_status(self, status: str):
        """Broadcast system status update."""
        await self.ws_manager.broadcast({
            'type': 'status',
            'status': status
        })
    
    async def broadcast_system_state(self):
        """Broadcast current system state."""
        await self.ws_manager.broadcast({
            'type': 'system_state',
            'running': self.is_running,
            'paused': getattr(self, 'is_paused', False)
        })
    
    async def web_run_job_search(self, search_term: str, location: str = "", max_jobs: int = 25):
        """Web-enabled version of run_job_search with real-time updates."""
        await self.broadcast_log(f"🔍 Starting job search for: '{search_term}'")
        await self.broadcast_log("🎯 Goal: Apply to ALL jobs found (no filtering)")
        await self.broadcast_status("Initializing...")
        
        self.is_running = True
        self.current_job_index = 0
        
        try:
            # Step 1: Search for jobs
            await self.broadcast_log("📋 Step 1: Searching for jobs...")
            await self.broadcast_status("Searching for jobs...")
            
            jobs = await self.job_search_agent.search_jobs(search_term)
            
            # Limit jobs if max_jobs is specified
            if max_jobs > 0:
                jobs = jobs[:max_jobs]
            
            if not jobs:
                await self.broadcast_log("❌ No jobs found for search term", "error")
                await self.broadcast_status("No jobs found")
                return
            
            await self.broadcast_log(f"🎯 Found {len(jobs)} jobs to apply to", "success")
            
            # Broadcast each job found
            for i, job in enumerate(jobs):
                if 'id' not in job:
                    job['id'] = f"job_{i}"  # Ensure each job has an ID
                await self.broadcast_job_found(job)
                await asyncio.sleep(0.1)  # Small delay for UI updates
            
            # Step 2: Apply to each job
            await self.broadcast_log("🚀 Step 2: Starting application process...")
            await self.broadcast_status("Applying to jobs...")
            
            for i, job in enumerate(jobs, 1):
                if not self.is_running:
                    await self.broadcast_log("⏹️ Process stopped by user")
                    break
                
                # Check for pause
                while getattr(self, 'is_paused', False) and self.is_running:
                    await asyncio.sleep(1)
                
                if not self.is_running:
                    break
                
                self.current_job_index = i
                await self.broadcast_log(f"📝 Applying to job {i}/{len(jobs)}")
                await self.broadcast_progress(20 + ((i - 1) / len(jobs) * 80))
                
                # Apply to job with updates
                await self.web_apply_to_job(job, i, len(jobs))
                
                # Delay between applications based on settings
                if i < len(jobs) and self.is_running:
                    delay = self.settings.get('delayBetweenJobs', 60)
                    await asyncio.sleep(delay)
            
            # Summary
            await self.broadcast_progress(100)
            await self.broadcast_status("Completed")
            await self.broadcast_log(f"🎉 Job search completed!", "success")
            await self.broadcast_log(f"📊 Total jobs: {len(jobs)}")
            await self.broadcast_log(f"✅ Successful applications: {self.successful_applications}")
            
            if len(jobs) > 0:
                rate = self.successful_applications / len(jobs) * 100
                await self.broadcast_log(f"📋 Application rate: {rate:.1f}%")
            
            # Broadcast session complete
            await self.ws_manager.broadcast({
                'type': 'session_complete',
                'applied': self.successful_applications,
                'total': len(jobs),
                'rate': self.successful_applications / len(jobs) * 100 if len(jobs) > 0 else 0
            })
            
        except Exception as e:
            await self.broadcast_log(f"❌ Error during job search: {e}", "error")
            await self.logger.log_error("job_search", str(e))
        
        finally:
            self.is_running = False
            await self.broadcast_system_state()
    
    async def web_apply_to_job(self, job: Dict[str, Any], job_num: int, total_jobs: int):
        """Web-enabled version of apply_to_job with real-time updates."""
        job_title = job.get('title', 'Unknown')
        job_company = job.get('company', 'Unknown')
        job_url = job.get('url', '')
        job_id = job.get('id', f'job_{job_num}')
        
        await self.broadcast_status(f"Applying: {job_title} at {job_company}")
        await self.broadcast_log(f"🎯 Applying: {job_title} at {job_company}")
        
        # Update job status to in progress
        job['status'] = 'applying'
        await self.broadcast_job_update(job)
        
        # Start overlord monitoring
        monitoring_task = None
        if self.overlord_agent:
            monitoring_task = asyncio.create_task(
                self.overlord_agent.monitor_application(job_url)
            )
        
        try:
            # Step 1: Navigate to job
            await self.broadcast_log("🧭 Navigating to job page...")
            nav_success = await self.navigation_agent.navigate_to_job(job_url)
            
            if not nav_success:
                await self.broadcast_log("❌ Failed to navigate to job", "error")
                job['status'] = 'failed'
                await self.broadcast_job_update(job)
                await self.logger.log_application(job, "NAVIGATION_FAILED")
                return
            
            # Step 2: Apply to job using form filling agent
            await self.broadcast_log("📝 Starting application process...")
            application_result = await self.form_filling_agent.apply_to_job(
                navigation_agent=self.navigation_agent,
                job_details=job
            )
            
            # Step 3: Handle any email verification if needed
            if application_result.get('needs_email_verification') and self.settings.get('enableEmail', True):
                await self.broadcast_log("📧 Handling email verification...")
                verification_result = await self.email_agent.handle_verification()
                if verification_result:
                    await self.broadcast_log("✅ Email verification completed", "success")
                else:
                    await self.broadcast_log("⚠️ Email verification failed", "error")
            
            # Log result
            if application_result.get('success'):
                await self.broadcast_log("✅ Application successful!", "success")
                self.successful_applications += 1
                job['status'] = 'success'
                await self.logger.log_application(job, "SUCCESS", application_result)
            else:
                await self.broadcast_log("❌ Application failed", "error")
                job['status'] = 'failed'
                await self.logger.log_application(job, "FAILED", application_result)
            
            self.total_applications += 1
            await self.broadcast_job_update(job)
            
        except Exception as e:
            await self.broadcast_log(f"❌ Error applying to job: {e}", "error")
            job['status'] = 'failed'
            await self.broadcast_job_update(job)
            await self.logger.log_application(job, "ERROR", {"error": str(e)})
        
        finally:
            # Stop monitoring
            if monitoring_task:
                monitoring_task.cancel()
    
    async def pause(self):
        """Pause the job application process."""
        self.is_paused = True
        await self.broadcast_log("⏸️ System paused")
        await self.broadcast_status("Paused")
        await self.broadcast_system_state()
    
    async def resume(self):
        """Resume the job application process."""
        self.is_paused = False
        await self.broadcast_log("▶️ System resumed")
        await self.broadcast_status("Running")
        await self.broadcast_system_state()
    
    async def stop(self):
        """Stop the job application process."""
        await self.broadcast_log("⏹️ Stopping job application system...")
        self.is_running = False
        self.is_paused = False
        
        # Shutdown agents
        if self.navigation_agent:
            await self.navigation_agent.shutdown()
        if self.form_filling_agent:
            await self.form_filling_agent.shutdown()
        if self.email_agent:
            await self.email_agent.shutdown()
        if self.overlord_agent:
            await self.overlord_agent.shutdown()
        
        await self.broadcast_log("✅ System shutdown complete", "success")
        await self.broadcast_status("Stopped")
        await self.broadcast_system_state()
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update system settings."""
        self.settings.update(settings)
        print(f"⚙️ Settings updated: {settings}")

class AutoApplyWebServer:
    """Main web server class."""
    
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.ws_manager = WebSocketManager()
        self.orchestrator = WebOrchestrator(self.ws_manager)
        
        # Setup routes
        self.setup_routes()
        self.setup_cors()
    
    def setup_routes(self):
        """Setup HTTP and WebSocket routes."""
        # Static file serving
        self.app.router.add_get('/', self.serve_index)
        self.app.router.add_static('/', path='.', name='static')
        
        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # API endpoints
        self.app.router.add_post('/api/initialize', self.initialize_system)
        self.app.router.add_get('/api/status', self.get_status)
    
    def setup_cors(self):
        """Setup CORS for the application."""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def serve_index(self, request):
        """Serve the main web interface."""
        try:
            # Try the new location first
            html_path = 'web_interface/web_interface.html'
            if not os.path.exists(html_path):
                # Fallback to old location
                html_path = 'web_interface/index.html'
            
            with open(html_path, 'r') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text="Web interface not found", status=404)
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        await self.ws_manager.add_connection(ws)
        
        # Send initial system state
        await ws.send_str(json.dumps({
            'type': 'system_state',
            'running': self.orchestrator.is_running,
            'paused': getattr(self.orchestrator, 'is_paused', False)
        }))
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.handle_websocket_message(data)
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON received: {msg.data}")
                elif msg.type == WSMsgType.ERROR:
                    print(f"❌ WebSocket error: {ws.exception()}")
        except Exception as e:
            print(f"❌ WebSocket handler error: {e}")
        finally:
            await self.ws_manager.remove_connection(ws)
        
        return ws
    
    async def handle_websocket_message(self, data: Dict[str, Any]):
        """Handle messages from WebSocket clients."""
        message_type = data.get('type')
        
        if message_type == 'start_search':
            if not self.orchestrator.is_running:
                search_term = data.get('searchTerm', '')
                location = data.get('location', '')
                max_jobs = data.get('maxJobs', 25)
                settings = data.get('settings', {})
                
                # Update settings
                self.orchestrator.update_settings(settings)
                
                # Initialize system if not already done
                if not self.orchestrator.vector_db:
                    await self.orchestrator.initialize()
                
                # Start the job search in background
                asyncio.create_task(
                    self.orchestrator.web_run_job_search(search_term, location, max_jobs)
                )
        
        elif message_type == 'pause':
            await self.orchestrator.pause()
        
        elif message_type == 'resume':
            await self.orchestrator.resume()
        
        elif message_type == 'stop':
            await self.orchestrator.stop()
        
        elif message_type == 'update_settings':
            settings = data.get('settings', {})
            self.orchestrator.update_settings(settings)
    
    async def initialize_system(self, request):
        """Initialize the orchestrator system."""
        try:
            if not self.orchestrator.vector_db:
                success = await self.orchestrator.initialize()
                return web.json_response({'success': success})
            return web.json_response({'success': True, 'message': 'Already initialized'})
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)}, status=500)
    
    async def get_status(self, request):
        """Get current system status."""
        return web.json_response({
            'running': self.orchestrator.is_running,
            'paused': getattr(self.orchestrator, 'is_paused', False),
            'total_applications': self.orchestrator.total_applications,
            'successful_applications': self.orchestrator.successful_applications
        })
    
    async def start_server(self):
        """Start the web server."""
        print("🚀 Starting AutoApply AI Web Server")
        print("=" * 50)
        
        # Initialize the orchestrator
        print("🤖 Initializing AI system...")
        try:
            success = await self.orchestrator.initialize()
            if success:
                print("✅ AI system initialized successfully")
            else:
                print("⚠️ AI system initialization had issues")
        except Exception as e:
            print(f"❌ AI system initialization failed: {e}")
        
        # Start the web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        print(f"🌐 Web server started at http://{self.host}:{self.port}")
        print("📱 Open your browser and navigate to the URL above")
        print("🎯 Ready to start applying to jobs!")
        print("\n🔧 Controls:")
        print("  - Use the web interface to start job searches")
        print("  - Press Ctrl+C to stop the server")
        
        try:
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Shutting down server...")
            await self.orchestrator.stop()
            await runner.cleanup()
            print("✅ Server stopped")

async def main():
    """Main entry point for the web server."""
    server = AutoApplyWebServer(host='localhost', port=8000)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())
