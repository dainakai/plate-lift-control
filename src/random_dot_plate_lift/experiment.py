"""Integration helper for experiment software."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from .controller import PlateController
from .exceptions import PlateLiftError


@contextmanager
def safe_shutdown_on_exit(controller: PlateController) -> Iterator[PlateController]:
    """Lower on normal exit or a non-motion experiment error.

    The caller deliberately chooses ``up`` or ``down`` inside the context.  A
    standalone ``platectl up`` remains raised because that is an explicit user
    command. After a motion/connection failure or user interrupt, do not
    issue an automatic recovery move: the caller must inspect the mechanism.
    """

    try:
        yield controller
    except (PlateLiftError, KeyboardInterrupt):
        raise
    except BaseException:
        controller.shutdown()
        raise
    else:
        controller.shutdown()
