
from tornado.ioloop import IOLoop

from bokeh.application import Application
from bokeh.application.handlers import ScriptHandler
from bokeh.server.server import Server


def _bokeh_init():
    io_loop = IOLoop.current()

    server = Server(
        {
            '/_address_search': Application(ScriptHandler(filename='address_search.py'))
		},
        io_loop=io_loop,
        allow_websocket_origin=["localhost:8080"]
    )
    server.start()
    io_loop.start()


if __name__ == '__main__':
    _bokeh_init()