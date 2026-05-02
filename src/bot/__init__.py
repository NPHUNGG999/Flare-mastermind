cat > src/bot/__init__.py << 'ENDOFFILE'
from .client import FlareBot
from .events import setup_events

__all__ = ["FlareBot", "setup_events"]
ENDOFFILE

echo "✅ bot __init__.py fixed!"
