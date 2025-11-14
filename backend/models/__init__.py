"""Re-export canonical models from models.models.

This module used to define duplicate models with different table names
(e.g. `user` vs `users`). To avoid mismatches, import and re-export the
definitions from `models.models` so the rest of the codebase always uses
the single canonical model definitions.
"""
from .models import User, Event

__all__ = ["User", "Event"]