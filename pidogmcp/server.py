#!/usr/bin/env python3
"""
FastMCP server that wraps the Sunfounder PiDog robot API.

Provides MCP tools for controlling a PiDog robot over HTTP,
including actions, movement, sensory reading, and audio playback.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Valid action names for the do_action tool (from pidog's ActionDict)
# ---------------------------------------------------------------------------
VALID_ACTIONS: list[str] = [
    # Legs
    "stand",
    "sit",
    "lie",
    "lie_with_hands_out",
    "forward",
    "backward",
    "turn_left",
    "turn_right",
    "trot",
    "stretch",
    "push_up",
    "doze_off",
    "half_sit",
    # Head
    "nod_lethargy",
    "shake_head",
    "tilting_head_left",
    "tilting_head_right",
    "tilting_head",
    "head_bark",
    "head_up_down",
    # Tail
    "wag_tail",
]

# ---------------------------------------------------------------------------
# Lazy singleton for the Pidog instance
# ---------------------------------------------------------------------------
_pidog_instance = None
_pidog_initialized = False


def get_pidog() -> "Pidog":  # noqa: F821
    """Return (and lazily create) the shared Pidog hardware instance."""
    global _pidog_instance, _pidog_initialized
    if not _pidog_initialized:
        try:
            from pidog import Pidog
        except ImportError as exc:
            raise RuntimeError(
                "The 'pidog' package is not installed. "
                "Install it with: pip install pidog"
            ) from exc
        _pidog_instance = Pidog()
        _pidog_initialized = True
    return _pidog_instance


# ---------------------------------------------------------------------------
# Lifespan: clean up hardware on shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def server_lifespan(mcp: FastMCP):
    """Manage Pidog hardware lifecycle."""
    yield
    # Shutdown: stop all threads and return to initial position
    global _pidog_initialized
    if _pidog_initialized and _pidog_instance is not None:
        try:
            _pidog_instance.close()
        except Exception:
            pass
        _pidog_initialized = False


# ---------------------------------------------------------------------------
# Create the FastMCP server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "pidog-robot",
    instructions="Control a Sunfounder PiDog robot. Call tools to execute actions, move body parts, read sensors, and play sounds.",
    lifespan=server_lifespan,
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def do_action(
    action_name: str,
    step_count: int = 1,
    speed: int = 50,
    pitch_comp: float = 0.0,
) -> str:
    """Execute a predefined robot action by name.

    Valid action names:
      Legs: stand, sit, lie, lie_with_hands_out, forward, backward,
            turn_left, turn_right, trot, stretch, push_up, doze_off, half_sit
      Head: nod_lethargy, shake_head, tilting_head_left, tilting_head_right,
            tilting_head, head_bark, head_up_down
      Tail: wag_tail

    Args:
        action_name: The name of the action to perform.
        step_count: Number of times to repeat the action (default 1).
        speed: Movement speed 0-100 (default 50).
        pitch_comp: Pitch compensation in degrees for head actions (default 0).

    Returns:
        A status message confirming the action was queued.
    """
    if action_name not in VALID_ACTIONS:
        return f"Error: Unknown action '{action_name}'. Valid actions: {', '.join(VALID_ACTIONS)}"
    try:
        dog = get_pidog()
        dog.do_action(action_name, step_count=step_count, speed=speed, pitch_comp=pitch_comp)
        return f"Action '{action_name}' queued successfully (steps={step_count}, speed={speed})."
    except Exception as exc:
        return f"Error executing action '{action_name}': {exc}"


@mcp.tool()
def legs_move(
    angles: list[float],
    immediately: bool = True,
    speed: int = 50,
) -> str:
    """Move the robot legs to specified angles.

    Args:
        angles: List of 8 leg servo angles in degrees. Order:
                [LF_leg, LF_foot, RF_leg, RF_foot, LH_leg, LH_foot, RH_leg, RH_foot].
        immediately: If True, clear existing actions before moving (default True).
        speed: Movement speed 0-100 (default 50).

    Returns:
        A status message confirming the movement was queued.
    """
    if len(angles) != 8:
        return "Error: angles must contain exactly 8 values."
    try:
        dog = get_pidog()
        dog.legs_move([angles], immediately=immediately, speed=speed)
        return f"Legs move queued (angles={angles}, speed={speed})."
    except Exception as exc:
        return f"Error moving legs: {exc}"


@mcp.tool()
def head_move(
    yaw: float = 0.0,
    roll: float = 0.0,
    pitch: float = 0.0,
    roll_comp: float = 0.0,
    pitch_comp: float = 0.0,
    immediately: bool = True,
    speed: int = 50,
) -> str:
    """Move the robot head to specified yaw/roll/pitch angles.

    Args:
        yaw: Yaw angle in degrees, range [-90, 90] (default 0).
        roll: Roll angle in degrees, range [-70, 70] (default 0).
        pitch: Pitch angle in degrees, range [-45, 30] (default 0).
        roll_comp: Roll compensation offset (default 0).
        pitch_comp: Pitch compensation offset (default 0).
        immediately: If True, clear existing actions before moving (default True).
        speed: Movement speed 0-100 (default 50).

    Returns:
        A status message confirming the movement was queued.
    """
    try:
        dog = get_pidog()
        dog.head_move(
            [[yaw, roll, pitch]],
            roll_comp=roll_comp,
            pitch_comp=pitch_comp,
            immediately=immediately,
            speed=speed,
        )
        return f"Head move queued (yaw={yaw}, roll={roll}, pitch={pitch}, speed={speed})."
    except Exception as exc:
        return f"Error moving head: {exc}"


@mcp.tool()
def head_move_raw(
    angles: list[float],
    immediately: bool = True,
    speed: int = 50,
) -> str:
    """Move the robot head using raw servo angles (bypasses RPY conversion).

    Args:
        angles: List of 3 head servo angles [yaw, roll, pitch] in degrees.
        immediately: If True, clear existing actions before moving (default True).
        speed: Movement speed 0-100 (default 50).

    Returns:
        A status message confirming the movement was queued.
    """
    if len(angles) != 3:
        return "Error: angles must contain exactly 3 values [yaw, roll, pitch]."
    try:
        dog = get_pidog()
        dog.head_move_raw([angles], immediately=immediately, speed=speed)
        return f"Head raw move queued (angles={angles}, speed={speed})."
    except Exception as exc:
        return f"Error moving head: {exc}"


@mcp.tool()
def tail_move(
    angles: list[float],
    immediately: bool = True,
    speed: int = 50,
) -> str:
    """Move the robot tail to specified angles.

    Args:
        angles: List of tail servo angles in degrees (typically a single value).
        immediately: If True, clear existing actions before moving (default True).
        speed: Movement speed 0-100 (default 50).

    Returns:
        A status message confirming the movement was queued.
    """
    try:
        dog = get_pidog()
        dog.tail_move([angles], immediately=immediately, speed=speed)
        return f"Tail move queued (angles={angles}, speed={speed})."
    except Exception as exc:
        return f"Error moving tail: {exc}"


@mcp.tool()
def set_pose(
    x: Optional[float] = None,
    y: Optional[float] = None,
    z: Optional[float] = None,
) -> str:
    """Set the robot body pose (position offset).

    Args:
        x: X-axis position offset (default: unchanged).
        y: Y-axis position offset (default: unchanged).
        z: Z-axis (height) offset in mm (default: unchanged).

    Returns:
        A status message confirming the pose was set.
    """
    try:
        dog = get_pidog()
        dog.set_pose(x=x, y=y, z=z)
        return f"Pose updated (x={x}, y={y}, z={z})."
    except Exception as exc:
        return f"Error setting pose: {exc}"


@mcp.tool()
def set_rpy(
    roll: Optional[float] = None,
    pitch: Optional[float] = None,
    yaw: Optional[float] = None,
    pid: bool = False,
) -> str:
    """Set the robot body orientation (roll/pitch/yaw Euler angles).

    Args:
        roll: Roll angle in degrees (default: unchanged).
        pitch: Pitch angle in degrees (default: unchanged).
        yaw: Yaw angle in degrees (default: unchanged).
        pid: If True, use PID-based smooth transition (default False).

    Returns:
        A status message confirming the orientation was set.
    """
    try:
        dog = get_pidog()
        dog.set_rpy(roll=roll, pitch=pitch, yaw=yaw, pid=pid)
        return f"RPY updated (roll={roll}, pitch={pitch}, yaw={yaw}, pid={pid})."
    except Exception as exc:
        return f"Error setting RPY: {exc}"


@mcp.tool()
def speak(
    name: str,
    volume: int = 100,
) -> str:
    """Play a sound file (non-blocking).

    Args:
        name: Sound file name (looked up in the pidog sounds directory,
              or an absolute path to an .mp3/.wav file).
        volume: Volume level 0-100 (default 100).

    Returns:
        A status message confirming the sound was queued.
    """
    try:
        dog = get_pidog()
        result = dog.speak(name, volume=volume)
        if result is False:
            return f"No sound file found for '{name}'."
        return f"Sound '{name}' playing (volume={volume})."
    except Exception as exc:
        return f"Error playing sound: {exc}"


@mcp.tool()
def read_distance() -> str:
    """Read the ultrasonic distance sensor value.

    Returns:
        The distance reading in cm (or -1 if not available).
    """
    try:
        dog = get_pidog()
        distance = dog.read_distance()
        return f"Distance: {distance} cm" if distance >= 0 else "Distance sensor not available."
    except Exception as exc:
        return f"Error reading distance: {exc}"


@mcp.tool()
def get_battery_voltage() -> str:
    """Read the current battery voltage.

    Returns:
        The battery voltage in volts.
    """
    try:
        dog = get_pidog()
        voltage = dog.get_battery_voltage()
        return f"Battery voltage: {voltage} V"
    except Exception as exc:
        return f"Error reading battery voltage: {exc}"


@mcp.tool()
def body_stop() -> str:
    """Stop all movement (legs, head, and tail) immediately.

    Returns:
        A confirmation message.
    """
    try:
        dog = get_pidog()
        dog.body_stop()
        return "All movement stopped."
    except Exception as exc:
        return f"Error stopping body: {exc}"


@mcp.tool()
def wait_all_done() -> str:
    """Block until all queued movements (legs, head, tail) are complete.

    Returns:
        A confirmation message when all movements finish.
    """
    try:
        dog = get_pidog()
        dog.wait_all_done()
        return "All movements complete."
    except Exception as exc:
        return f"Error waiting for movements: {exc}"


@mcp.tool()
def set_body_height(height: int) -> str:
    """Set the robot body height for pose calculations.

    Args:
        height: Body height in mm, range 20-95.

    Returns:
        A confirmation message.
    """
    if not 20 <= height <= 95:
        return "Error: height must be between 20 and 95 mm."
    try:
        dog = get_pidog()
        dog.body_height = height
        return f"Body height set to {height} mm."
    except Exception as exc:
        return f"Error setting body height: {exc}"


@mcp.tool()
def set_leg_speed(speed: int) -> str:
    """Set the default leg movement speed.

    Args:
        speed: Speed value 0-100 (default 90).

    Returns:
        A confirmation message.
    """
    if not 0 <= speed <= 100:
        return "Error: speed must be between 0 and 100."
    try:
        dog = get_pidog()
        dog.legs_speed = speed
        return f"Leg speed set to {speed}."
    except Exception as exc:
        return f"Error setting leg speed: {exc}"


@mcp.tool()
def set_head_speed(speed: int) -> str:
    """Set the default head movement speed.

    Args:
        speed: Speed value 0-100 (default 90).

    Returns:
        A confirmation message.
    """
    if not 0 <= speed <= 100:
        return "Error: speed must be between 0 and 100."
    try:
        dog = get_pidog()
        dog.head_speed = speed
        return f"Head speed set to {speed}."
    except Exception as exc:
        return f"Error setting head speed: {exc}"


@mcp.tool()
def set_tail_speed(speed: int) -> str:
    """Set the default tail movement speed.

    Args:
        speed: Speed value 0-100 (default 90).

    Returns:
        A confirmation message.
    """
    if not 0 <= speed <= 100:
        return "Error: speed must be between 0 and 100."
    try:
        dog = get_pidog()
        dog.tail_speed = speed
        return f"Tail speed set to {speed}."
    except Exception as exc:
        return f"Error setting tail speed: {exc}"


@mcp.tool()
def list_actions() -> str:
    """List all valid action names available for the do_action tool.

    Returns:
        A formatted list of all valid action names grouped by body part.
    """
    return (
        "Valid actions:\n"
        "  Legs: stand, sit, lie, lie_with_hands_out, forward, backward, "
        "turn_left, turn_right, trot, stretch, push_up, doze_off, half_sit\n"
        "  Head: nod_lethargy, shake_head, tilting_head_left, tilting_head_right, "
        "tilting_head, head_bark, head_up_down\n"
        "  Tail: wag_tail"
    )


@mcp.tool()
def rgb_set_mode(
    mode: str,
    color: str = "cyan",
    bps: float = 1.0,
) -> str:
    """Set the RGB LED strip display mode.

    Args:
        mode: Display mode (e.g. 'breath', 'speak', 'listen', 'black').
        color: LED color name (default 'cyan').
        bps: Brightness/pulse speed (default 1.0).

    Returns:
        A confirmation message.
    """
    try:
        dog = get_pidog()
        dog.rgb_strip.set_mode(mode, color=color, bps=bps)
        return f"RGB mode set to '{mode}' (color={color}, bps={bps})."
    except Exception as exc:
        return f"Error setting RGB mode: {exc}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Start the FastMCP HTTP server on port 8080."""
    import os

    host = os.getenv("PIDOGMCP_HOST", "0.0.0.0")
    port = int(os.getenv("PIDOGMCP_PORT", "8080"))

    print(f"Starting PiDog MCP server on {host}:{port}")
    print(f"Connect to http://{host if host != '0.0.0.0' else 'localhost'}:{port}/mcp")

    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
    )


if __name__ == "__main__":
    main()
