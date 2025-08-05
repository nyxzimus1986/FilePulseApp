# Contributing to FilePulseApp

Thank you for your interest in contributing to FilePulseApp! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic knowledge of Python and tkinter

### Setting Up Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/FilePulseApp.git
   cd FilePulseApp
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Create a development branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Contribution Guidelines

### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints where appropriate
- Include docstrings for all classes, methods, and functions
- Keep line length under 100 characters
- Use meaningful variable and function names

### Example Code Style:
```python
def monitor_directory(self, path: str, recursive: bool = True) -> bool:
    """Monitor a directory for file changes.
    
    Args:
        path: Directory path to monitor
        recursive: Whether to monitor subdirectories
        
    Returns:
        True if monitoring started successfully
        
    Raises:
        ValueError: If path is invalid
    """
    if not os.path.exists(path):
        raise ValueError(f"Path does not exist: {path}")
    
    # Implementation here
    return True
```

### Commit Messages
Use clear and descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and pull requests when applicable
- Keep the first line under 50 characters
- Provide detailed description in the body if needed

**Good examples:**
```
Add system/user change separation to file monitoring

- Implement FileEvent classification system
- Add visual distinction with icons (👤/🔧)
- Include configurable pattern matching
- Update GUI with filtering controls

Fixes #123
```

### Testing
- Write tests for new features
- Ensure all existing tests pass
- Test on multiple platforms when possible
- Include integration tests for GUI components

### Documentation
- Update README.md if adding new features
- Add inline code documentation
- Update configuration examples
- Include usage examples for new features

## 🐛 Bug Reports

When reporting bugs, please include:
1. **Environment information**:
   - Python version
   - Operating system
   - FilePulseApp version
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Error messages** (if any)
6. **Screenshots** (for GUI issues)

## 💡 Feature Requests

When suggesting new features:
1. **Describe the problem** the feature would solve
2. **Explain the proposed solution**
3. **Consider alternative solutions**
4. **Provide use cases and examples**

## 🔄 Pull Request Process

1. **Ensure your code follows the style guidelines**
2. **Update documentation** as needed
3. **Add or update tests** for your changes
4. **Ensure all tests pass**
5. **Update the README.md** with details of changes if applicable
6. **Create a descriptive pull request**:
   - Clear title and description
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

### Pull Request Template:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or marked as such)
```

## 🎯 Development Focus Areas

We're particularly interested in contributions in these areas:

### High Priority
- **Cross-platform compatibility** improvements
- **Performance optimizations** for large directory monitoring
- **Advanced filtering options** and search capabilities
- **Plugin system** architecture
- **Unit and integration tests**

### Medium Priority
- **Additional GUI themes** and customization options
- **Notification system** enhancements
- **Configuration management** improvements
- **Documentation** and examples
- **Internationalization** support

### Future Features
- **Web interface** for remote monitoring
- **Database integration** for event storage
- **Advanced analytics** and reporting
- **REST API** for integration with other tools

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=filepulse

# Run specific test file
python -m pytest tests/test_monitor.py
```

### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies
- Test edge cases and error conditions

## 📁 Project Structure

```
FilePulseApp/
├── filepulse/              # Main package
│   ├── __init__.py         # Package initialization
│   ├── gui.py              # GUI interface
│   ├── monitor.py          # File monitoring core
│   ├── config.py           # Configuration management
│   └── ...                 # Other modules
├── tests/                  # Test files
├── docs/                   # Documentation
├── assets/                 # Static assets
├── examples/               # Usage examples
└── scripts/                # Utility scripts
```

## 🤝 Community Guidelines

- **Be respectful** and inclusive in all interactions
- **Help newcomers** get started with the project
- **Provide constructive feedback** in code reviews
- **Follow the code of conduct** (treat everyone with respect)
- **Ask questions** if you're unsure about anything

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Don't hesitate to ask for feedback on your PRs

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** contributor list
- **Release notes** for significant contributions
- **GitHub contributor graphs** and statistics

## 📄 License

By contributing to FilePulseApp, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to FilePulseApp! 🎉
