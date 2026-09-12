"""Domain-specific errors mapped to stable CLI exit codes."""


class PlateLiftError(RuntimeError):
    exit_code = 3


class HardwareConnectionError(PlateLiftError):
    exit_code = 2


class MotionFault(PlateLiftError):
    exit_code = 3


class MotionTimeout(MotionFault):
    exit_code = 4


class ConcurrentCommandError(PlateLiftError):
    exit_code = 5
