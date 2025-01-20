from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import logging
from typing import Dict, List, Optional
import re
from collections import defaultdict

class MonadAssistant:
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        self.setup_openai()
        self.load_documentation()
        self.setup_context()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monad_assistant.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_openai(self):
        """Setup OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in .env file")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo-16k"
        self.max_tokens = 2000

    def load_documentation(self):
        """Load and process documentation"""
        try:
            with open('monad_docs.json', 'r', encoding='utf-8') as f:
                self.docs = json.load(f)
            self.logger.info("Documentation loaded successfully")
            
            # Create searchable index
            self.doc_index = defaultdict(list)
            self.build_search_index()
            
        except FileNotFoundError:
            self.logger.error("Documentation file not found. Run docs_fetcher.py first")
            raise
        except json.JSONDecodeError:
            self.logger.error("Invalid documentation format")
            raise
        except Exception as e:
            self.logger.error(f"Error loading documentation: {str(e)}")
            raise

    def build_search_index(self):
        """Build enhanced keyword index for documentation"""
        for section, pages in self.docs.items():
            for title, content in pages.items():
                # Index all words from content and title
                text = f"{title} {str(content['content'])}".lower()
                
                # Extract technical terms and keywords
                technical_terms = re.findall(r'(?:monad|blockchain|smart contract|api|rpc|eth_\w+|debug_\w+|transaction|block|consensus|execution|parallel|async)\w*', text)
                general_words = set(re.findall(r'\b\w{3,}\b', text))
                
                # Weight technical terms higher
                for term in technical_terms:
                    self.doc_index[term].append((section, title, 2.0))  # Higher weight
                
                # Add section-specific boosting
                section_boost = {
                    'api': 1.5,
                    'architecture': 1.3,
                    'getting-started': 1.2
                }.get(section, 1.0)
                
                for word in general_words:
                    self.doc_index[word].append((section, title, 1.0 * section_boost))

    def setup_context(self):
        """Setup enhanced context for the assistant"""
        self.context = """You are a Monad blockchain expert assistant. Use ONLY the provided documentation to answer questions.

        RESPONSE GUIDELINES:

        1. Technical Accuracy:
           - Use ONLY information from the provided documentation
           - Include specific technical details and mechanisms
           - Reference relevant documentation sections and URLs
           - If information isn't in docs, clearly state that

        2. Response Structure:
           - Start with a clear, concise overview
           - Follow with technical details and explanations
           - Include relevant code examples when available
           - End with related documentation references

        3. Code Examples:
           - Use exact code from documentation when available
           - Ensure code examples are properly formatted
           - Include comments explaining key parts
           - Reference the source documentation URL

        4. API References:
           - Provide exact endpoint specifications
           - Include all relevant parameters
           - Show example requests and responses
           - Reference the API documentation URL

        5. Architecture Explanations:
           - Explain how components interact
           - Detail the technical mechanisms
           - Reference specific documentation sections
           - Include diagrams or visual descriptions when available

        ALWAYS:
        - Stay strictly within the provided documentation
        - Include URLs to relevant documentation sections
        - Offer to provide more specific details if needed
        - Clearly indicate when information is not in the documentation
        - Format code blocks properly with appropriate language tags
        """

    def find_relevant_content(self, question: str) -> str:
        """Find relevant documentation content with improved matching"""
        # Extract keywords from question
        keywords = set(re.findall(r'\b\w{3,}\b', question.lower()))
        technical_terms = re.findall(r'(?:monad|blockchain|smart contract|api|rpc|eth_\w+|debug_\w+|transaction|block|consensus|execution|parallel|async)\w*', question.lower())
        
        # Score sections based on relevance
        section_scores = defaultdict(float)
        
        # Process general keywords
        for keyword in keywords:
            matches = self.doc_index.get(keyword, [])
            for section, title, weight in matches:
                section_scores[(section, title)] += weight
        
        # Boost score for technical term matches
        for term in technical_terms:
            matches = self.doc_index.get(term, [])
            for section, title, weight in matches:
                section_scores[(section, title)] += weight * 2  # Double weight for technical terms
        
        # Additional context-based boosting
        question_lower = question.lower()
        if 'how to' in question_lower or 'how do i' in question_lower:
            for section, title in section_scores:
                if section == 'getting-started':
                    section_scores[(section, title)] *= 1.5
        elif 'api' in question_lower or 'endpoint' in question_lower:
            for section, title in section_scores:
                if section == 'api':
                    section_scores[(section, title)] *= 1.5
        
        # Sort by relevance score
        sorted_sections = sorted(
            section_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]  # Top 3 most relevant
        
        # Build content string with metadata
        content = []
        for (section, title), score in sorted_sections:
            doc_content = self.docs[section][title]
            content.append(f"\nSection: {section}")
            content.append(f"Title: {title}")
            content.append(f"URL: {doc_content['url']}")
            content.append(str(doc_content['content']))
            content.append("-" * 80)
        
        return "\n".join(content)

    def detect_question_type(self, question: str) -> str:
        """Detect the type of question with enhanced categorization"""
        question_lower = question.lower()
        
        # Technical patterns
        if any(term in question_lower for term in ['architecture', 'consensus', 'execution', 'parallel']):
            return "technical_architecture"
        elif any(term in question_lower for term in ['api', 'endpoint', 'rpc', 'eth_', 'debug_']):
            return "api_reference"
        elif any(term in question_lower for term in ['how to', 'how do i', 'implement', 'deploy']):
            return "implementation"
        elif any(term in question_lower for term in ['what is', 'what are', 'explain', 'describe']):
            return "explanation"
        else:
            return "general"

    def ask(self, question: str) -> str:
        """Process question and generate response"""
        try:
            # Get relevant documentation content
            relevant_content = self.find_relevant_content(question)
            
            # Detect question type
            question_type = self.detect_question_type(question)
            
            # Build complete prompt
            prompt = f"""Question Type: {question_type}

            Relevant Documentation:
            {relevant_content}

            Question: {question}

            Remember to:
            1. Use specific details from the documentation above
            2. Include technical information and URLs
            3. Format code examples properly
            4. Offer to explain more
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.context},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=self.max_tokens,
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"

    def chat(self):
        """Run interactive chat session"""
        print("\n🚀 Welcome to Monad Assistant!")
        print("Ask anything about Monad (type 'exit' to quit)")
        print("\nExample questions:")
        print("- What is Monad's architecture?")
        print("- How does parallel execution work?")
        print("- What APIs are available for smart contracts?")
        print("- How do I deploy a contract using Foundry?")
        print("- Explain Monad's consensus mechanism")
        
        while True:
            question = input("\nQuestion: ").strip()
            if question.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nThinking...")
            response = self.ask(question)
            print(f"\nResponse:\n{response}\n")

if __name__ == "__main__":
    try:
        assistant = MonadAssistant()
        assistant.chat()
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        print(f"\nError: {str(e)}")
        print("Please ensure documentation is loaded and OPENAI_API_KEY is set")