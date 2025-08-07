import json
import time
import pip_system_certs.wrapt_requests
import requests
import os
import getpass


class AIQueryHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://llm-proxy-api.ai.eng.netapp.com"

    def load_your_key(self):
        """Load API key - implement as required."""
        return self.api_key

    def detect_user(self):
        """Detect current user - implement as required."""
        # Try to get user from environment variables or system
        user = os.environ.get("USERNAME") or os.environ.get("USER") or getpass.getuser()
        return user

    def test_connection(self):
        """Test connectivity to NetApp's internal LLM proxy API."""
        try:
            # Test basic internet connectivity
            response = requests.get("https://www.google.com", timeout=5)
            print("✓ Internet connection: OK")
        except requests.RequestException:
            print("✗ Internet connection: FAILED")
            return False

        try:
            # Test NetApp LLM proxy API connectivity
            test_response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": "Bearer " + self.load_your_key()},
                json={
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": "test"}],
                    "user": self.detect_user(),
                    "max_tokens": 10,
                },
                timeout=10,
            )

            if test_response.status_code == 200:
                print("✓ NetApp LLM Proxy API connection: OK")
                return True
            else:
                print(
                    f"✗ NetApp LLM Proxy API connection: HTTP {test_response.status_code}"
                )
                print(f"Response: {test_response.text}")
                return False

        except requests.RequestException as e:
            print(f"✗ NetApp LLM Proxy API connection: {e}")
            return False

    def generate_offline_response(self, user_question, analysis_data):
        """Generate a basic response using only the analysis data when AI is unavailable."""
        protocols = analysis_data.get("protocols", {})
        total_packets = analysis_data.get("total_packets", 0)
        top_ips = analysis_data.get("top_source_ips", {})

        if "protocol" in user_question.lower():
            protocol_list = list(protocols.keys())
            return (
                f"Based on the packet analysis, the following protocols were detected in this trace:\n\n"
                + f"• {', '.join(protocol_list)}\n\n"
                + f"Protocol distribution:\n"
                + "\n".join(
                    [
                        f"• {proto}: {count} packets"
                        for proto, count in protocols.items()
                    ]
                )
                + f"\n\nTotal packets analyzed: {total_packets}"
            )

        elif "ip" in user_question.lower() or "address" in user_question.lower():
            ip_list = list(top_ips.keys())[:5]
            return (
                f"Top source IP addresses in this trace:\n\n"
                + "\n".join(
                    [
                        f"• {ip}: {count} packets"
                        for ip, count in list(top_ips.items())[:5]
                    ]
                )
                + f"\n\nTotal packets analyzed: {total_packets}"
            )

        else:
            return (
                f"OFFLINE MODE - AI analysis unavailable.\n\n"
                + f"Basic packet trace summary:\n"
                + f"• Total packets: {total_packets}\n"
                + f"• Protocols found: {', '.join(protocols.keys())}\n"
                + f"• Top source IPs: {', '.join(list(top_ips.keys())[:3])}\n\n"
                + f"For AI analysis, ensure NetApp LLM proxy access is configured."
            )

    def query(self, user_question, analysis_data, conversation_history=None):
        """Send query to NetApp's LLM proxy API with pcap analysis data and conversation history."""

        print("Testing connectivity...")
        if not self.test_connection():
            print("\n" + "=" * 60)
            print("NETWORK CONNECTIVITY ISSUE DETECTED")
            print("=" * 60)
            print("Falling back to offline analysis mode...")
            print("=" * 60)

            response = self.generate_offline_response(user_question, analysis_data)
            self.append_to_dataset(user_question, response)
            return response

        # Prepare context for AI
        context = f"""
You are an expert network analyst. You have been provided with analysis data from a pcap (packet capture) file.
The user will ask questions about this network traffic data. Please provide clear, accurate answers in plain English.

Analysis Data:
{json.dumps(analysis_data)}

Please answer the following question about this network traffic data:
"""
        # Build messages with previous context
        messages = [{"role": "system", "content": context}]
        if conversation_history:
            for entry in conversation_history:
                messages.append({"role": "user", "content": entry["query"]})
                messages.append({"role": "assistant", "content": entry["response"]})
        messages.append({"role": "user", "content": user_question})

        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(
                    f"Sending query to NetApp LLM Proxy (attempt {attempt + 1}/{max_retries})..."
                )

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": "Bearer " + self.load_your_key()},
                    json={
                        "model": "gpt-4o",
                        "messages": messages,
                        "user": self.detect_user(),
                        "max_tokens": 500,
                        "temperature": 0.2,
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    result = response.json()
                    response_content = result["choices"][0]["message"]["content"].strip()
                    self.append_to_dataset(user_question, response_content)
                    return response_content
                else:
                    print(f"API error: HTTP {response.status_code}")
                    print(f"Response: {response.text}")
                    if attempt == max_retries - 1:
                        response = self.generate_offline_response(
                            user_question, analysis_data
                        )
                        self.append_to_dataset(user_question, response)
                        return response

            except requests.RequestException as e:
                print(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print(
                        "Failed to connect to NetApp LLM Proxy. Switching to offline mode..."
                    )
                    response = self.generate_offline_response(user_question, analysis_data)
                    self.append_to_dataset(user_question, response)
                    return response

            except Exception as e:
                print(f"Unexpected error: {e}. Switching to offline mode...")
                response = self.generate_offline_response(user_question, analysis_data)
                self.append_to_dataset(user_question, response)
                return response

        response = self.generate_offline_response(user_question, analysis_data)
        self.append_to_dataset(user_question, response)
        return response

    def append_to_dataset(self, user_question, response):
        """Append the query and response to a JSON file."""
        print("Appending to dataset...")
        dataset_file = "dataset.json"
        entry = {"question": user_question, "response": response}

        try:
            if os.path.exists(dataset_file):
                with open(dataset_file, "r") as file:
                    data = json.load(file)
            else:
                data = []

            data.append(entry)

            try:
                with open(dataset_file, "w") as file:
                    print(f"Appending to dataset file: {dataset_file}")
                    json.dump(data, file, indent=4)
            except Exception as e:
                print(f"Error writing to dataset.json: {e}")
        except Exception as e:
            print(f"Failed to append to dataset file: {e}")
