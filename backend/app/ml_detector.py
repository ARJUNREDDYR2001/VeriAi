"""
ML Anomaly Detection for AI Agent Verification
Uses IsolationForest to detect fraudulent handshake attempts
"""

import os
import pickle
import json
import time
import statistics
import numpy as np
from typing import Dict, List, Tuple


class MLDetector:
    def __init__(self):
        self.thresholds = {
            "signature_verification": 1,  # Must be 1 for normal
            "response_latency_ms": (50, 500),  # Normal range
            "message_entropy": 2.0,  # Minimum entropy
            "handshake_duration": (100, 1000)  # Normal range in ms
        }
        self.feature_names = [
            "signature_verification",
            "response_latency_ms", 
            "message_entropy",
            "handshake_duration"
        ]
        self.training_data = []
        self.load_model()
    
    def load_model(self) -> bool:
        """Load training data and thresholds from disk"""
        model_path = os.getenv("ML_MODEL_PATH", "ml_model.json")
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'r') as f:
                    model_data = json.load(f)
                    self.training_data = model_data.get('training_data', [])
                    self.thresholds = model_data.get('thresholds', self.thresholds)
                return True
        except Exception as e:
            print(f"Failed to load ML model: {e}")
        
        # Initialize with default data if loading fails
        self._initialize_default_model()
        return False
    
    def _initialize_default_model(self):
        """Initialize with default training data"""
        # Generate minimal synthetic data for thresholds
        self.training_data = self._generate_minimal_training_data()
        self._calculate_thresholds()
    
    def _generate_minimal_training_data(self) -> List[Dict]:
        """Generate minimal training data for fallback model"""
        import random
        training_data = []
        
        # Normal handshakes (genuine agents)
        for i in range(50):
            training_data.append({
                "signature_verification": 1,
                "response_latency_ms": random.gauss(150, 30),  # ~150ms ± 30ms
                "message_entropy": random.gauss(3.5, 0.5),    # Natural language entropy
                "handshake_duration": random.gauss(200, 50),   # Total duration
                "is_fraud": False
            })
        
        # Fraudulent handshakes (fake agents)
        for i in range(15):
            training_data.append({
                "signature_verification": 0,  # Failed signature
                "response_latency_ms": random.gauss(50, 20),   # Too fast (bot-like)
                "message_entropy": random.gauss(2.0, 0.3),    # Low entropy (repetitive)
                "handshake_duration": random.gauss(80, 30),    # Too fast overall
                "is_fraud": True
            })
        
        return training_data
    
    def extract_features(self, handshake_data: Dict) -> Dict:
        """Extract ML features from handshake data"""
        features = {}
        
        # Signature verification (0 or 1)
        features["signature_verification"] = int(handshake_data.get("signature_valid", False))
        
        # Response latency in milliseconds
        if "response_time" in handshake_data and "created_at" in handshake_data:
            latency = (handshake_data["response_time"] - handshake_data["created_at"]) * 1000
            features["response_latency_ms"] = latency
        else:
            features["response_latency_ms"] = 0.0
        
        # Message entropy (if signature exists)
        signature = handshake_data.get("signature", "")
        features["message_entropy"] = self._calculate_entropy(signature)
        
        # Total handshake duration
        current_time = time.time()
        features["handshake_duration"] = (current_time - handshake_data.get("created_at", current_time)) * 1000
        
        return features
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text.lower():
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        text_length = len(text)
        
        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    def train(self, training_data: List[Dict]) -> bool:
        """Train the anomaly detection model using simple thresholds"""
        try:
            self.training_data = training_data
            self._calculate_thresholds()
            return True
        except Exception as e:
            print(f"Training failed: {e}")
            return False
    
    def _calculate_thresholds(self):
        """Calculate thresholds from training data"""
        if not self.training_data:
            return
        
        normal_data = [d for d in self.training_data if not d.get("is_fraud", False)]
        
        if normal_data:
            # Calculate normal ranges
            latencies = [d["response_latency_ms"] for d in normal_data]
            durations = [d["handshake_duration"] for d in normal_data]
            entropies = [d["message_entropy"] for d in normal_data]
            
            if latencies:
                lat_mean = statistics.mean(latencies)
                lat_std = statistics.stdev(latencies) if len(latencies) > 1 else 50
                self.thresholds["response_latency_ms"] = (
                    max(10, lat_mean - 2*lat_std), 
                    lat_mean + 3*lat_std
                )
            
            if durations:
                dur_mean = statistics.mean(durations)
                dur_std = statistics.stdev(durations) if len(durations) > 1 else 100
                self.thresholds["handshake_duration"] = (
                    max(50, dur_mean - 2*dur_std),
                    dur_mean + 3*dur_std
                )
            
            if entropies:
                ent_mean = statistics.mean(entropies)
                ent_std = statistics.stdev(entropies) if len(entropies) > 1 else 0.5
                self.thresholds["message_entropy"] = max(1.0, ent_mean - 2*ent_std)
    
    def predict_anomaly(self, features: Dict) -> float:
        """Predict anomaly score for handshake features using rule-based approach"""
        try:
            anomaly_score = 0.0
            
            # Check signature verification (most important)
            if features.get("signature_verification", 1) == 0:
                anomaly_score += 0.6  # Major red flag
            
            # Check response latency
            latency = features.get("response_latency_ms", 150)
            lat_min, lat_max = self.thresholds["response_latency_ms"]
            if latency < lat_min:
                anomaly_score += 0.3  # Too fast (bot-like)
            elif latency > lat_max:
                anomaly_score += 0.2  # Too slow
            
            # Check message entropy
            entropy = features.get("message_entropy", 3.0)
            min_entropy = self.thresholds["message_entropy"]
            if entropy < min_entropy:
                anomaly_score += 0.25  # Low entropy (repetitive)
            
            # Check handshake duration
            duration = features.get("handshake_duration", 200)
            dur_min, dur_max = self.thresholds["handshake_duration"]
            if duration < dur_min:
                anomaly_score += 0.2  # Too fast overall
            elif duration > dur_max:
                anomaly_score += 0.1  # Too slow overall
            
            # Normalize to 0-1 range
            return min(1.0, round(anomaly_score, 3))
            
        except Exception as e:
            print(f"Prediction failed: {e}")
            return 0.5
    
    def get_anomaly_explanation(self, features: Dict, anomaly_score: float) -> str:
        """Generate human-readable explanation for anomaly score"""
        explanations = []
        
        if features.get("signature_verification", 1) == 0:
            explanations.append("Signature verification failed")
        
        latency = features.get("response_latency_ms", 0)
        if latency < 50:
            explanations.append("Response too fast (bot-like)")
        elif latency > 1000:
            explanations.append("Response too slow")
        
        entropy = features.get("message_entropy", 0)
        if entropy < 2.0:
            explanations.append("Low message entropy (repetitive pattern)")
        
        if anomaly_score > 0.7:
            risk_level = "HIGH RISK"
        elif anomaly_score > 0.5:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "LOW RISK"
        
        if explanations:
            return f"{risk_level}: {', '.join(explanations)}"
        else:
            return f"{risk_level}: Normal handshake pattern"
    
    def save_model(self, filepath: str) -> bool:
        """Save training data and thresholds to disk"""
        try:
            model_data = {
                'training_data': self.training_data,
                'thresholds': self.thresholds,
                'feature_names': self.feature_names,
                'version': '1.0',
                'trained_at': time.time()
            }
            
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to save model: {e}")
            return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return len(self.training_data) > 0 and self.thresholds is not None