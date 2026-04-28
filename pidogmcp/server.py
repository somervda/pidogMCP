#!/usr/bin/env python3
"""
FastMCP server for wrapping the Sunfounder PiDog robot API.
Runs as an HTTP server on port 8080.
"""

import os
import logging
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import pidog - may not be available in all environments
try:
    from pidog import Pidog
    PIDOG_AVAILABLE = True
except ImportError:
    logger.warning("pidog module not available - server will run in mock mode")
    PIDOG_AVAILABLE = False
    Pidog = None

# Valid action names for the do_action tool
VALID_ACTIONS = [
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
    "nod_lethargy",
    "shake_head",
    "tilting_head_left",
    "tilting_head_right",
    "tilting_head",
    "head_bark",
    "wag_tail",
    "head_up_down",
    "half_sit",
]

# Global pidog instance
pidog_instance: Optional[Any] = None


def get_pidog() -> Any:
    """Get or initialize the pidog instance."""
    global pidog_instance
    if pidog_instance is None:
        if not PIDOG_AVAILABLE:
            raise RuntimeError("pidog module not available")
        pidog_instance = Pidog()
    return pidog_instance


def close_pidog() -> None:
    """Close the pidog instance."""
    global pidog_instance
    if pidog_instance is not None:
        try:
            pidog_instance.close()
        except Exception as e:
            logger.error(f"Error closing pidog: {e}")
        pidog_instance = None


# Create FastMCP server
app = FastMCP("pidog-mcp", "FastMCP server for Sunfounder PiDog robot")


@app.tool()
def do_action(
    action_name: str,
    step_count: int = 1,
    speed: int = 50,
    pitch_comp: int = 0,
) -> str:
    """
    Execute a predefined action on the pidog robot.
    
    Valid actions: stand, sit, lie, lie_with_hands_out, forward, backward, 
    turn_left, turn_right, trot, stretch, push_up, doze_off, nod_lethargy, 
    shake_head, tilting_head_left, tilting_head_right, tilting_head, head_bark, 
    wag_tail, head_up_down, half_sit
    
    Args:
        action_name: Name of the action to perform
        step_count: Number of times to repeat the action
        speed: Speed of movement (0-100)
        pitch_comp: Pitch compensation for head movements
    
    Returns:
        Status message
    """
    if action_name not in VALID_ACTIONS:
        return f"Error: Invalid action '{action_name}'. Valid actions: {', '.join(VALID_ACTIONS)}"
    
    if not PIDOG_AVAILABLE:
        return f"Mock: Would execute action '{action_name}' ({step_count} times) at speed {speed}"
    
    try:
        pidog = get_pidog()
        pidog.do_action(action_name, step_count=step_count, speed=speed, pitch_comp=pitch_comp)
        return f"Successfully executed action '{action_name}' ({step_count} times) at speed {speed}"
    except Exception as e:
        return f"Error executing action: {e}"


@app.tool()
def stop_movement() -> str:
    """Stop all movement on the pidog robot."""
    if not PIDOG_AVAILABLE:
        return "Mock: All movement stopped"
    
    try:
        pidog = get_pidog()
        pidog.body_stop()
        return "Successfully stopped all movement"
    except Exception as e:
        return f"Error stopping movement: {e}"


@app.tool()
def wait_movement_done() -> str:
    """Wait for all current movements to complete."""
    if not PIDOG_AVAILABLE:
        return "Mock: Waited for movement completion"
    
    try:
        pidog = get_pidog()
        pidog.wait_all_done()
        return "All movements completed"
    except Exception as e:
        return f"Error waiting for movement: {e}"


@app.tool()
def is_movement_done() -> str:
    """Check if all movements are complete."""
    if not PIDOG_AVAILABLE:
        return "Mock: Movement is complete"
    
    try:
        pidog = get_pidog()
        is_done = pidog.is_all_done()
        return f"Movement complete: {is_done}"
    except Exception as e:
        return f"Error checking movement status: {e}"


