#!/usr/bin/env python3
"""
Pidog MCP Server — wraps the SunFounder Pidog robot API via FastMCP (streamable-http).

Provides tools for:
  - Connection lifecycle (connect / disconnect / status)
  - Actions & movement (do_action, legs/head/tail move, stop)
  - Posture & kinematics (set_pose, set_rpy, pose2coords, pose2legs_angle)
  - Sensors (read_distance, get_battery_voltage, imu_data)
  - Audio (speak)
  - Calibration (set_leg_offsets, set_head_offsets, set_tail_offset)
"""

import os
import sys
import time
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Module-level singleton so tools share the same Pidog instance
# ---------------------------------------------------------------------------
_pidog_instance = None


def _get_pidog():
    """Return the current Pidog instance, raising if not connected."""
    global _pidog_instance
    if _pidog_instance is None:
        raise RuntimeError(
            "Pidog not connected. Call `pidog_connect` first."
        )
    return _pidog_instance


# ---------------------------------------------------------------------------
# FastMCP server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "pidog-mcp",
    instructions="Control a SunFounder PiDog robot. Call `pidog_connect` before using any other tool.",
)


# ===================================================================
# Connection / Lifecycle
# ===================================================================

@mcp.tool()
def pidog_connect(
    leg_pins: Optional[str] = None,
    head_pins: Optional[str] = None,
    tail_pin: Optional[str] = None,
) -> str:
    """Connect to / initialise the PiDog hardware.

    Args:
        leg_pins: Comma-separated leg servo pin numbers (default: 2,3,7,8,0,1,10,11).
        head_pins: Comma-separated head servo pin numbers (default: 4,6,5).
        tail_pin: Comma-separated tail servo pin number (default: 9).

    Returns:
        Confirmation message.
    """
    global _pidog_instance

    # Parse optional pin lists
    kw = {}
    if leg_pins:
        kw["leg_pins"] = [int(p) for p in leg_pins.split(",")]
    if head_pins:
        kw["head_pins"] = [int(p) for p in head_pins.split(",")]
    if tail_pin:
        kw["tail_pin"] = [int(p) for p in tail_pin.split(",")]

    try:
        from pidog.pidog import Pidog

        if _pidog_instance is not None:
            try:
                _pidog_instance.close()
            except Exception:
                pass

        _pidog_instance = Pidog(**kw)
        return "PiDog connected successfully."
    except ImportError:
        raise RuntimeError(
            "The `pidog` package is not installed. "
            "Install it with: pip install pidog  (or clone from GitHub)."
        )
    except OSError as e:
        raise RuntimeError(f"I2C / hardware initialisation failed: {e}")


@mcp.tool()
def pidog_disconnect() -> str:
    """Disconnect and cleanly shut down all PiDog threads."""
    global _pidog_instance
    if _pidog_instance is None:
        return "PiDog was not connected."
    try:
        _pidog_instance.close()
    except Exception as e:
        return f"Warning: error during disconnect: {e}"
    finally:
        _pidog_instance = None
    return "PiDog disconnected."


@mcp.tool()
def pidog_status() -> dict:
    """Return the current connection status of the PiDog."""
    return {"connected": _pidog_instance is not None}


# ===================================================================
# Actions (pre-defined)
# ===================================================================

@mcp.tool()
def do_action(
    action_name: str,
    step_count: int = 1,
    speed: int = 50,
    pitch_comp: float = 0.0,
    wait: bool = True,
) -> str:
    """Execute a pre-defined PiDog action by name.

    Available actions include:
      stand, sit, lie, lie_with_hands_out, forward, backward,
      turn_left, turn_right, trot, stretch, push_up, doze_off,
      nod_lethargy, shake_head, tilting_head_left, tilting_head_right,
      tilting_head, head_bark, wag_tail, head_up_down, half_sit

    Args:
        action_name: Name of the action to perform.
        step_count: Number of times to repeat the action.
        speed: Movement speed (0-100).
        pitch_comp: Pitch compensation offset for head actions.
        wait: If True, block until the action completes.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    dog.do_action(action_name, step_count=step_count, speed=speed, pitch_comp=pitch_comp)
    if wait:
        dog.wait_all_done()
    return f"Action '{action_name}' executed ({step_count} step(s))."


# ===================================================================
# Legs
# ===================================================================

@mcp.tool()
def legs_move(
    angles: str,
    speed: int = 50,
    immediately: bool = True,
    wait: bool = True,
) -> str:
    """Move the PiDog legs to target angles.

    Args:
        angles: Comma-separated list of angle frames. Each frame is 8 angles
            (leg1_joint1, leg1_joint2, …, leg4_joint2) separated by semicolons.
            Example: "10,20,-10,-20,30,40,-30,-40" for a single frame,
            or "10,20,-10,-20,30,40,-30,-40;15,25,-15,-25,35,45,-35,-45" for two frames.
        speed: Movement speed (0-100).
        immediately: If True, clear the existing action buffer first.
        wait: If True, block until leg movement completes.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    frames = angles.split(";")
    target = [[float(a) for a in f.split(",")] for f in frames]
    dog.legs_move(target, immediately=immediately, speed=speed)
    if wait:
        dog.wait_legs_done()
    return f"Legs moved to {len(frames)} frame(s)."


