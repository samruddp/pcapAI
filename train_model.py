#!/usr/bin/env python3
"""
Reinforcement Learning Model Training Script

This script trains the reinforcement learning model using collected user feedback.
It should be run periodically to incorporate new feedback and improve the AI's
response quality.

Features:
- Batch training from accumulated feedback
- Feedback statistics and analytics
- Model performance tracking
- Training data validation
- Learned pattern visualization

Training Process:
1. Load feedback data from JSON file
2. Extract features and calculate rewards
3. Update response patterns based on feedback
4. Save improved model to disk
5. Display training statistics

Usage:
    python train_model.py --show-stats    # Show statistics and train
    python train_model.py                 # Train without statistics

Author: Enhanced for RL capabilities
Date: August 2025
"""

import argparse
from feedback_handler import FeedbackHandler
from rl_trainer import RLTrainer

def main():
    parser = argparse.ArgumentParser(description='Train the RL model with collected feedback')
    parser.add_argument('--feedback-file', default='feedback_data.json', 
                       help='Path to feedback data file')
    parser.add_argument('--model-file', default='rl_model.pkl',
                       help='Path to save/load the trained model')
    parser.add_argument('--show-stats', action='store_true',
                       help='Show feedback statistics')
    
    args = parser.parse_args()
    
    # Initialize components
    feedback_handler = FeedbackHandler(args.feedback_file)
    rl_trainer = RLTrainer(feedback_handler)
    
    if args.show_stats:
        # Show feedback statistics
        stats = feedback_handler.get_feedback_statistics()
        print("Feedback Statistics:")
        print("=" * 40)
        print(f"Total sessions: {stats['total_sessions']}")
        print(f"Rated sessions: {stats['rated_sessions']}")
        
        if stats['rated_sessions'] > 0:
            print(f"Average rating: {stats['avg_rating']:.2f}/5.0")
            print("\nRating distribution:")
            for rating, count in stats['rating_distribution'].items():
                print(f"  {rating} star(s): {count} responses")
            
            # Show training data availability
            positive_examples = feedback_handler.get_training_data(min_rating=4)
            negative_examples = feedback_handler.get_negative_examples(max_rating=2)
            
            print(f"\nTraining data available:")
            print(f"  Positive examples (4-5 stars): {len(positive_examples)}")
            print(f"  Negative examples (1-2 stars): {len(negative_examples)}")
    
    # Train the model
    if feedback_handler.get_feedback_statistics()['rated_sessions'] > 0:
        print("\nTraining model with feedback data...")
        trained_count = rl_trainer.train_from_feedback()
        print(f"✓ Model trained with {trained_count} feedback examples")
        
        # Save the model
        rl_trainer.save_model(args.model_file)
        print(f"✓ Model saved to {args.model_file}")
        
        # Show learned patterns
        print(f"\nLearned patterns:")
        for pattern_type, patterns in rl_trainer.response_patterns.items():
            if patterns and not pattern_type.startswith('avoid_'):
                avg_reward = sum(p['reward'] for p in patterns) / len(patterns)
                print(f"  {pattern_type}: {len(patterns)} examples (avg reward: {avg_reward:.2f})")
    else:
        print("No feedback data available for training.")

if __name__ == "__main__":
    main()
