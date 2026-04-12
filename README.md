# Pidog HTTP FastMCP Wrapper

This project exposes the SunFounder `Pidog` API as a remote MCP server over HTTP.

The wrapper is implemented in [main.py](main.py) using `FastMCP` with `streamable-http` transport.

## What is wrapped

The service focuses on the primary control and sensor methods from `pidog.py`:

- Connection lifecycle: `pidog_connect`, `pidog_disconnect`, `pidog_status`
- Action/motion: `do_action`, `legs_move`, `head_move`, `head_move_raw`, `tail_move`, `stop_and_lie`, `wait_all_done`
- Audio: `speak`
- Kinematics/posture: `set_pose`, `set_rpy`, `pose2coords`, `pose2legs_angle`
- Sensors: `read_distance`, `get_battery_voltage`

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

