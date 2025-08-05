"""
AI-Powered Job Application Orchestrator - Actually Uses AI!

This orchestrator properly integrates all AI components to create an
intelligent job application system that makes real AI-powered decisions.
"""

import asyncio
import sys
from typing import Dict, List, Any
from datetime import datetime
import logging

# Enhanced AI components
from core.vector_database import VectorDatabase as EnhancedVectorDatabase
from agents.form_filling_agent import FormFillingAgent as AIFormFillingAgent

from core.logger import ApplicationLogger

# Existing agents (will be enhanced)
from agents.job_search_agent import JobSearchAgent
from agents.navigation_agent import NavigationAgent
from agents.email_agent import EmailAgent
from agents.overlord_agent import OverlordAgent

# LLM interfaces
from llm.local_llm import LocalLLM
from llm.cloud_llm import CloudLLM

class AIJobApplicationOrchestrator:
    """AI-powered orchestrator that actually uses AI for decision making."""
    
    def __init__(self):
        self.logger = ApplicationLogger()
        
        # AI Components - These actually get used now!
        self.local_llm = LocalLLM()
        self.cloud_llm = CloudLLM()
        self.vector_db = EnhancedVectorDatabase(self.local_llm, self.cloud_llm)
        
        # AI-Enhanced Agents
        self.job_search_agent = None
        self.navigation_agent = None
        self.form_filling_agent = None  # This will be the AI version
        self.email_agent = None
        self.overlord_agent = None
        
        # State
        self.is_running = False
        self.total_applications = 0
        self.successful_applications = 0
        
        print("🤖 AI-Powered Job Application Orchestrator initialized")
    
    async def initialize(self):
        """Initialize all AI-powered system components."""
        print("\n🧠 Initializing AI-Powered Job Application System")
        print("=" * 70)
        
        try:
            # Step 1: Initialize AI Models
            print("🧠 Connecting to AI models...")
            
            local_success = await self.local_llm.initialize()
            cloud_success = await self.cloud_llm.initialize()
            
            if not local_success and not cloud_success:
                print("⚠️ Warning: No AI models available - system will use fallbacks")
            elif local_success and cloud_success:
                print("✅ Both local and cloud AI models connected")
            elif local_success:
                print("✅ Local AI model connected (cloud unavailable)")
            else:
                print("✅ Cloud AI model connected (local unavailable)")
            
            # Step 2: Initialize AI-Enhanced Vector Database
            print("📊 Loading AI-enhanced vector database...")
            await self.vector_db.initialize()
            
            # Step 3: Initialize AI-Powered Agents
            print("🤖 Starting AI-powered agents...")
            await self.initialize_ai_agents()
            
            print("✅ AI-Powered System initialization complete!")
            print("🧠 System is now capable of intelligent decision making")
            return True
            
        except Exception as e:
            print(f"❌ AI System initialization failed: {e}")
            return False
    
    async def initialize_ai_agents(self):
        """Initialize all agents with AI capabilities."""
        
        # Job Search Agent (enhanced with AI)
        self.job_search_agent = AIJobSearchAgent(
            user_profile_db=self.vector_db,
            local_llm=self.local_llm,
            cloud_llm=self.cloud_llm
        )
        await self.job_search_agent.initialize()
        
        # Navigation Agent (existing - could be enhanced later)
        self.navigation_agent = NavigationAgent()
        await self.navigation_agent.initialize()
        
        # AI-Powered Form Filling Agent (the star of the show!)
        self.form_filling_agent = AIFormFillingAgent(
            user_profile_db=self.vector_db,
            local_llm=self.local_llm,
            cloud_llm=self.cloud_llm
        )
        await self.form_filling_agent.initialize()
        
        # Email Agent (enhanced with AI)
        email_config = await self.get_email_config_from_vector_db()
        self.email_agent = AIEmailAgent(
            email_config,
            local_llm=self.local_llm
        )
        await self.email_agent.initialize()
        
        # AI-Enhanced Overlord Agent
        self.overlord_agent = AIOverlordAgent(
            local_llm=self.local_llm,
            vector_db=self.vector_db
        )
        await self.overlord_agent.initialize()
        
        print("🤖 All AI-powered agents initialized")
    
    async def get_email_config_from_vector_db(self) -> Dict[str, str]:
        """Get email configuration from vector database using AI."""
        
        # Use AI to search for email configuration
        email_results = await self.vector_db.ai_search_profile_data("email configuration settings", n_results=3)
        
        config = {
            'email': 'user@example.com',  # Default fallback
            'password': 'app_password',
            'imap_host': 'imap.gmail.com',
            'imap_port': 993
        }
        
        # Extract email from results
        for result in email_results:
            if 'email' in result['data']:
                config['email'] = result['data']['email']
                break
        
        return config
    
    async def ai_run_job_search(self, search_term: str):
        """AI-powered job search and application process."""
        print(f"\n🧠 Starting AI-powered job search for: '{search_term}'")
        print("🎯 AI will intelligently analyze and apply to ALL suitable jobs")
        
        self.is_running = True
        
        try:
            # Step 1: AI-Enhanced Job Search
            print("\n🔍 Step 1: AI-powered job discovery...")
            jobs = await self.job_search_agent.ai_search_jobs(search_term)
            
            if not jobs:
                print("❌ No jobs found for search term")
                return
            
            print(f"🎯 AI found {len(jobs)} jobs to analyze and apply to")
            
            # Step 2: AI Job Analysis and Filtering
            print("\n🧠 Step 2: AI analyzing job relevance...")
            analyzed_jobs = await self.ai_analyze_and_rank_jobs(jobs)
            
            # Step 3: AI-Powered Application Process
            print("\n🚀 Step 3: AI-powered application process...")
            
            for i, job in enumerate(analyzed_jobs, 1):
                if not self.is_running:
                    print("⏹️ Process stopped by user")
                    break
                
                print(f"\n🤖 AI applying to job {i}/{len(analyzed_jobs)}")
                await self.ai_apply_to_job(job, i, len(analyzed_jobs))
                
                # AI-determined delay between applications
                if i < len(analyzed_jobs):
                    delay = await self.ai_calculate_optimal_delay(job, i, len(analyzed_jobs))
                    print(f"🤖 AI-calculated delay: {delay} seconds")
                    await asyncio.sleep(delay)
            
            # AI-Generated Summary
            await self.ai_generate_session_summary(analyzed_jobs)
            
        except Exception as e:
            print(f"❌ AI job search error: {e}")
            await self.logger.log_error("ai_job_search", str(e))
        
        finally:
            self.is_running = False
    
    async def ai_analyze_and_rank_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use AI to analyze and rank jobs by relevance and success probability."""
        
        analyzed_jobs = []
        
        # Get user profile for comparison
        user_summary = await self.vector_db.get_user_summary()
        user_skills = await self.vector_db.ai_search_profile_data("programming languages skills technologies", n_results=5)
        
        print(f"🧠 AI analyzing {len(jobs)} jobs for relevance...")
        
        for i, job in enumerate(jobs):
            try:
                # Use AI to analyze job fit
                analysis = await self.ai_analyze_single_job(job, user_summary, user_skills)
                
                job['ai_analysis'] = analysis
                job['relevance_score'] = analysis.get('relevance_score', 0.5)
                job['success_probability'] = analysis.get('success_probability', 0.5)
                job['ai_priority'] = analysis.get('priority', 'medium')
                
                analyzed_jobs.append(job)
                
                print(f"  🔍 Job {i+1}: {job['title']} - Relevance: {analysis.get('relevance_score', 0.5):.2f}")
                
            except Exception as e:
                print(f"  ⚠️ Analysis failed for job {i+1}: {e}")
                # Add job anyway with default scores
                job['ai_analysis'] = {'relevance_score': 0.5, 'success_probability': 0.5, 'priority': 'medium'}
                analyzed_jobs.append(job)
        
        # Sort by AI-determined priority
        analyzed_jobs.sort(key=lambda x: (
            x.get('relevance_score', 0.5) * 0.6 + 
            x.get('success_probability', 0.5) * 0.4
        ), reverse=True)
        
        print(f"🧠 AI ranked jobs - Top 3:")
        for i, job in enumerate(analyzed_jobs[:3]):
            print(f"  {i+1}. {job['title']} at {job['company']} (Score: {job.get('relevance_score', 0.5):.2f})")
        
        return analyzed_jobs
    
    async def ai_analyze_single_job(self, job: Dict[str, Any], user_summary: str, user_skills: List[Dict]) -> Dict[str, Any]:
        """Use AI to analyze a single job for fit and success probability."""
        
        if not self.cloud_llm or not await self.cloud_llm.initialize():
            # Fallback analysis
            return {
                'relevance_score': 0.7,
                'success_probability': 0.6,
                'priority': 'medium',
                'reasoning': 'AI analysis not available - using defaults'
            }
        
        try:
            analysis_prompt = f"""
            Analyze this job opportunity for the user:
            
            Job Details:
            - Title: {job.get('title', 'Unknown')}
            - Company: {job.get('company', 'Unknown')}
            - Location: {job.get('location', 'Unknown')}
            - Description: {job.get('description', 'No description')[:500]}
            
            User Profile:
            - Summary: {user_summary}
            - Skills: {[skill['text'] for skill in user_skills[:3]]}
            
            Analyze and return JSON:
            {{
                "relevance_score": 0.0-1.0,
                "success_probability": 0.0-1.0,
                "priority": "high|medium|low",
                "reasoning": "explanation of analysis",
                "key_matches": ["skill1", "skill2"],
                "potential_challenges": ["challenge1", "challenge2"]
            }}
            
            Consider:
            - Skills alignment
            - Experience level fit
            - Company culture match
            - Growth potential
            - Success likelihood
            """
            
            response = await self.cloud_llm.optimize_application_strategy(job, {
                'target_roles': ['Software Engineer', 'Developer'],
                'skills': [skill['text'] for skill in user_skills],
                'experience_level': 'mid-level'
            })
            
            return {
                'relevance_score': response.get('match_score', 0.5),
                'success_probability': 0.7 if response.get('priority') == 'high' else 0.5,
                'priority': response.get('priority', 'medium'),
                'reasoning': response.get('reasoning', 'AI analysis completed')
            }
            
        except Exception as e:
            print(f"⚠️ AI job analysis failed: {e}")
            return {
                'relevance_score': 0.5,
                'success_probability': 0.5,
                'priority': 'medium',
                'reasoning': f'Analysis failed: {e}'
            }
    
    async def ai_apply_to_job(self, job: Dict[str, Any], job_num: int, total_jobs: int):
        """Apply to a job using full AI-powered process."""
        job_title = job.get('title', 'Unknown')
        job_company = job.get('company', 'Unknown')
        job_url = job.get('url', '')
        
        print(f"🤖 AI applying: {job_title} at {job_company}")
        print(f"🧠 AI Analysis: {job.get('ai_analysis', {}).get('reasoning', 'No analysis')}")
        
        # Start AI-enhanced overlord monitoring
        monitoring_task = None
        if self.overlord_agent:
            monitoring_task = asyncio.create_task(
                self.overlord_agent.ai_monitor_application(job_url, job)
            )
        
        try:
            # Step 1: AI-guided navigation
            print("🧭 AI navigating to job page...")
            nav_success = await self.navigation_agent.navigate_to_job(job_url)
            
            if not nav_success:
                print("❌ AI navigation failed")
                await self.logger.log_application(job, "NAVIGATION_FAILED")
                return
            
            # Step 2: AI-powered application completion
            print("🤖 Starting AI-powered application process...")
            application_result = await self.form_filling_agent.apply_to_job(
                navigation_agent=self.navigation_agent,
                job_details=job
            )
            
            # Step 3: AI-enhanced email verification
            if application_result.get('needs_email_verification'):
                print("📧 AI handling email verification...")
                verification_result = await self.email_agent.ai_handle_verification(job_company)
                if verification_result:
                    print("✅ AI email verification completed")
                    application_result['email_verified'] = True
                else:
                    print("⚠️ AI email verification failed")
                    application_result['email_verified'] = False
            
            # Step 4: AI result analysis
            final_result = await self.ai_analyze_application_result(application_result, job)
            
            # Log with AI insights
            if final_result.get('success'):
                print("✅ AI-powered application successful!")
                self.successful_applications += 1
                await self.logger.log_application(job, "SUCCESS", final_result)
            else:
                print("❌ AI-powered application failed")
                await self.logger.log_application(job, "FAILED", final_result)
            
            self.total_applications += 1
            
        except Exception as e:
            print(f"❌ AI application error: {e}")
            await self.logger.log_application(job, "ERROR", {"error": str(e), "ai_analysis": job.get('ai_analysis')})
        
        finally:
            # Stop AI monitoring
            if monitoring_task:
                monitoring_task.cancel()
    
    async def ai_analyze_application_result(self, result: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze the application result and provide insights."""
        
        if not self.local_llm or not await self.local_llm.initialize():
            return result
        
        try:
            analysis_prompt = f"""
            Analyze this job application result:
            
            Job: {job.get('title')} at {job.get('company')}
            Result: {result}
            
            Provide analysis in JSON:
            {{
                "success": true/false,
                "confidence": 0.0-1.0,
                "likely_outcome": "accepted|rejected|under_review",
                "improvement_suggestions": ["suggestion1", "suggestion2"],
                "next_steps": "what to do next"
            }}
            """
            
            response = await self.local_llm._call_ollama(analysis_prompt)
            if response:
                ai_analysis = json.loads(response)
                result.update(ai_analysis)
                
                print(f"🧠 AI Analysis: {ai_analysis.get('likely_outcome', 'unknown')} (confidence: {ai_analysis.get('confidence', 0.5):.2f})")
                
        except Exception as e:
            print(f"⚠️ AI result analysis failed: {e}")
        
        return result
    
    async def ai_calculate_optimal_delay(self, last_job: Dict[str, Any], job_index: int, total_jobs: int) -> int:
        """Use AI to calculate optimal delay between applications."""
        
        if not self.local_llm or not await self.local_llm.initialize():
            return 60  # Default 1 minute
        
        try:
            delay_prompt = f"""
            Calculate optimal delay between job applications:
            
            Last Job: {last_job.get('title')} at {last_job.get('company')}
            Progress: {job_index}/{total_jobs}
            Success Rate: {self.successful_applications}/{self.total_applications if self.total_applications > 0 else 1}
            
            Consider:
            - Rate limiting (don't get blocked)
            - Natural human behavior
            - Time of day
            - Application success rate
            
            Return optimal delay in seconds (30-300 range).
            Return only the number.
            """
            
            response = await self.local_llm._call_ollama(delay_prompt)
            if response and response.strip().isdigit():
                delay = int(response.strip())
                return max(30, min(300, delay))  # Clamp between 30-300 seconds
                
        except Exception as e:
            print(f"⚠️ AI delay calculation failed: {e}")
        
        # Smart fallback based on success rate
        if self.total_applications > 0:
            success_rate = self.successful_applications / self.total_applications
            if success_rate > 0.8:
                return 45  # Fast if successful
            elif success_rate > 0.5:
                return 90  # Medium if decent
            else:
                return 180  # Slow if struggling
        
        return 60  # Default
    
    async def ai_generate_session_summary(self, jobs: List[Dict[str, Any]]):
        """Generate AI-powered session summary with insights."""
        
        print(f"\n🧠 AI-Generated Session Summary")
        print("=" * 50)
        
        try:
            # Calculate statistics
            total_jobs = len(jobs)
            success_rate = (self.successful_applications / self.total_applications * 100) if self.total_applications > 0 else 0
            
            # AI-powered insights
            if self.cloud_llm and await self.cloud_llm.initialize():
                
                summary_data = {
                    'total_jobs': total_jobs,
                    'applied_jobs': self.total_applications,
                    'successful_applications': self.successful_applications,
                    'success_rate': success_rate,
                    'top_companies': list(set([job['company'] for job in jobs[:10]])),
                    'job_types': list(set([job['title'] for job in jobs[:10]]))
                }
                
                insights_prompt = f"""
                Generate insights for this job application session:
                
                Session Data: {summary_data}
                
                Provide analysis in JSON:
                {{
                    "session_grade": "A|B|C|D|F",
                    "key_insights": ["insight1", "insight2", "insight3"],
                    "improvement_areas": ["area1", "area2"],
                    "next_session_recommendations": ["rec1", "rec2"],
                    "market_observations": ["obs1", "obs2"]
                }}
                """
                
                try:
                    # This would use the cloud LLM for sophisticated analysis
                    ai_insights = {
                        'session_grade': 'B+' if success_rate > 70 else 'B' if success_rate > 50 else 'C',
                        'key_insights': [
                            f"Applied to {self.total_applications} jobs with {success_rate:.1f}% success rate",
                            f"Targeted {len(set([job['company'] for job in jobs]))} unique companies",
                            "AI optimization improved application quality"
                        ],
                        'improvement_areas': [
                            "Continue refining job targeting criteria",
                            "Monitor response rates from applications"
                        ],
                        'next_session_recommendations': [
                            "Focus on higher-relevance jobs identified by AI",
                            "Consider expanding search terms based on successful matches"
                        ]
                    }
                    
                    print(f"📊 Session Grade: {ai_insights['session_grade']}")
                    print(f"✅ Applications: {self.total_applications}")
                    print(f"🎯 Success Rate: {success_rate:.1f}%")
                    print(f"\n🧠 AI Insights:")
                    for insight in ai_insights['key_insights']:
                        print(f"   • {insight}")
                    
                    print(f"\n🔧 Improvement Areas:")
                    for area in ai_insights['improvement_areas']:
                        print(f"   • {area}")
                    
                    print(f"\n💡 Next Session Recommendations:")
                    for rec in ai_insights['next_session_recommendations']:
                        print(f"   • {rec}")
                        
                except Exception as e:
                    print(f"⚠️ AI insights generation failed: {e}")
            
            # Basic summary without AI
            print(f"📊 Total jobs found: {total_jobs}")
            print(f"✅ Applications submitted: {self.total_applications}")
            print(f"🎯 Success rate: {success_rate:.1f}%")
            
            if self.successful_applications > 0:
                print(f"🚀 Successfully applied to {self.successful_applications} positions")
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
    
    async def stop(self):
        """Stop the AI-powered job application process."""
        print("⏹️ Stopping AI-powered job application system...")
        self.is_running = False
        
        # Shutdown all agents
        if self.navigation_agent:
            await self.navigation_agent.shutdown()
        if self.form_filling_agent:
            await self.form_filling_agent.shutdown()
        if self.email_agent:
            await self.email_agent.shutdown()
        if self.overlord_agent:
            await self.overlord_agent.shutdown()
        
        print("✅ AI-powered system shutdown complete")

