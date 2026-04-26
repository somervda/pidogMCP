#!/usr/bin/env python3
"""
FastMCP server wrapping the Sunfounder PiDog robot API.

Exposes the Pidog class methods as MCP tools for:
- Action playback (stand, sit, walk, trot, etc.)
- Movement control (legs, head, tail positioning)
- Sensor access (distance, battery, IMU)
- Audio playback
- Calibration and status queries
"""

import os
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Lazily-instantiated Pidog instance so the server can start without hardware
_pidog = None


def get_pidog():
    """Return a singleton Pidog instance, creating it on first use."""
    global _pidog
    if _pidog is None:
        from pidog import Pidog
        _pidog = Pidog()
    return _pidog


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

@asynccontextmanager
async def server_lifespan(mcp: FastMCP):
    """Lifespan handler — initialise / clean up the Pidog instance."""
    global _pidog
    try:
        from pidog import Pidog
        _pidog = Pidog()
        yield {"message": "PiDog MCP server connected to robot hardware."}
    except Exception as exc:
        yield {"message": f"PiDog MCP server started (no hardware): {exc}"}
    finally:
        cleanup_pidog()


def cleanup_pidog():
    """Safely close the Pidog instance on server shutdown."""
    global _pidog
    if _pidog is not None:
        try:
            _pidog.close()
        except Exception:
            pass
        _pidog = None


# Create the FastMCP instance
mcp = FastMCP(
    "pidog-mcp",
    lifespan=server_lifespan,
)

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def do_action(action_name: str, step_count: int = 1, speed: int = 50) -> str:
    """Execute a pre-defined robot action.

    Available actions:
      - stand          Stand up on all four legs
      - sit            Sit down on haunches
      - lie            Lie flat on the ground
      - lie_with_hands_out  Lie with front legs stretched forward
      - forward        Walk forward
      - backward       Walk backward
      - turn_left      Turn left while walking
      - turn_right     Turn right while walking
      - trot           Trot (fast run) forward
      - stretch        Stretch (extend legs)
      - push_up        Do a push-up motion
      - doze_off       Doze off (gentle rocking motion)
      - nod_lethargy   Nod slowly as if falling asleep
      - shake_head     Shake head left / right
      - tilting_head_left   Tilt head to the left
      - tilting_head_right  Tilt head to the right
      - tilting_head    Alternate tilting head left and right
      - head_bark      Bark motion (head snap up and down)
      - head_up_down   Move head up and down
      - wag_tail       Wag tail back and forth
      - half_sit       Half-sit position

    Args:
        action_name: Name of the action to perform.
        step_count:  Number of times to repeat the action (default 1).
        speed:       Movement speed 0-100 (default 50).
    """
    dog = get_pidog()
    dog.do_action(action_name, step_count=step_count, speed=speed)
    return f"Action '{action_name}' queued (steps={step_count}, speed={speed})."


@mcp.tool()
def legs_move(angles: list, immediately: bool = True, speed: int = 50) -> str:
    """Move legs to target angles.

    Args:
        angles:      List of angle sequences (each sequence has 8 values — one per leg joint).
        immediately: Clear existing queue before moving (default True).
        speed:       Movement speed 0-100 (default 50).
    """
    dog = get_pidog()
    dog.legs_move(angles, immediately=immediately, speed=speed)
    return f"Legs move queued (speed={speed})."


@mcp.tool()
def head_move(yrps: list, immediately: bool = True, speed: int = 50) -> str:
    """Move head to target yaw/roll/pitch positions.

    Args:
        yrps:        List of [yaw, roll, pitch] targets (degrees).
        immediately: Clear existing queue before moving (default True).
        speed:       Movement speed 0-100 (default 50).
    """
    dog = get_pidog()
    dog.head_move(yrps, immediately=immediately, speed=speed)
    return f"Head move queued (speed={speed})."


@mcp.tool()
def head_move_raw(angles: list, immediately: bool = True, speed: int = 50) -> str:
    """Move head servos with raw angle values (no RPY conversion).

    Args:
        angles:      List of [yaw_servo, roll_servo, pitch_servo] sequences.
        immediately: Clear existing queue before moving (default True).
        speed:       Movement speed 0-100 (default 50).
    """
    dog = get_pidog()
    dog.head_move_raw(angles, immediately=immediately, speed=speed)
    return f"Head raw move queued (speed={speed})."


@mcp.tool()
def tail_move(angles: list, immediately: bool = True, speed: int = 50) -> str:
    """Move tail to target angles.

    Args:
        angles:      List of angle sequences (each sequence has 1 value).
        immediately: Clear existing queue before moving (default True).
        speed:       Movement speed 0-100 (default 50).
    """
    dog = get_pidog()
    dog.tail_move(angles, immediately=immediately, speed=speed)
    return f"Tail move queued (speed={speed})."


