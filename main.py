#!/usr/bin/env python3
"""PiDog MCP Server - Wraps the Sunfounder PiDog robot API."""

import os
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP, Context

# Lazy-import pidog to avoid hardware errors at server startup
_pidog_instance = None


def _get_pidog():
    """Get or create the singleton Pidog instance."""
    global _pidog_instance
    if _pidog_instance is None:
        try:
            from pidog import Pidog
            _pidog_instance = Pidog()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PiDog: {e}")
    return _pidog_instance


def _check_pidog():
    """Check that pidog is connected and raise if not."""
    if _pidog_instance is None:
        raise RuntimeError("PiDog not initialized. Call connect first.")
    return _pidog_instance


# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "pidog-mcp",
    instructions="Control a Sunfounder PiDog robot. Manage connection, movement, actions, sensors, and audio.",
)

# ---------------------------------------------------------------------------
# Connection tools
# ---------------------------------------------------------------------------
@mcp.tool()
def connect() -> str:
    """Initialize and connect to the PiDog robot hardware.

    Returns a confirmation message on success.
    """
    try:
        dog = _get_pidog()
        return f"Connected to PiDog successfully. Battery voltage: {dog.get_battery_voltage()}V"
    except Exception as e:
        return f"Failed to connect: {e}"


@mcp.tool()
def disconnect() -> str:
    """Disconnect from the PiDog robot and release hardware resources.

    Returns a confirmation message.
    """
    global _pidog_instance
    try:
        if _pidog_instance:
            _pidog_instance.close()
            _pidog_instance = None
        return "Disconnected from PiDog."
    except Exception as e:
        return f"Error during disconnect: {e}"


@mcp.tool()
def status() -> dict:
    """Get the current status of the PiDog robot.

    Returns:
        Dictionary with connection status, battery voltage, and motion state.
    """
    dog = _check_pidog()
    return {
        "connected": True,
        "battery_voltage": dog.get_battery_voltage(),
        "legs_done": dog.is_legs_done(),
        "head_done": dog.is_head_done(),
        "tail_done": dog.is_tail_done(),
        "all_done": dog.is_all_done(),
    }


# ---------------------------------------------------------------------------
# Action tools
# ---------------------------------------------------------------------------
@mcp.tool()
def do_action(
    action_name: str,
    step_count: int = 1,
    speed: int = 50,
    pitch_comp: float = 0.0,
) -> str:
    """Execute a predefined robot action by name.

    Available actions:
      Legs:
        - stand: Stand up on all four legs
        - sit: Sit on hind legs
        - lie: Lie flat on the ground
        - lie_with_hands_out: Lie with front legs extended
        - forward: Walk forward
        - backward: Walk backward
        - turn_left: Turn left while walking
        - turn_right: Turn right while walking
        - trot: Trot forward (faster gait)
        - stretch: Stretch legs
        - push_up: Do a push-up motion
        - doze_off: Simulate dozing off (leg motion)
        - half_sit: Half-sitting posture

      Head:
        - nod_lethargy: Nod slowly as if sleepy
        - shake_head: Shake head side to side
        - tilting_head_left: Tilt head to the left
        - tilting_head_right: Tilt head to the right
        - tilting_head: Tilt head left and right alternately
        - head_bark: Look up and bark motion
        - head_up_down: Move head up and down

      Tail:
        - wag_tail: Wag the tail back and forth

    Args:
        action_name: Name of the action to perform (see list above).
        step_count: Number of times to repeat the action (default 1).
        speed: Execution speed 0-100 (default 50).
        pitch_comp: Pitch compensation angle for head actions (default 0.0).

    Returns:
        Confirmation or error message.
    """
    dog = _check_pidog()
    try:
        dog.do_action(action_name, step_count=step_count, speed=speed, pitch_comp=pitch_comp)
        return f"Action '{action_name}' queued ({step_count} step(s), speed={speed})."
    except Exception as e:
        return f"Action failed: {e}"


