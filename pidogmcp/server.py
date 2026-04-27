from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP(
    "pidogmcp",
    instructions="MCP server for controlling the Sunfounder PiDog robot via the pidog library. "
    "The primary tool is `do_action` which triggers predefined robot actions. "
    "Additional tools provide direct control over legs, head, tail, and robot state.",
)


# ── Available actions (from pidog actions_dictionary.py) ──────────────────
#
#  LEG ACTIONS (body movement via legs):
#    stand          – Stand up on all four legs
#    sit            – Sit down
#    lie            – Lie down (doggy position)
#    lie_with_hands_out  – Lie down with front paws extended forward
#    forward        – Walk forward
#    backward       – Walk backward
#    turn_left      – Turn left
#    turn_right     – Turn right
#    trot           – Trot (faster walk)
#    stretch        – Stretch (extend body forward)
#    push_up        – Push-up exercise
#    doze_off       – Doze off (nodding sleep motion)
#    half_sit       – Half-sit position
#
#  HEAD ACTIONS (yaw / roll / pitch):
#    nod_lethargy   – Nod lethargically (drowsy head bobbing)
#    shake_head     – Shake head side to side
#    tilting_head_left  – Tilt head to the left
#    tilting_head_right – Tilt head to the right
#    tilting_head   – Alternate tilting head left and right
#    head_bark      – Head bark motion (look up)
#    head_up_down   – Move head up and down
#    wag_tail       – Wag tail (mapped to head on some robots)
#
#  NOTES:
#    - Each action has an associated "part" ('legs', 'head', or 'tail')
#      that determines which robot component is affected.
#    - Actions accept parameters: action_name (str), step_count (int,
#      default 1), speed (int, default 50), pitch_comp (float, default 0).
#    - step_count controls how many times the action repeats.
#    - speed controls servo speed (0–100).
#    - pitch_comp adjusts head pitch compensation.

ACTIONS_DESCRIPTION = """\
Available actions for the PiDog robot:

LEG ACTIONS (body/legs movement):
  stand                  – Stand up on all four legs
  sit                    – Sit down
  lie                    – Lie down (doggy position)
  lie_with_hands_out     – Lie down with front paws extended
  forward                – Walk forward
  backward               – Walk backward
  turn_left              – Turn left
  turn_right             – Turn right
  trot                   – Trot (faster walk)
  stretch                – Stretch body forward
  push_up                – Push-up exercise
  doze_off               – Doze off (nodding sleep motion)
  half_sit               – Half-sit position

HEAD ACTIONS (head movement):
  nod_lethargy           – Nod lethargically (drowsy head bobbing)
  shake_head             – Shake head side to side
  tilting_head_left      – Tilt head to the left
  tilting_head_right     – Tilt head to the right
  tilting_head           – Alternate tilting head left and right
  head_bark              – Head bark motion (look up)
  head_up_down           – Move head up and down
  wag_tail               – Wag tail motion

All actions accept: action_name (str), step_count (int, default 1),
speed (int, default 50), pitch_comp (float, default 0).
"""


# ── Tool: do_action ──────────────────────────────────────────────────────
@mcp.tool(
    description=(
        "Execute a predefined PiDog robot action. "
        + ACTIONS_DESCRIPTION
    ),
)
def do_action(
    action_name: str = "sit",
    step_count: int = 1,
    speed: int = 50,
    pitch_comp: float = 0,
) -> str:
    """Execute a predefined PiDog robot action by name."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.do_action(action_name, step_count=step_count, speed=speed, pitch_comp=pitch_comp)
        dog.wait_all_done()
        dog.close()
        return (
            f"Action '{action_name}' executed successfully "
            f"(steps={step_count}, speed={speed}, pitch_comp={pitch_comp})."
        )
    except Exception as e:
        return f"Error executing action '{action_name}': {e}"


# ── Tool: get_battery_voltage ────────────────────────────────────────────
@mcp.tool(
    description="Get the current battery voltage of the PiDog robot in volts."
)
def get_battery_voltage() -> str:
    """Return the PiDog battery voltage."""
    try:
        from pidog import Pidog

        dog = Pidog()
        voltage = dog.get_battery_voltage()
        dog.close()
        return f"Battery voltage: {voltage} V"
    except Exception as e:
        return f"Error reading battery voltage: {e}"


# ── Tool: get_distance ───────────────────────────────────────────────────
@mcp.tool(
    description="Read the ultrasonic distance sensor value (in cm) from the PiDog robot."
)
def get_distance() -> str:
    """Return the ultrasonic distance reading."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.sensory_process_start()
        import time

        time.sleep(0.1)
        distance = dog.read_distance()
        dog.close_all_thread()
        dog.close()
        return f"Distance: {distance} cm"
    except Exception as e:
        return f"Error reading distance sensor: {e}"