@app.tool()
def move_legs(
    target_angles: list,
    speed: int = 50,
    immediately: bool = True,
) -> str:
    """
    Move the legs to specified angles.
    
    Args:
        target_angles: List of 8 angles for the legs [LF_leg, LF_foot, RF_leg, RF_foot, LH_leg, LH_foot, RH_leg, RH_foot]
        speed: Speed of movement (0-100)
        immediately: Whether to stop current movements first
    
    Returns:
        Status message
    """
    if not PIDOG_AVAILABLE:
        return f"Mock: Legs moved to {target_angles} at speed {speed}"
    
    try:
        pidog = get_pidog()
        pidog.legs_move(target_angles, immediately=immediately, speed=speed)
        return f"Successfully moved legs to {target_angles} at speed {speed}"
    except Exception as e:
        return f"Error moving legs: {e}"


@app.tool()
def move_head(
    target_yrp: list,
    speed: int = 50,
    roll_comp: int = 0,
    pitch_comp: int = 0,
    immediately: bool = True,
) -> str:
    """
    Move the head to specified yaw/roll/pitch angles.
    
    Args:
        target_yrp: [yaw, roll, pitch] angles in degrees
        speed: Speed of movement (0-100)
        roll_comp: Roll compensation
        pitch_comp: Pitch compensation
        immediately: Whether to stop current movements first
    
    Returns:
        Status message
    """
    if not PIDOG_AVAILABLE:
        return f"Mock: Head moved to {target_yrp} at speed {speed}"
    
    try:
        pidog = get_pidog()
        pidog.head_move([target_yrp], roll_comp=roll_comp, pitch_comp=pitch_comp, 
                       immediately=immediately, speed=speed)
        return f"Successfully moved head to {target_yrp} at speed {speed}"
    except Exception as e:
        return f"Error moving head: {e}"


@app.tool()
def move_tail(
    target_angle: int,
    speed: int = 50,
    immediately: bool = True,
) -> str:
    """
    Move the tail to specified angle.
    
    Args:
        target_angle: Tail angle in degrees
        speed: Speed of movement (0-100)
        immediately: Whether to stop current movements first
    
    Returns:
        Status message
    """
    if not PIDOG_AVAILABLE:
        return f"Mock: Tail moved to {target_angle} at speed {speed}"
    
    try:
        pidog = get_pidog()
        pidog.tail_move([[target_angle]], immediately=immediately, speed=speed)
        return f"Successfully moved tail to {target_angle} at speed {speed}"
    except Exception as e:
        return f"Error moving tail: {e}"


@app.tool()
def set_body_pose(
    x: Optional[float] = None,
    y: Optional[float] = None,
    z: Optional[float] = None,
) -> str:
    """
    Set the body pose (position).
    
    Args:
        x: X position (body forward/backward)
        y: Y position (body left/right)
        z: Z position (body height)
    
    Returns:
        Status message
    """
    if not PIDOG_AVAILABLE:
        return f"Mock: Body pose set to x={x}, y={y}, z={z}"
    
    try:
        pidog = get_pidog()
        pidog.set_pose(x=x, y=y, z=z)
        return f"Successfully set body pose to x={x}, y={y}, z={z}"
    except Exception as e:
        return f"Error setting body pose: {e}"


@app.tool()
def set_body_rotation(
    roll: Optional[float] = None,
    pitch: Optional[float] = None,
    yaw: Optional[float] = None,
) -> str:
    """
    Set the body rotation (roll/pitch/yaw).
    
    Args:
        roll: Roll angle in degrees
        pitch: Pitch angle in degrees
        yaw: Yaw angle in degrees
    
    Returns:
        Status message
    """
    if not PIDOG_AVAILABLE:
        return f"Mock: Body rotation set to roll={roll}, pitch={pitch}, yaw={yaw}"
    
    try:
        pidog = get_pidog()
        pidog.set_rpy(roll=roll, pitch=pitch, yaw=yaw)
        return f"Successfully set body rotation to roll={roll}, pitch={pitch}, yaw={yaw}"
    except Exception as e:
        return f"Error setting body rotation: {e}"


