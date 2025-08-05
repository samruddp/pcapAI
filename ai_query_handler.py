"""
Enhanced AI Query Handler with Reinforcement Learning

This module handles AI queries to NetApp's LLM proxy API and includes
reinforcement learning capabilities to improve responses over time.

Enhanced Features (RL Branch):
- Reinforcement Learning integration for response improvement
- User feedback collection system
- Response enhancement based on learned patterns
- Session tracking for feedback correlation
- Fallback feedback collection utilities

Original Features:
- NetApp LLM proxy API integration
- Connectivity testing and error handling
- Offline mode fallback when API is unavailable
- SSL certificate handling for corporate environments

Author: Enhanced for RL capabilities
Date: August 2025
"""

import json
import time
import pip_system_certs.wrapt_requests
import requests
import os
import getpass
from feedback_handler import FeedbackHandler
from rl_trainer import RLTrainer


class AIQueryHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://llm-proxy-api.ai.eng.netapp.com"
        self.feedback_handler = FeedbackHandler()
        self.rl_trainer = RLTrainer(self.feedback_handler)
        self.current_session_id = None

    def load_your_key(self):
        """Load API key - implement as required."""
        return self.api_key

    def enhance_response_with_rl(self, response, analysis_data, query):
        """Enhance response based on reinforcement learning recommendations."""
        try:
            recommendations = self.rl_trainer.get_response_recommendations(analysis_data, query)
            
            # Apply style preferences if available
            style_prefs = recommendations.get("style_preferences", {})
            
            if style_prefs.get("use_bullet_points") and "•" not in response and "-" not in response:
                # Convert to bullet points if preferred
                lines = response.split('\n')
                if len(lines) > 1:
                    enhanced_lines = []
                    for line in lines:
                        if line.strip() and not line.startswith('•') and not line.startswith('-'):
                            enhanced_lines.append(f"• {line.strip()}")
                        else:
                            enhanced_lines.append(line)
                    response = '\n'.join(enhanced_lines)
            
            return response
        except Exception as e:
            print(f"RL enhancement failed: {e}")
            return response

    def collect_user_feedback(self, session_id=None):
        """Collect feedback from user about the response."""
        if not session_id:
            session_id = self.current_session_id
        
        if not session_id:
            print("No active session to collect feedback for.")
            return False
        
        print("\n" + "="*50)
        print("FEEDBACK COLLECTION")
        print("="*50)
        print("Please rate the AI response (1-5 scale):")
        print("1 = Very Poor, 2 = Poor, 3 = Average, 4 = Good, 5 = Excellent")
        
        try:
            # Use a more robust input method
            import sys
            
            # Flush any pending output
            sys.stdout.flush()
            
            # Get rating with validation
            while True:
                try:
                    rating_input = input("Rating (1-5): ").strip()
                    if not rating_input:
                        print("Please enter a rating between 1 and 5.")
                        continue
                    
                    rating = int(rating_input)
                    if rating < 1 or rating > 5:
                        print("Invalid rating. Please enter a number between 1 and 5.")
                        continue
                    break
                except ValueError:
                    print("Invalid input. Please enter a number between 1 and 5.")
                    continue
                except (EOFError, KeyboardInterrupt):
                    print("\nFeedback collection cancelled.")
                    return False
            
            # Get additional feedback
            try:
                feedback_text = input("Additional feedback (optional): ").strip()
            except (EOFError, KeyboardInterrupt):
                feedback_text = ""
            
            improved_response = None
            if rating <= 3:
                print("Would you like to provide an improved version of the response?")
                try:
                    provide_improvement = input("Enter 'y' to provide improvement, or press Enter to skip: ").strip().lower()
                    if provide_improvement == 'y':
                        print("Please provide your improved response:")
                        improved_response = input().strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nSkipping improved response.")
                    improved_response = None
            
            # Save feedback
            success = self.feedback_handler.collect_feedback(
                session_id, rating, feedback_text, improved_response
            )
            
            if success:
                print("✓ Feedback collected successfully!")
                
                # Trigger retraining if we have enough new feedback
                stats = self.feedback_handler.get_feedback_statistics()
                if stats["rated_sessions"] > 0 and stats["rated_sessions"] % 5 == 0:
                    print("Training model with new feedback...")
                    trained_count = self.rl_trainer.train_from_feedback()
                    print(f"✓ Model updated with {trained_count} examples!")
                
                return True
            else:
                print("✗ Failed to save feedback.")
                return False
                
        except Exception as e:
            print(f"Error during feedback collection: {e}")
            return False

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

    def query(self, user_question, analysis_data, pcap_file=""):
        """Send query to NetApp's LLM proxy API with pcap analysis data and RL enhancement."""

        print("Testing connectivity...")
        if not self.test_connection():
            print("\n" + "=" * 60)
            print("NETWORK CONNECTIVITY ISSUE DETECTED")
            print("=" * 60)
            print("Falling back to offline analysis mode...")
            print("=" * 60)

            response = self.generate_offline_response(user_question, analysis_data)
            
            # Create session for offline response too
            self.current_session_id = self.feedback_handler.create_session(
                pcap_file, user_question, analysis_data, response
            )
            
            return response

        # Get RL recommendations for context enhancement
        recommendations = self.rl_trainer.get_response_recommendations(analysis_data, user_question)

        # Prepare enhanced context for AI
        context = f"""
You are an expert network analyst. You have been provided with analysis data from a pcap (packet capture) file.
The user will ask questions about this network traffic data. Please provide clear, accurate answers in plain English.

Analysis Data:
{json.dumps(analysis_data, indent=2)}

Response Guidelines based on user preferences:
{json.dumps(recommendations.get("style_preferences", {}), indent=2)}

Please answer the following question about this network traffic data:
"""

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
                        "messages": [
                            {"role": "system", "content": context},
                            {"role": "user", "content": user_question},
                        ],
                        "user": self.detect_user(),
                        "max_tokens": 500,
                        "temperature": 0.7,
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"].strip()
                    
                    # Enhance response with RL
                    enhanced_response = self.enhance_response_with_rl(ai_response, analysis_data, user_question)
                    
                    # Create session for feedback collection
                    self.current_session_id = self.feedback_handler.create_session(
                        pcap_file, user_question, analysis_data, enhanced_response
                    )
                    
                    return enhanced_response
                else:
                    print(f"API error: HTTP {response.status_code}")
                    print(f"Response: {response.text}")
                    if attempt == max_retries - 1:
                        fallback_response = self.generate_offline_response(user_question, analysis_data)
                        self.current_session_id = self.feedback_handler.create_session(
                            pcap_file, user_question, analysis_data, fallback_response
                        )
                        return fallback_response

            except requests.RequestException as e:
                print(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print(
                        "Failed to connect to NetApp LLM Proxy. Switching to offline mode..."
                    )
                    fallback_response = self.generate_offline_response(user_question, analysis_data)
                    self.current_session_id = self.feedback_handler.create_session(
                        pcap_file, user_question, analysis_data, fallback_response
                    )
                    return fallback_response

            except Exception as e:
                print(f"Unexpected error: {e}. Switching to offline mode...")
                fallback_response = self.generate_offline_response(user_question, analysis_data)
                self.current_session_id = self.feedback_handler.create_session(
                    pcap_file, user_question, analysis_data, fallback_response
                )
                return fallback_response

        fallback_response = self.generate_offline_response(user_question, analysis_data)
        self.current_session_id = self.feedback_handler.create_session(
            pcap_file, user_question, analysis_data, fallback_response
        )
        return fallback_response
