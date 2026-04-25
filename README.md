# PiDog HTTP FastMCP Wrapper

This project exposes the SunFounder `Pidog` robot API as a remote MCP server over HTTP.

The wrapper is implemented in [main.py](main.py) using `FastMCP` with `streamable-http` transport.

## Available Tools

### Connection / Lifecycle
| Tool | Description |
|------|-------------|
| `pidog_connect` | Initialise / connect to PiDog hardware (optional custom pin mappings) |
| `pidog_disconnect` | Shut down all threads and disconnect |
| `pidog_status` | Return current connection status |

### Pre-defined Actions
| Tool | Description |
|------|-------------|
| `do_action` | Execute a named action (stand, sit, lie, forward, backward, turn_left, turn_right, trot, stretch, push_up, doze_off, nod_lethargy, shake_head, tilting_head, head_bark, wag_tail, head_up_down, half_sit, ...) |

### Legs
| Tool | Description |
|------|-------------|
| `legs_move` | Move legs to target angle frames |
| `legs_stop` | Clear leg action buffer and stop |

### Head
| Tool | Description |
|------|-------------|
| `head_move` | Move head by Yaw/Roll/Pitch angles |
| `head_move_raw` | Move head by raw servo angles |
| `head_stop` | Clear head action buffer and stop |

### Tail
| Tool | Description |
|------|-------------|
| `tail_move` | Move tail to target angle |
| `tail_stop` | Clear tail action buffer and stop |

### Body
| Tool | Description |
|------|-------------|
| `body_stop` | Stop all body movement (legs + head + tail) |
| `stop_and_lie` | Stop and return to lying-down position |
| `wait_all_done` | Block until all pending actions complete |

### Posture / Kinematics
| Tool | Description |
|------|-------------|
| `set_pose` | Set body position (x, y, z) |
| `set_rpy` | Set body rotation (roll, pitch, yaw) with optional PID control |
| `pose2coords` | Calculate target leg/body coordinates from current pose |
| `pose2legs_angle` | Calculate target leg angles from current pose |

### Sensors
| Tool | Description |
|------|-------------|
| `read_distance` | Read ultrasonic distance sensor (cm) |
| `get_battery_voltage` | Read battery voltage (V) |
| `get_imu_data` | Read IMU accelerometer, gyroscope, pitch, and roll |

### Audio
| Tool | Description |
|------|-------------|
| `speak` | Play a sound file (blocking or non-blocking) |

### Calibration
| Tool | Description |
|------|-------------|
| `set_leg_offsets` | Set calibration offsets for 8 leg servos |
| `set_head_offsets` | Set calibration offsets for 3 head servos |
| `set_tail_offset` | Set calibration offset for tail servo |

### Status
| Tool | Description |
|------|-------------|
| `is_all_done` | Check whether all pending actions have completed |

## Run

1. Install dependencies:

```powershell
uv sync
```

2. Start MCP server:

```powershell
uv run main.py
```

The server listens on:

- host: `PIDOG_MCP_HOST` (default `0.0.0.0`)
- port: `PIDOG_MCP_PORT` (default `8000`)

So the MCP endpoint is available at:

- `http://localhost:8000/mcp`

## Usage notes

- Call `pidog_connect` before issuing movement/sensor tools.
- Most movement tools provide `wait` to block until actions complete.
- If the `pidog` package or hardware stack is unavailable, connection will fail with a clear runtime error.
- Use `pidog_disconnect` to shut down robot threads cleanly.