@mcp.tool()
def body_stop() -> str:
    """Stop all movement (legs, head, and tail)."""
    dog = get_pidog()
    dog.body_stop()
    return "All movement stopped."


@mcp.tool()
def legs_stop() -> str:
    """Stop leg movement."""
    dog = get_pidog()
    dog.legs_stop()
    return "Leg movement stopped."


@mcp.tool()
def head_stop() -> str:
    """Stop head movement."""
    dog = get_pidog()
    dog.head_stop()
    return "Head movement stopped."


@mcp.tool()
def tail_stop() -> str:
    """Stop tail movement."""
    dog = get_pidog()
    dog.tail_stop()
    return "Tail movement stopped."


@mcp.tool()
def set_pose(x: float = None, y: float = None, z: float = None) -> str:
    """Set the body pose (position offset).

    Args:
        x: Forward / backward offset.
        y: Left / right offset.
        z: Height offset.
    """
    dog = get_pidog()
    dog.set_pose(x=x, y=y, z=z)
    return f"Pose updated (x={x}, y={y}, z={z})."


@mcp.tool()
def set_rpy(roll: float = None, pitch: float = None, yaw: float = None, pid: bool = False) -> str:
    """Set body roll / pitch / yaw orientation.

    Args:
        roll:  Roll angle in degrees.
        pitch: Pitch angle in degrees.
        yaw:   Yaw angle in degrees.
        pid:   Use PID control for smooth transition (default False).
    """
    dog = get_pidog()
    dog.set_rpy(roll=roll, pitch=pitch, yaw=yaw, pid=pid)
    return f"RPY updated (roll={roll}, pitch={pitch}, yaw={yaw}, pid={pid})."


@mcp.tool()
def set_body_height(height: int) -> str:
    """Set the body height for pose calculations.

    Args:
        height: Body height in mm (typical range 20-95).
    """
    dog = get_pidog()
    dog.body_height = height
    return f"Body height set to {height} mm."


@mcp.tool()
def speak(name: str, volume: int = 100) -> str:
    """Play a sound file (non-blocking).

    Args:
        name:   Sound file name (looked up in the pidog/sounds directory).
        volume: Volume 0-100 (default 100).
    """
    dog = get_pidog()
    result = dog.speak(name, volume=volume)
    if result is False:
        return f"No sound file found for '{name}'."
    return f"Playing sound '{name}' (volume={volume})."


@mcp.tool()
def read_distance() -> str:
    """Read the ultrasonic sensor distance value.

    Returns:
        The current distance reading in cm (or -1 if unavailable).
    """
    dog = get_pidog()
    dist = dog.read_distance()
    return f"Distance: {dist} cm" if dist >= 0 else "Distance sensor unavailable."


@mcp.tool()
def get_battery_voltage() -> str:
    """Read the current battery voltage.

    Returns:
        The battery voltage in Volts.
    """
    dog = get_pidog()
    voltage = dog.get_battery_voltage()
    return f"Battery voltage: {voltage} V"


@mcp.tool()
def set_leg_offsets(offsets: list, reset: list = None) -> str:
    """Set leg servo calibration offsets.

    Args:
        offsets: List of 8 offset values (one per leg joint).
        reset:   Optional list of 8 angles to reset servos to.
    """
    dog = get_pidog()
    dog.set_leg_offsets(offsets, reset_list=reset)
    return f"Leg offsets set: {offsets}"


@mcp.tool()
def set_head_offsets(offsets: list) -> str:
    """Set head servo calibration offsets.

    Args:
        offsets: List of 3 offset values [yaw, roll, pitch].
    """
    dog = get_pidog()
    dog.set_head_offsets(offsets)
    return f"Head offsets set: {offsets}"


@mcp.tool()
def set_tail_offset(offset: list) -> str:
    """Set tail servo calibration offset.

    Args:
        offset: List with 1 offset value.
    """
    dog = get_pidog()
    dog.set_tail_offset(offset)
    return f"Tail offset set: {offset}"


@mcp.tool()
def wait_all_done() -> str:
    """Block until all queued movements (legs, head, tail) are complete."""
    dog = get_pidog()
    dog.wait_all_done()
    return "All movements complete."


@mcp.tool()
def is_all_done() -> str:
    """Check whether all queued movements are complete.

    Returns:
        True if all movements are done, False otherwise.
    """
    dog = get_pidog()
    done = dog.is_all_done()
    return "All done" if done else "Movements in progress."


@mcp.tool()
def list_actions() -> str:
    """List all available pre-defined actions for do_action.

    Returns:
        A comma-separated list of action names.
    """
    dog = get_pidog()
    actions = sorted(dog.actions_dict.keys())
    return ", ".join(actions)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    host = os.environ.get("PIDOG_MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("PIDOG_MCP_PORT", "8000"))
    mcp.run(host=host, port=port)