# ── Tool: get_imu_data ───────────────────────────────────────────────────
@mcp.tool(
    description="Get the current IMU (Inertial Measurement Unit) data including acceleration and gyroscope readings from the PiDog robot."
)
def get_imu_data() -> str:
    """Return IMU acceleration and gyroscope data."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog._imu_thread()  # trigger one read cycle
        acc = dog.accData
        gyro = dog.gyroData
        dog.close_all_thread()
        dog.close()
        return f"IMU – Accel: [{acc[0]:.2f}, {acc[1]:.2f}, {acc[2]:.2f}] g, Gyro: [{gyro[0]:.2f}, {gyro[1]:.2f}, {gyro[2]:.2f}] deg/s"
    except Exception as e:
        return f"Error reading IMU data: {e}"


# ── Tool: set_legs_speed ─────────────────────────────────────────────────
@mcp.tool(
    description="Set the speed of the PiDog robot's leg servos. Speed range: 0–100 (higher = faster)."
)
def set_legs_speed(speed: int = 50) -> str:
    """Set leg servo speed (0–100)."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.legs_speed = speed
        dog.close()
        return f"Legs speed set to: {speed}"
    except Exception as e:
        return f"Error setting legs speed: {e}"


# ── Tool: set_head_speed ─────────────────────────────────────────────────
@mcp.tool(
    description="Set the speed of the PiDog robot's head servos. Speed range: 0–100 (higher = faster)."
)
def set_head_speed(speed: int = 50) -> str:
    """Set head servo speed (0–100)."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.head_speed = speed
        dog.close()
        return f"Head speed set to: {speed}"
    except Exception as e:
        return f"Error setting head speed: {e}"


# ── Tool: set_tail_speed ─────────────────────────────────────────────────
@mcp.tool(
    description="Set the speed of the PiDog robot's tail servo. Speed range: 0–100 (higher = faster)."
)
def set_tail_speed(speed: int = 50) -> str:
    """Set tail servo speed (0–100)."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.tail_speed = speed
        dog.close()
        return f"Tail speed set to: {speed}"
    except Exception as e:
        return f"Error setting tail speed: {e}"


# ── Tool: set_body_height ────────────────────────────────────────────────
@mcp.tool(
    description="Set the body height of the PiDog robot. Height range: 20–95 (higher = taller)."
)
def set_body_height(height: int = 80) -> str:
    """Set the robot body height (20–95)."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.body_height = height
        dog.close()
        return f"Body height set to: {height}"
    except Exception as e:
        return f"Error setting body height: {e}"


# ── Tool: stop_robot ─────────────────────────────────────────────────────
@mcp.tool(
    description="Stop all PiDog robot movements and return to the initial lying position."
)
def stop_robot() -> str:
    """Stop all robot movements and return to initial position."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.stop_and_lie(speed=85)
        dog.close()
        return "Robot stopped and returned to initial lying position."
    except Exception as e:
        return f"Error stopping robot: {e}"


