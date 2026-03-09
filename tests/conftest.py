"""Test configuration ensuring local package imports."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Drop preloaded openpcb modules from non-workspace locations.
for module_name in list(sys.modules):
    if module_name == "openpcb" or module_name.startswith("openpcb."):
        del sys.modules[module_name]
