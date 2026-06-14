"""
Ballistocardiography (BCG) Analysis Module for Smart Sleep Systems
Analyzes cardiac and respiratory signals from embedded pressure sensors
Detects sleep stages and physiological anomalies
"""

import numpy as np
from scipy import signal
from dataclasses import dataclass
from typing import Tuple, List
from enum import Enum


class SleepStage(Enum):
    """Sleep stage classification"""
    AWAKE = 0
    LIGHT_SLEEP = 1
    DEEP_SLEEP = 2
    REM_SLEEP = 3


@dataclass
class BCGSignal:
    """Ballistocardiography signal data"""
    timestamp: float
    raw_signal: np.ndarray  # Raw sensor readings
    sample_rate: int  # Hz
    
    def duration(self) -> float:
        """Get signal duration in seconds"""
        return len(self.raw_signal) / self.sample_rate


class SignalProcessor:
    """
    Processes raw BCG sensor data and extracts physiological parameters
    Implements IIR filters and feature extraction
    """
    
    def __init__(self, sample_rate: int = 100):
        """
        Initialize signal processor
        
        Args:
            sample_rate: Sampling rate in Hz (typical: 50-200 Hz)
        """
        self.sample_rate = sample_rate
        self.nyquist_freq = sample_rate / 2
        
    def remove_motion_artifacts(self, signal_data: np.ndarray) -> np.ndarray:
        """
        Remove motion artifacts using adaptive filtering
        Low-pass filter to remove high-frequency noise from movement
        
        Args:
            signal_data: Raw sensor signal
            
        Returns:
            Filtered signal
        """
        # Design low-pass filter (cutoff: 2 Hz for cardiac + respiratory bands)
        cutoff_freq = 2.0  # Hz
        normalized_cutoff = cutoff_freq / self.nyquist_freq
        
        # Butterworth filter design
        b, a = signal.butter(4, normalized_cutoff, btype='low')
        
        # Apply filter (forward-backward to preserve phase)
        filtered = signal.filtfilt(b, a, signal_data)
        
        return filtered
    
    def extract_cardiac_signal(self, 
                              bcg_signal: np.ndarray,
                              motion_filtered: np.ndarray) -> np.ndarray:
        """
        Extract cardiac signal from BCG
        Isolates heart rate band (0.8-2.5 Hz, or 48-150 bpm)
        
        Args:
            bcg_signal: Original BCG signal
            motion_filtered: Motion-artifact-removed signal
            
        Returns:
            Bandpass-filtered cardiac signal
        """
        # Band-pass filter for heart rate (0.8-2.5 Hz)
        low_cutoff = 0.8 / self.nyquist_freq
        high_cutoff = 2.5 / self.nyquist_freq
        
        b, a = signal.butter(4, [low_cutoff, high_cutoff], btype='band')
        cardiac_signal = signal.filtfilt(b, a, motion_filtered)
        
        return cardiac_signal
    
    def extract_respiratory_signal(self,
                                  motion_filtered: np.ndarray) -> np.ndarray:
        """
        Extract respiratory signal from BCG
        Isolates respiratory band (0.1-0.5 Hz, or 6-30 breaths/min)
        
        Args:
            motion_filtered: Motion-artifact-removed signal
            
        Returns:
            Bandpass-filtered respiratory signal
        """
        # Band-pass filter for respiration (0.1-0.5 Hz)
        low_cutoff = 0.1 / self.nyquist_freq
        high_cutoff = 0.5 / self.nyquist_freq
        
        b, a = signal.butter(4, [low_cutoff, high_cutoff], btype='band')
        respiratory_signal = signal.filtfilt(b, a, motion_filtered)
        
        return respiratory_signal
    
    def detect_peaks(self, 
                    signal_data: np.ndarray,
                    distance: int = None,
                    height: float = None) -> np.ndarray:
        """
        Detect peaks in filtered signal (heartbeats)
        
        Args:
            signal_data: Filtered signal
            distance: Minimum distance between peaks (samples)
            height: Minimum peak height
            
        Returns:
            Array of peak indices
        """
        if distance is None:
            distance = int(0.4 * self.sample_rate)  # Min 0.4s between beats (150 bpm max)
        
        if height is None:
            height = np.std(signal_data) * 0.5
        
        peaks, _ = signal.find_peaks(signal_data, distance=distance, height=height)
        
        return peaks
    
    def calculate_heart_rate(self, cardiac_signal: np.ndarray) -> float:
        """
        Calculate instantaneous heart rate from cardiac signal
        
        Args:
            cardiac_signal: Bandpass-filtered cardiac signal
            
        Returns:
            Heart rate in beats per minute (bpm)
        """
        peaks = self.detect_peaks(cardiac_signal)
        
        if len(peaks) < 2:
            return 0.0
        
        # Calculate intervals between beats
        intervals = np.diff(peaks)  # in samples
        interval_seconds = intervals / self.sample_rate
        
        # Heart rate = 60 / interval (seconds)
        heart_rates = 60.0 / interval_seconds
        
        # Return median heart rate (robust to outliers)
        return float(np.median(heart_rates))
    
    def calculate_heart_rate_variability(self, 
                                        cardiac_signal: np.ndarray) -> Tuple[float, float]:
        """
        Calculate heart rate variability (HRV) metrics
        HRV indicates autonomic nervous system balance
        
        Args:
            cardiac_signal: Bandpass-filtered cardiac signal
            
        Returns:
            Tuple of (SDNN, RMSSD) in milliseconds
        """
        peaks = self.detect_peaks(cardiac_signal)
        
        if len(peaks) < 3:
            return 0.0, 0.0
        
        # RR intervals (time between consecutive heartbeats)
        intervals_ms = np.diff(peaks) / self.sample_rate * 1000
        
        # SDNN: Standard Deviation of NN intervals
        sdnn = np.std(intervals_ms)
        
        # RMSSD: Root Mean Square of Successive Differences
        successive_diffs = np.diff(intervals_ms)
        rmssd = np.sqrt(np.mean(successive_diffs**2))
        
        return sdnn, rmssd
    
    def calculate_respiratory_rate(self, respiratory_signal: np.ndarray) -> float:
        """
        Calculate respiratory rate from respiratory signal
        
        Args:
            respiratory_signal: Bandpass-filtered respiratory signal
            
        Returns:
            Respiratory rate in breaths per minute
        """
        peaks = self.detect_peaks(respiratory_signal)
        
        if len(peaks) < 2:
            return 0.0
        
        # Calculate intervals between breaths
        intervals = np.diff(peaks)  # in samples
        interval_seconds = intervals / self.sample_rate
        
        # Respiratory rate = 60 / interval (seconds)
        respiratory_rates = 60.0 / interval_seconds
        
        # Return median respiratory rate
        return float(np.median(respiratory_rates))


