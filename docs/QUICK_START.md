# 🚀 Quick Start Guide

## Installation

### Prerequisites
- Python 3.8 or higher
- pip or conda
- Git

### Setup

```bash
# Clone or navigate to the repository
cd /workspaces/CodeAlpha_IOTTASK-2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running Examples

### 1. Autonomous Drone Delivery

```bash
cd code-examples/drone-delivery
python autonomous_navigation.py
```

**Output:**
- Generates delivery route optimization
- Simulates autonomous flight with obstacle avoidance
- Outputs control commands and telemetry

### 2. Smart Health Monitoring

```bash
cd code-examples/health-monitoring
python bcg_analysis.py
```

**Output:**
- BCG signal analysis
- Heart rate and respiratory rate calculation
- Sleep stage classification
- Anomaly detection

### 3. Security & Fraud Detection

```bash
cd code-examples/security-fraud-detection
python behavioral_biometrics.py
```

**Output:**
- Behavioral biometrics analysis
- User trust scoring
- Fraud risk assessment
- Multi-modal threat detection

---

## Project Structure

### Documentation (`docs/`)
- **REPORT.md** - Complete technical report
- **ARCHITECTURE.md** - Detailed architecture framework
- **case-study-*.md** - Individual case study deep-dives
- **KEY_ENABLERS.md** - 5G, 6G, and TinyML technologies
- **CHALLENGES_AND_FUTURE.md** - Technical challenges and solutions

### Code Examples (`code-examples/`)
- **drone-delivery/** - Autonomous drone systems
- **health-monitoring/** - Physiological monitoring
- **security-fraud-detection/** - Security analysis
- **common/** - Shared utilities and base classes

### Architecture Diagrams (`architecture-diagrams/`)
- ASCII diagrams for all three case studies
- Data flow representations
- System architecture visualizations

### Interactive Notebooks (`notebooks/`)
- Jupyter notebooks for hands-on learning
- Analysis and visualization examples
- Tutorial walkthroughs

---

## Key Concepts

### AIoT Stack
```
Device Layer    → Raw sensor data collection
    ↓
Edge Layer      → Real-time processing & inference (<50ms)
    ↓
Cloud Layer     → Global intelligence & model training
```

### Three Case Studies

| Case Study | Domain | Key Technology | Performance |
|-----------|--------|-----------------|-------------|
| Drone Delivery | Logistics | Computer Vision, 5G | 60+ fps detection |
| Health Monitoring | Healthcare | BCG, Signal Processing | >95% accuracy |
| Security | Cybersecurity | Behavioral AI, Deepfake Detection | 99.5% fraud prevention |

---

## Dependencies

### Core Libraries
```python
numpy              # Numerical computing
scipy              # Scientific computing (signal processing)
tensorflow         # ML inference (edge)
scikit-learn       # Machine learning utilities
```

### Communication
```python
paho-mqtt          # MQTT protocol
requests           # HTTP/REST calls
```

### Data & Visualization
```python
pandas             # Data manipulation
matplotlib         # Plotting
```

---

## Configuration

### Model Configuration (`config/model_config.json`)
```json
{
  "drone_navigation": {
    "model": "yolov5-nano",
    "inference_speed_ms": 45,
    "accuracy": 0.85
  },
  "health_monitoring": {
    "model": "lstm_sleep_classifier",
    "accuracy": 0.95,
    "processing_latency_ms": 100
  },
  "fraud_detection": {
    "model": "behavioral_biometrics",
    "trust_threshold": 0.85,
    "fraud_risk_threshold": 0.6
  }
}
```

### Device Profiles (`config/device_profiles.json`)
```json
{
  "drone": {
    "battery_capacity_wh": 5000,
    "max_speed_ms": 15,
    "sensors": ["lidar", "camera", "imu", "gps"]
  },
  "smart_mattress": {
    "sampling_rate_hz": 100,
    "sensor_types": ["pressure", "thermal"],
    "channels": 16
  },
  "smartphone": {
    "processors": ["touchscreen", "accelerometer", "microphone"],
    "sampling_rate_hz": 100,
    "local_ml_capability": true
  }
}
```

---

## Testing

### Run Unit Tests
```bash
python -m pytest tests/
```

### Run Specific Example
```bash
python code-examples/drone-delivery/autonomous_navigation.py
```

---

## Common Issues

### Issue: ImportError for numpy
**Solution:**
```bash
pip install --upgrade numpy scipy
```

### Issue: MQTT Connection Failed
**Solution:**
- Ensure MQTT broker is running
- Check network connectivity
- Verify MQTT credentials

### Issue: Insufficient Memory on Edge Device
**Solution:**
- Use quantized TinyML models
- Reduce model precision (float32 → int8)
- Implement model pruning

---

## Performance Tuning

### Edge Inference Optimization
```python
# Use quantized models for faster inference
model = tf.lite.Interpreter('model_quantized.tflite')
model.allocate_tensors()
```

### Reduce Latency
- Process data locally on edge
- Batch processing when possible
- Use compressed data formats (protobuf)

---

## Deployment

### Docker Deployment
```bash
docker build -t aiot-system:1.0 .
docker run -p 8883:8883 aiot-system:1.0
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/aiot-edge
```

---

## Next Steps

1. **Study the Architecture** - Read `docs/ARCHITECTURE.md`
2. **Review Case Studies** - Study `docs/case-study-*.md`
3. **Run Examples** - Execute code in `code-examples/`
4. **Modify & Extend** - Adapt examples for your use case
5. **Deploy** - Use provided Docker/K8s configs

---

## Additional Resources

- [Full Technical Report](REPORT.md)
- [Architecture Framework](ARCHITECTURE.md)
- [TensorFlow Lite Documentation](https://www.tensorflow.org/lite)
- [5G Standards (3GPP)](https://www.3gpp.org/)
- [MQTT Protocol](http://mqtt.org/)

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Join community discussions
- **Documentation**: Check the `docs/` directory

---

**Ready to explore intelligent IoT systems? Start with an example above! 🚀**
