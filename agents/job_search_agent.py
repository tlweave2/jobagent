"""
Job Search Agent - LinkedIn and External Job Discovery

This agent searches for jobs across LinkedIn and external job sites.
It finds ALL jobs matching the search term with no filtering or limits.
"""

import asyncio
import time
from typing import List, Dict, Any
from urllib.parse import urlencode
from playwright.async_api import async_playwright

class JobSearchAgent:
    """Agent responsible for finding all jobs matching search criteria."""
    
    def __init__(self, user_profile_db):
        self.user_profile_db = user_profile_db
        self.browser = None
        self.context = None
        self.page = None
        
        print("🔍 Job Search Agent initialized")
    
    async def initialize(self):
        """Initialize the browser and search capabilities."""
        print("🔍 Starting browser for job search...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        self.page = await self.context.new_page()
        
        print("✅ Job Search Agent ready")
    
    async def search_jobs(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for ALL jobs matching the search term."""
        print(f"🔍 Searching for jobs: '{search_term}'")
        
        all_jobs = []
        
        # Search LinkedIn
        linkedin_jobs = await self.search_linkedin_jobs(search_term)
        all_jobs.extend(linkedin_jobs)
        print(f"   📋 Found {len(linkedin_jobs)} LinkedIn jobs")
        
        # Search other job sites
        external_jobs = await self.search_external_sites(search_term)
        all_jobs.extend(external_jobs)
        print(f"   📋 Found {len(external_jobs)} external jobs")
        
        # Remove duplicates
        unique_jobs = self.deduplicate_jobs(all_jobs)
        print(f"🎯 Total unique jobs found: {len(unique_jobs)}")
        
        return unique_jobs
    
    async def search_linkedin_jobs(self, search_term: str) -> List[Dict[str, Any]]:
        """Search LinkedIn for all matching jobs."""
        jobs = []
        
        try:
            # Build LinkedIn search URL
            search_params = {
                'keywords': search_term,
                'location': 'United States',
                'f_LF': 'f_AL',  # Easy Apply filter
                'sortBy': 'DD'   # Sort by date (newest first)
            }
            
            search_url = f"https://www.linkedin.com/jobs/search/?{urlencode(search_params)}"
            print(f"🌐 Loading LinkedIn search: {search_url}")
            
            await self.page.goto(search_url, timeout=30000)
            await self.page.wait_for_load_state("networkidle")
            
            # Handle LinkedIn login if needed
            if "login" in self.page.url:
                print("🔐 LinkedIn login required...")
                await self.handle_linkedin_login()
                # Retry search after login
                await self.page.goto(search_url, timeout=30000)
                await self.page.wait_for_load_state("networkidle")
            
            # Extract all job cards
            jobs = await self.extract_linkedin_job_cards()
            
            # Load more jobs by scrolling and clicking "See more jobs"
            await self.load_all_linkedin_jobs()
            more_jobs = await self.extract_linkedin_job_cards()
            jobs.extend(more_jobs)
            
        except Exception as e:
            print(f"❌ Error searching LinkedIn: {e}")
        
        return jobs
    
    async def extract_linkedin_job_cards(self) -> List[Dict[str, Any]]:
        """Extract job information from LinkedIn job cards."""
        jobs = []
        
        try:
            # Wait for job cards to load
            await asyncio.sleep(3)
            
            # Find all job card elements
            job_cards = await self.page.query_selector_all(".jobs-search__results-list li")
            
            for card in job_cards:
                try:
                    # Extract job URL
                    link_element = await card.query_selector("a[data-control-name='job_search_job_result_click']")
                    if not link_element:
                        continue
                    
                    job_url = await link_element.get_attribute("href")
                    if not job_url:
                        continue
                    
                    # Make sure it's a full URL
                    if job_url.startswith("/"):
                        job_url = "https://www.linkedin.com" + job_url
                    
                    # Extract job title
                    title_element = await card.query_selector(".job-search-card__title")
                    title = await title_element.inner_text() if title_element else "Unknown Title"
                    title = title.strip()
                    
                    # Extract company
                    company_element = await card.query_selector(".job-search-card__subtitle")
                    company = await company_element.inner_text() if company_element else "Unknown Company"
                    company = company.strip()
                    
                    # Extract location
                    location_element = await card.query_selector(".job-search-card__location")
                    location = await location_element.inner_text() if location_element else "Unknown Location"
                    location = location.strip()
                    
                    # Check if it has Easy Apply
                    easy_apply_element = await card.query_selector("button:has-text('Easy Apply')")
                    has_easy_apply = easy_apply_element is not None
                    
                    # Only include Easy Apply jobs
                    if has_easy_apply:
                        jobs.append({
                            'url': job_url,
                            'title': title,
                            'company': company,
                            'location': location,
                            'source': 'LinkedIn',
                            'easy_apply': True
                        })
                    
                except Exception as e:
                    print(f"   ⚠️  Error extracting job card: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error extracting job cards: {e}")
        
        return jobs
    
    async def load_all_linkedin_jobs(self):
        """Load all available jobs by scrolling and clicking 'See more jobs'."""
        try:
            # Scroll to bottom to load more jobs
            for _ in range(5):  # Scroll multiple times
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            
            # Look for "See more jobs" button and click it
            see_more_buttons = await self.page.query_selector_all("button:has-text('See more jobs')")
            for button in see_more_buttons:
                try:
                    if await button.is_visible():
                        await button.click()
                        await asyncio.sleep(3)
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"   ⚠️  Error loading more jobs: {e}")
    
    async def handle_linkedin_login(self):
        """Handle LinkedIn login if required."""
        # This would integrate with the user's stored credentials
        # For now, we'll wait for manual login
        print("⚠️  LinkedIn login required - please log in manually")
        print("⏳ Waiting for login to complete...")
        
        # Wait for URL to change away from login page
        try:
            await self.page.wait_for_url(lambda url: "login" not in url, timeout=60000)
            print("✅ Login completed")
        except:
            print("⚠️  Login timeout - continuing anyway")
    
    async def search_external_sites(self, search_term: str) -> List[Dict[str, Any]]:
        """Search external job sites (Indeed, Glassdoor, etc.)."""
        jobs = []
        
        # For now, we'll focus on LinkedIn
        # Future expansion would include Indeed, Glassdoor, etc.
        print("📋 External job site search not yet implemented")
        
        return jobs
    
    def deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate jobs based on URL and title+company."""
        seen_urls = set()
        seen_jobs = set()
        unique_jobs = []
        
        for job in jobs:
            # Check URL
            if job['url'] in seen_urls:
                continue
            
            # Check title + company combination
            job_signature = (job['title'].lower(), job['company'].lower())
            if job_signature in seen_jobs:
                continue
            
            seen_urls.add(job['url'])
            seen_jobs.add(job_signature)
            unique_jobs.append(job)
        
        return unique_jobs
    
    async def shutdown(self):
        """Shutdown the job search agent."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("🔍 Job Search Agent shut down")
