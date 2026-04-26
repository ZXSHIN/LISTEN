#!/usr/bin/env python3
"""
LISTEN - OSINT & Dorking Desktop Toolkit
Entry point
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from ui.app import LISTENApp
    app = LISTENApp()
    app.mainloop()


if __name__ == "__main__":
    main()
