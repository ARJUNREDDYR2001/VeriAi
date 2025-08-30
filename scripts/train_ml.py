#!/usr/bin/env python3
"""
ML Model Training Script
Generates synthetic handshake data and trains simple rule-based anomaly detection
"""

import os
import sys
import json
import random
import statistics
import time


def generate_synthetic_data(n_normal=160, n_fraud=40):
    """Generate synthetic handshake data for training"""
    print(f"🔄 Generating {n_normal} normal + {n_fraud} fraud samples...")
    
    data = []
    
    # Generate normal handshakes (genuine agents)
    for i in range(n_normal):
        sample = {
            # Signature verification: genuine agents succeed
            "signature_verification": 1,
            
            # Response latency: normal human-like timing (100-300ms)
            "response_latency_ms": random.gauss(180, 40),
            
            # Message entropy: natural language has good entropy (3-4.5)
            "message_entropy": random.gauss(3.8, 0.4),
            
            # Handshake duration: reasonable total time (150-400ms)
            "handshake_duration": random.gauss(250, 60),
            
            # Label
            "is_fraud": False
        }
        
        # Add some variation
        if random.random() < 0.1:  # 10% slower responses
            sample["response_latency_ms"] *= 1.5
            sample["handshake_duration"] *= 1.3
        
        data.append(sample)
    
    # Generate fraudulent handshakes (fake agents)
    for i in range(n_fraud):
        fraud_type = random.choice(["signature_fail", "bot_timing", "low_entropy", "mixed"])
        
        if fraud_type == "signature_fail":
            # Failed signature verification
            sample = {
                "signature_verification": 0,  # Failed signature
                "response_latency_ms": random.gauss(120, 30),
                "message_entropy": random.gauss(3.2, 0.5),
                "handshake_duration": random.gauss(180, 40),
                "is_fraud": True
            }
        
        elif fraud_type == "bot_timing":
            # Bot-like timing (too fast)
            sample = {
                "signature_verification": random.choice([0, 1]),
                "response_latency_ms": random.gauss(25, 10),  # Very fast
                "message_entropy": random.gauss(2.8, 0.3),
                "handshake_duration": random.gauss(50, 20),   # Very fast overall
                "is_fraud": True
            }
        
        elif fraud_type == "low_entropy":
            # Low entropy responses (repetitive/predictable)
            sample = {
                "signature_verification": random.choice([0, 1]),
                "response_latency_ms": random.gauss(100, 25),
                "message_entropy": random.gauss(1.8, 0.4),   # Low entropy
                "handshake_duration": random.gauss(150, 30),
                "is_fraud": True
            }
        
        else:  # mixed anomalies
            sample = {
                "signature_verification": 0,
                "response_latency_ms": random.gauss(40, 15),   # Fast
                "message_entropy": random.gauss(2.0, 0.3),    # Low entropy
                "handshake_duration": random.gauss(80, 25),    # Fast overall
                "is_fraud": True
            }
        
        # Ensure non-negative values
        sample["response_latency_ms"] = max(1, sample["response_latency_ms"])
        sample["handshake_duration"] = max(1, sample["handshake_duration"])
        sample["message_entropy"] = max(0.1, sample["message_entropy"])
        
        data.append(sample)
    
    return data


def train_model(data):
    """Train simple rule-based model on synthetic data"""
    print("🤖 Training rule-based anomaly detection model...")
    
    # Calculate thresholds from normal data
    normal_data = [d for d in data if not d["is_fraud"]]
    fraud_data = [d for d in data if d["is_fraud"]]
    
    print(f"\n📊 Data Analysis:")
    print(f"Normal samples: {len(normal_data)}")
    print(f"Fraud samples: {len(fraud_data)}")
    
    # Calculate statistics for normal data
    if normal_data:
        latencies = [d["response_latency_ms"] for d in normal_data]
        durations = [d["handshake_duration"] for d in normal_data]
        entropies = [d["message_entropy"] for d in normal_data]
        
        lat_mean = statistics.mean(latencies)
        lat_std = statistics.stdev(latencies) if len(latencies) > 1 else 50
        
        dur_mean = statistics.mean(durations)
        dur_std = statistics.stdev(durations) if len(durations) > 1 else 100
        
        ent_mean = statistics.mean(entropies)
        ent_std = statistics.stdev(entropies) if len(entropies) > 1 else 0.5
        
        thresholds = {
            "signature_verification": 1,  # Must be 1 for normal
            "response_latency_ms": (
                max(10, lat_mean - 2*lat_std), 
                lat_mean + 3*lat_std
            ),
            "message_entropy": max(1.0, ent_mean - 2*ent_std),
            "handshake_duration": (
                max(50, dur_mean - 2*dur_std),
                dur_mean + 3*dur_std
            )
        }
        
        print(f"\n🔍 Calculated Thresholds:")
        print(f"Response latency: {thresholds['response_latency_ms'][0]:.1f} - {thresholds['response_latency_ms'][1]:.1f} ms")
        print(f"Message entropy: >= {thresholds['message_entropy']:.2f}")
        print(f"Handshake duration: {thresholds['handshake_duration'][0]:.1f} - {thresholds['handshake_duration'][1]:.1f} ms")
        
        return thresholds, data
    
    return None, data


