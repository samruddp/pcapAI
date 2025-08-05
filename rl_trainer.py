"""
Reinforcement Learning Trainer Module

This module implements reinforcement learning algorithms to improve AI responses
based on user feedback. It learns patterns from user preferences and applies
them to enhance future responses.

Key Features:
- Pattern learning from positive and negative feedback
- Response style preference detection
- Query-type specific improvements
- Reward-based learning algorithm
- Model persistence and continuous learning

Algorithm Overview:
1. Extract features from queries and analysis data
2. Calculate rewards based on user ratings and feedback text
3. Learn patterns from positive examples (high ratings)
4. Avoid patterns from negative examples (low ratings)
5. Apply learned preferences to enhance future responses

Author: Enhanced for RL capabilities
Date: August 2025
"""

import json
import numpy as np
from collections import defaultdict
import pickle
from datetime import datetime
from feedback_handler import FeedbackHandler

class RLTrainer:
    def __init__(self, feedback_handler=None, learning_rate=0.1, discount_factor=0.9):
        self.feedback_handler = feedback_handler or FeedbackHandler()
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
        # Store learned patterns and preferences
        self.response_patterns = defaultdict(list)
        self.query_patterns = defaultdict(list)
        self.user_preferences = {}
        
        # Load existing model if available
        self.load_model()
    
    def save_model(self, model_file="rl_model.pkl"):
        """Save the trained model."""
        model_data = {
            "response_patterns": dict(self.response_patterns),
            "query_patterns": dict(self.query_patterns),
            "user_preferences": self.user_preferences,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, model_file="rl_model.pkl"):
        """Load existing trained model."""
        try:
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
                self.response_patterns = defaultdict(list, model_data.get("response_patterns", {}))
                self.query_patterns = defaultdict(list, model_data.get("query_patterns", {}))
                self.user_preferences = model_data.get("user_preferences", {})
        except FileNotFoundError:
            print("No existing model found. Starting fresh.")
    
    def extract_features(self, analysis_data, query):
        """Extract features from analysis data and query."""
        features = {}
        
        # Query features
        query_words = query.lower().split()
        features["query_length"] = len(query_words)
        features["has_protocol_question"] = any(word in query_words for word in ["protocol", "protocols"])
        features["has_traffic_question"] = any(word in query_words for word in ["traffic", "volume", "amount"])
        features["has_security_question"] = any(word in query_words for word in ["attack", "security", "malicious", "suspicious"])
        
        # Analysis data features
        if isinstance(analysis_data, dict):
            features["total_packets"] = analysis_data.get("total_packets", 0)
            features["protocol_count"] = len(analysis_data.get("protocols", {}))
            features["unique_ips"] = len(set(list(analysis_data.get("top_source_ips", {}).keys()) + 
                                           list(analysis_data.get("top_destination_ips", {}).keys())))
            features["avg_packet_size"] = analysis_data.get("avg_packet_size", 0)
        
        return features
    
    def calculate_reward(self, rating, feedback_text=""):
        """Calculate reward based on user rating and feedback."""
        # Base reward from rating (1-5 scale)
        base_reward = (rating - 3) * 2  # Convert 1-5 to -4 to +4
        
        # Bonus/penalty based on feedback keywords
        feedback_lower = feedback_text.lower()
        
        # Positive feedback keywords
        positive_keywords = ["good", "excellent", "helpful", "accurate", "clear", "perfect"]
        negative_keywords = ["bad", "wrong", "unclear", "inaccurate", "confusing", "useless"]
        
        feedback_bonus = 0
        for keyword in positive_keywords:
            if keyword in feedback_lower:
                feedback_bonus += 0.5
        
        for keyword in negative_keywords:
            if keyword in feedback_lower:
                feedback_bonus -= 0.5
        
        return base_reward + feedback_bonus
    
    def train_from_feedback(self):
        """Train the model using collected feedback data."""
        training_data = []
        
        # Get all sessions with feedback
        for session in self.feedback_handler.feedback_data["sessions"]:
            if session.get("rating") is not None:
                features = self.extract_features(session["analysis_data"], session["query"])
                reward = self.calculate_reward(session["rating"], session.get("user_feedback", ""))
                
                training_example = {
                    "features": features,
                    "query": session["query"],
                    "response": session["ai_response"],
                    "improved_response": session.get("improved_response"),
                    "reward": reward,
                    "rating": session["rating"]
                }
                training_data.append(training_example)
        
        # Learn patterns from positive examples (high reward)
        positive_examples = [ex for ex in training_data if ex["reward"] > 0]
        for example in positive_examples:
            self._update_patterns(example, positive=True)
        
        # Learn to avoid patterns from negative examples
        negative_examples = [ex for ex in training_data if ex["reward"] < 0]
        for example in negative_examples:
            self._update_patterns(example, positive=False)
        
        # Save updated model
        self.save_model()
        
        return len(training_data)
    
    def _update_patterns(self, example, positive=True):
        """Update learned patterns based on feedback."""
        features = example["features"]
        query = example["query"]
        response = example["improved_response"] or example["response"]
        
        # Create pattern key based on query type and features
        pattern_key = self._create_pattern_key(features, query)
        
        pattern_data = {
            "features": features,
            "response_style": self._analyze_response_style(response),
            "reward": example["reward"],
            "positive": positive
        }
        
        if positive:
            self.response_patterns[pattern_key].append(pattern_data)
        else:
            # Store negative patterns to avoid
            negative_key = f"avoid_{pattern_key}"
            self.response_patterns[negative_key].append(pattern_data)
    
    def _create_pattern_key(self, features, query):
        """Create a pattern key based on features and query type."""
        query_lower = query.lower()
        
        if features.get("has_protocol_question"):
            return "protocol_query"
        elif features.get("has_traffic_question"):
            return "traffic_query"
        elif features.get("has_security_question"):
            return "security_query"
        else:
            return "general_query"
    
    def _analyze_response_style(self, response):
        """Analyze the style and structure of a response."""
        if not response:
            return {}
        
        lines = response.split('\n')
        words = response.split()
        
        style = {
            "length": len(words),
            "has_bullet_points": any(line.strip().startswith(('-', '*', '•')) for line in lines),
            "has_numbers": any(line.strip()[0].isdigit() for line in lines if line.strip()),
            "technical_level": self._assess_technical_level(response),
            "structure": "structured" if len(lines) > 3 else "simple"
        }
        
        return style
    
    def _assess_technical_level(self, response):
        """Assess the technical level of a response."""
        technical_terms = ["tcp", "udp", "ip", "protocol", "packet", "port", "header", 
                          "payload", "ethernet", "arp", "icmp", "dns", "http", "https"]
        
        response_lower = response.lower()
        technical_count = sum(1 for term in technical_terms if term in response_lower)
        
        if technical_count > 10:
            return "high"
        elif technical_count > 5:
            return "medium"
        else:
            return "low"
    
    def get_response_recommendations(self, analysis_data, query):
        """Get recommendations for improving response based on learned patterns."""
        features = self.extract_features(analysis_data, query)
        pattern_key = self._create_pattern_key(features, query)
        
        recommendations = {
            "style_preferences": {},
            "content_suggestions": [],
            "avoid_patterns": []
        }
        
        # Get positive patterns for this query type
        if pattern_key in self.response_patterns:
            positive_patterns = [p for p in self.response_patterns[pattern_key] if p["positive"]]
            if positive_patterns:
                # Aggregate style preferences
                avg_length = np.mean([p["response_style"]["length"] for p in positive_patterns])
                preferred_structure = max(set([p["response_style"]["structure"] for p in positive_patterns]),
                                        key=[p["response_style"]["structure"] for p in positive_patterns].count)
                
                recommendations["style_preferences"] = {
                    "preferred_length": avg_length,
                    "preferred_structure": preferred_structure,
                    "use_bullet_points": np.mean([p["response_style"]["has_bullet_points"] for p in positive_patterns]) > 0.5
                }
        
        # Get patterns to avoid
        avoid_key = f"avoid_{pattern_key}"
        if avoid_key in self.response_patterns:
            recommendations["avoid_patterns"] = [p["response_style"] for p in self.response_patterns[avoid_key]]
        
        return recommendations
