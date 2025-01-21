def ask(self, question: str) -> str:
    """Process question and generate response"""
    try:
        question_type = self.detect_question_type(question)
        relevant_docs = self.find_relevant_docs(question)
        
        prompt = f"""Question Type: {question_type}
        
        Background Knowledge:
        {relevant_docs}
        
        Question: {question}

        Instructions:
        1. Respond in a friendly, conversational tone
        2. Never mention "documentation" or "based on" in your response
        3. If the question is outside your knowledge:
           - Acknowledge it honestly
           - Share related insights you're confident about
           - Keep the conversation flowing
        4. Use simple analogies and comparisons when helpful
        5. Focus on practical benefits and real-world applications
        6. Keep technical details clear but not overwhelming

        Remember: You're a knowledgeable friend having a casual conversation about Monad. 
        Be engaging and natural while maintaining accuracy."""

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a friendly Monad blockchain expert having a casual conversation. You're knowledgeable and enthusiastic but always honest about what you do and don't know."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Slightly higher for more natural language
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
            
    except Exception as e:
        self.logger.error(f"Error generating response: {str(e)}")
        return "I encountered an error. Please try again."