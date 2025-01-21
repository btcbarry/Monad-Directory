import openai
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional
import re
from collections import defaultdict
import json

class MonadAssistant:
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        self.setup_openai()
        self.load_docs()
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
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Missing OPENAI_API_KEY")
            
            openai.api_key = api_key
            self.model = "gpt-3.5-turbo"
            self.max_tokens = 2000
            self.logger.info("OpenAI client initialized successfully")
        except Exception as e:
            self.logger.error(f"OpenAI client initialization error: {str(e)}")
            raise

    def load_docs(self):
        """Load the scraped Monad documentation"""
        try:
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'monad_docs.json'),
                os.path.join(os.getcwd(), 'monad_docs.json'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monad_docs.json')
            ]
            
            docs_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    docs_path = path
                    break
            
            if not docs_path:
                raise FileNotFoundError("Could not find monad_docs.json in any expected location")
            
            with open(docs_path, 'r', encoding='utf-8') as f:
                self.docs = json.load(f)
                self.logger.info(f"Documentation loaded successfully from {docs_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading documentation: {str(e)}")
            raise

    def setup_context(self):
        """Setup context for the assistant"""
        self.context = """You are an expert on Monad blockchain who speaks naturally and confidently. 
        You know that Monad is a high-performance L1 blockchain with 10,000 TPS capability, while Ethereum 
        processes about 15-30 TPS on its base layer. When answering questions:

        1. Focus on Monad's key strengths:
           - High performance (10,000 TPS)
           - Full Ethereum compatibility
           - Developer-friendly environment
           - Advanced execution engine
           - Optimized for DeFi and complex applications

        2. Technical Accuracy:
           - Provide accurate technical information
           - Include specific technical details when available
           - If unsure, be honest but helpful

        3. Response Style:
           - Speak naturally and confidently
           - Avoid phrases like "according to documentation"
           - Use clear, engaging language
           - Include technical details without being overly formal

        4. When discussing technical aspects:
           - Explain concepts clearly without being overly technical
           - Use real-world comparisons when helpful
           - Highlight practical benefits for users and developers

        5. For uncertain areas:
           - Focus on known capabilities
           - Be honest about limitations
           - Maintain a helpful, forward-looking tone

        Remember: You're having a conversation, not reading from a manual. Keep responses 
        clear, engaging, and focused on providing valuable insights about Monad."""

    def detect_question_type(self, question: str) -> str:
        """Detect the type of question"""
        question_lower = question.lower()
        
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

    def find_relevant_docs(self, question: str) -> str:
        """Find relevant documentation for the question"""
        keywords = question.lower().split()
        
        scored_content = []
        for section, pages in self.docs.items():
            for title, content in pages.items():
                score = 0
                content_lower = content['content'].lower()
                
                matches = []
                for word in keywords:
                    if word in content_lower:
                        score += 1
                        matches.append(word)
                    if word in title.lower():
                        score += 2
                        matches.append(f"{word}(title)")
                
                if matches:
                    scored_content.append({
                        'title': title,
                        'content': content['content'],
                        'score': score,
                        'matches': matches
                    })
        
        scored_content.sort(key=lambda x: x['score'], reverse=True)
        top_content = scored_content[:3]
        
        relevant_content = [
            f"\nFrom {item['title']}:\n{item['content'].strip()}"
            for item in top_content
        ]
        
        return "\n".join(relevant_content) if relevant_content else "No specific documentation found."

    def ask(self, question: str) -> str:
        """Process question and generate response"""
        try:
            question_type = self.detect_question_type(question)
            relevant_docs = self.find_relevant_docs(question)
            
            prompt = f"""Question Type: {question_type}
            
            Relevant Information:
            {relevant_docs}
            
            Question: {question}

            Instructions:
            1. Use the provided information to inform your response, but speak naturally
            2. Focus on Monad's strengths and capabilities
            3. If specific information isn't available, focus on related aspects you're confident about
            4. Use a conversational tone while maintaining technical accuracy
            5. Format key points clearly but avoid saying "according to documentation"
            6. If the question is outside Monad's scope, acknowledge this and guide the conversation 
               back to relevant Monad topics
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.context},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "I encountered an error. Please try again."

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
        print("Please ensure OPENAI_API_KEY is set")