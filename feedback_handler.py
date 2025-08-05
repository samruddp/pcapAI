"""
Feedback Handler Module for Reinforcement Learning

This module implements a comprehensive feedback collection system that enables 
reinforcement learning capabilities for the pcapAI tool.

Key Features:
- User feedback collection (1-5 star ratings + text feedback)
- Session tracking with unique identifiers
- Improved response suggestions from users
- Training data preparation for RL algorithms
- Feedback statistics and analytics

Author: Enhanced for RL capabilities
Date: August 2025
"""

import json
import uuid
from datetime import datetime
import os

class FeedbackHandler:
    def __init__(self, feedback_file="feedback_data.json"):
        self.feedback_file = feedback_file
        self.feedback_data = self.load_feedback_data()
    
    def load_feedback_data(self):
        """Load existing feedback data from file."""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {"sessions": []}
        return {"sessions": []}
    
    def save_feedback_data(self):
        """Save feedback data to file."""
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
    
    def create_session(self, pcap_file, query, analysis_data, ai_response):
        """Create a new feedback session."""
        session_id = str(uuid.uuid4())
        session = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "pcap_file": pcap_file,
            "query": query,
            "analysis_data": analysis_data,
            "ai_response": ai_response,
            "user_feedback": None,
            "rating": None,
            "improved_response": None,
            "feedback_timestamp": None
        }
        
        self.feedback_data["sessions"].append(session)
        self.save_feedback_data()
        return session_id
    
    def collect_feedback(self, session_id, rating, feedback_text, improved_response=None):
        """Collect user feedback for a session."""
        for session in self.feedback_data["sessions"]:
            if session["session_id"] == session_id:
                session["rating"] = rating
                session["user_feedback"] = feedback_text
                session["improved_response"] = improved_response
                session["feedback_timestamp"] = datetime.now().isoformat()
                self.save_feedback_data()
                return True
        return False
    
    def get_training_data(self, min_rating=3):
        """Get positive examples for training (rating >= min_rating)."""
        positive_examples = []
        for session in self.feedback_data["sessions"]:
            if session.get("rating") and session["rating"] >= min_rating:
                positive_examples.append({
                    "context": session["analysis_data"],
                    "query": session["query"],
                    "response": session["improved_response"] or session["ai_response"],
                    "rating": session["rating"]
                })
        return positive_examples
    
    def get_negative_examples(self, max_rating=2):
        """Get negative examples for training (rating <= max_rating)."""
        negative_examples = []
        for session in self.feedback_data["sessions"]:
            if session.get("rating") and session["rating"] <= max_rating:
                negative_examples.append({
                    "context": session["analysis_data"],
                    "query": session["query"],
                    "bad_response": session["ai_response"],
                    "improved_response": session["improved_response"],
                    "rating": session["rating"],
                    "feedback": session["user_feedback"]
                })
        return negative_examples
    
    def get_feedback_statistics(self):
        """Get statistics about collected feedback."""
        total_sessions = len(self.feedback_data["sessions"])
        rated_sessions = [s for s in self.feedback_data["sessions"] if s.get("rating")]
        
        if not rated_sessions:
            return {"total_sessions": total_sessions, "rated_sessions": 0, "avg_rating": 0}
        
        avg_rating = sum(s["rating"] for s in rated_sessions) / len(rated_sessions)
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[i] = len([s for s in rated_sessions if s["rating"] == i])
        
        return {
            "total_sessions": total_sessions,
            "rated_sessions": len(rated_sessions),
            "avg_rating": avg_rating,
            "rating_distribution": rating_distribution
        }