# ── Tool: play_sound ─────────────────────────────────────────────────────
@mcp.tool(
    description="Play a sound effect on the PiDog robot. Provide the sound file name (without extension) from the robot's sound library."
)
def play_sound(name: str = "pant", volume: int = 100) -> str:
    """Play a sound effect on the PiDog robot."""
    try:
        from pidog import Pidog

        dog = Pidog()
        result = dog.speak(name, volume=volume)
        dog.close()
        if result is False:
            return f"Sound '{name}' not found."
        return f"Playing sound '{name}' at volume {volume}."
    except Exception as e:
        return f"Error playing sound '{name}': {e}"


# ── Tool: set_rgb_color ──────────────────────────────────────────────────
@mcp.tool(
    description="Set the RGB LED strip color on the PiDog robot. Use color names like 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'white', 'black' (off)."
)
def set_rgb_color(color: str = "green", mode: str = "breath", bps: float = 1.0) -> str:
    """Set the RGB LED strip color and mode on the PiDog robot."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.rgb_strip.set_mode(mode, color=color, bps=bps)
        dog.close()
        return f"RGB LED set to '{color}' in '{mode}' mode at {bps} bps."
    except Exception as e:
        return f"Error setting RGB color: {e}"


# ── Tool: direct_legs_move ───────────────────────────────────────────────
@mcp.tool(
    description="Directly move the PiDog robot's legs to specified angles. Provide a list of 8 servo angles [lf_leg, lf_foot, rf_leg, rf_foot, lb_leg, lb_foot, rb_leg, rb_foot]. Each angle is in degrees."
)
def direct_legs_move(angles: list = None, speed: int = 50) -> str:
    """Directly set leg servo angles (8 values)."""
    try:
        from pidog import Pidog

        if angles is None:
            angles = [0] * 8

        dog = Pidog()
        dog.legs_move(angles, immediately=True, speed=speed)
        dog.wait_legs_done()
        dog.close()
        return f"Legs moved to angles: {angles} (speed={speed})"
    except Exception as e:
        return f"Error moving legs: {e}"


# ── Tool: direct_head_move ───────────────────────────────────────────────
@mcp.tool(
    description="Directly move the PiDog robot's head. Provide yaw, roll, pitch angles as a list [yaw, roll, pitch]. Each angle is in degrees."
)
def direct_head_move(angles: list = None, speed: int = 50) -> str:
    """Directly set head servo angles [yaw, roll, pitch]."""
    try:
        from pidog import Pidog

        if angles is None:
            angles = [0, 0, 45]  # default pitch offset

        dog = Pidog()
        dog.head_move_raw(angles, immediately=True, speed=speed)
        dog.wait_head_done()
        dog.close()
        return f"Head moved to angles: {angles} (speed={speed})"
    except Exception as e:
        return f"Error moving head: {e}"


# ── Tool: direct_tail_move ───────────────────────────────────────────────
@mcp.tool(
    description="Directly move the PiDog robot's tail. Provide a list with 1 servo angle in degrees."
)
def direct_tail_move(angles: list = None, speed: int = 50) -> str:
    """Directly set tail servo angle (1 value)."""
    try:
        from pidog import Pidog

        if angles is None:
            angles = [0]

        dog = Pidog()
        dog.tail_move(angles, immediately=True, speed=speed)
        dog.wait_tail_done()
        dog.close()
        return f"Tail moved to angles: {angles} (speed={speed})"
    except Exception as e:
        return f"Error moving tail: {e}"


# ── Tool: reset_robot ────────────────────────────────────────────────────
@mcp.tool(
    description="Reset the PiDog robot to its initial position (lie down) and close all threads cleanly."
)
def reset_robot() -> str:
    """Reset the robot to initial position and close all threads."""
    try:
        from pidog import Pidog

        dog = Pidog()
        dog.stop_and_lie(speed=85)
        dog.close()
        return "Robot reset to initial position and all threads closed."
    except Exception as e:
        return f"Error resetting robot: {e}"


# ── Tool: list_actions ───────────────────────────────────────────────────
@mcp.tool(
    description="List all available PiDog robot actions with their descriptions."
)
def list_actions() -> str:
    """Return a formatted list of all available robot actions."""
    return ACTIONS_DESCRIPTION


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


# ── Main entry point ─────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
