from __future__ import annotations

import os
import threading
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

from mcp.server.fastmcp import FastMCP

try:
    from pidog import Pidog as _Pidog
except Exception as exc:  # pragma: no cover - depends on host runtime/hardware
    _Pidog = None
    _PIDOG_IMPORT_ERROR = exc
else:
    _PIDOG_IMPORT_ERROR = None


mcp = FastMCP(
    "pidog-http",
    instructions=(
        "Remote HTTP MCP wrapper for SunFounder Pidog. "
        "Connect first with pidog_connect, then issue movement/sensor tools."
    ),
)


@dataclass
class PidogRuntime:
    dog: Any | None = None
    lock: threading.RLock = field(default_factory=threading.RLock)


runtime = PidogRuntime()


def _ensure_pidog_available() -> None:
    if _Pidog is None:
        raise RuntimeError(
            "Pidog package is not importable in this environment. "
            f"Original import error: {_PIDOG_IMPORT_ERROR}"
        )


def _require_connected() -> Any:
    if runtime.dog is None:
        raise RuntimeError("Pidog is not connected. Call pidog_connect first.")
    return runtime.dog


def _validate_speed(speed: int) -> int:
    if speed < 0 or speed > 100:
        raise ValueError("speed must be within 0..100")
    return speed


def _validate_angle_frames(frames: list[list[float]], expected_len: int, label: str) -> None:
    if not frames:
        raise ValueError(f"{label} cannot be empty")
    for idx, frame in enumerate(frames):
        if len(frame) != expected_len:
            raise ValueError(
                f"{label}[{idx}] must have {expected_len} values, got {len(frame)}"
            )


@mcp.tool()
def pidog_connect(
    leg_pins: list[int] | None = None,
    head_pins: list[int] | None = None,
    tail_pin: list[int] | None = None,
    force_reconnect: bool = False,
) -> dict[str, Any]:
    """Connect to a physical Pidog and initialize hardware threads."""
    with runtime.lock:
        if runtime.dog is not None and not force_reconnect:
            return {"connected": True, "reused": True}

        if runtime.dog is not None and force_reconnect:
            with suppress(Exception):
                runtime.dog.close()
            runtime.dog = None

        _ensure_pidog_available()

        kwargs: dict[str, Any] = {}
        if leg_pins is not None:
            kwargs["leg_pins"] = leg_pins
        if head_pins is not None:
            kwargs["head_pins"] = head_pins
        if tail_pin is not None:
            kwargs["tail_pin"] = tail_pin

        runtime.dog = _Pidog(**kwargs)
        return {
            "connected": True,
            "reused": False,
            "thread_list": list(getattr(runtime.dog, "thread_list", [])),
        }


@mcp.tool()
def pidog_disconnect() -> dict[str, Any]:
    """Close the current Pidog connection and stop robot threads safely."""
    with runtime.lock:
        if runtime.dog is None:
            return {"connected": False, "message": "Already disconnected"}

        with suppress(Exception):
            runtime.dog.close()
        runtime.dog = None
        return {"connected": False}


@mcp.tool()
def pidog_status() -> dict[str, Any]:
    """Return connection status and basic runtime fields from the Pidog instance."""
    with runtime.lock:
        if runtime.dog is None:
            return {"connected": False}

        dog = runtime.dog
        return {
            "connected": True,
            "thread_list": list(getattr(dog, "thread_list", [])),
            "exit_flag": bool(getattr(dog, "exit_flag", False)),
            "body_height": getattr(dog, "body_height", None),
        }


@mcp.tool()
def do_action(
    action_name: str,
    step_count: int = 1,
    speed: int = 50,
    pitch_comp: float = 0.0,
    wait: bool = True,
) -> dict[str, Any]:
    """Run a named built-in Pidog action (for example: sit, stand, lie, walk)."""
    if step_count < 1:
        raise ValueError("step_count must be >= 1")
    _validate_speed(speed)

    with runtime.lock:
        dog = _require_connected()
        dog.do_action(action_name, step_count=step_count, speed=speed, pitch_comp=pitch_comp)
        if wait:
            dog.wait_all_done()
        return {
            "ok": True,
            "action": action_name,
            "step_count": step_count,
            "speed": speed,
            "waited": wait,
        }


@mcp.tool()
def legs_move(
    target_angles: list[list[float]],
    immediately: bool = True,
    speed: int = 50,
    wait: bool = False,
) -> dict[str, Any]:
    """Queue leg movement frames, each frame containing 8 servo angles."""
    _validate_speed(speed)
    _validate_angle_frames(target_angles, expected_len=8, label="target_angles")

    with runtime.lock:
        dog = _require_connected()
        dog.legs_move(target_angles, immediately=immediately, speed=speed)
        if wait:
            dog.wait_legs_done()
        return {"ok": True, "frames": len(target_angles), "waited": wait}


