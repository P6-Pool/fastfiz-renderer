import threading
import time

from google.protobuf import empty_pb2

import grpc
from concurrent import futures
from .ShowShotsServiceHandler import ShowShotsServiceHandler
from .ShowGameServiceHandler import ShowGameServiceHandler
from ..compiled_protos import api_pb2, api_pb2_grpc


class Server:
    def __init__(self, show_shots_handler: ShowShotsServiceHandler, show_games_handler: ShowGameServiceHandler):
        self.show_shots_handler: ShowShotsServiceHandler = show_shots_handler
        self.show_game_handler: ShowGameServiceHandler = show_games_handler

        self.CueCanvasService_instance = self.CueCanvasService(self)

    class CueCanvasService(api_pb2_grpc.CueCanvasAPIServicer):
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance

        def ShowShots(self, request: api_pb2.ShowShotsRequest, context):
            self.outer_instance.show_shots_handler.update_shots_trees(request.shots)
            self.outer_instance.show_shots_handler.update_table_state(request.tableState)
            return empty_pb2.Empty()

        def ShowGames(self, request: api_pb2.ShowGamesRequest, context):
            self.outer_instance.show_game_handler.update_games(request.games)
            return empty_pb2.Empty()

    def serve_shots_display(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        api_pb2_grpc.add_CueCanvasAPIServicer_to_server(self.CueCanvasService_instance, server)
        server.add_insecure_port('[::]:50051')
        server.start()

        self.show_shots_handler.start_server_window()

        server.wait_for_termination()

    def serve_game_display(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        api_pb2_grpc.add_CueCanvasAPIServicer_to_server(self.CueCanvasService_instance, server)
        server.add_insecure_port('[::]:50051')
        server.start()

        self.show_game_handler.start_server_window()

        server.wait_for_termination()

    def serve_loaded_games(self, show_game_request_binary_file_path: str):
        show_games_request = self._read_protobuf_from_file(show_game_request_binary_file_path)
        self._set_interval(lambda: self.show_game_handler.update_games(show_games_request.games), 1.5)
        self.show_game_handler.start_server_window()

    @staticmethod
    def _set_interval(func, sec):
        t = threading.Timer(sec, func)
        t.start()
        return t

    @staticmethod
    def _read_protobuf_from_file(filename) -> api_pb2.ShowGamesRequest:
        # Read the bytes from the file
        with open(filename, "rb") as f:
            protobuf_bytes = f.read()

        # Parse the bytes into a Protocol Buffers object
        protobuf_message = api_pb2.ShowGamesRequest()
        protobuf_message.ParseFromString(protobuf_bytes)

        return protobuf_message