# ---------------------------------------------------------------------------
# Movement tools
# ---------------------------------------------------------------------------
@mcp.tool()
def legs_move(
    target_angles: list,
    immediately: bool = True,
    speed: int = 50,
) -> str:
    """Move the robot legs to specified angles.

    Args:
        target_angles: List of angle lists (each inner list has 8 servo angles for the 4 legs).
        immediately: If True, clear pending leg actions before moving (default True).
        speed: Movement speed 0-100 (default 50).

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.legs_move(target_angles, immediately=immediately, speed=speed)
        return "Leg move command queued."
    except Exception as e:
        return f"Legs move failed: {e}"


@mcp.tool()
def head_move(
    target_yrps: list,
    roll_comp: float = 0.0,
    pitch_comp: float = 0.0,
    immediately: bool = True,
    speed: int = 50,
) -> str:
    """Move the robot head to specified yaw/roll/pitch positions.

    Args:
        target_yrps: List of [yaw, roll, pitch] angle lists.
        roll_comp: Roll compensation angle (default 0.0).
        pitch_comp: Pitch compensation angle (default 0.0).
        immediately: If True, clear pending head actions before moving (default True).
        speed: Movement speed 0-100 (default 50).

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.head_move(
            target_yrps,
            roll_comp=roll_comp,
            pitch_comp=pitch_comp,
            immediately=immediately,
            speed=speed,
        )
        return "Head move command queued."
    except Exception as e:
        return f"Head move failed: {e}"


@mcp.tool()
def head_move_raw(
    target_angles: list,
    immediately: bool = True,
    speed: int = 50,
) -> str:
    """Move the robot head using raw servo angles.

    Args:
        target_angles: List of [yaw_servo, roll_servo, pitch_servo] angle lists.
        immediately: If True, clear pending head actions before moving (default True).
        speed: Movement speed 0-100 (default 50).

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.head_move_raw(target_angles, immediately=immediately, speed=speed)
        return "Head raw move command queued."
    except Exception as e:
        return f"Head raw move failed: {e}"


@mcp.tool()
def tail_move(
    target_angles: list,
    immediately: bool = True,
    speed: int = 50,
) -> str:
    """Move the robot tail to specified angles.

    Args:
        target_angles: List of angle lists for the tail servo.
        immediately: If True, clear pending tail actions before moving (default True).
        speed: Movement speed 0-100 (default 50).

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.tail_move(target_angles, immediately=immediately, speed=speed)
        return "Tail move command queued."
    except Exception as e:
        return f"Tail move failed: {e}"


# ---------------------------------------------------------------------------
# Stop / Wait tools
# ---------------------------------------------------------------------------
@mcp.tool()
def stop_all() -> str:
    """Stop all robot motion (legs, head, and tail).

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.body_stop()
        return "All motion stopped."
    except Exception as e:
        return f"Stop failed: {e}"


@mcp.tool()
def stop_and_lie(speed: int = 85) -> str:
    """Stop all motion and return the robot to a lying-down rest position.

    Args:
        speed: Movement speed 0-100 (default 85).

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.stop_and_lie(speed=speed)
        return "Robot stopped and lying down."
    except Exception as e:
        return f"Stop and lie failed: {e}"


@mcp.tool()
def wait_all_done() -> str:
    """Wait for all pending leg, head, and tail actions to complete.

    Returns:
        Confirmation message when all actions are done.
    """
    dog = _check_pidog()
    try:
        dog.wait_all_done()
        return "All actions completed."
    except Exception as e:
        return f"Wait failed: {e}"


# ---------------------------------------------------------------------------
# Sensor tools
# ---------------------------------------------------------------------------
@mcp.tool()
def read_distance() -> dict:
    """Read the current distance from the ultrasonic sensor.

    Returns:
        Dictionary with distance value in centimeters.
    """
    dog = _check_pidog()
    try:
        dist = dog.read_distance()
        return {"distance_cm": dist}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_battery_voltage() -> dict:
    """Read the current battery voltage.

    Returns:
        Dictionary with battery voltage in volts.
    """
    dog = _check_pidog()
    try:
        voltage = dog.get_battery_voltage()
        return {"battery_voltage_v": voltage}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Audio tools
