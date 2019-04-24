#!/usr/bin/env python3

import functools
import asyncio
import websockets
import asn1tools


async def echo(websocket, _, c_source):
    print('Client connected!')

    while True:
        data = await websocket.recv()
        print('Received:', c_source.decode('B', data))
        await websocket.send(data)
        print('Response sent.')


def main():
    c_source = asn1tools.compile_files([
        'asn1/c_source.asn',
        'asn1/programming_types.asn'
    ], 'oer')

    start_server = websockets.serve(
        functools.partial(echo, c_source=c_source),
        'localhost',
        8765)

    print('Listening for websocket clients on localhost:8765...')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


main()
