import openai

class OpenAILLM:
    def __init__(self, api_key):
        openai.api_key = api_key
    
    def query_llm(self, prompt, query, model="gpt-4", max_tokens=4096):
        try:
            # Combine prompt and query
            full_prompt = f"{prompt}\n{query}"
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=max_tokens,  # Adjust based on needs
                temperature=0.7,  # Adjust creativity
            )
            
            # Extract response text
            reply = response['choices'][0]['message']['content'].strip()
            return reply
        
        except Exception as e:
            return f"An error occurred: {str(e)}"