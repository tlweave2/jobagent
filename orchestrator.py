"""
Job Application Orchestrator - Main System Controller

This is the central hub that coordinates all agents to automatically apply to jobs.
Architecture: Multi-agent system with LangChain, Vector DB, and AI decision making.
"""

import asyncio
import sys
from typing import Dict, List, Any
from datetime import datetime
import logging

# Core components
from core.vector_database import VectorDatabase
from core.logger import ApplicationLogger

# Agents
from agents.job_search_agent import JobSearchAgent
from agents.navigation_agent import NavigationAgent
from agents.form_filling_agent import FormFillingAgent
from agents.email_agent import EmailAgent
from agents.overlord_agent import OverlordAgent

# LLM interfaces
from llm.local_llm import LocalLLM
from llm.cloud_llm import CloudLLM

class JobApplicationOrchestrator:
    """Main orchestrator that coordinates all agents."""
    
    def __init__(self):
        self.logger = ApplicationLogger()
        self.vector_db = None
        self.local_llm = None
        self.cloud_llm = None
        
        # Agents
        self.job_search_agent = None
        self.navigation_agent = None
        self.form_filling_agent = None
        self.email_agent = None
        self.overlord_agent = None
        
        # State
        self.is_running = False
        self.total_applications = 0
        self.successful_applications = 0
        
        print("🎯 Job Application Orchestrator initialized")
    
    async def initialize(self):
        """Initialize all system components."""
        print("\n🚀 Initializing Job Application System")
        print("=" * 60)
        
        try:
            # Initialize vector database
            print("📊 Loading vector database...")
            self.vector_db = VectorDatabase()
            await self.vector_db.initialize()
            
            # Initialize LLMs
            print("🧠 Connecting to AI models...")
            self.local_llm = LocalLLM()
            self.cloud_llm = CloudLLM()
            
            # Initialize agents
            print("🤖 Starting agents...")
            await self.initialize_agents()
            
            print("✅ System initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def initialize_agents(self):
        """Initialize all agents."""
        # Job Search Agent
        self.job_search_agent = JobSearchAgent(
            user_profile_db=self.vector_db
        )
        await self.job_search_agent.initialize()
        
        # Navigation Agent
        self.navigation_agent = NavigationAgent()
        await self.navigation_agent.initialize()
        
        # Form Filling Agent
        self.form_filling_agent = FormFillingAgent(
            user_profile_db=self.vector_db
        )
        await self.form_filling_agent.initialize()
        
        # Email Agent
        email_config = {
            'email': 'user@example.com',  # Will be loaded from vector DB
            'password': 'app_password',   # Will be loaded from vector DB
            'imap_server': 'imap.gmail.com',
            'imap_port': 993
        }
        self.email_agent = EmailAgent(email_config)
        await self.email_agent.initialize()
        
        # Overlord Agent (monitors everything)
        self.overlord_agent = OverlordAgent()
        await self.overlord_agent.initialize()
    
    async def run_job_search(self, search_term: str):
        """Main entry point: search and apply to ALL jobs found."""
        print(f"\n🔍 Starting job search for: '{search_term}'")
        print("🎯 Goal: Apply to ALL jobs found (no filtering)")
        
        self.is_running = True
        
        try:
            # Step 1: Search for jobs
            print("\n📋 Step 1: Searching for jobs...")
            jobs = await self.job_search_agent.search_jobs(search_term)
            
            if not jobs:
                print("❌ No jobs found for search term")
                return
            
            print(f"🎯 Found {len(jobs)} jobs to apply to")
            
            # Step 2: Apply to each job
            print("\n🚀 Step 2: Starting application process...")
            
            for i, job in enumerate(jobs, 1):
                if not self.is_running:
                    print("⏹️  Process stopped by user")
                    break
                
                print(f"\n📝 Applying to job {i}/{len(jobs)}")
                await self.apply_to_job(job)
                
                # Brief delay between applications
                if i < len(jobs):
                    await asyncio.sleep(5)
            
            # Summary
            print(f"\n🎉 Job search completed!")
            print(f"📊 Total jobs: {len(jobs)}")
            print(f"✅ Successful applications: {self.successful_applications}")
            print(f"📋 Application rate: {self.successful_applications/len(jobs)*100:.1f}%")
            
        except Exception as e:
            print(f"❌ Error during job search: {e}")
            await self.logger.log_error("job_search", str(e))
        
        finally:
            self.is_running = False
    
    async def apply_to_job(self, job: Dict[str, Any]):
        """Apply to a single job with full agent coordination."""
        job_title = job.get('title', 'Unknown')
        job_company = job.get('company', 'Unknown')
        job_url = job.get('url', '')
        
        print(f"🎯 Applying: {job_title} at {job_company}")
        
        # Start overlord monitoring
        monitoring_task = asyncio.create_task(
            self.overlord_agent.monitor_application(job_url)
        )
        
        try:
            # Step 1: Navigate to job
            print("🧭 Navigating to job page...")
            nav_success = await self.navigation_agent.navigate_to_job(job_url)
            
            if not nav_success:
                print("❌ Failed to navigate to job")
                await self.logger.log_application(job, "NAVIGATION_FAILED")
                return
            
            # Step 2: Apply to job using form filling agent
            print("📝 Starting application process...")
            application_result = await self.form_filling_agent.apply_to_job(
                navigation_agent=self.navigation_agent,
                job_details=job
            )
            
            # Step 3: Handle any email verification if needed
            if application_result.get('needs_email_verification'):
                print("📧 Handling email verification...")
                verification_result = await self.email_agent.handle_verification()
                if verification_result:
                    print("✅ Email verification completed")
                else:
                    print("⚠️  Email verification failed")
            
            # Log result
            if application_result.get('success'):
                print("✅ Application successful!")
                self.successful_applications += 1
                await self.logger.log_application(job, "SUCCESS", application_result)
            else:
                print("❌ Application failed")
                await self.logger.log_application(job, "FAILED", application_result)
            
            self.total_applications += 1
            
        except Exception as e:
            print(f"❌ Error applying to job: {e}")
            await self.logger.log_application(job, "ERROR", {"error": str(e)})
        
        finally:
            # Stop monitoring
            monitoring_task.cancel()
    
    async def stop(self):
        """Stop the job application process."""
        print("⏹️  Stopping job application system...")
        self.is_running = False
        
        # Shutdown agents
        if self.navigation_agent:
            await self.navigation_agent.shutdown()
        if self.form_filling_agent:
            await self.form_filling_agent.shutdown()
        if self.email_agent:
            await self.email_agent.shutdown()
        if self.overlord_agent:
            await self.overlord_agent.shutdown()
        
        print("✅ System shutdown complete")

async def main():
    """Main entry point - launches web interface by default."""
    print("🤖 AutoApply AI - Intelligent Job Application System")
    print("=" * 60)
    print("🌐 Starting web interface...")
    
    try:
        # Try to start the web interface
        from web_interface.web_server import AutoApplyWebServer
        import webbrowser
        
        server = AutoApplyWebServer(host='localhost', port=8000)
        
        # Open browser after a short delay
        def open_browser():
            print("🌐 Opening web browser at http://localhost:8000")
            webbrowser.open('http://localhost:8000')
        
        # Schedule browser opening after 2 seconds
        import asyncio
        asyncio.get_event_loop().call_later(2, open_browser)
        
        # Start the server
        await server.start_server()
        
    except ImportError as e:
        print(f"⚠️  Web interface not available: {e}")
        print("🔄 Falling back to command line interface...")
        await main_cli()
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        print("🔄 Falling back to command line interface...")
        await main_cli()

async def main_cli():
    """Command line interface fallback."""
    print("💻 Command Line Interface")
    print("=" * 30)
    
    # Get search term from user
    search_term = input("\n🔍 Enter job search term: ").strip()
    
    if not search_term:
        print("❌ No search term provided")
        return
    
    # Initialize orchestrator
    orchestrator = JobApplicationOrchestrator()
    
    try:
        # Initialize system
        success = await orchestrator.initialize()
        if not success:
            print("❌ System initialization failed")
            return
        
        # Confirm with user
        print(f"\n⚠️  WARNING: This will apply to ALL jobs found for '{search_term}'")
        print("This system does not filter or limit applications.")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("👋 Operation cancelled")
            return
        
        # Run job search and applications
        await orchestrator.run_job_search(search_term)
        
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        await orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
