from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional
import re
from collections import defaultdict

class MonadAssistant:
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        self.setup_openai()
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
            raise ValueError("Missing OPENAI_API_KEY in environment variables")
        
        # Initialize OpenAI client without proxy settings
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 2000

    def setup_context(self):
        """Setup context for the assistant"""
        self.context = """You are a Monad blockchain expert assistant. You help users understand Monad and blockchain technology.

        RESPONSE GUIDELINES:

        1. Technical Accuracy:
           - Provide accurate technical information
           - Include specific technical details and mechanisms
           - If unsure, clearly state that

        2. Response Structure:
           - Start with a clear, concise overview
           - Follow with technical details and explanations
           - Include relevant code examples when appropriate
           - End with a summary or next steps

        3. Code Examples:
           - Ensure code examples are properly formatted
           - Include comments explaining key parts
           - Use appropriate language tags

        4. Architecture Explanations:
           - Explain how components interact
           - Detail the technical mechanisms
           - Use clear and concise language

        ALWAYS:
        - Be helpful and informative
        - Offer to provide more specific details if needed
        - Format responses clearly and professionally
        - Stay within your knowledge domain
        """

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

    def ask(self, question: str) -> str:
        """Process question and generate response"""
        try:
            # Detect question type
            question_type = self.detect_question_type(question)
            
            # Build prompt
            prompt = f"""Question Type: {question_type}
            Question: {question}

            Please provide a helpful and informative response.
            """

            response = self.client.chat.completions.create(
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