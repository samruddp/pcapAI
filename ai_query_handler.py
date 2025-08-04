import openai
import json
import time
import requests

class AIQueryHandler:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.api_key = api_key
    
    def test_connection(self):
        """Test internet connectivity and OpenAI API access."""
        try:
            # Test basic internet connectivity
            response = requests.get("https://www.google.com", timeout=5)
            print("✓ Internet connection: OK")
        except requests.RequestException:
            print("✗ Internet connection: FAILED")
            return False
        
        try:
            # Test OpenAI API connectivity
            response = requests.get("https://api.openai.com/v1/models", 
                                  headers={"Authorization": f"Bearer {self.api_key}"}, 
                                  timeout=10)
            if response.status_code == 200:
                print("✓ OpenAI API connection: OK")
                return True
            else:
                print(f"✗ OpenAI API connection: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.RequestException as e:
            print(f"✗ OpenAI API connection: {e}")
            return False
    
    def query(self, user_question, analysis_data):
        """Send query to OpenAI with pcap analysis data."""
        
        print("Testing connectivity...")
        if not self.test_connection():
            raise Exception("Connection test failed. Check your internet connection and API key.")
        
        # Prepare context for AI
        context = f"""
You are an expert network analyst. You have been provided with analysis data from a pcap (packet capture) file.
The user will ask questions about this network traffic data. Please provide clear, accurate answers in plain English.

Analysis Data:
{json.dumps(analysis_data, indent=2)}

Please answer the following question about this network traffic data:
"""
        
        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Sending query to OpenAI (attempt {attempt + 1}/{max_retries})...")
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": user_question}
                    ],
                    max_tokens=500,
                    temperature=0.7,
                    timeout=30
                )
                
                return response.choices[0].message.content.strip()
                
            except openai.APIConnectionError as e:
                print(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    raise Exception(f"Failed to connect to OpenAI API after {max_retries} attempts. Check your internet connection.")
            
            except openai.APIError as e:
                raise Exception(f"OpenAI API error: {e}")
            
            except Exception as e:
                raise Exception(f"Unexpected error querying OpenAI API: {e}")
