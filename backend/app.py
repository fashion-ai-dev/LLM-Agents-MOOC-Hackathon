from fastapi.staticfiles import StaticFiles
import uvloop
import asyncio
from aiohttp import web
import aiofiles
import json
from concurrent.futures import ProcessPoolExecutor
from master_agent.master_agent import maestro_agent
from globals import user_tokens
from dotenv import load_dotenv
from platform_hub.logs import get_logs_from_mongo
from shared import sio
import uuid
import os
import aiohttp_cors
import logging
from platform_hub.logs import send_error_log
from openai_client.connection import OpenAISingleton


logging.basicConfig(level=logging.INFO)

load_dotenv()
port = os.getenv('PORT', 3001)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = web.Application()
sio.attach(app)

static_route = app.router.add_static('/public/', path='public', name='public')

cors = aiohttp_cors.setup(app)
cors.add(static_route, {
    "http://localhost:5173": aiohttp_cors.ResourceOptions(
        allow_methods="*",         # 
        allow_headers="*",         # 
        allow_credentials=True,    # 
        expose_headers="*"         #
    )
})




tasks = {}

# Pool de processos para tarefas pesadas
executor = ProcessPoolExecutor(max_workers=4)

async def index(request):
    try:
        async with aiofiles.open('index.html', mode='r') as f:
            content = await f.read()
        return web.Response(text=content, content_type='text/html')
    except Exception as e:
        return web.Response(text=f"Error: {str(e)}", content_type='text/html')

app.router.add_get('/', index)

@sio.event
async def connect(sid, environ):
    print(f"Cliente conectado: {sid}")

@sio.event
async def register(sid, data):
    try:
        data = json.loads(data)
        email = data.get('email')
        customer = data.get('customer')
        catalog_token = data.get('catalogToken')
        userId = data.get('id')

        

        if catalog_token:
            user_tokens[sid] = {
                'email': email,
                'customer': 1,
                'role': "admin",
                'catalogToken': catalog_token,
                'sid': sid,
                'userId': userId
            }

        print(f"Cliente registrado: Email: {email}, SessionID: {sid}")

        await sio.emit('register_success', None, to=sid)
        
        await sio.emit('conversation_history', [], to=sid)
    except Exception as e:
        send_error_log(sid, e)
        print(f"Erro ao processar registro: {e}")

@sio.event
async def conversation(sid, data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        message_id = str(uuid.uuid4())
        if data.get('thread_id', None) is None:
            data['thread_id'] = str(uuid.uuid4())

        data['message']['id'] = message_id
        
        if data.get("open_ai_key", None) is None:
            raise Exception("OpenAI key not found in the request.")
        
        OpenAISingleton(data.get("open_ai_key"))

        # Criar uma task assíncrona para o processamento do maestro_agent e associar ao sid
        task = asyncio.create_task(process_conversation(data, sid, message_id))
        tasks[sid] = task  # Armazenar a task associada ao sid

    except Exception as e:
        error_message = 'An unexpected error occurred on the server.'
        logging.info(f"Mensagem recebida de {sid}: {data}")
        logging.error(f"Erro ao processar mensagem de chat (conversation): {e}")

        send_error_log(sid, e)
        await sio.emit('conversation_error', error_message, to=sid)

@sio.event
async def cancel_conversation(sid):
    try:
        task = tasks.get(sid)
        if task and not task.done():
            task.cancel()  # Cancelar a tarefa
            try:
                await task  # Esperar o cancelamento completo
            except asyncio.CancelledError:
                logging.info(f"Tarefa do cliente {sid} foi cancelada com sucesso.")

        # Notificar o cliente de que a conversa foi cancelada
        await sio.emit('conversation_cancelled', {'message': 'Conversa cancelada'}, to=sid)

    except Exception as e:
        logging.error(f"Erro ao cancelar a conversa para {sid}: {e}")
        await sio.emit('conversation_error', {'message': 'Erro ao cancelar conversa'}, to=sid)

async def process_conversation(data, sid, message_id):
    try:
        # Chame diretamente se for uma coroutine
        response = await maestro_agent(data, sid)

        response = { 'message': {
                        'id': message_id,
                        'response': response.get("html_answer"),
                    },
                    'file_url': response.get("file_url", None),
                    'thread_id': data['thread_id']
                    }

        await sio.emit('conversation_success', response, to=sid)
    except asyncio.CancelledError:
        logging.info(f"Tarefa para o cliente {sid} foi cancelada.")
        return  # Garantir que o cancelamento seja tratado corretamente
    except Exception as e:
        error_message = 'An unexpected error occurred on the server.'
        logging.error(f"Erro ao processar mensagem de chat (process_conversation): {e}")
        send_error_log(sid, e)
        await sio.emit('conversation_error', error_message, to=sid)

@sio.event
async def get_thread(sid, data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        user_info = user_tokens.get(sid)

        thread = None

        await sio.emit('get_thread_success', thread, to=sid)
    except Exception as e:
        send_error_log(sid, e)
        logging.error(f"NOVO Erro ao processar solicitação de thread: {e}")

@sio.event
async def get_thread_list_by_user_and_customer(sid, data):
    try:
        threads = None

        if isinstance(data, str):
            data = json.loads(data)

        user_info = user_tokens.get(sid)

        # if user_info.get('role', {}).get('id') == 1 and data.get('customer_id'):
        #   threads = None

        await sio.emit('get_thread_list_by_user_and_customer_success', threads, to=sid)
    except Exception as e:
        send_error_log(sid, e)
        logging.error(f"Erro ao processar solicitação de thread: {e}")

@sio.event
async def get_log_list_by_user_and_customer(sid, data):
    try:
        logs = None

        if isinstance(data, str):
            data = json.loads(data)

        user_info = user_tokens.get(sid)

        if user_info.get('role', {}).get('id') == 1 and data.get('customer_id'):
          logs = get_logs_from_mongo(data['user_id'], data['customer_id'], data.get('thread_id'))

        await sio.emit('get_log_list_by_user_and_customer_success', logs, to=sid)
    except Exception as e:
        send_error_log(sid, e)
        logging.error(f"Erro ao processar solicitação de logs: {e}")

def download_luan_object(sid, data):
    thread_id = data.get("thread_id")
    user_info = user_tokens.get(sid)
    thread_data = []

    if thread_data:
        sio.emit('luan_object_success', thread_data, sid)
    else:
        sio.emit('error', {"error": "Thread not found"}, sid)

@sio.event
def disconnect(sid):
    print(f"Cliente desconectado: {sid}")
    if sid in tasks:
        task = tasks.pop(sid)  # Remover a task associada ao sid
        if not task.done():
            task.cancel()  # Cancelar a task se ainda estiver em andamento
            logging.info(f"Tarefa para o cliente {sid} foi cancelada ao desconectar.")

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=int(port))
