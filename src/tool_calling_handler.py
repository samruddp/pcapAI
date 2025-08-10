import json
import time
import pip_system_certs.wrapt_requests
import requests
import os
import getpass
from src.tool_factory import ToolFactory


class ToolCallingHandler:
    def __init__(self, api_key, test_mode=False):
        self.api_key = api_key
        self.test_mode = test_mode
        self.base_url = "https://llm-proxy-api.ai.eng.netapp.com"
        self.tool_factory = ToolFactory()
    
    def log_debug(self, message):
        """Print debug messages only in test mode."""
        if self.test_mode:
            print(message)

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
            self.log_debug("✓ Internet connection: OK")
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
                self.log_debug("✓ NetApp LLM Proxy API connection: OK")
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

    def define_tools(self):
        """Define the tools available for function calling."""
        return self.tool_factory.get_tool_definitions()

    def execute_tool(self, tool_name, arguments, analysis_data):
        """Execute a tool function and return results."""
        return self.tool_factory.execute_tool(tool_name, arguments, analysis_data)

    def generate_offline_response(self, user_question, analysis_data):
        """Generate a basic response using only the analysis data when AI is unavailable."""
        protocols = analysis_data.get("protocols", {})
        total_packets = analysis_data.get("total_packets", 0)
        top_ips = analysis_data.get("top_source_ips", {})

        return (
            f"OFFLINE MODE (Tool Calling) - AI analysis unavailable.\n\n"
            + f"Basic packet trace summary:\n"
            + f"• Total packets: {total_packets}\n"
            + f"• Protocols found: {', '.join(protocols.keys()) if protocols else 'Unknown'}\n"
            + f"• Top source IPs: {', '.join(list(top_ips.keys())[:3]) if top_ips else 'Unknown'}\n\n"
            + f"For AI analysis with tool calling, ensure NetApp LLM proxy access is configured."
        )

    def query(self, user_question, analysis_data, conversation_history=None):
        """Send query to NetApp's LLM proxy API with tool calling support."""

        print("🔧 TOOL CALLING HANDLER - Starting query processing")
        print(f"📝 User Question: {user_question}")
        print(f"📊 Analysis Data Keys: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}")
        
        self.log_debug("🔧 Using Tool Calling Handler for large PCAP file")
        self.log_debug("Testing connectivity...")
        
        # Check if filtered data exists and use it instead of original analysis data
        filtered_data_file = "temp_filtered_data.json"
        if os.path.exists(filtered_data_file):
            try:
                with open(filtered_data_file, 'r') as f:
                    filtered_data = json.load(f)
                    print(f"📁 Found existing filtered data file with {len(filtered_data.get('packets', []))} packets")
                    self.log_debug(f"📁 Using filtered data from {filtered_data_file}")
                    analysis_data = filtered_data
            except Exception as e:
                print(f"❌ Error loading filtered data: {e}")
                self.log_debug(f"Error loading filtered data: {e}, using original data")
        else:
            print("📁 No existing filtered data file found, using original analysis data")
        
        if not self.test_connection():
            print("\n" + "=" * 60)
            print("NETWORK CONNECTIVITY ISSUE DETECTED")
            print("=" * 60)
            print("Falling back to offline analysis mode...")
            print("=" * 60)

            response = self.generate_offline_response(user_question, analysis_data)
            self.append_to_dataset(user_question, response)
            return response

        # Prepare context for AI with tool calling
        context = f"""
You are an expert network analyst with access to a tool for filtering NFS packets.
You have been provided with analysis data from a pcap (packet capture) file.
You have a bunch of tools available to filter the input data and use it for generating the response.

Current Analysis Data:
{json.dumps(analysis_data, default=str)}

Please answer the user's question using the provided analysis data. If the user requests NFS filtering, use the filter_nfs_packets tool.
"""

        # Build messages with previous context
        messages = [{"role": "system", "content": context}]
        if conversation_history:
            for entry in conversation_history[-3:]:  # Limit context for large files
                messages.append({"role": "user", "content": entry["query"]})
                messages.append({"role": "assistant", "content": entry["response"]})
        messages.append({"role": "user", "content": user_question})

        # Get available tools
        tools = self.define_tools()
        
        print(f"🛠️ Available tools: {[tool['function']['name'] for tool in tools]}")
        print(f"📨 Total messages to send: {len(messages)}")
        print(f"📤 Context length: {len(context)} characters")

        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🚀 Attempt {attempt + 1}/{max_retries}: Sending query to OpenAI API...")
                self.log_debug(
                    f"Sending query with tool calling to NetApp LLM Proxy (attempt {attempt + 1}/{max_retries})..."
                )

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": "Bearer " + self.load_your_key()},
                    json={
                        "model": "gpt-4o",
                        "messages": messages,
                        "tools": tools,
                        "tool_choice": "auto",
                        "user": self.detect_user(),
                        "max_tokens": 1000,
                        "temperature": 0.2,
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    result = response.json()
                    message = result["choices"][0]["message"]
                    
                    print(f"✅ API Response received successfully")
                    print(f"🔍 Response has tool_calls: {bool(message.get('tool_calls'))}")
                    
                    # Check if the AI wants to call tools
                    if message.get("tool_calls"):
                        print(f"🔧 Tool calls detected: {len(message['tool_calls'])} tools to execute")
                        return self._handle_tool_calls(message, analysis_data, user_question, messages, tools)
                    else:
                        # No tools called, return direct response
                        print("💬 No tool calls - returning direct response")
                        response_content = message["content"]
                        self.append_to_dataset(user_question, response_content)
                        return response_content
                        
                else:
                    print(f"API error: HTTP {response.status_code}")
                    print(f"Response: {response.text}")
                    if attempt == max_retries - 1:
                        response = self.generate_offline_response(user_question, analysis_data)
                        self.append_to_dataset(user_question, response)
                        return response

            except requests.RequestException as e:
                print(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print("Failed to connect to NetApp LLM Proxy. Switching to offline mode...")
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

    def _handle_tool_calls(self, message, analysis_data, user_question, messages, tools):
        """Handle tool calls from the AI with multiple rounds of interaction."""
        print("\n" + "="*60)
        print("🔧 STARTING TOOL CALLING WORKFLOW")
        print("="*60)
        
        # Execute all tool calls
        tool_results = []
        updated_analysis_data = analysis_data
        
        print(f"🔨 Executing {len(message['tool_calls'])} tool calls...")
        
        for i, tool_call in enumerate(message["tool_calls"], 1):
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])
            
            print(f"🔧 Tool {i}: {function_name}")
            print(f"📋 Arguments: {arguments}")
            
            self.log_debug(f"🔧 Executing tool: {function_name} with args: {arguments}")
            
            result = self.execute_tool(function_name, arguments, analysis_data)
            
            print(f"✅ Tool {i} execution completed")
            print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            # If the tool returned filtered data, use it for subsequent context
            if result.get("filtered_data"):
                updated_analysis_data = result["filtered_data"]
                print(f"🔄 Updated analysis data with filtered results from {function_name}")
                self.log_debug(f"📊 Updated analysis data with filtered results")
            
            tool_results.append({
                "tool_call_id": tool_call["id"],
                "function_name": function_name,
                "result": result
            })

        # Add the assistant's tool call message
        messages.append(message)
        
        # Add tool results
        print(f"📝 Adding tool results to conversation context...")
        for tool_result in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_result["tool_call_id"],
                "content": json.dumps(tool_result["result"])
            })

        print(f"📨 Total messages in conversation: {len(messages)}")

        # Round 1: Get initial AI response after tool execution
        print("\n🔄 ROUND 1: Getting initial AI response after tool execution...")
        try:
            self.log_debug("🔄 Round 1: Getting initial AI response after tool execution...")
            round1_response = requests.post(
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

            if round1_response.status_code == 200:
                result = round1_response.json()
                round1_content = result["choices"][0]["message"]["content"]
                messages.append({"role": "assistant", "content": round1_content})
                print(f"✅ Round 1 successful - Response length: {len(round1_content)} characters")
                self.log_debug(f"✓ Round 1 complete")
            else:
                print(f"❌ Round 1 failed: HTTP {round1_response.status_code}")
                self.log_debug(f"Round 1 failed: HTTP {round1_response.status_code}")
                
        except Exception as e:
            print(f"❌ Round 1 error: {e}")
            self.log_debug(f"Round 1 error: {e}")

        # Round 2: Provide filtered data context and ask for analysis
        if updated_analysis_data != analysis_data:
            print("\n🔄 ROUND 2: Providing filtered data context for analysis...")
            print(f"📊 Filtered data contains {len(updated_analysis_data.get('packets', []))} packets")
            self.log_debug("🔄 Round 2: Providing filtered data context...")
            filtered_context = f"""
Based on the tool execution, here is the filtered dataset for your analysis:

Filtered Analysis Data:
{json.dumps(updated_analysis_data, default=str)}

Please analyze this filtered data and provide insights relevant to the user's original question: "{user_question}"
"""
            messages.append({
                "role": "user", 
                "content": filtered_context
            })

            try:
                round2_response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": "Bearer " + self.load_your_key()},
                    json={
                        "model": "gpt-4o",
                        "messages": messages,
                        "user": self.detect_user(),
                        "max_tokens": 600,
                        "temperature": 0.2,
                    },
                    timeout=30,
                )

                if round2_response.status_code == 200:
                    result = round2_response.json()
                    round2_content = result["choices"][0]["message"]["content"]
                    messages.append({"role": "assistant", "content": round2_content})
                    print(f"✅ Round 2 successful - Response length: {len(round2_content)} characters")
                    self.log_debug(f"✓ Round 2 complete")
                else:
                    print(f"❌ Round 2 failed: HTTP {round2_response.status_code}")
                    self.log_debug(f"Round 2 failed: HTTP {round2_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Round 2 error: {e}")
                self.log_debug(f"Round 2 error: {e}")
        else:
            print("\n⏭️ ROUND 2: Skipped - No filtered data available")

        # Round 3: Final comprehensive response
        print("\n🔄 ROUND 3: Getting final comprehensive response...")
        self.log_debug("🔄 Round 3: Getting final comprehensive response...")
        final_prompt = f"""
Now provide a comprehensive final answer to the user's question: "{user_question}"

Summarize your findings from the analysis and provide a clear, actionable response. Include specific details and numbers where relevant.
"""
        messages.append({
            "role": "user",
            "content": final_prompt
        })

        try:
            final_response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": "Bearer " + self.load_your_key()},
                json={
                    "model": "gpt-4o",
                    "messages": messages,
                    "user": self.detect_user(),
                    "max_tokens": 800,
                    "temperature": 0.2,
                },
                timeout=30,
            )

            if final_response.status_code == 200:
                result = final_response.json()
                response_content = result["choices"][0]["message"]["content"]
                print(f"✅ Round 3 successful - Final response length: {len(response_content)} characters")
                print("🎉 TOOL CALLING WORKFLOW COMPLETED SUCCESSFULLY")
                print("="*60)
                self.log_debug(f"✓ Round 3 complete - Final response ready")
                self.append_to_dataset(user_question, response_content)
                return response_content
            else:
                print(f"❌ Round 3 failed: HTTP {final_response.status_code}")
                print("🔄 Falling back to tool results summary")
                self.log_debug(f"Round 3 failed: HTTP {final_response.status_code}")
                # Fallback to tool results summary
                summary = self._summarize_tool_results(tool_results)
                self.append_to_dataset(user_question, summary)
                return summary

        except Exception as e:
            print(f"❌ Round 3 error: {e}")
            print("🔄 Falling back to tool results summary")
            print(f"Error getting final AI response: {e}")
            summary = self._summarize_tool_results(tool_results)
            self.append_to_dataset(user_question, summary)
            return summary

    def _summarize_tool_results(self, tool_results):
        """Create a summary from tool results when AI is unavailable."""
        summary = "Tool Analysis Results:\n\n"
        
        for tool_result in tool_results:
            function_name = tool_result["function_name"]
            result = tool_result["result"]
            
            summary += f"🔧 {function_name}:\n"
            if isinstance(result, dict):
                for key, value in result.items():
                    if key != "error":
                        summary += f"  • {key}: {value}\n"
                if "error" in result:
                    summary += f"  ❌ Error: {result['error']}\n"
            else:
                summary += f"  • Result: {result}\n"
            summary += "\n"
        
        return summary.strip()

    def append_to_dataset(self, user_question, response):
        """Append the query and response to a JSON file."""
        self.log_debug("Appending to dataset...")
        dataset_file = "dataset.json"
        entry = {"question": user_question, "response": response, "handler": "tool_calling"}

        try:
            if os.path.exists(dataset_file):
                with open(dataset_file, "r") as file:
                    data = json.load(file)
            else:
                data = []

            data.append(entry)

            try:
                with open(dataset_file, "w") as file:
                    self.log_debug(f"Appending to dataset file: {dataset_file}")
                    json.dump(data, file, indent=4)
            except Exception as e:
                print(f"Error writing to dataset.json: {e}")
        except Exception as e:
            print(f"Failed to append to dataset file: {e}")
