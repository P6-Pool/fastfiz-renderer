import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "compiled_protos"))
)


from .GameBall import GameBall
from .GameTable import GameTable
from .GameHandler import GameHandler
from .ServerHandler import ServerHandler
from .Server import Server
from .compiled_protos import api_pb2, api_pb2_grpc
