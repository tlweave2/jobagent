"""
Vector Database - User Profile and Resume Data Storage

Stores user information in a vector database for intelligent retrieval
during job applications. Built from user questionnaire responses.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import chromadb
import yaml

class VectorDatabase:
    """Vector database for storing and retrieving user profile data."""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.user_data = {}
        self.initialized = False
        
        print("📊 Vector Database initialized")
    
    async def initialize(self):
        """Initialize the vector database."""
        try:
            # Initialize ChromaDB with new persistent client
            self.client = chromadb.PersistentClient(
                path="./database/chroma_db"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="user_profile",
                metadata={"description": "User profile and resume data"}
            )
            
            # Load user data if exists
            await self.load_user_data()
            
            self.initialized = True
            print("✅ Vector database ready")
            
        except Exception as e:
            print(f"❌ Vector database initialization failed: {e}")
            raise
    
    async def load_user_data(self):
        """Load existing user data from files."""
        try:
            # Try to load from YAML files
            profile_file = Path("data/user_profile.yaml")
            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    profile_data = yaml.safe_load(f)
                
                # Store basic profile data
                await self.store_profile_data(profile_data)
                print("📋 Loaded existing user profile")
            
            # Check if we have questionnaire data
            questionnaire_file = Path("data/questionnaire_responses.json")
            if questionnaire_file.exists():
                with open(questionnaire_file, 'r') as f:
                    questionnaire_data = json.load(f)
                
                await self.store_questionnaire_data(questionnaire_data)
                print("📝 Loaded questionnaire responses")
            else:
                print("📝 No questionnaire data found - user should complete questionnaire")
        
        except Exception as e:
            print(f"⚠️  Error loading user data: {e}")
    
    async def store_profile_data(self, profile_data: Dict[str, Any]):
        """Store basic profile data in vector database."""
        try:
            # Convert profile data to searchable text chunks
            chunks = []
            
            # Personal information
            if profile_data.get('full_name'):
                chunks.append({
                    'id': 'personal_name',
                    'text': f"My name is {profile_data['full_name']}",
                    'category': 'personal',
                    'data': {'name': profile_data['full_name']}
                })
            
            if profile_data.get('email'):
                chunks.append({
                    'id': 'personal_email',
                    'text': f"My email address is {profile_data['email']}",
                    'category': 'contact',
                    'data': {'email': profile_data['email']}
                })
            
            if profile_data.get('phone'):
                chunks.append({
                    'id': 'personal_phone',
                    'text': f"My phone number is {profile_data['phone']}",
                    'category': 'contact',
                    'data': {'phone': profile_data['phone']}
                })
            
            if profile_data.get('location'):
                chunks.append({
                    'id': 'personal_location',
                    'text': f"I am located in {profile_data['location']}",
                    'category': 'personal',
                    'data': {'location': profile_data['location']}
                })
            
            # Work authorization
            if profile_data.get('visa_status'):
                chunks.append({
                    'id': 'work_authorization',
                    'text': f"My work authorization status: {profile_data['visa_status']}",
                    'category': 'work_auth',
                    'data': {'visa_status': profile_data['visa_status']}
                })
            
            # Default answers
            if profile_data.get('default_answers'):
                for answer in profile_data['default_answers']:
                    question = answer.get('question', '')
                    response = answer.get('answer', '')
                    chunks.append({
                        'id': f"default_answer_{len(chunks)}",
                        'text': f"Question: {question} Answer: {response}",
                        'category': 'default_answers',
                        'data': answer
                    })
            
            # Store in vector database
            if chunks:
                self.collection.upsert(
                    documents=[chunk['text'] for chunk in chunks],
                    ids=[chunk['id'] for chunk in chunks],
                    metadatas=[{
                        'category': chunk['category'],
                        'data': json.dumps(chunk['data'])
                    } for chunk in chunks]
                )
                
                print(f"📊 Stored {len(chunks)} profile data chunks")
        
        except Exception as e:
            print(f"❌ Error storing profile data: {e}")
    
    async def store_questionnaire_data(self, questionnaire_data: Dict[str, Any]):
        """Store detailed questionnaire responses."""
        try:
            chunks = []
            
            for key, value in questionnaire_data.items():
                if isinstance(value, str) and value.strip():
                    chunks.append({
                        'id': f'questionnaire_{key}',
                        'text': f"{key}: {value}",
                        'category': 'questionnaire',
                        'data': {key: value}
                    })
            
            if chunks:
                self.collection.upsert(
                    documents=[chunk['text'] for chunk in chunks],
                    ids=[chunk['id'] for chunk in chunks],
                    metadatas=[{
                        'category': chunk['category'],
                        'data': json.dumps(chunk['data'])
                    } for chunk in chunks]
                )
                
                print(f"📝 Stored {len(chunks)} questionnaire responses")
        
        except Exception as e:
            print(f"❌ Error storing questionnaire data: {e}")
    
    async def search_profile_data(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant profile data based on query."""
        try:
            if not self.initialized:
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    formatted_results.append({
                        'text': doc,
                        'category': metadata.get('category', 'unknown'),
                        'data': json.loads(metadata.get('data', '{}'))
                    })
            
            return formatted_results
        
        except Exception as e:
            print(f"❌ Error searching profile data: {e}")
            return []
    
    async def get_contact_info(self) -> Dict[str, str]:
        """Get basic contact information."""
        try:
            contact_data = {}
            
            # Search for contact information
            name_results = await self.search_profile_data("name full name")
            email_results = await self.search_profile_data("email address")
            phone_results = await self.search_profile_data("phone number")
            location_results = await self.search_profile_data("location address")
            
            # Extract data
            for result in name_results:
                if 'name' in result['data']:
                    contact_data['name'] = result['data']['name']
                    break
            
            for result in email_results:
                if 'email' in result['data']:
                    contact_data['email'] = result['data']['email']
                    break
            
            for result in phone_results:
                if 'phone' in result['data']:
                    contact_data['phone'] = result['data']['phone']
                    break
            
            for result in location_results:
                if 'location' in result['data']:
                    contact_data['location'] = result['data']['location']
                    break
            
            return contact_data
        
        except Exception as e:
            print(f"❌ Error getting contact info: {e}")
            return {}
    
    async def get_work_authorization(self) -> Dict[str, str]:
        """Get work authorization information."""
        try:
            auth_results = await self.search_profile_data("work authorization visa sponsorship")
            
            for result in auth_results:
                if 'visa_status' in result['data']:
                    return result['data']
            
            return {}
        
        except Exception as e:
            print(f"❌ Error getting work authorization: {e}")
            return {}
    
    async def answer_question(self, question: str) -> Optional[str]:
        """Find the best answer to a specific question."""
        try:
            # Search for relevant answers
            results = await self.search_profile_data(question, n_results=3)
            
            # Look for exact or similar question matches
            for result in results:
                if result['category'] == 'default_answers':
                    stored_question = result['data'].get('question', '').lower()
                    if any(word in stored_question for word in question.lower().split()):
                        return result['data'].get('answer')
            
            # Look for general questionnaire responses
            for result in results:
                if result['category'] == 'questionnaire':
                    return list(result['data'].values())[0]
            
            return None
        
        except Exception as e:
            print(f"❌ Error answering question: {e}")
            return None
