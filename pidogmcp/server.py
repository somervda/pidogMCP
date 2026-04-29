#!/usr/bin/env python3
"""
FastMCP server that wraps the pidog robot API.
Provides remote access to pidog functionality via MCP tools and resources.
"""

import os
import sys
import asyncio
from typing import Any, Optional
from enum import Enum

from mcp.server.fastmcp import FastMCP

# Try to import pidog, fall back to mock mode if not available
try:
    from pidog import Pidog
    PIDOG_AVAILABLE = True
except ImportError:
    PIDOG_AVAILABLE = False
    print("Warning: pidog module not available. Running in mock mode.", file=sys.stderr)

# Configuration
MCP_HOST = os.getenv("PIDOG_MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("PIDOG_MCP_PORT", "8080"))

# Global pidog instance
pidog_instance: Optional[Any] = None


def get_pidog() -> Optional[Any]:
    """Get or create the global pidog instance."""
    global pidog_instance
    if pidog_instance is None and PIDOG_AVAILABLE:
        try:
            pidog_instance = Pidog()
        except Exception as e:
            print(f"Error initializing Pidog: {e}", file=sys.stderr)
            return None
    return pidog_instance


def cleanup_pidog():
    """Clean up the pidog instance."""
    global pidog_instance
    if pidog_instance is not None:
        try:
            pidog_instance.close()
        except Exception as e:
            print(f"Error closing Pidog: {e}", file=sys.stderr)
        pidog_instance = None


# Create FastMCP server
server = FastMCP("Pidog MCP Server")


@server.tool()
def do_action(
    action_name: str,
    step_count: int = 1,
    speed: int = 50,
    pitch_comp: int = 0,
) -> dict:
    """
    Execute a predefined action on the Pidog robot.
    
    Valid action names:
    - stand: Stand upright
    - sit: Sit down
    - lie: Lie flat on the ground
    - lie_with_hands_out: Lie down with front legs extended
    - forward: Walk forward
    - backward: Walk backward
    - turn_left: Turn left while moving forward
    - turn_right: Turn right while moving forward
    - trot: Fast trotting gait
    - stretch: Stretch the body
    - push_up: Do push-ups
    - doze_off: Doze off with nodding head
    - nod_lethargy: Nod head with lethargy
    - shake_head: Shake head left and right
    - tilting_head_left: Tilt head to the left
    - tilting_head_right: Tilt head to the right
    - tilting_head: Tilt head left and right repeatedly
    - head_bark: Raise head and bark position
    - wag_tail: Wag tail
    - head_up_down: Move head up and down
    - half_sit: Half-sitting position
    
    Args:
        action_name: Name of the action to perform
        step_count: Number of times to repeat the action (default: 1)
        speed: Speed of movement 0-100 (default: 50)
        pitch_comp: Pitch compensation in degrees (default: 0)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available. Running in mock mode.",
            "action": action_name,
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
            "action": action_name,
        }
    
    try:
        pidog.do_action(action_name, step_count=step_count, speed=speed, pitch_comp=pitch_comp)
        return {
            "status": "success",
            "message": f"Action '{action_name}' executed successfully",
            "action": action_name,
            "steps": step_count,
            "speed": speed,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing action: {str(e)}",
            "action": action_name,
        }


@server.tool()
def move_legs(
    angles: list[float],
    speed: int = 50,
    immediately: bool = True,
) -> dict:
    """
    Move the legs to specified angles.
    
    Args:
        angles: List of 8 angles for the 4 legs (leg_angle, foot_angle for each)
        speed: Speed of movement 0-100 (default: 50)
        immediately: Stop current movement and move immediately (default: True)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        pidog.legs_move(angles, speed=speed, immediately=immediately)
        return {
            "status": "success",
            "message": "Legs moved successfully",
            "angles": angles,
            "speed": speed,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error moving legs: {str(e)}",
        }


@server.tool()
def move_head(
    target_yrps: list[list[float]],
    speed: int = 50,
    immediately: bool = True,
    roll_comp: int = 0,
    pitch_comp: int = 0,
) -> dict:
    """
    Move the head to specified yaw, roll, pitch positions.
    
    Args:
        target_yrps: List of [yaw, roll, pitch] positions (in degrees)
        speed: Speed of movement 0-100 (default: 50)
        immediately: Stop current movement and move immediately (default: True)
        roll_comp: Roll compensation (default: 0)
        pitch_comp: Pitch compensation (default: 0)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        pidog.head_move(target_yrps, speed=speed, immediately=immediately, roll_comp=roll_comp, pitch_comp=pitch_comp)
        return {
            "status": "success",
            "message": "Head moved successfully",
            "positions": target_yrps,
            "speed": speed,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error moving head: {str(e)}",
        }


@server.tool()
def move_tail(
    target_angles: list[list[float]],
    speed: int = 50,
    immediately: bool = True,
) -> dict:
    """
    Move the tail to specified angles.
    
    Args:
        target_angles: List of tail angles
        speed: Speed of movement 0-100 (default: 50)
        immediately: Stop current movement and move immediately (default: True)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        pidog.tail_move(target_angles, speed=speed, immediately=immediately)
        return {
            "status": "success",
            "message": "Tail moved successfully",
            "angles": target_angles,
            "speed": speed,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error moving tail: {str(e)}",
        }


@server.tool()
def stop_movement() -> dict:
    """
    Stop all current movement (legs, head, and tail).
    
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        pidog.body_stop()
        return {
            "status": "success",
            "message": "All movement stopped",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error stopping movement: {str(e)}",
        }


@server.tool()
def wait_movement_done() -> dict:
    """
    Wait until all current movement (legs, head, and tail) is complete.
    
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        pidog.wait_all_done()
        return {
            "status": "success",
            "message": "All movement completed",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error waiting for movement: {str(e)}",
        }


@server.tool()
def is_movement_done() -> dict:
    """
    Check if all current movement is complete.
    
    Returns:
        Dictionary with status and result message including is_done flag
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
            "is_done": False,
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
            "is_done": False,
        }
    
    try:
        is_done = pidog.is_all_done()
        return {
            "status": "success",
            "is_done": is_done,
            "legs_done": pidog.is_legs_done(),
            "head_done": pidog.is_head_done(),
            "tail_done": pidog.is_tail_done(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking movement status: {str(e)}",
            "is_done": False,
        }


@server.tool()
def set_body_pose(x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> dict:
    """
    Set the body pose (position) in 3D space.
    
    Args:
        x: X coordinate (optional)
        y: Y coordinate (optional)
        z: Z coordinate/height (optional)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        pidog.set_pose(x=x, y=y, z=z)
        return {
            "status": "success",
            "message": "Body pose set successfully",
            "x": x,
            "y": y,
            "z": z,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error setting body pose: {str(e)}",
        }


@server.tool()
def set_body_rotation(roll: Optional[float] = None, pitch: Optional[float] = None, yaw: Optional[float] = None) -> dict:
    """
    Set the body rotation (roll, pitch, yaw).
    
    Args:
        roll: Roll angle in degrees (optional)
        pitch: Pitch angle in degrees (optional)
        yaw: Yaw angle in degrees (optional)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        pidog.set_rpy(roll=roll, pitch=pitch, yaw=yaw)
        return {
            "status": "success",
            "message": "Body rotation set successfully",
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error setting body rotation: {str(e)}",
        }


@server.tool()
def get_battery_voltage() -> dict:
    """
    Get the current battery voltage.
    
    Returns:
        Dictionary with status and battery voltage in volts
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
            "voltage": None,
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
            "voltage": None,
        }
    
    try:
        voltage = pidog.get_battery_voltage()
        return {
            "status": "success",
            "voltage": voltage,
            "unit": "volts",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading battery voltage: {str(e)}",
            "voltage": None,
        }


