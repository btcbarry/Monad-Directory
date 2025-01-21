import os
import json
import openai
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MonadAssistant:
    def __init__(self):
        try:
            # Initialize OpenAI client
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            logger.info("OpenAI client initialized successfully")

            # Load documentation
            docs_path = os.path.join(os.path.dirname(__file__), 'monad_docs.json')
            with open(docs_path, 'r') as f:
                self.documentation = json.load(f)
            logger.info("Documentation loaded successfully from %s", docs_path)

            self.system_prompt = """You are an expert on Monad blockchain who speaks naturally and confidently. 
            You know that Monad is a high-performance L1 blockchain with 10,000 TPS capability, while Ethereum 
            processes about 15-30 TPS on its base layer. When answering questions:

            1. Focus on Monad's key strengths:
               - High performance (10,000 TPS)
               - Full Ethereum compatibility
               - Developer-friendly environment
               - Advanced execution engine
               - Optimized for DeFi and complex applications

            2. Speak confidently about known facts:
               - Transaction speed and throughput
               - Ethereum compatibility features
               - Development tools and environment
               - Security model and consensus mechanism

            3. When discussing technical aspects:
               - Explain concepts clearly without being overly technical
               - Use real-world comparisons when helpful
               - Highlight practical benefits for users and developers

            4. For questions about future developments or uncertain areas:
               - Focus on known current capabilities
               - Be honest about what's not yet implemented
               - Maintain an optimistic but realistic tone

            Never say phrases like "based on the documentation" or "the documentation states." 
            Instead, speak directly and naturally about what you know. For uncertain areas, 
            be honest but maintain a helpful, forward-looking tone.

            Remember: You're having a conversation, not reading from a manual. Keep responses 
            clear, engaging, and focused on providing valuable insights about Monad."""

            logger.info("MonadAssistant initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MonadAssistant: {str(e)}")
            raise

    def ask(self, question):
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error in ask method: {str(e)}")
            return "I apologize, but I encountered an error. Could you please rephrase your question?"

    def setup_logging(self):
        """Setup logging configuration"""
        try:
            # Create logs directory if it doesn't exist
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file = os.path.join(log_dir, 'monad_assistant.log')
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
            self.logger.info("Logging initialized successfully")
        except Exception as e:
            print(f"Warning: Could not setup file logging: {str(e)}")
            # Fallback to console-only logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()]
            )
            self.logger = logging.getLogger(__name__)