def save_model(thresholds, training_data, filepath="backend/ml_model.json"):
    """Save trained model to disk"""
    print(f"💾 Saving model to {filepath}...")
    
    model_data = {
        'thresholds': thresholds,
        'training_data': training_data,
        'feature_names': ["signature_verification", "response_latency_ms", "message_entropy", "handshake_duration"],
        'version': '1.0',
        'trained_at': time.time()
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(model_data, f, indent=2)
    
    print(f"✅ Model saved successfully!")
    return filepath


def visualize_data(data, save_plots=False):
    """Create simple text-based visualizations of the training data"""
    print("📈 Creating data analysis...")
    
    try:
        normal_data = [d for d in data if not d["is_fraud"]]
        fraud_data = [d for d in data if d["is_fraud"]]
        
        print(f"\n📊 Data Distribution:")
        print(f"Normal samples: {len(normal_data)}")
        print(f"Fraud samples: {len(fraud_data)}")
        
        if normal_data:
            normal_latencies = [d["response_latency_ms"] for d in normal_data]
            normal_entropies = [d["message_entropy"] for d in normal_data]
            
            print(f"\n📈 Normal Data Statistics:")
            print(f"Latency: {statistics.mean(normal_latencies):.1f}ms ± {statistics.stdev(normal_latencies) if len(normal_latencies) > 1 else 0:.1f}")
            print(f"Entropy: {statistics.mean(normal_entropies):.2f} ± {statistics.stdev(normal_entropies) if len(normal_entropies) > 1 else 0:.2f}")
        
        if fraud_data:
            fraud_latencies = [d["response_latency_ms"] for d in fraud_data]
            fraud_entropies = [d["message_entropy"] for d in fraud_data]
            fraud_sig_fails = sum(1 for d in fraud_data if d["signature_verification"] == 0)
            
            print(f"\n🚨 Fraud Data Statistics:")
            print(f"Latency: {statistics.mean(fraud_latencies):.1f}ms ± {statistics.stdev(fraud_latencies) if len(fraud_latencies) > 1 else 0:.1f}")
            print(f"Entropy: {statistics.mean(fraud_entropies):.2f} ± {statistics.stdev(fraud_entropies) if len(fraud_entropies) > 1 else 0:.2f}")
            print(f"Signature failures: {fraud_sig_fails}/{len(fraud_data)} ({fraud_sig_fails/len(fraud_data)*100:.1f}%)")
        
    except Exception as e:
        print(f"⚠️ Analysis error: {e}")


def test_model(model_path="backend/ml_model.json"):
    """Test the saved model with sample data"""
    print(f"\n🧪 Testing saved model from {model_path}...")
    
    try:
        with open(model_path, 'r') as f:
            model_data = json.load(f)
        
        thresholds = model_data['thresholds']
        
        # Test cases
        test_cases = [
            {
                "name": "Normal Handshake",
                "features": {
                    "signature_verification": 1,
                    "response_latency_ms": 180,
                    "message_entropy": 3.8,
                    "handshake_duration": 250
                },
                "expected": "Normal"
            },
            {
                "name": "Failed Signature",
                "features": {
                    "signature_verification": 0,
                    "response_latency_ms": 150,
                    "message_entropy": 3.5,
                    "handshake_duration": 200
                },
                "expected": "Anomaly"
            },
            {
                "name": "Bot-like Timing",
                "features": {
                    "signature_verification": 1,
                    "response_latency_ms": 25,
                    "message_entropy": 2.0,
                    "handshake_duration": 50
                },
                "expected": "Anomaly"
            },
            {
                "name": "Slow Response",
                "features": {
                    "signature_verification": 1,
                    "response_latency_ms": 800,
                    "message_entropy": 3.2,
                    "handshake_duration": 900
                },
                "expected": "Normal/Anomaly"
            }
        ]
        
        for test_case in test_cases:
            features = test_case["features"]
            
            # Calculate anomaly score using rule-based approach
            anomaly_score = 0.0
            
            if features["signature_verification"] == 0:
                anomaly_score += 0.6
            
            lat_min, lat_max = thresholds["response_latency_ms"]
            latency = features["response_latency_ms"]
            if latency < lat_min or latency > lat_max:
                anomaly_score += 0.3
            
            if features["message_entropy"] < thresholds["message_entropy"]:
                anomaly_score += 0.25
            
            dur_min, dur_max = thresholds["handshake_duration"]
            duration = features["handshake_duration"]
            if duration < dur_min or duration > dur_max:
                anomaly_score += 0.2
            
            anomaly_score = min(1.0, anomaly_score)
            result = "Anomaly" if anomaly_score > 0.5 else "Normal"
            
            print(f"  {test_case['name']}: {result} (score: {anomaly_score:.3f}) - Expected: {test_case['expected']}")
        
        print("✅ Model testing complete!")
        
    except Exception as e:
        print(f"❌ Model testing failed: {e}")


def main():
    """Main training script"""
    print("🚀 VeriAI ML Model Training")
    print("=" * 30)
    
    # Generate synthetic data
    data = generate_synthetic_data(n_normal=160, n_fraud=40)
    
    print(f"\n📊 Dataset Summary:")
    print(f"Total samples: {len(data)}")
    normal_count = len([d for d in data if not d['is_fraud']])
    fraud_count = len([d for d in data if d['is_fraud']])
    print(f"Normal samples: {normal_count}")
    print(f"Fraud samples: {fraud_count}")
    print(f"Fraud rate: {fraud_count/len(data):.1%}")
    
    # Train model
    thresholds, training_data = train_model(data)
    
    # Save model
    model_path = save_model(thresholds, training_data)
    
    # Create visualizations
    if len(sys.argv) > 1 and sys.argv[1] == "--plot":
        visualize_data(data, save_plots=True)
    
    # Test model
    test_model(model_path)
    
    print(f"\n🎉 Training complete! Model saved to {model_path}")
    print("💡 You can now start the backend server and run the demo.")


if __name__ == "__main__":
    main()