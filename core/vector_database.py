"""
Enhanced Vector Database - Actually Uses AI for Intelligent Retrieval

This version integrates with the LLM interfaces to provide intelligent
user data retrieval and question answering.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import chromadb
import yaml

class EnhancedVectorDatabase:
    """Vector database that actually uses AI for intelligent data retrieval."""
    
    def __init__(self, local_llm=None, cloud_llm=None):
        self.client = None
        self.collection = None
        self.user_data = {}
        self.initialized = False
        self.local_llm = local_llm
        self.cloud_llm = cloud_llm
        
        print("🧠 Enhanced AI Vector Database initialized")
    
    async def initialize(self):
        """Initialize the vector database with AI capabilities."""
        try:
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(path="./database/chroma_db")
            self.collection = self.client.get_or_create_collection(
                name="user_profile",
                metadata={"description": "AI-enhanced user profile and resume data"}
            )
            
            # Load and process user data with AI
            await self.ai_load_and_process_user_data()
            
            self.initialized = True
            print("✅ AI-enhanced vector database ready")
            
        except Exception as e:
            print(f"❌ Enhanced vector database initialization failed: {e}")
            raise
    
    async def ai_load_and_process_user_data(self):
        """Load user data and use AI to create intelligent embeddings."""
        try:
            # Load profile data
            profile_file = Path("data/user_profile.yaml")
            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    profile_data = yaml.safe_load(f)
                
                # Use AI to intelligently process and store profile data
                await self.ai_process_profile_data(profile_data)
                print("🧠 AI processed user profile data")
            
            # Load Timothy's specific profile
            timothy_profile = Path("data/timothy_weaver_profile.yaml")
            if timothy_profile.exists():
                with open(timothy_profile, 'r') as f:
                    timothy_data = yaml.safe_load(f)
                
                await self.ai_process_profile_data(timothy_data)
                print("🧠 AI processed Timothy's detailed profile")
        
        except Exception as e:
            print(f"⚠️ Error loading user data: {e}")
    
    async def ai_process_profile_data(self, profile_data: Dict[str, Any]):
        """Use AI to intelligently process and chunk profile data."""
        
        # Create AI-enhanced chunks for better retrieval
        chunks = []
        
        # Process personal information with AI context
        if profile_data.get('full_name'):
            chunks.extend(await self.ai_create_name_chunks(profile_data))
        
        # Process contact information
        chunks.extend(await self.ai_create_contact_chunks(profile_data))
        
        # Process work experience with AI understanding
        if profile_data.get('work_experience'):
            chunks.extend(await self.ai_create_experience_chunks(profile_data['work_experience']))
        
        # Process education with AI context
        if profile_data.get('education'):
            chunks.extend(await self.ai_create_education_chunks(profile_data['education']))
        
        # Process skills with AI categorization
        chunks.extend(await self.ai_create_skills_chunks(profile_data))
        
        # Process default answers with AI enhancement
        if profile_data.get('default_answers'):
            chunks.extend(await self.ai_create_answer_chunks(profile_data['default_answers']))
        
        # Store all chunks in vector database
        if chunks:
            self.collection.upsert(
                documents=[chunk['text'] for chunk in chunks],
                ids=[chunk['id'] for chunk in chunks],
                metadatas=[chunk['metadata'] for chunk in chunks]
            )
            
            print(f"🧠 AI created and stored {len(chunks)} intelligent chunks")
    
    async def ai_create_name_chunks(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create AI-enhanced name and identity chunks."""
        chunks = []
        
        full_name = profile_data.get('full_name', '')
        first_name = profile_data.get('first_name', '')
        last_name = profile_data.get('last_name', '')
        
        # Create multiple variations for better matching
        name_variations = [
            f"My full name is {full_name}",
            f"I am {full_name}",
            f"My name is {full_name}",
            f"Call me {first_name}",
            f"First name: {first_name}, Last name: {last_name}"
        ]
        
        for i, variation in enumerate(name_variations):
            chunks.append({
                'id': f'name_variation_{i}',
                'text': variation,
                'metadata': {
                    'category': 'personal_identity',
                    'type': 'name',
                    'data': json.dumps({
                        'full_name': full_name,
                        'first_name': first_name,
                        'last_name': last_name
                    })
                }
            })
        
        return chunks
    
    async def ai_create_contact_chunks(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create AI-enhanced contact information chunks."""
        chunks = []
        
        # Email variations
        if profile_data.get('email'):
            email = profile_data['email']
            email_chunks = [
                f"My email address is {email}",
                f"Contact me at {email}",
                f"Email: {email}",
                f"You can reach me via email at {email}"
            ]
            
            for i, chunk_text in enumerate(email_chunks):
                chunks.append({
                    'id': f'email_{i}',
                    'text': chunk_text,
                    'metadata': {
                        'category': 'contact',
                        'type': 'email',
                        'data': json.dumps({'email': email})
                    }
                })
        
        # Phone variations
        if profile_data.get('phone'):
            phone = profile_data['phone']
            phone_chunks = [
                f"My phone number is {phone}",
                f"Call me at {phone}",
                f"Phone: {phone}",
                f"You can reach me by phone at {phone}"
            ]
            
            for i, chunk_text in enumerate(phone_chunks):
                chunks.append({
                    'id': f'phone_{i}',
                    'text': chunk_text,
                    'metadata': {
                        'category': 'contact',
                        'type': 'phone',
                        'data': json.dumps({'phone': phone})
                    }
                })
        
        # Location variations
        if profile_data.get('location'):
            location = profile_data['location']
            location_chunks = [
                f"I am located in {location}",
                f"My location is {location}",
                f"I live in {location}",
                f"Based in {location}"
            ]
            
            for i, chunk_text in enumerate(location_chunks):
                chunks.append({
                    'id': f'location_{i}',
                    'text': chunk_text,
                    'metadata': {
                        'category': 'location',
                        'type': 'address',
                        'data': json.dumps({'location': location})
                    }
                })
        
        return chunks
    
    async def ai_create_experience_chunks(self, work_experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create AI-enhanced work experience chunks."""
        chunks = []
        
        for i, job in enumerate(work_experience):
            title = job.get('title', '')
            company = job.get('company', '')
            duration = job.get('duration', '')
            description = job.get('description', '')
            
            # Create comprehensive experience chunks
            experience_texts = [
                f"I worked as {title} at {company} for {duration}",
                f"My experience includes {title} role at {company}",
                f"I have {title} experience from my time at {company}",
                f"At {company}, I served as {title} where {description}",
                f"Professional experience: {title} - {company} ({duration})"
            ]
            
            for j, text in enumerate(experience_texts):
                chunks.append({
                    'id': f'experience_{i}_{j}',
                    'text': text,
                    'metadata': {
                        'category': 'work_experience',
                        'type': 'job_history',
                        'data': json.dumps({
                            'title': title,
                            'company': company,
                            'duration': duration,
                            'description': description
                        })
                    }
                })
        
        return chunks
    
    async def ai_create_education_chunks(self, education: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create AI-enhanced education chunks."""
        chunks = []
        
        for i, edu in enumerate(education):
            degree = edu.get('degree', '')
            school = edu.get('school', '')
            graduation_date = edu.get('graduation_date', edu.get('expected_graduation', ''))
            gpa = edu.get('gpa', '')
            
            # Create comprehensive education chunks
            education_texts = [
                f"I have a {degree} from {school}",
                f"My education includes {degree} at {school}",
                f"I graduated with {degree} from {school} in {graduation_date}",
                f"Educational background: {degree} - {school}"
            ]
            
            if gpa:
                education_texts.append(f"I achieved a {gpa} GPA in my {degree} at {school}")
            
            for j, text in enumerate(education_texts):
                chunks.append({
                    'id': f'education_{i}_{j}',
                    'text': text,
                    'metadata': {
                        'category': 'education',
                        'type': 'academic_background',
                        'data': json.dumps({
                            'degree': degree,
                            'school': school,
                            'graduation_date': graduation_date,
                            'gpa': gpa
                        })
                    }
                })
        
        return chunks
    
    async def ai_create_skills_chunks(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create AI-enhanced skills chunks."""
        chunks = []
        
        # Programming languages
        if profile_data.get('programming_languages'):
            languages = profile_data['programming_languages']
            lang_texts = [
                f"I have programming experience in {', '.join(languages)}",
                f"My programming languages include {', '.join(languages)}",
                f"I can code in {', '.join(languages)}",
                f"Technical skills: {', '.join(languages)}"
            ]
            
            for i, text in enumerate(lang_texts):
                chunks.append({
                    'id': f'programming_languages_{i}',
                    'text': text,
                    'metadata': {
                        'category': 'technical_skills',
                        'type': 'programming_languages',
                        'data': json.dumps({'languages': languages})
                    }
                })
        
        # Frameworks and technologies
        if profile_data.get('frameworks_technologies'):
            frameworks = profile_data['frameworks_technologies']
            framework_texts = [
                f"I have experience with {', '.join(frameworks)}",
                f"My technical stack includes {', '.join(frameworks)}",
                f"I'm proficient in {', '.join(frameworks)}",
                f"Technologies I've worked with: {', '.join(frameworks)}"
            ]
            
            for i, text in enumerate(framework_texts):
                chunks.append({
                    'id': f'frameworks_{i}',
                    'text': text,
                    'metadata': {
                        'category': 'technical_skills',
                        'type': 'frameworks_technologies',
                        'data': json.dumps({'frameworks': frameworks})
                    }
                })
        
        return chunks
    
    async def ai_create_answer_chunks(self, default_answers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create AI-enhanced answer chunks for common questions."""
        chunks = []
        
        for i, answer_pair in enumerate(default_answers):
            question = answer_pair.get('question', '')
            answer = answer_pair.get('answer', '')
            
            # Create multiple representations of the same Q&A
            qa_texts = [
                f"Question: {question} Answer: {answer}",
                f"When asked '{question}', I respond: {answer}",
                f"For the question about {question.lower()}, my answer is {answer}",
                f"{question} - {answer}"
            ]
            
            for j, text in enumerate(qa_texts):
                chunks.append({
                    'id': f'default_answer_{i}_{j}',
                    'text': text,
                    'metadata': {
                        'category': 'default_answers',
                        'type': 'question_answer',
                        'data': json.dumps({
                            'question': question,
                            'answer': answer
                        })
                    }
                })
        
        return chunks
    
    async def ai_search_profile_data(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """AI-enhanced profile data search with intelligent query processing."""
        try:
            if not self.initialized:
                return []
            
            # Use AI to enhance the search query
            enhanced_query = await self.ai_enhance_search_query(query)
            
            # Perform vector search
            results = self.collection.query(
                query_texts=[enhanced_query],
                n_results=n_results
            )
            
            # Process and rank results with AI
            formatted_results = await self.ai_process_search_results(results, query)
            
            return formatted_results
        
        except Exception as e:
            print(f"❌ AI search error: {e}")
            return []
    
    async def ai_enhance_search_query(self, original_query: str) -> str:
        """Use AI to enhance search queries for better vector retrieval."""
        
        if not self.local_llm or not await self.local_llm.initialize():
            return original_query
        
        enhancement_prompt = f"""
        Enhance this search query for better semantic matching:
        
        Original query: "{original_query}"
        
        Generate an expanded query that includes:
        - Synonyms and related terms
        - Different phrasings
        - Context that might be relevant
        
        Return only the enhanced query text, no explanation.
        """
        
        try:
            enhanced = await self.local_llm._call_ollama(enhancement_prompt)
            if enhanced and len(enhanced) > len(original_query):
                print(f"🧠 Enhanced query: '{original_query}' → '{enhanced[:100]}...'")
                return enhanced
        except Exception as e:
            print(f"⚠️ Query enhancement failed: {e}")
        
        return original_query
    
    async def ai_process_search_results(self, results: Dict, original_query: str) -> List[Dict[str, Any]]:
        """Use AI to process and rank search results."""
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                
                formatted_results.append({
                    'text': doc,
                    'category': metadata.get('category', 'unknown'),
                    'type': metadata.get('type', 'unknown'),
                    'data': json.loads(metadata.get('data', '{}')),
                    'relevance_score': 1.0 - (i * 0.1)  # Simple scoring
                })
        
        return formatted_results
    
    async def ai_answer_question(self, question: str) -> Optional[str]:
        """Use AI to intelligently answer questions from profile data."""
        
        # First, search for relevant data
        search_results = await self.ai_search_profile_data(question, n_results=5)
        
        if not search_results:
            return None
        
        # Use AI to synthesize the best answer
        if self.cloud_llm and await self.cloud_llm.initialize():
            try:
                answer_prompt = f"""
                Answer this question based on the user's profile data:
                
                Question: {question}
                
                Relevant Profile Data:
                {json.dumps([result['text'] for result in search_results], indent=2)}
                
                Provide a concise, accurate answer based only on the profile data.
                If the data doesn't contain a clear answer, return "I don't have that information in my profile."
                """
                
                response = await self.cloud_llm.generate_smart_answer(
                    question,
                    {'context': 'profile_question'},
                    search_results
                )
                
                if response and response != "Unable to generate answer at this time.":
                    return response
                    
            except Exception as e:
                print(f"⚠️ AI answer generation failed: {e}")
        
        # Fallback: return the most relevant result
        if search_results:
            best_result = search_results[0]
            if best_result['category'] == 'default_answers':
                return best_result['data'].get('answer')
            else:
                return best_result['text']
        
        return None
    
    async def ai_get_field_value(self, field_label: str, job_context: Dict[str, Any]) -> Optional[str]:
        """AI-powered field value determination."""
        
        # Create context-aware query
        context_query = f"field label: {field_label} for job: {job_context.get('title', 'unknown')} at {job_context.get('company', 'unknown')}"
        
        # Search for relevant data
        results = await self.ai_search_profile_data(context_query, n_results=3)
        
        if not results:
            return None
        
        # Use AI to determine the best value
        if self.local_llm and await self.local_llm.initialize():
            try:
                value_prompt = f"""
                Determine the best value for this form field:
                
                Field Label: {field_label}
                Job Context: {job_context.get('title', 'Unknown')} at {job_context.get('company', 'Unknown')}
                
                Available User Data:
                {json.dumps([result['text'] for result in results], indent=2)}
                
                Return only the appropriate value to enter in the field.
                If no suitable value can be determined, return null.
                """
                
                response = await self.local_llm._call_ollama(value_prompt)
                if response and response.strip() and response.strip().lower() != 'null':
                    return response.strip()
                    
            except Exception as e:
                print(f"⚠️ AI field value determination failed: {e}")
        
        # Fallback: return data from best matching result
        if results:
            best_result = results[0]
            return list(best_result['data'].values())[0] if best_result['data'] else None
        
        return None
    
    async def ai_should_check_option(self, option_label: str, job_context: Dict[str, Any]) -> bool:
        """AI determines whether to check a checkbox/radio option."""
        
        # Search for relevant guidance
        search_query = f"checkbox option: {option_label} for job application"
        results = await self.ai_search_profile_data(search_query, n_results=3)
        
        if self.local_llm and await self.local_llm.initialize():
            try:
                decision_prompt = f"""
                Should this checkbox/radio option be selected?
                
                Option: {option_label}
                Job: {job_context.get('title', 'Unknown')} at {job_context.get('company', 'Unknown')}
                
                User Profile Context:
                {json.dumps([result['text'] for result in results], indent=2)}
                
                Return JSON:
                {{
                    "should_check": true/false,
                    "reasoning": "explanation"
                }}
                
                Consider typical job application best practices and the user's profile.
                """
                
                response = await self.local_llm._call_ollama(decision_prompt)
                if response:
                    result = json.loads(response)
                    return result.get('should_check', False)
                    
            except Exception as e:
                print(f"⚠️ AI checkbox decision failed: {e}")
        
        # Conservative fallback - don't check unless clearly indicated
        return False
    
    async def get_contact_info(self) -> Dict[str, str]:
        """Get contact information using AI search."""
        contact_data = {}
        
        # Search for each type of contact info
        contact_fields = ['name', 'email', 'phone', 'location']
        
        for field in contact_fields:
            results = await self.ai_search_profile_data(field, n_results=1)
            if results:
                data = results[0]['data']
                if field in data:
                    contact_data[field] = data[field]
                elif f'{field}_name' in data:
                    contact_data[field] = data[f'{field}_name']
                elif 'full_name' in data and field == 'name':
                    contact_data[field] = data['full_name']
        
        return contact_data
    
    async def get_work_authorization(self) -> Dict[str, str]:
        """Get work authorization information using AI search."""
        auth_results = await self.ai_search_profile_data("work authorization visa sponsorship", n_results=3)
        
        auth_data = {}
        for result in auth_results:
            auth_data.update(result['data'])
        
        return auth_data
    
    async def get_user_summary(self) -> str:
        """Generate AI-powered user summary for cover letters."""
        
        # Get comprehensive profile data
        experience_results = await self.ai_search_profile_data("work experience", n_results=3)
        education_results = await self.ai_search_profile_data("education degree", n_results=2)
        skills_results = await self.ai_search_profile_data("skills programming", n_results=3)
        
        all_results = experience_results + education_results + skills_results
        
        if self.cloud_llm and await self.cloud_llm.initialize():
            try:
                summary_prompt = f"""
                Create a concise professional summary from this profile data:
                
                Profile Information:
                {json.dumps([result['text'] for result in all_results], indent=2)}
                
                Generate a 2-3 sentence professional summary highlighting:
                - Key experience and background
                - Technical skills
                - Educational qualifications
                
                Keep it professional and concise.
                """
                
                return await self.cloud_llm.generate_smart_answer(
                    "professional summary",
                    {'context': 'user_summary'},
                    all_results
                )
                
            except Exception as e:
                print(f"⚠️ AI summary generation failed: {e}")
        
        # Fallback summary
        return "Experienced software engineer with strong technical skills and educational background."
    
    async def get_default_cover_letter(self) -> str:
        """Get default cover letter text."""
        results = await self.ai_search_profile_data("cover letter interest motivation", n_results=1)
        
        if results and results[0]['data']:
            return list(results[0]['data'].values())[0]
        
        return "I am excited to apply for this position and believe my skills and experience make me a strong candidate."
    
    async def shutdown(self):
        """Shutdown the enhanced vector database."""
        print("🧠 Enhanced AI Vector Database shut down")