import socketio

sio = socketio.AsyncServer(cors_allowed_origins='*', allow_upgrades=True, ping_timeout=320)

async def send_logs(sid, log_message):
    await sio.emit('agent_status', log_message, to=sid)


async def send_agent_status(sid, status):
    await sio.emit('agent_status', status, to=sid)
