#!/usr/bin/env python3
"""
Standalone Feedback Collection Utility

This utility provides an alternative way to collect user feedback when the main
application's input handling encounters issues. It can be run separately to
provide feedback for the most recent session.

Use Cases:
- When main script's input handling freezes
- Batch feedback collection
- Retrospective feedback after analysis

Features:
- Feedback for the last session
- Rating validation (1-5 scale)
- Optional improved response collection
- Feedback statistics display

Usage:
    python collect_feedback.py

Author: Enhanced for RL capabilities
Date: August 2025
"""

import json
import sys
from feedback_handler import FeedbackHandler

def collect_feedback_standalone():
    """Standalone feedback collection for the last session."""
    
    feedback_handler = FeedbackHandler()
    
    # Get the last session
    if not feedback_handler.feedback_data["sessions"]:
        print("No sessions found to provide feedback for.")
        return
    
    last_session = feedback_handler.feedback_data["sessions"][-1]
    
    if last_session.get("rating") is not None:
        print("This session already has feedback.")
        print(f"Current rating: {last_session['rating']}/5")
        overwrite = input("Do you want to overwrite the existing feedback? (y/n): ").strip().lower()
        if overwrite != 'y':
            return
    
    print("\n" + "="*60)
    print("STANDALONE FEEDBACK COLLECTION")
    print("="*60)
    print(f"Query: {last_session['query']}")
    print(f"Response: {last_session['ai_response'][:200]}...")
    print("-" * 60)
    
    print("Please rate the AI response (1-5 scale):")
    print("1 = Very Poor, 2 = Poor, 3 = Average, 4 = Good, 5 = Excellent")
    
    # Get rating
    while True:
        try:
            rating_input = input("Rating (1-5): ").strip()
            if not rating_input:
                print("Please enter a rating.")
                continue
            
            rating = int(rating_input)
            if 1 <= rating <= 5:
                break
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nFeedback collection cancelled.")
            return
    
    # Get additional feedback
    try:
        feedback_text = input("Additional feedback (optional): ").strip()
    except KeyboardInterrupt:
        feedback_text = ""
    
    # Get improved response if rating is low
    improved_response = None
    if rating <= 3:
        try:
            print("Would you like to provide an improved version of the response?")
            improve = input("Enter 'y' for yes, or press Enter to skip: ").strip().lower()
            if improve == 'y':
                print("Please enter your improved response:")
                improved_response = input("Improved response: ").strip()
        except KeyboardInterrupt:
            print("\nSkipping improved response.")
    
    # Save feedback
    success = feedback_handler.collect_feedback(
        last_session["session_id"], rating, feedback_text, improved_response
    )
    
    if success:
        print("✓ Feedback saved successfully!")
        
        # Show statistics
        stats = feedback_handler.get_feedback_statistics()
        print(f"\nFeedback Statistics:")
        print(f"• Total sessions: {stats['total_sessions']}")
        print(f"• Rated sessions: {stats['rated_sessions']}")
        if stats['rated_sessions'] > 0:
            print(f"• Average rating: {stats['avg_rating']:.2f}/5.0")
    else:
        print("✗ Failed to save feedback.")

if __name__ == "__main__":
    collect_feedback_standalone()
