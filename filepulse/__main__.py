"""
Entry point for FilePulseApp when run as a module.

This allows the package to be executed with 'python -m filepulse'.
"""

from .cli import main

if __name__ == '__main__':
    main()
