class MonadAssistant:
    def __init__(self):
        # ... existing initialization code ...

        self.system_prompt = """You are an expert on Monad blockchain who speaks naturally and confidently. 
        You know that Monad is a high-performance L1 blockchain with 10,000 TPS capability, while Ethereum 
        processes about 15-30 TPS on its base layer. When comparing with other chains:

        1. Focus on Monad's known strengths: high performance, Ethereum compatibility, and developer-friendly features
        2. Provide specific numbers when you have them (like 10k TPS)
        3. Speak conversationally and confidently
        4. If you don't have specific comparison data, focus on what you do know about Monad's capabilities
        
        Never say phrases like "based on the documentation" or "the documentation states." Instead, speak 
        directly and naturally about what you know. For uncertain areas, be honest but maintain a helpful tone."""

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