@mcp.tool()
def legs_stop() -> str:
    """Stop all leg movement immediately."""
    dog = _get_pidog()
    dog.legs_stop()
    return "Legs stopped."


# ===================================================================
# Head
# ===================================================================

@mcp.tool()
def head_move(
    yaw: float,
    roll: float,
    pitch: float,
    roll_comp: float = 0.0,
    pitch_comp: float = 0.0,
    speed: int = 50,
    immediately: bool = True,
    wait: bool = True,
) -> str:
    """Move the PiDog head to target Yaw/Roll/Pitch angles.

    Args:
        yaw: Yaw angle in degrees (-90 to 90).
        roll: Roll angle in degrees (-70 to 70).
        pitch: Pitch angle in degrees (-45 to 30).
        roll_comp: Roll compensation offset.
        pitch_comp: Pitch compensation offset.
        speed: Movement speed (0-100).
        immediately: If True, clear the existing action buffer first.
        wait: If True, block until head movement completes.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    dog.head_move(
        [[yaw, roll, pitch]],
        roll_comp=roll_comp,
        pitch_comp=pitch_comp,
        immediately=immediately,
        speed=speed,
    )
    if wait:
        dog.wait_head_done()
    return f"Head moved to yaw={yaw}, roll={roll}, pitch={pitch}."


@mcp.tool()
def head_move_raw(
    yaw: float,
    roll: float,
    pitch: float,
    speed: int = 50,
    immediately: bool = True,
    wait: bool = True,
) -> str:
    """Move the PiDog head using raw servo angles (no YRP conversion).

    Args:
        yaw: Raw yaw servo angle.
        roll: Raw roll servo angle.
        pitch: Raw pitch servo angle.
        speed: Movement speed (0-100).
        immediately: If True, clear the existing action buffer first.
        wait: If True, block until head movement completes.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    dog.head_move_raw([[yaw, roll, pitch]], immediately=immediately, speed=speed)
    if wait:
        dog.wait_head_done()
    return f"Head raw moved to yaw={yaw}, roll={roll}, pitch={pitch}."


@mcp.tool()
def head_stop() -> str:
    """Stop all head movement immediately."""
    dog = _get_pidog()
    dog.head_stop()
    return "Head stopped."


# ===================================================================
# Tail
# ===================================================================

@mcp.tool()
def tail_move(
    angle: float,
    speed: int = 50,
    immediately: bool = True,
    wait: bool = True,
) -> str:
    """Move the PiDog tail to a target angle.

    Args:
        angle: Tail servo angle in degrees.
        speed: Movement speed (0-100).
        immediately: If True, clear the existing action buffer first.
        wait: If True, block until tail movement completes.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    dog.tail_move([[angle]], immediately=immediately, speed=speed)
    if wait:
        dog.wait_tail_done()
    return f"Tail moved to angle={angle}."


@mcp.tool()
def tail_stop() -> str:
    """Stop all tail movement immediately."""
    dog = _get_pidog()
    dog.tail_stop()
    return "Tail stopped."


# ===================================================================
# Body (combined stop / pose)
# ===================================================================

@mcp.tool()
def body_stop() -> str:
    """Stop all body movement (legs + head + tail)."""
    dog = _get_pidog()
    dog.body_stop()
    return "All body movement stopped."


@mcp.tool()
def stop_and_lie(speed: int = 85) -> str:
    """Stop all movement and return the robot to a lying-down position.

    Args:
        speed: Movement speed (0-100).

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    dog.stop_and_lie(speed=speed)
    return "Robot stopped and lying down."


@mcp.tool()
def wait_all_done() -> str:
    """Block until all pending leg, head, and tail actions complete."""
    dog = _get_pidog()
    dog.wait_all_done()
    return "All actions completed."


# ===================================================================
# Posture / Kinematics
# ===================================================================

@mcp.tool()
def set_pose(x: float = 0.0, y: float = 0.0, z: float = 80.0) -> str:
    """Set the body pose (position in 3D space).

    Args:
        x: X offset (lateral).
        y: Y offset (forward/backward).
        z: Z height (body height in mm).

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    dog.set_pose(x=x, y=y, z=z)
    return f"Pose set to x={x}, y={y}, z={z}."


@mcp.tool()
def set_rpy(
    roll: float = 0.0,
    pitch: float = 0.0,
    yaw: float = 0.0,
    pid: bool = False,
) -> str:
    """Set the body rotation (Euler angles).

    Args:
        roll: Roll angle in degrees.
        pitch: Pitch angle in degrees.
        yaw: Yaw angle in degrees.
        pid: If True, use PID control for smooth transition.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    dog.set_rpy(roll=roll, pitch=pitch, yaw=yaw, pid=pid)
    return f"RPY set to roll={roll}, pitch={pitch}, yaw={yaw} (pid={pid})."


