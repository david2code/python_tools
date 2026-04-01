#!/bin/python3

# apt install python3-websockets

import asyncio
import websockets
import ssl

async def echo(websocket, path):
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(f"Echo: {message}")

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="cert/server.pem", keyfile="cert/server-key.pem")
start_server = websockets.serve(echo, "0.0.0.0", 8765, ssl=ssl_context)

#start_server = websockets.serve(echo, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


