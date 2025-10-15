import sys
from pathlib import Path
# make project importable
sys.path.append(str(Path(__file__).resolve().parent))

from app import create_app
app = create_app()
print('APP IMPORT OK, BLUEPRINTS:', sorted(list(app.blueprints.keys())))
print('CONFIG KEYS:', sorted(list(app.config.keys()) )[:20])
