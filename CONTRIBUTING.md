# Contributing to AIoT Integration Project

Thank you for your interest in contributing! This document provides guidelines for contributing to the AIoT project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Follow professional standards
- Report issues through proper channels

## How to Contribute

### 1. Reporting Issues

**Before creating an issue:**
- Check existing issues to avoid duplicates
- Provide clear, descriptive titles
- Include steps to reproduce
- Provide expected vs. actual behavior

**Issue Template:**
```markdown
**Description**
Brief description of the issue

**Reproduction Steps**
1. Step 1
2. Step 2
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happened

**Environment**
- Python version
- Operating system
- Relevant packages
```

### 2. Submitting Pull Requests

**Before starting:**
- Fork the repository
- Create a branch: `git checkout -b feature/your-feature`
- Make changes in small, logical commits
- Test your changes thoroughly

**PR Guidelines:**
1. **Title**: Clear, concise description
2. **Description**: Explain what and why
3. **References**: Link related issues
4. **Testing**: Include test results
5. **Documentation**: Update docs if needed

**PR Checklist:**
- [ ] Code follows project style
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commits have descriptive messages
- [ ] No breaking changes (or documented)

### 3. Code Style

**Python Style (PEP 8):**
```python
# Use snake_case for variables and functions
def calculate_heart_rate(sensor_data):
    pass

# Use CamelCase for classes
class BehavioralBiometricAnalyzer:
    pass

# Type hints for clarity
def process_signal(data: np.ndarray) -> float:
    pass

# Docstrings for all public functions
def extract_features(signal: np.ndarray) -> dict:
    """
    Extract features from signal.
    
    Args:
        signal: Input signal array
        
    Returns:
        Dictionary of extracted features
    """
    pass
```

**Naming Conventions:**
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_prefix`

### 4. Testing

**Run tests before submitting:**
```bash
pytest tests/
python -m pytest --cov=code_examples tests/
```

**Writing tests:**
```python
def test_heart_rate_calculation():
    """Test heart rate calculation with known data"""
    signal_processor = SignalProcessor(sample_rate=100)
    test_signal = generate_test_signal()
    
    heart_rate = signal_processor.calculate_heart_rate(test_signal)
    
    assert 60 < heart_rate < 100, "Heart rate should be in normal range"
```

### 5. Documentation

**Update documentation for:**
- New features
- API changes
- Bug fixes (if affecting usage)
- Performance improvements

**Documentation Format:**
```markdown
# Feature Title

## Overview
Brief description

## Usage
```python
# Example code
```

## Parameters
- `param1`: Description
- `param2`: Description

## Returns
Description of return value

## Examples
Practical examples
```

### 6. Commit Messages

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Code refactoring
- `test`: Test additions
- `perf`: Performance improvement

**Examples:**
```
feat(drone-delivery): Add wind compensation algorithm

fix(health-monitoring): Correct BCG filter coefficients

docs(architecture): Update system diagrams

perf(fraud-detection): Optimize behavioral biometrics calculation
```

## Project Structure

```
AIoT_Integration/
├── docs/              # Documentation
├── code-examples/     # Implementation examples
├── notebooks/         # Jupyter notebooks
├── tests/             # Unit tests
├── config/            # Configuration files
└── README.md          # Project overview
```

## Adding New Features

### 1. Case Study Implementation

If adding a new use case:
1. Create directory in `code-examples/`
2. Add implementation files
3. Create documentation in `docs/`
4. Add Jupyter notebook in `notebooks/`
5. Update main README

### 2. Architecture Extension

If extending the AIoT architecture:
1. Update `docs/ARCHITECTURE.md`
2. Add ASCII diagrams
3. Provide code examples
4. Document integration points

## Review Process

1. **Automated Checks**
   - Linting (pylint)
   - Code style (black)
   - Tests (pytest)

2. **Manual Review**
   - Code quality
   - Documentation
   - Design decisions
   - Performance

3. **Approval**
   - At least one maintainer review
   - All CI checks pass
   - Documentation complete

## Performance Guidelines

### Edge Devices
- Model size: <50 MB
- Inference latency: <100 ms
- Memory footprint: <2 GB

### Cloud Services
- Response time: <1 second
- Throughput: 1M+ events/second
- Scalability: Horizontal scaling support

## Security

- No hardcoded credentials
- Use environment variables for secrets
- Follow OWASP guidelines
- Security-focused code review

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check documentation: `docs/`
- Review examples: `code-examples/`
- Open an issue with `[QUESTION]` label

---

**Thank you for contributing! Together we're building intelligent IoT systems.** 🚀
