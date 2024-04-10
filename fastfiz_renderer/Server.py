from google.protobuf import empty_pb2

import grpc
from concurrent import futures
from .ServerHandler import ServerHandler
from .compiled_protos import api_pb2, api_pb2_grpc


class Server:
    def __init__(self, server_handler: ServerHandler):
        self.server_handler: ServerHandler = server_handler
        self.CueCanvasService_instance = self.CueCanvasService(self)

    class CueCanvasService(api_pb2_grpc.CueCanvasAPIServicer):
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance

        def ShowShots(self, request: api_pb2.ShowShotsRequest, context):
            self.outer_instance.server_handler.update_shots_trees(request.shots)
            self.outer_instance.server_handler.update_table_state(request.tableState)
            return empty_pb2.Empty()

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        api_pb2_grpc.add_CueCanvasAPIServicer_to_server(self.CueCanvasService_instance, server)
        server.add_insecure_port('[::]:50051')
        server.start()

        self.server_handler.start_server_window()

        server.wait_for_termination()