# ---------------------------------------------------------------------------
@mcp.tool()
def speak(
    name: str,
    volume: int = 100,
) -> str:
    """Play an audio file (non-blocking).

    Args:
        name: Sound file name (without extension) or full file path.
        volume: Volume level 0-100 (default 100).

    Returns:
        Confirmation or error message.
    """
    dog = _check_pidog()
    try:
        result = dog.speak(name, volume=volume)
        if result is False:
            return f"No sound found for '{name}'."
        return f"Playing sound: {name} (volume={volume})."
    except Exception as e:
        return f"Speak failed: {e}"


@mcp.tool()
def speak_block(
    name: str,
    volume: int = 100,
) -> str:
    """Play an audio file (blocking - waits for playback to finish).

    Args:
        name: Sound file name (without extension) or full file path.
        volume: Volume level 0-100 (default 100).

    Returns:
        Confirmation or error message.
    """
    dog = _check_pidog()
    try:
        result = dog.speak_block(name, volume=volume)
        if result is False:
            return f"No sound found for '{name}'."
        return f"Sound '{name}' playback complete."
    except Exception as e:
        return f"Speak block failed: {e}"


# ---------------------------------------------------------------------------
# Calibration tools
# ---------------------------------------------------------------------------
@mcp.tool()
def set_leg_offsets(cali_list: list, reset_list: Optional[list] = None) -> str:
    """Set calibration offsets for the leg servos.

    Args:
        cali_list: List of 8 offset values for the leg servos.
        reset_list: Optional list of 8 angles to reset servos to.

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.set_leg_offsets(cali_list, reset_list=reset_list)
        return "Leg offsets set."
    except Exception as e:
        return f"Set leg offsets failed: {e}"


@mcp.tool()
def set_head_offsets(cali_list: list) -> str:
    """Set calibration offsets for the head servos.

    Args:
        cali_list: List of 3 offset values for yaw, roll, pitch servos.

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.set_head_offsets(cali_list)
        return "Head offsets set."
    except Exception as e:
        return f"Set head offsets failed: {e}"


@mcp.tool()
def set_tail_offset(cali_list: list) -> str:
    """Set calibration offset for the tail servo.

    Args:
        cali_list: List with 1 offset value for the tail servo.

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.set_tail_offset(cali_list)
        return "Tail offset set."
    except Exception as e:
        return f"Set tail offset failed: {e}"


# ---------------------------------------------------------------------------
# Pose / Kinematics tools
# ---------------------------------------------------------------------------
@mcp.tool()
def set_pose(x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> str:
    """Set the robot body pose (position).

    Args:
        x: X position offset (default: current value).
        y: Y position offset (default: current value).
        z: Z height (default: current value).

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.set_pose(x=x, y=y, z=z)
        return "Pose set."
    except Exception as e:
        return f"Set pose failed: {e}"


@mcp.tool()
def set_rpy(
    roll: Optional[float] = None,
    pitch: Optional[float] = None,
    yaw: Optional[float] = None,
    pid: bool = False,
) -> str:
    """Set the robot body orientation (roll/pitch/yaw Euler angles).

    Args:
        roll: Roll angle in degrees (default: current value).
        pitch: Pitch angle in degrees (default: current value).
        yaw: Yaw angle in degrees (default: current value).
        pid: If True, use PID control for smooth adjustment (default False).

    Returns:
        Confirmation message.
    """
    dog = _check_pidog()
    try:
        dog.set_rpy(roll=roll, pitch=pitch, yaw=yaw, pid=pid)
        return "RPY set."
    except Exception as e:
        return f"Set RPY failed: {e}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    """Run the MCP server."""
    host = os.environ.get("PIDOG_MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("PIDOG_MCP_PORT", "8090"))
    mcp.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    main()