class SleepStageClassifier:
    """
    Classifies sleep stages based on physiological signals
    Uses machine learning features from cardiac and respiratory data
    """
    
    def __init__(self):
        """Initialize sleep stage classifier"""
        self.processor = SignalProcessor()
        # Simplified thresholds for demonstration
        # In production: use trained ML model
        
    def extract_features(self, bcg_signal: BCGSignal) -> dict:
        """
        Extract features for sleep stage classification
        
        Args:
            bcg_signal: BCG signal data
            
        Returns:
            Dictionary of extracted features
        """
        # Remove motion artifacts
        filtered = self.processor.remove_motion_artifacts(bcg_signal.raw_signal)
        
        # Extract cardiac and respiratory signals
        cardiac = self.processor.extract_cardiac_signal(bcg_signal.raw_signal, filtered)
        respiratory = self.processor.extract_respiratory_signal(filtered)
        
        # Calculate physiological parameters
        heart_rate = self.processor.calculate_heart_rate(cardiac)
        sdnn, rmssd = self.processor.calculate_heart_rate_variability(cardiac)
        resp_rate = self.processor.calculate_respiratory_rate(respiratory)
        
        # Calculate signal characteristics
        cardiac_amplitude = np.std(cardiac)
        respiratory_amplitude = np.std(respiratory)
        movement = np.std(np.diff(bcg_signal.raw_signal))
        
        features = {
            'heart_rate': heart_rate,
            'heart_rate_variability_sdnn': sdnn,
            'heart_rate_variability_rmssd': rmssd,
            'respiratory_rate': resp_rate,
            'cardiac_amplitude': cardiac_amplitude,
            'respiratory_amplitude': respiratory_amplitude,
            'movement': movement
        }
        
        return features
    
    def classify_sleep_stage(self, features: dict) -> SleepStage:
        """
        Classify sleep stage based on extracted features
        Uses simplified thresholds (production version would use ML model)
        
        Args:
            features: Extracted features dictionary
            
        Returns:
            Predicted sleep stage
        """
        hr = features['heart_rate']
        hrv = features['heart_rate_variability_sdnn']
        resp = features['respiratory_rate']
        movement = features['movement']
        
        # Simplified classification logic
        
        # REM Sleep: Higher HR, higher HRV, lower amplitude
        if hr > 70 and hrv > 50 and movement < 0.1:
            return SleepStage.REM_SLEEP
        
        # Deep Sleep: Lower HR, lower HRV, slow respiration, low movement
        elif hr < 55 and hrv < 30 and resp < 12 and movement < 0.05:
            return SleepStage.DEEP_SLEEP
        
        # Light Sleep: Moderate HR, moderate HRV
        elif hr < 65 and movement < 0.2:
            return SleepStage.LIGHT_SLEEP
        
        # Awake: High movement, high HR
        else:
            return SleepStage.AWAKE
    
    def detect_anomalies(self, features: dict) -> List[str]:
        """
        Detect physiological anomalies that may indicate sleep disorders
        
        Args:
            features: Extracted features dictionary
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Sleep apnea indicators: breathing pauses, low SpO2
        if features['respiratory_rate'] < 8:
            anomalies.append("Possible sleep apnea - respiratory rate too low")
        
        # Arrhythmia indicators
        if features['heart_rate'] < 40 or features['heart_rate'] > 120:
            anomalies.append("Possible cardiac arrhythmia - abnormal heart rate")
        
        # Excessive movement
        if features['movement'] > 0.5:
            anomalies.append("Excessive movement - possible restless leg syndrome")
        
        # Heart rate variability abnormalities
        if features['heart_rate_variability_sdnn'] < 10:
            anomalies.append("Low heart rate variability - possible autonomic dysfunction")
        
        return anomalies


# Example usage
if __name__ == "__main__":
    # Simulate BCG sensor data (6-hour sleep recording at 100 Hz)
    sample_rate = 100
    duration_seconds = 60  # 1 minute for demo
    t = np.arange(0, duration_seconds, 1/sample_rate)
    
    # Simulate BCG signal: combination of cardiac and respiratory
    cardiac_freq = 1.2  # Hz (72 bpm)
    respiratory_freq = 0.25  # Hz (15 breaths/min)
    
    bcg_raw = (
        2.0 * np.sin(2 * np.pi * cardiac_freq * t) +  # Cardiac component
        0.5 * np.sin(2 * np.pi * respiratory_freq * t) +  # Respiratory component
        0.3 * np.random.randn(len(t))  # Noise
    )
    
    # Create BCG signal object
    bcg_signal = BCGSignal(
        timestamp=0.0,
        raw_signal=bcg_raw,
        sample_rate=sample_rate
    )
    
    # Process and classify
    classifier = SleepStageClassifier()
    features = classifier.extract_features(bcg_signal)
    sleep_stage = classifier.classify_sleep_stage(features)
    anomalies = classifier.detect_anomalies(features)
    
    print("=" * 50)
    print("BCG Analysis Results")
    print("=" * 50)
    print(f"\nPhysiological Parameters:")
    print(f"  Heart Rate: {features['heart_rate']:.1f} bpm")
    print(f"  HRV (SDNN): {features['heart_rate_variability_sdnn']:.1f} ms")
    print(f"  HRV (RMSSD): {features['heart_rate_variability_rmssd']:.1f} ms")
    print(f"  Respiratory Rate: {features['respiratory_rate']:.1f} breaths/min")
    
    print(f"\nSleep Classification:")
    print(f"  Current Sleep Stage: {sleep_stage.name}")
    
    if anomalies:
        print(f"\n⚠️ Detected Anomalies:")
        for anomaly in anomalies:
            print(f"  - {anomaly}")
    else:
        print(f"\n✅ No anomalies detected")
    
    print("\n✅ BCG analysis example completed!")