@mcp.tool()
def head_move(
    target_yrps: list[list[float]],
    roll_comp: float = 0.0,
    pitch_comp: float = 0.0,
    immediately: bool = True,
    speed: int = 50,
    wait: bool = False,
) -> dict[str, Any]:
    """Queue head movement frames in yaw/roll/pitch format (3 values per frame)."""
    _validate_speed(speed)
    _validate_angle_frames(target_yrps, expected_len=3, label="target_yrps")

    with runtime.lock:
        dog = _require_connected()
        dog.head_move(
            target_yrps,
            roll_comp=roll_comp,
            pitch_comp=pitch_comp,
            immediately=immediately,
            speed=speed,
        )
        if wait:
            dog.wait_head_done()
        return {"ok": True, "frames": len(target_yrps), "waited": wait}


@mcp.tool()
def head_move_raw(
    target_angles: list[list[float]],
    immediately: bool = True,
    speed: int = 50,
    wait: bool = False,
) -> dict[str, Any]:
    """Queue raw head servo angle frames (3 values per frame)."""
    _validate_speed(speed)
    _validate_angle_frames(target_angles, expected_len=3, label="target_angles")

    with runtime.lock:
        dog = _require_connected()
        dog.head_move_raw(target_angles, immediately=immediately, speed=speed)
        if wait:
            dog.wait_head_done()
        return {"ok": True, "frames": len(target_angles), "waited": wait}


@mcp.tool()
def tail_move(
    target_angles: list[list[float]],
    immediately: bool = True,
    speed: int = 50,
    wait: bool = False,
) -> dict[str, Any]:
    """Queue tail movement frames, one angle value per frame."""
    _validate_speed(speed)
    _validate_angle_frames(target_angles, expected_len=1, label="target_angles")

    with runtime.lock:
        dog = _require_connected()
        dog.tail_move(target_angles, immediately=immediately, speed=speed)
        if wait:
            dog.wait_tail_done()
        return {"ok": True, "frames": len(target_angles), "waited": wait}


@mcp.tool()
def stop_and_lie(speed: int = 85) -> dict[str, Any]:
    """Stop queued actions and return robot to the default lie posture."""
    _validate_speed(speed)
    with runtime.lock:
        dog = _require_connected()
        dog.stop_and_lie(speed=speed)
        return {"ok": True, "speed": speed}


@mcp.tool()
def speak(name: str, volume: int = 100, block: bool = False) -> dict[str, Any]:
    """Play a named sound from Pidog sound assets or an explicit file path."""
    if volume < 0 or volume > 100:
        raise ValueError("volume must be within 0..100")

    with runtime.lock:
        dog = _require_connected()
        if block:
            result = dog.speak_block(name, volume=volume)
        else:
            result = dog.speak(name, volume=volume)
        return {"ok": result is not False, "name": name, "volume": volume, "block": block}


@mcp.tool()
def set_pose(x: float | None = None, y: float | None = None, z: float | None = None) -> dict[str, Any]:
    """Set body pose vector targets in millimeters."""
    with runtime.lock:
        dog = _require_connected()
        dog.set_pose(x=x, y=y, z=z)
        return {"ok": True, "pose": [float(dog.pose[0, 0]), float(dog.pose[1, 0]), float(dog.pose[2, 0])]}


@mcp.tool()
def set_rpy(
    roll: float | None = None,
    pitch: float | None = None,
    yaw: float | None = None,
    pid: bool = False,
) -> dict[str, Any]:
    """Set roll/pitch/yaw targets in degrees, optionally using Pidog PID compensation."""
    with runtime.lock:
        dog = _require_connected()
        dog.set_rpy(roll=roll, pitch=pitch, yaw=yaw, pid=pid)
        return {"ok": True, "rpy_radians": [float(dog.rpy[0]), float(dog.rpy[1]), float(dog.rpy[2])]}


@mcp.tool()
def pose2coords() -> dict[str, Any]:
    """Convert current pose/rpy to body and leg coordinates using Pidog kinematics."""
    with runtime.lock:
        dog = _require_connected()
        return dog.pose2coords()


@mcp.tool()
def pose2legs_angle() -> dict[str, Any]:
    """Convert current pose/rpy to 8 servo leg angles."""
    with runtime.lock:
        dog = _require_connected()
        angles = dog.pose2legs_angle()
        return {"angles": angles}


@mcp.tool()
def read_distance() -> dict[str, Any]:
    """Read ultrasonic distance in centimeters from the sensory process."""
    with runtime.lock:
        dog = _require_connected()
        return {"distance_cm": dog.read_distance()}


@mcp.tool()
def get_battery_voltage() -> dict[str, Any]:
    """Read battery voltage via robot_hat utility hooks exposed by Pidog."""
    with runtime.lock:
        dog = _require_connected()
        return {"voltage": dog.get_battery_voltage()}


@mcp.tool()
def wait_all_done() -> dict[str, Any]:
    """Block until queued legs, head, and tail actions finish."""
    with runtime.lock:
        dog = _require_connected()
        dog.wait_all_done()
        return {"ok": True}


def run_server() -> None:
    """Run as a remote HTTP MCP server on /mcp using streamable-http transport."""
    host = os.getenv("PIDOG_MCP_HOST", "0.0.0.0")
    port = int(os.getenv("PIDOG_MCP_PORT", "8000"))
    mcp.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    run_server()
