from bitstring import BitStream
from threading import Thread
import multiprocess as mp
import numpy as np
import subprocess
import asyncio
import logging
import ujson

from pyrtmp.rtmp import SimpleRTMPController, RTMPProtocol, SimpleRTMPServer
from pyrtmp.amf.serializers import AMF0Deserializer
from pyrtmp.session_manager import SessionManager
from pyrtmp.flv import FLVMediaType, FLVWriter
from pyrtmp import StreamClosedException

from .content_supplier import *


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class RtmpSupplier(ContentSupplier):
    data = SupplierData(None, None)
    ready = False

    def __init__(self) -> None:
        self.converter = subprocess.Popen(Rf"ffmpeg -probesize 32 -flags low_delay -r 60 -i pipe: -vf vflip -f rawvideo -pix_fmt rgb24 -r 60 pipe:".split(),
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.buffer = None

        stream_thread = Thread(target=asyncio.run, args=(self._start_server(),))
        stream_thread.daemon = True
        stream_thread.start()

    def set_resolution(self, resolution):
        self.image_size = resolution[0] * resolution[1] * 3#bytes

    def has_client(self) -> bool:
        return self.ready

    def get_data(self) -> SupplierData:
        # Blocking
        if not self.converter.stdout.closed:
            self.data.pixels = np.frombuffer(self.converter.stdout.read(self.image_size), dtype=np.uint8)

        return self.data

    async def _start_server(self):
        server = RtmpServerStarter(self._on_connection, self._on_video_data, self._on_node_data)
        await server.create()
        await server.start()
        await server.wait_closed()

    def _on_connection(self):
        self.ready = True

    def _on_video_data(self, data):
        self.converter.stdin.write(data)

    def _on_node_data(self, hierarchy):
        self.data.nodes = hierarchy


class RTMP2FLVController(SimpleRTMPController):

    def __init__(self, connection_callback, video_callback, node_callback):
        super().__init__()
        self.video_callback = video_callback
        self.node_callback = node_callback
        self.connection_callback = connection_callback

    async def on_ns_publish(self, session, message) -> None:
        session.state = FLVWriter()
        self.video_callback(session.state.write_header())
        self.connection_callback()
        await super().on_ns_publish(session, message)

    async def on_metadata(self, session, message) -> None:
        session.state.write(0, message.to_raw_meta(), FLVMediaType.OBJECT)
        await super().on_metadata(session, message)

    async def on_unknown_message(self, _: SessionManager, message) -> None:
        stream = BitStream(message.payload)
        _ = AMF0Deserializer.from_stream(stream)
        data = AMF0Deserializer.from_stream(stream)
        self.node_callback(ujson.decode(data))

    async def on_video_message(self, session, message) -> None:
        bytes = session.state.write(message.timestamp, message.payload, FLVMediaType.VIDEO)
        self.video_callback(bytes)
        await super().on_video_message(session, message)

    async def on_stream_closed(self, session: SessionManager, exception: StreamClosedException) -> None:
        await super().on_stream_closed(session, exception)


class RtmpServerStarter(SimpleRTMPServer):

    def __init__(self, connection_callback, video_callback, node_callback):
        super().__init__()
        self.video_callback = video_callback
        self.node_callback = node_callback
        self.connection_callback = connection_callback

    async def create(self, host: str = "127.0.0.1", port: int = 1935):
        loop = asyncio.get_event_loop()
        self.server = await loop.create_server(
            lambda: RTMPProtocol(controller=RTMP2FLVController(
                self.connection_callback,
                self.video_callback,
                self.node_callback)),
            host=host,
            port=port,
        )
