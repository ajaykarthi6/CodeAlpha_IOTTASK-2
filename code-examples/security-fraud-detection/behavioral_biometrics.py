"""
Behavioral Biometrics Module for AI-Driven Security
Analyzes user behavior patterns from device sensors for continuous authentication
Detects anomalies and potential fraud indicators
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import deque
from enum import Enum


class UserTrustScore(Enum):
    """User trust assessment levels"""
    UNTRUSTED = 0.0
    LOW_TRUST = 0.3
    MEDIUM_TRUST = 0.6
    HIGH_TRUST = 0.85
    FULLY_TRUSTED = 1.0


@dataclass
class TouchEvent:
    """Represents a touchscreen interaction"""
    timestamp: float
    x_position: float  # 0-1 normalized
    y_position: float  # 0-1 normalized
    pressure: float  # 0-1 normalized
    contact_area: float  # mm²
    duration: float  # seconds


@dataclass
class TypingEvent:
    """Represents a keyboard input event"""
    timestamp: float
    key_code: int
    key_dwell_time: float  # time key is held down (ms)
    flight_time: float  # time between key releases and next press (ms)


class BehavioralBiometricAnalyzer:
    """
    Analyzes behavioral biometrics for continuous user authentication
    Builds user profile from normal behavior and detects anomalies
    """
    
    def __init__(self, 
                 sample_size: int = 100,
                 threshold_sigma: float = 3.0):
        """
        Initialize behavioral biometric analyzer
        
        Args:
            sample_size: Number of samples to maintain for profile
            threshold_sigma: Z-score threshold for anomaly detection
        """
        self.sample_size = sample_size
        self.threshold_sigma = threshold_sigma
        
        # User profiles (built from historical data)
        self.touch_profile = {
            'pressure_mean': 0.5,
            'pressure_std': 0.1,
            'speed_mean': 100,  # pixels per second
            'speed_std': 30,
            'acceleration_mean': 50,
            'acceleration_std': 20,
        }
        
        self.typing_profile = {
            'dwell_time_mean': 100,  # ms
            'dwell_time_std': 30,
            'flight_time_mean': 80,  # ms
            'flight_time_std': 25,
        }
        
        # Recent event history
        self.touch_history: deque = deque(maxlen=sample_size)
        self.typing_history: deque = deque(maxlen=sample_size)
        
        self.trust_history: List[float] = []
        
    def add_touch_event(self, event: TouchEvent) -> float:
        """
        Process touch event and compute anomaly score
        
        Args:
            event: TouchEvent data
            
        Returns:
            Anomaly score (0.0 = normal, 1.0 = highly anomalous)
        """
        self.touch_history.append(event)
        
        if len(self.touch_history) < 2:
            return 0.0
        
        # Calculate touch metrics
        prev_event = list(self.touch_history)[-2]
        
        # Distance traveled
        dx = event.x_position - prev_event.x_position
        dy = event.y_position - prev_event.y_position
        distance = np.sqrt(dx**2 + dy**2)
        
        # Speed (pixels per second)
        time_delta = max(event.timestamp - prev_event.timestamp, 0.001)
        speed = distance / time_delta * 1000  # normalize to 1000-pixel screen
        
        # Pressure analysis
        pressure_zscore = abs(
            (event.pressure - self.touch_profile['pressure_mean']) / 
            (self.touch_profile['pressure_std'] + 1e-6)
        )
        
        # Speed analysis
        speed_zscore = abs(
            (speed - self.touch_profile['speed_mean']) / 
            (self.touch_profile['speed_std'] + 1e-6)
        )
        
        # Combined anomaly score (normalized 0-1)
        anomaly_score = min(1.0, (pressure_zscore + speed_zscore) / (2 * self.threshold_sigma))
        
        return anomaly_score
    
    def add_typing_event(self, event: TypingEvent) -> float:
        """
        Process typing event and compute anomaly score
        
        Args:
            event: TypingEvent data
            
        Returns:
            Anomaly score (0.0 = normal, 1.0 = highly anomalous)
        """
        self.typing_history.append(event)
        
        if len(self.typing_history) < 2:
            return 0.0
        
        # Dwell time analysis (how long key is held)
        dwell_zscore = abs(
            (event.key_dwell_time - self.typing_profile['dwell_time_mean']) / 
            (self.typing_profile['dwell_time_std'] + 1e-6)
        )
        
        # Flight time analysis (time between keystrokes)
        prev_event = list(self.typing_history)[-2]
        flight_time = event.timestamp - prev_event.timestamp
        
        flight_zscore = abs(
            (flight_time - self.typing_profile['flight_time_mean']) / 
            (self.typing_profile['flight_time_std'] + 1e-6)
        )
        
        # Combined anomaly score
        anomaly_score = min(1.0, (dwell_zscore + flight_zscore) / (2 * self.threshold_sigma))
        
        return anomaly_score
    
    def extract_behavioral_features(self) -> Dict[str, float]:
        """
        Extract aggregate behavioral features from recent events
        
        Args:
            None
            
        Returns:
            Dictionary of behavioral features
        """
        features = {}
        
        # Touch features
        if len(self.touch_history) > 1:
            pressures = [e.pressure for e in self.touch_history]
            features['avg_pressure'] = np.mean(pressures)
            features['pressure_consistency'] = 1.0 / (1.0 + np.std(pressures))
            
            # Calculate speeds
            speeds = []
            for i in range(1, len(self.touch_history)):
                prev = self.touch_history[i-1]
                curr = self.touch_history[i]
                dx = curr.x_position - prev.x_position
                dy = curr.y_position - prev.y_position
                dist = np.sqrt(dx**2 + dy**2)
                time_delta = curr.timestamp - prev.timestamp
                if time_delta > 0:
                    speeds.append(dist / time_delta)
            
            if speeds:
                features['avg_touch_speed'] = np.mean(speeds)
                features['touch_speed_consistency'] = 1.0 / (1.0 + np.std(speeds))
        
        # Typing features
        if len(self.typing_history) > 1:
            dwell_times = [e.key_dwell_time for e in self.typing_history]
            features['avg_dwell_time'] = np.mean(dwell_times)
            features['dwell_time_consistency'] = 1.0 / (1.0 + np.std(dwell_times))
            
            flight_times = []
            for i in range(1, len(self.typing_history)):
                flight_times.append(
                    self.typing_history[i].timestamp - self.typing_history[i-1].timestamp
                )
            
            if flight_times:
                features['avg_flight_time'] = np.mean(flight_times)
                features['flight_time_consistency'] = 1.0 / (1.0 + np.std(flight_times))
        
        return features
    
    def compute_user_trust_score(self, 
                                 recent_anomalies: List[float],
                                 window_size: int = 10) -> Tuple[float, UserTrustScore]:
        """
        Compute overall user trust score from recent anomalies
        
        Args:
            recent_anomalies: List of recent anomaly scores
            window_size: Number of recent events to consider
            
        Returns:
            Tuple of (trust_score_0_to_1, trust_level_enum)
        """
        if not recent_anomalies:
            return 1.0, UserTrustScore.FULLY_TRUSTED
        
        # Use recent window
        recent = recent_anomalies[-window_size:]
        
        # Average anomaly score
        avg_anomaly = np.mean(recent)
        
        # Trust = 1 - anomaly
        trust_score = 1.0 - avg_anomaly
        
        # Classify trust level
        if trust_score >= 0.85:
            trust_level = UserTrustScore.FULLY_TRUSTED
        elif trust_score >= 0.6:
            trust_level = UserTrustScore.HIGH_TRUST
        elif trust_score >= 0.3:
            trust_level = UserTrustScore.MEDIUM_TRUST
        elif trust_score >= 0.1:
            trust_level = UserTrustScore.LOW_TRUST
        else:
            trust_level = UserTrustScore.UNTRUSTED
        
        return trust_score, trust_level


class FraudDetectionEngine:
    """
    Detects potential fraud using multi-modal analysis
    Combines behavioral biometrics, device context, and pattern analysis
    """
    
    def __init__(self, device_id: str):
        """
        Initialize fraud detection engine
        
        Args:
            device_id: Unique device identifier
        """
        self.device_id = device_id
        self.behavioral_analyzer = BehavioralBiometricAnalyzer()
        self.known_locations = set()
        self.known_times = {'business_hours': (9, 17), 'timezone': 'UTC'}
        
    def check_location_anomaly(self,
                               latitude: float,
                               longitude: float) -> float:
        """
        Check for location anomalies
        
        Args:
            latitude, longitude: Current location
            
        Returns:
            Location anomaly score (0.0-1.0)
        """
        location = (round(latitude, 2), round(longitude, 2))
        
        # If not in known locations, flag as anomaly
        if location not in self.known_locations and len(self.known_locations) > 5:
            return 0.7  # Medium-high anomaly
        
        # Add to known locations
        self.known_locations.add(location)
        
        return 0.0  # Normal
    
    def check_time_anomaly(self, timestamp: float, hour: int) -> float:
        """
        Check for temporal anomalies
        
        Args:
            timestamp: Unix timestamp
            hour: Hour of day (0-23)
            
        Returns:
            Time anomaly score (0.0-1.0)
        """
        business_start, business_end = self.known_times['business_hours']
        
        # Flag if activity outside business hours with high value
        if hour < business_start or hour > business_end:
            return 0.3  # Low-medium anomaly
        
        return 0.0  # Normal
    
    def detect_deepfake_indicators(self,
                                   audio_features: Dict[str, float]) -> float:
        """
        Detect AI-generated (deepfake) audio indicators
        
        Args:
            audio_features: Extracted audio features
                - mfcc_variance: Variance in MFCCs (AI generated typically lower)
                - prosody_smoothness: Smoothness of pitch (AI typically smoother)
                - spectral_entropy: Spectral entropy (AI typically different)
                
        Returns:
            Deepfake probability score (0.0-1.0)
        """
        deepfake_score = 0.0
        
        # Check MFCC variance (AI generated has lower variance)
        if audio_features.get('mfcc_variance', 1.0) < 0.3:
            deepfake_score += 0.3
        
        # Check prosody smoothness (AI generated has unnaturally smooth pitch)
        if audio_features.get('prosody_smoothness', 0.5) > 0.8:
            deepfake_score += 0.3
        
        # Check spectral entropy
        if abs(audio_features.get('spectral_entropy', 0.5) - 0.6) > 0.15:
            deepfake_score += 0.2
        
        return min(1.0, deepfake_score)
    
    def assess_fraud_risk(self,
                         behavioral_anomaly: float,
                         location_anomaly: float,
                         time_anomaly: float,
                         deepfake_score: float) -> Tuple[float, str]:
        """
        Assess overall fraud risk by combining multiple signals
        
        Args:
            behavioral_anomaly: Behavioral biometric anomaly score
            location_anomaly: Location anomaly score
            time_anomaly: Temporal anomaly score
            deepfake_score: Deepfake detection score
            
        Returns:
            Tuple of (fraud_risk_0_to_1, recommendation_string)
        """
        # Weighted combination of anomalies
        weights = {
            'behavioral': 0.4,
            'location': 0.2,
            'time': 0.1,
            'deepfake': 0.3
        }
        
        fraud_risk = (
            weights['behavioral'] * behavioral_anomaly +
            weights['location'] * location_anomaly +
            weights['time'] * time_anomaly +
            weights['deepfake'] * deepfake_score
        )
        
        # Generate recommendation
        if fraud_risk > 0.8:
            recommendation = "🚨 CRITICAL: Block transaction immediately. Verify with user."
        elif fraud_risk > 0.6:
            recommendation = "⚠️ HIGH RISK: Require additional authentication (2FA/PIN)."
        elif fraud_risk > 0.4:
            recommendation = "🔸 MEDIUM RISK: Monitor closely. Log suspicious activity."
        elif fraud_risk > 0.2:
            recommendation = "🔻 LOW RISK: Allow transaction with logging."
        else:
            recommendation = "✅ LOW RISK: Proceed normally."
        
        return fraud_risk, recommendation


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Behavioral Biometrics & Fraud Detection Analysis")
    print("=" * 60)
    
    # Initialize analyzer and engine
    analyzer = BehavioralBiometricAnalyzer()
    engine = FraudDetectionEngine(device_id="DEVICE_001")
    
    # Simulate touch events (normal user)
    print("\n1. Processing Normal Touch Events:")
    normal_touches = [
        TouchEvent(0.0, 0.3, 0.5, 0.6, 50, 0.1),
        TouchEvent(0.1, 0.32, 0.52, 0.58, 48, 0.15),
        TouchEvent(0.3, 0.35, 0.55, 0.62, 52, 0.12),
    ]
    
    touch_anomalies = []
    for touch in normal_touches:
        anomaly = analyzer.add_touch_event(touch)
        touch_anomalies.append(anomaly)
        print(f"  Touch event: anomaly score = {anomaly:.3f}")
    
    # Simulate typing events
    print("\n2. Processing Typing Events:")
    typing_events = [
        TypingEvent(0.5, 65, 120, 80),
        TypingEvent(0.7, 66, 125, 75),
        TypingEvent(0.9, 67, 118, 85),
    ]
    
    typing_anomalies = []
    for typing in typing_events:
        anomaly = analyzer.add_typing_event(typing)
        typing_anomalies.append(anomaly)
        print(f"  Typing event: anomaly score = {anomaly:.3f}")
    
    # Extract behavioral features
    print("\n3. Behavioral Features:")
    features = analyzer.extract_behavioral_features()
    for key, value in features.items():
        print(f"  {key}: {value:.3f}")
    
    # Compute trust score
    print("\n4. User Trust Assessment:")
    all_anomalies = touch_anomalies + typing_anomalies
    trust_score, trust_level = analyzer.compute_user_trust_score(all_anomalies)
    print(f"  Trust Score: {trust_score:.3f}")
    print(f"  Trust Level: {trust_level.name}")
    
    # Assess fraud risk
    print("\n5. Fraud Risk Assessment:")
    behavioral_anomaly = np.mean(all_anomalies)
    location_anomaly = engine.check_location_anomaly(40.7128, -74.0060)
    time_anomaly = engine.check_time_anomaly(0, 14)
    
    audio_features = {
        'mfcc_variance': 0.8,
        'prosody_smoothness': 0.3,
        'spectral_entropy': 0.55
    }
    deepfake_score = engine.detect_deepfake_indicators(audio_features)
    
    fraud_risk, recommendation = engine.assess_fraud_risk(
        behavioral_anomaly,
        location_anomaly,
        time_anomaly,
        deepfake_score
    )
    
    print(f"  Fraud Risk Score: {fraud_risk:.3f}")
    print(f"  Recommendation: {recommendation}")
    
    print("\n" + "=" * 60)
    print("✅ Fraud detection analysis completed!")
    print("=" * 60)