@app.tool()
def get_battery_voltage() -> str:
    """Get the battery voltage."""
    if not PIDOG_AVAILABLE:
        return "Mock: Battery voltage 12.0V"
    
    try:
        pidog = get_pidog()
        voltage = pidog.get_battery_voltage()
        return f"Battery voltage: {voltage}V"
    except Exception as e:
        return f"Error getting battery voltage: {e}"


@app.tool()
def get_distance() -> str:
    """Get the ultrasonic distance reading."""
    if not PIDOG_AVAILABLE:
        return "Mock: Distance 50.0cm"
    
    try:
        pidog = get_pidog()
        distance = pidog.read_distance()
        return f"Distance: {distance}cm"
    except Exception as e:
        return f"Error getting distance: {e}"


@app.tool()
def get_imu_data() -> str:
    """Get IMU (accelerometer, gyroscope) data."""
    if not PIDOG_AVAILABLE:
        return "Mock: IMU data unavailable"
    
    try:
        pidog = get_pidog()
        acc = pidog.accData
        gyro = pidog.gyroData
        pitch = pidog.pitch
        roll = pidog.roll
        return (
            f"Accelerometer: {acc}\n"
            f"Gyroscope: {gyro}\n"
            f"Pitch: {pitch}°\n"
            f"Roll: {roll}°"
        )
    except Exception as e:
        return f"Error getting IMU data: {e}"


@app.tool()
def speak(name: str, volume: int = 100) -> str:
    """
    Play a sound asynchronously.
    
    Args:
        name: Name of the sound file (without extension) in the sounds directory
        volume: Volume level (0-100)
    
    Returns:
        Status message
    """
    if not PIDOG_AVAILABLE:
        return f"Mock: Playing sound '{name}' at volume {volume}"
    
    try:
        pidog = get_pidog()
        pidog.speak(name, volume=volume)
        return f"Successfully started playing sound '{name}' at volume {volume}"
    except Exception as e:
        return f"Error playing sound: {e}"


@app.tool()
def speak_block(name: str, volume: int = 100) -> str:
    """
    Play a sound and wait for it to complete.
    
    Args:
        name: Name of the sound file (without extension) in the sounds directory
        volume: Volume level (0-100)
    
    Returns:
        Status message
    """
    if not PIDOG_AVAILABLE:
        return f"Mock: Played sound '{name}' at volume {volume}"
    
    try:
        pidog = get_pidog()
        pidog.speak_block(name, volume=volume)
        return f"Successfully played sound '{name}' at volume {volume}"
    except Exception as e:
        return f"Error playing sound: {e}"


@app.tool()
def list_available_actions() -> str:
    """List all available action names that can be used with do_action tool."""
    return f"Available actions:\n" + "\n".join(f"  - {action}" for action in VALID_ACTIONS)


@app.resource("pidog://status")
def get_status() -> str:
    """Get the current status of the pidog server."""
    if not PIDOG_AVAILABLE:
        return "PiDog MCP Server (mock mode - pidog module not available)"
    
    try:
        pidog = get_pidog()
        voltage = pidog.get_battery_voltage()
        is_done = pidog.is_all_done()
        return (
            f"PiDog MCP Server Status:\n"
            f"  Battery Voltage: {voltage}V\n"
            f"  Movement Complete: {is_done}"
        )
    except Exception as e:
        return f"Error getting status: {e}"


def main():
    """Main entry point for the MCP server."""
    import uvicorn
    
    host = os.getenv("PIDOG_MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PIDOG_MCP_PORT", 8080))
    
    logger.info(f"Starting PiDog MCP server on {host}:{port}")
    logger.info(f"PiDog module available: {PIDOG_AVAILABLE}")
    
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        close_pidog()
    except Exception as e:
        logger.error(f"Error running server: {e}")
        close_pidog()


if __name__ == "__main__":
    main()
