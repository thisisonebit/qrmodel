"""Quick import and QR generation smoke test for the prototype.

This script imports the app module and calls generate_qr to confirm the
functionality works in this environment without starting the Flask server.
"""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import app

def main():
    url = 'http://example.com/product/ors'
    rel = app.generate_qr(url, 'test-ors')
    print('QR generated at static path:', rel)

if __name__ == '__main__':
    main()
