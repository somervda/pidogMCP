from mcp.server.fastmcp import FastMCP
import logging

# We'll try to import Pidog. Since this MCP server is intended to run on the robot,
# we assume the pidog package is installed in the environment.
try:
    from pidog import Pidog
except ImportError:
    # Fallback for development/testing on non-robot machines
    # This allows the server to start even if the hardware library is missing,
    # though tools will fail when called.
    Pidog = None

# Initialize FastMCP server
mcp = FastMCP("pidog")

# Global robot instance
robot = None

def get_robot():
    global robot
    if robot is None:
        if Pidog is None:
            raise RuntimeError("pidog package is not installed. This server must run on a device with pidog hardware support.")
        try:
            robot = Pidog()
        except Exception as e:
            logging.error(f"Failed to initialize Pidog: {e}")
            raise RuntimeError(f"Could not initialize Pidog hardware: {e}")
    return robot

@mcp.tool()
def get_distance() -> float:
    """Returns the current distance from the ultrasonic sensor in meters."""
    return get_robot().read_distance()

@mcp.tool()
def move_legs(angles: list[float], speed: int = 50) -> str:
    """Moves the legs to the specified angles."""
    get_robot().legs_move(angles, speed=speed)
    return "Legs movement command sent."

@mcp.tool()
def move_head(target_yrps: list[list[float]], roll_comp: float = 0, pitch_comp: float = 0, speed: int = 50) -> str:
    """Moves the head to the specified target YRP (Yaw, Roll, Pitch) angles."""
    get_robot().head_move(target_yrps, roll_comp=roll_comp, pitch_comp=pitch_comp, speed=speed)
    return "Head movement command sent."

@mcp.tool()
def move_tail(angles: list[float], speed: int = 50) -> str:
    """Moves the tail to the specified angles."""
    get_robot().tail_move(angles, speed=speed)
    return "Tail movement command sent."

@mcp.tool()
def do_action(action_name: str, step_count: int = 1, speed: int = 50) -> str:
    """Performs a predefined action on the robot (e.g., 'lie', 'walk')."""
    get_robot().do_action(action_name, step_count=step_count, speed=speed)
    return f"Action '{action_name}' command sent."

@mcp.tool()
def speak(name: str, volume: int = 100) -> bool:
    """Plays a sound file by name (without extension)."""
    return get_robot().speak(name, volume=volume)

@mcp.tool()
def get_battery_voltage() -> float:
    """Returns the current battery voltage."""
    return get_robot().get_battery_voltage()

@mcp.tool()
def stop_and_lie(speed: int = 85) -> str:
    """Stops the robot and puts it in a lying position."""
    get_robot().stop_and_lie(speed=speed)
    return "Stop and lie command sent."

if __name__ == "__main__":
    mcp.run()