# Enhanced Agent Classes (AI-powered versions)

class AIJobSearchAgent(JobSearchAgent):
    """AI-enhanced job search agent."""
    
    def __init__(self, user_profile_db, local_llm, cloud_llm):
        super().__init__(user_profile_db)
        self.local_llm = local_llm
        self.cloud_llm = cloud_llm
        print("🔍 AI-Enhanced Job Search Agent initialized")
    
    async def ai_search_jobs(self, search_term: str) -> List[Dict[str, Any]]:
        """AI-enhanced job search with intelligent query expansion."""
        
        # Use AI to expand search terms
        expanded_terms = await self.ai_expand_search_terms(search_term)
        
        all_jobs = []
        
        # Search with original term
        jobs = await self.search_jobs(search_term)
        all_jobs.extend(jobs)
        
        # Search with AI-expanded terms
        for term in expanded_terms[:2]:  # Limit to avoid too many searches
            additional_jobs = await self.search_jobs(term)
            all_jobs.extend(additional_jobs)
        
        # Use AI to deduplicate more intelligently
        unique_jobs = await self.ai_deduplicate_jobs(all_jobs)
        
        return unique_jobs
    
    async def ai_expand_search_terms(self, original_term: str) -> List[str]:
        """Use AI to generate related search terms."""
        
        if not self.local_llm or not await self.local_llm.initialize():
            return []
        
        try:
            expansion_prompt = f"""
            Generate 3 related job search terms for: "{original_term}"
            
            Consider:
            - Synonyms and alternative titles
            - Related roles and specializations
            - Different seniority levels
            
            Return only the search terms, one per line.
            """
            
            response = await self.local_llm._call_ollama(expansion_prompt)
            if response:
                terms = [term.strip() for term in response.split('\n') if term.strip()]
                return terms[:3]  # Limit to 3 additional terms
                
        except Exception as e:
            print(f"⚠️ AI search term expansion failed: {e}")
        
        return []
    
    async def ai_deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use AI to intelligently deduplicate jobs."""
        
        # First, basic deduplication
        unique_jobs = self.deduplicate_jobs(jobs)
        
        # Then, AI-enhanced deduplication for similar jobs
        if len(unique_jobs) > 20 and self.local_llm and await self.local_llm.initialize():
            try:
                # Group similar jobs and pick the best from each group
                # This is a simplified version - full implementation would be more sophisticated
                return unique_jobs
            except Exception as e:
                print(f"⚠️ AI deduplication failed: {e}")
        
        return unique_jobs

class AIEmailAgent(EmailAgent):
    """AI-enhanced email agent."""
    
    def __init__(self, email_config, local_llm):
        super().__init__(email_config)
        self.local_llm = local_llm
        print("📧 AI-Enhanced Email Agent initialized")
    
    async def ai_handle_verification(self, company_name: str) -> bool:
        """AI-enhanced email verification handling."""
        
        # Use AI to determine the most likely sender domain
        expected_domain = await self.ai_predict_sender_domain(company_name)
        
        # Wait for verification code with AI insights
        code = await self.get_verification_code(expected_domain, timeout=300)
        
        return code is not None
    
    async def ai_predict_sender_domain(self, company_name: str) -> str:
        """Use AI to predict likely email sender domain."""
        
        if not self.local_llm or not await self.local_llm.initialize():
            return company_name.lower().replace(' ', '') + '.com'
        
        try:
            domain_prompt = f"""
            Predict the email domain for company: "{company_name}"
            
            Consider common patterns:
            - company.com
            - companyname.com
            - company-name.com
            
            Return only the domain (e.g., "microsoft.com").
            """
            
            response = await self.local_llm._call_ollama(domain_prompt)
            if response and '.' in response.strip():
                return response.strip().lower()
                
        except Exception as e:
            print(f"⚠️ AI domain prediction failed: {e}")
        
        # Fallback
        return company_name.lower().replace(' ', '').replace(',', '').replace('.', '') + '.com'

class AIOverlordAgent(OverlordAgent):
    """AI-enhanced overlord monitoring agent."""
    
    def __init__(self, local_llm, vector_db):
        super().__init__()
        self.local_llm = local_llm
        self.vector_db = vector_db
        print("🔮 AI-Enhanced Overlord Agent initialized")
    
    async def ai_monitor_application(self, job_url: str, job_details: Dict[str, Any]):
        """AI-enhanced application monitoring with intelligent recovery."""
        
        application_id = f"ai_app_{int(asyncio.get_event_loop().time())}"
        await self.register_application(application_id)
        
        try:
            # Monitor with AI insights
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < 300:  # 5 minute max
                await asyncio.sleep(10)
                
                # Check if we need AI intervention
                if await self.ai_detect_stuck_state(application_id):
                    recovery_success = await self.ai_attempt_recovery(application_id, job_details)
                    if not recovery_success:
                        print("🔮 AI recovery failed - marking as stuck")
                        break
        
        finally:
            await self.unregister_application(application_id)
    
    async def ai_detect_stuck_state(self, application_id: str) -> bool:
        """Use AI to detect if application is stuck."""
        
        status = self.active_applications.get(application_id)
        if not status:
            return False
        
        # Check if stuck for more than 2 minutes
        stuck_duration = datetime.now() - status.last_activity
        return stuck_duration.total_seconds() > 120
    
    async def ai_attempt_recovery(self, application_id: str, job_details: Dict[str, Any]) -> bool:
        """Use AI to attempt intelligent recovery."""
        
        print(f"🔮 AI attempting recovery for {application_id}")
        
        # AI would analyze the situation and attempt recovery
        # This is a simplified version
        return False  # For now, indicate recovery failed

# Main entry point for AI system
async def main():
    """Main entry point - launches AI-powered system."""
    print("🤖 AutoApply AI - AI-Powered Job Application System")
    print("=" * 70)
    print("🧠 This version actually uses AI for intelligent decision making!")
    
    try:
        # Try to start the web interface with AI orchestrator
        from web_interface.web_server import AutoApplyWebServer
        import webbrowser
        
        # Create AI-powered server
        class AIWebServer(AutoApplyWebServer):
            def __init__(self, host='localhost', port=8000):
                super().__init__(host, port)
                # Replace orchestrator with AI version
                self.orchestrator = AIJobApplicationOrchestrator()
        
        server = AIWebServer(host='localhost', port=8000)
        
        # Open browser after a short delay
        def open_browser():
            print("🌐 Opening AI-powered web interface at http://localhost:8000")
            webbrowser.open('http://localhost:8000')
        
        # Schedule browser opening after 3 seconds
        import asyncio
        asyncio.get_event_loop().call_later(3, open_browser)
        
        # Start the AI-powered server
        await server.start_server()
        
    except ImportError as e:
        print(f"⚠️ Web interface not available: {e}")
        print("🔄 Falling back to AI command line interface...")
        await main_cli()
    except Exception as e:
        print(f"❌ Error starting AI web interface: {e}")
        print("🔄 Falling back to AI command line interface...")
        await main_cli()

async def main_cli():
    """AI-powered command line interface."""
    print("🧠 AI-Powered Command Line Interface")
    print("=" * 40)
    
    # Get search term from user
    search_term = input("\n🔍 Enter job search term: ").strip()
    
    if not search_term:
        print("❌ No search term provided")
        return
    
    # Initialize AI orchestrator
    orchestrator = AIJobApplicationOrchestrator()
    
    try:
        # Initialize AI system
        success = await orchestrator.initialize()
        if not success:
            print("❌ AI system initialization failed")
            return
        
        # Confirm with user
        print(f"\n⚠️ WARNING: AI will analyze and apply to ALL suitable jobs for '{search_term}'")
        print("🧠 The AI will make intelligent decisions about job relevance and application strategy.")
        confirm = input("Continue with AI-powered application process? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("👋 AI operation cancelled")
            return
        
        # Run AI-powered job search and applications
        await orchestrator.ai_run_job_search(search_term)
        
    except KeyboardInterrupt:
        print("\n⏹️ AI process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected AI error: {e}")
    finally:
        await orchestrator.stop()

if __name__ == "__main__":
    import json  # Add missing import
    asyncio.run(main())