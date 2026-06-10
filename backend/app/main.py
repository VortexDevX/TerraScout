from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import ValidationError

from app.analysis import build_ops_summary
from app.config import settings
from app.mock import mock_observations
from app.protocol import ControlRequest, Envelope, ExecutionResult, MoveToRequest, Observation, TrainingFeedback, envelope
from app.runtime import DashboardHub, RuntimeState
from app.storage import EventStore
from app.training import build_training_examples, examples_to_jsonl, summarize_examples

store = EventStore(settings.db_path)
runtime = RuntimeState(store)
hub = DashboardHub()
mock_task: asyncio.Task[None] | None = None


async def _dashboard_broadcast_loop() -> None:
    while True:
        await hub.broadcast(await runtime.snapshot())
        await asyncio.sleep(settings.dashboard_interval_ms / 1000)


async def _mock_loop() -> None:
    async for observation in mock_observations(settings.observation_interval_ms):
        await runtime.handle_observation(observation, connection_status="mock_connected")


def _start_mock_task() -> bool:
    global mock_task
    if mock_task and not mock_task.done():
        return False
    mock_task = asyncio.create_task(_mock_loop())
    return True


def _stop_mock_task() -> bool:
    global mock_task
    if not mock_task or mock_task.done():
        return False
    mock_task.cancel()
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    dashboard_task = asyncio.create_task(_dashboard_broadcast_loop())
    if settings.mock_mode:
        _start_mock_task()
    try:
        yield
    finally:
        dashboard_task.cancel()
        _stop_mock_task()
        tasks = [dashboard_task]
        if mock_task:
            tasks.append(mock_task)
        for task in tasks:
            with suppress(asyncio.CancelledError):
                await task


app = FastAPI(title="TerraScout Backend", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "protocol_version": settings.protocol_version}


@app.get("/telemetry")
async def telemetry() -> dict:
    return (await runtime.snapshot()).model_dump(mode="json")


@app.post("/control/start")
async def control_start(request: ControlRequest = ControlRequest()) -> dict[str, bool | str]:
    await runtime.set_autonomy(True, mode=request.mode)
    return {"autonomy_enabled": True, "mission_mode": request.mode}


@app.post("/control/stop")
async def control_stop() -> dict[str, bool]:
    await runtime.set_autonomy(False)
    return {"autonomy_enabled": False}


@app.post("/control/move_to")
async def control_move_to(request: MoveToRequest) -> dict:
    command = await runtime.queue_move_to(request.target, max_duration_ms=request.max_duration_ms)
    return {"queued": True, "command": command.model_dump(mode="json")}


@app.get("/replay/events")
async def replay_events(limit: int = 100, event_type: str | None = None) -> dict:
    return {"events": store.list_events(limit=limit, event_type=event_type)}


@app.get("/training/examples")
async def training_examples(limit: int = 500) -> dict:
    events = store.list_events(limit=limit, event_type="decision_cycle")
    return {"examples": build_training_examples(events)}


@app.get("/training/export.jsonl", response_class=PlainTextResponse)
async def training_export_jsonl(limit: int = 1000) -> str:
    events = store.list_events(limit=limit, event_type="decision_cycle")
    return examples_to_jsonl(build_training_examples(events))


@app.get("/training/summary")
async def training_summary(limit: int = 1000) -> dict:
    events = store.list_events(limit=limit, event_type="decision_cycle")
    examples = build_training_examples(events)
    return summarize_examples(examples, store.count_by_type())


@app.get("/ops/summary")
async def ops_summary(limit: int = 1000) -> dict:
    return build_ops_summary(store.list_events(limit=limit))


@app.post("/training/feedback")
async def training_feedback(feedback: TrainingFeedback) -> dict[str, bool]:
    store.append("training_feedback", feedback)
    return {"ok": True}


@app.post("/mock/start")
async def start_mock() -> dict[str, bool]:
    return {"started": _start_mock_task()}


@app.post("/mock/stop")
async def stop_mock() -> dict[str, bool | str]:
    stopped = _stop_mock_task()
    await runtime.set_connection_status("offline")
    return {"stopped": stopped, "connection_status": "offline"}


@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    queue = await hub.subscribe()
    try:
        await websocket.send_json(envelope("telemetry", await runtime.snapshot()).model_dump(mode="json"))
        while True:
            snapshot = await queue.get()
            await websocket.send_json(envelope("telemetry", snapshot).model_dump(mode="json"))
    except WebSocketDisconnect:
        pass
    finally:
        await hub.unsubscribe(queue)


@app.websocket("/ws/bot")
async def bot_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_json()
            try:
                message = Envelope.model_validate(raw)
                if message.type == "observation":
                    observation = Observation.model_validate(message.payload)
                    command = await runtime.handle_observation(observation)
                    await websocket.send_json(envelope("command", command).model_dump(mode="json"))
                elif message.type == "execution_result":
                    result = ExecutionResult.model_validate(message.payload)
                    await runtime.handle_execution_result(result)
                    await websocket.send_json(envelope("ack", {"ok": True}).model_dump(mode="json"))
                else:
                    await websocket.send_json(
                        envelope("error", {"message": f"Unsupported message type: {message.type}"}).model_dump(
                            mode="json"
                        )
                    )
            except ValidationError as exc:
                await websocket.send_json(
                    envelope("error", {"message": "Invalid payload", "details": exc.errors()}).model_dump(mode="json")
                )
    except WebSocketDisconnect:
        store.append("bot_disconnect", {"message": "bot websocket disconnected"})
        await runtime.set_connection_status("offline")