@mcp.tool()
def pose2coords() -> dict:
    """Calculate the current target coordinates for legs and body from the current pose.

    Returns:
        Dictionary with 'leg' and 'body' coordinate lists.
    """
    dog = _get_pidog()
    data = dog.pose2coords()
    return {"leg": data["leg"], "body": data["body"]}


@mcp.tool()
def pose2legs_angle() -> list:
    """Calculate the current target leg angles from the current pose.

    Returns:
        List of 8 leg joint angles.
    """
    dog = _get_pidog()
    angles = dog.pose2legs_angle()
    return angles


# ===================================================================
# Sensors
# ===================================================================

@mcp.tool()
def read_distance() -> dict:
    """Read the current ultrasonic distance sensor value.

    Returns:
        Dictionary with distance value in cm.
    """
    dog = _get_pidog()
    dist = dog.read_distance()
    return {"distance_cm": dist}


@mcp.tool()
def get_battery_voltage() -> dict:
    """Read the current battery voltage.

    Returns:
        Dictionary with battery voltage in volts.
    """
    dog = _get_pidog()
    voltage = dog.get_battery_voltage()
    return {"battery_voltage_v": voltage}


@mcp.tool()
def get_imu_data() -> dict:
    """Read the current IMU (accelerometer + gyroscope) data.

    Returns:
        Dictionary with accelerometer (ax, ay, az), gyroscope (gx, gy, gz),
        and computed pitch/roll angles.
    """
    dog = _get_pidog()
    return {
        "accelerometer": {
            "ax": dog.accData[0],
            "ay": dog.accData[1],
            "az": dog.accData[2],
        },
        "gyroscope": {
            "gx": dog.gyroData[0],
            "gy": dog.gyroData[1],
            "gz": dog.gyroData[2],
        },
        "pitch_degrees": round(dog.pitch, 2),
        "roll_degrees": round(dog.roll, 2),
    }


# ===================================================================
# Audio
# ===================================================================

@mcp.tool()
def speak(name: str, volume: int = 100, blocking: bool = False) -> str:
    """Play a sound file on the PiDog speaker.

    Args:
        name: Sound file name (without extension). The server will look for
            .mp3 or .wav in the PiDog sounds directory. You can also pass
            an absolute file path.
        volume: Volume level 0-100.
        blocking: If True, block until playback finishes.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    if blocking:
        result = dog.speak_block(name, volume=volume)
    else:
        result = dog.speak(name, volume=volume)
    if result is False:
        return f"No sound file found for '{name}'."
    return f"Playing sound: {name} (volume={volume})."


# ===================================================================
# Calibration
# ===================================================================

@mcp.tool()
def set_leg_offsets(offsets: str, reset_angles: Optional[str] = None) -> str:
    """Set calibration offsets for leg servos.

    Args:
        offsets: Comma-separated list of 8 offset values (one per leg joint).
        reset_angles: Optional comma-separated list of 8 angles to reset to.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    cali = [float(v) for v in offsets.split(",")]
    rst = None
    if reset_angles:
        rst = [float(v) for v in reset_angles.split(",")]
    dog.set_leg_offsets(cali, reset_list=rst)
    return "Leg offsets updated."


@mcp.tool()
def set_head_offsets(offsets: str) -> str:
    """Set calibration offsets for head servos.

    Args:
        offsets: Comma-separated list of 3 offset values (yaw, roll, pitch).

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    cali = [float(v) for v in offsets.split(",")]
    dog.set_head_offsets(cali)
    return "Head offsets updated."


@mcp.tool()
def set_tail_offset(offset: float) -> str:
    """Set calibration offset for the tail servo.

    Args:
        offset: Tail servo offset value.

    Returns:
        Confirmation message.
    """
    dog = _get_pidog()
    dog.set_tail_offset([offset])
    return f"Tail offset set to {offset}."


# ===================================================================
# Status queries
# ===================================================================

@mcp.tool()
def is_all_done() -> dict:
    """Check whether all pending actions (legs, head, tail) have completed.

    Returns:
        Dictionary with done status for each part and overall.
    """
    dog = _get_pidog()
    return {
        "legs_done": dog.is_legs_done(),
        "head_done": dog.is_head_done(),
        "tail_done": dog.is_tail_done(),
        "all_done": dog.is_all_done(),
    }


# ===================================================================
# Entry point
# ===================================================================

def main():
    host = os.environ.get("PIDOG_MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("PIDOG_MCP_PORT", "8000"))
    print(f"Starting PiDog MCP server on {host}:{port}")
    mcp.run(host=host, port=port, transport="streamable-http")


if __name__ == "__main__":
    main()
