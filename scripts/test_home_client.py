import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `import app` finds the package when
# this script is executed from the scripts/ directory.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app


app = create_app()

with app.test_client() as c:
    try:
        rv = c.get('/')
        print('status_code:', rv.status_code)
        data = rv.get_data(as_text=True)
        print('body len:', len(data))
        print(data[:2000])
    except Exception as e:
        # Print exception and full traceback to help debugging
        import traceback

        print('EXCEPTION while requesting /')
        traceback.print_exc()
