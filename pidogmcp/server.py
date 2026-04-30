import os
import threading
from typing import Optional, Literal

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "pidog-mcp",
    instructions=(
        "Remote MCP server that wraps the SunFounder PiDog robot API. "
        "Expose tools to trigger built-in actions, speak sounds, read sensors, and query status."
    ),
    json_response=True,
)


_dog_lock = threading.Lock()
_dog = None  # lazily initialized Pidog instance


def _get_dog():
    global _dog
    with _dog_lock:
        if _dog is None:
            try:
                from pidog.pidog import Pidog  # type: ignore
            except Exception as e:  # pragma: no cover
                raise RuntimeError(
                    "Failed to import 'pidog'. Install and run this on the PiDog device."
                ) from e

            _dog = Pidog()
        return _dog


ActionName = Literal[
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


@mcp.tool()
def do_action(action_name: ActionName, step_count: int = 1, speed: int = 50, pitch_comp: int = 0) -> str:
    """
    Perform a built-in PiDog action animation.

    Valid actions: stand, sit, lie, lie_with_hands_out, forward, backward, turn_left, turn_right, trot, stretch, push_up, doze_off, nod_lethargy, shake_head, tilting_head_left, tilting_head_right, tilting_head, head_bark, wag_tail, head_up_down, half_sit.

    Parameters:
    - action_name: One of the valid action names above.
    - step_count: Number of times to repeat the action (>= 1).
    - speed: Motion speed 0-100 (PiDog default behavior uses ~50-90).
    - pitch_comp: Pitch compensation used by some head actions.
    """
    if step_count < 1:
        raise ValueError("step_count must be >= 1")
    if speed < 0 or speed > 100:
        raise ValueError("speed must be between 0 and 100")

    dog = _get_dog()
    dog.do_action(action_name, step_count=step_count, speed=speed, pitch_comp=pitch_comp)
    return f"action={action_name} repeated={step_count} speed={speed}"


@mcp.tool()
def stop_and_lie(speed: int = 85) -> str:
    """
    Stop ongoing motions and return the robot to a resting "lie" posture.

    Parameters:
    - speed: Motion speed 0-100 while returning to rest.
    """
    if speed < 0 or speed > 100:
        raise ValueError("speed must be between 0 and 100")
    dog = _get_dog()
    dog.stop_and_lie(speed=speed)
    return "stopped and returned to lie posture"


@mcp.tool()
def speak(name: str, volume: int = 100) -> str:
    """
    Play a built-in sound on the PiDog.

    Parameters:
    - name: Sound file base name (e.g., "bark") or absolute path.
    - volume: 0-100 volume percentage.
    """
    if volume < 0 or volume > 100:
        raise ValueError("volume must be between 0 and 100")
    dog = _get_dog()
    ok = dog.speak(name, volume=volume)
    return "sound played" if ok is not False else "no sound found"


@mcp.tool()
def read_distance() -> float:
    """
    Read the latest measured distance from the ultrasonic sensor in centimeters.
    """
    dog = _get_dog()
    return float(dog.read_distance())


@mcp.tool()
def get_battery_voltage() -> float:
    """
    Get the current battery voltage in volts.
    """
    dog = _get_dog()
    return float(dog.get_battery_voltage())


@mcp.tool()
def shutdown() -> str:
    """
    Gracefully stop threads and release PiDog resources for a clean shutdown.
    """
    global _dog
    if _dog is not None:
        try:
            _dog.close()
        finally:
            _dog = None
    return "pidog shutdown complete"


def main() -> None:  # pragma: no cover
    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "0.0.0.0")
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        stateless_http=True,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