@server.tool()
def get_distance() -> dict:
    """
    Get the current distance reading from the ultrasonic sensor (if available).
    
    Returns:
        Dictionary with status and distance in centimeters
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
            "distance": None,
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
            "distance": None,
        }
    
    try:
        distance = pidog.read_distance()
        return {
            "status": "success",
            "distance": distance,
            "unit": "cm",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading distance: {str(e)}",
            "distance": None,
        }


@server.tool()
def get_imu_data() -> dict:
    """
    Get the current IMU (accelerometer and gyroscope) data.
    
    Returns:
        Dictionary with accelerometer and gyroscope readings
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
            "data": None,
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
            "data": None,
        }
    
    try:
        acc_data = pidog.accData
        gyro_data = pidog.gyroData
        return {
            "status": "success",
            "accelerometer": {
                "x": acc_data[0],
                "y": acc_data[1],
                "z": acc_data[2],
            },
            "gyroscope": {
                "x": gyro_data[0],
                "y": gyro_data[1],
                "z": gyro_data[2],
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading IMU data: {str(e)}",
            "data": None,
        }


@server.tool()
def speak(name: str, volume: int = 100) -> dict:
    """
    Play an audio file from the sound directory (non-blocking).
    
    Args:
        name: Filename (without extension) or full path to audio file
        volume: Volume level 0-100 (default: 100)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        result = pidog.speak(name, volume=volume)
        if result is False:
            return {
                "status": "error",
                "message": f"Audio file not found: {name}",
            }
        return {
            "status": "success",
            "message": f"Playing audio: {name}",
            "volume": volume,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error playing audio: {str(e)}",
        }


@server.tool()
def speak_block(name: str, volume: int = 100) -> dict:
    """
    Play an audio file from the sound directory (blocking until complete).
    
    Args:
        name: Filename (without extension) or full path to audio file
        volume: Volume level 0-100 (default: 100)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        result = pidog.speak_block(name, volume=volume)
        if result is False:
            return {
                "status": "error",
                "message": f"Audio file not found: {name}",
            }
        return {
            "status": "success",
            "message": f"Audio playback completed: {name}",
            "volume": volume,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error playing audio: {str(e)}",
        }


@server.tool()
def reset_to_lie_position(speed: int = 85) -> dict:
    """
    Stop all movement and return to the lying position.
    
    Args:
        speed: Speed of movement 0-100 (default: 85)
        
    Returns:
        Dictionary with status and result message
    """
    if not PIDOG_AVAILABLE:
        return {
            "status": "error",
            "message": "Pidog module not available",
        }
    
    pidog = get_pidog()
    if pidog is None:
        return {
            "status": "error",
            "message": "Failed to initialize Pidog",
        }
    
    try:
        pidog.stop_and_lie(speed=speed)
        return {
            "status": "success",
            "message": "Robot stopped and returned to lying position",
            "speed": speed,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error resetting position: {str(e)}",
        }


@server.resource("status")
def get_status() -> str:
    """
    Get the current status of the Pidog server.
    
    Returns:
        Plain text status information
    """
    if not PIDOG_AVAILABLE:
        return "PidogMCP Status\n===============\nMode: Mock (Pidog module not available)\nPort: {}\nHost: {}".format(MCP_PORT, MCP_HOST)
    
    pidog = get_pidog()
    if pidog is None:
        return "PidogMCP Status\n===============\nMode: Initialized but failed to create instance\nPort: {}\nHost: {}".format(MCP_PORT, MCP_HOST)
    
    try:
        battery = pidog.get_battery_voltage()
        distance = pidog.read_distance()
        is_done = pidog.is_all_done()
        
        status = f"""PidogMCP Status
===============
Mode: Active
Port: {MCP_PORT}
Host: {MCP_HOST}
Battery Voltage: {battery}V
Distance: {distance}cm
Movement Done: {is_done}
"""
        return status
    except Exception as e:
        return f"PidogMCP Status\n===============\nMode: Active but with errors\nPort: {MCP_PORT}\nHost: {MCP_HOST}\nError: {str(e)}"


def main():
    """Main entry point for the FastMCP server."""
    print(f"Starting PidogMCP server on {MCP_HOST}:{MCP_PORT}")
    print(f"Pidog module available: {PIDOG_AVAILABLE}")
    
    # Start the server
    import uvicorn
    try:
        uvicorn.run(
            server.asgi(),
            host=MCP_HOST,
            port=MCP_PORT,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
        cleanup_pidog()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        cleanup_pidog()
        sys.exit(1)


if __name__ == "__main__":
    main()
