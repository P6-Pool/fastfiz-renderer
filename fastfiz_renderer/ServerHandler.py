from typing import Tuple

from p5 import *
import fastfiz as ff
from .compiled_protos import api_pb2
from vectormath import Vector2

from .GameTable import GameTable


class ServerHandler:
    _instance = None

    def __init__(self, mac_mode=False, window_pos: Tuple[int, int] = (100, 100), frames_per_second: int = 60,
                 scaling: int = 200, horizontal_mode: bool = False):
        if ServerHandler._instance is None:
            self._game_table: Optional[GameTable] = None

            self._mac_mode: bool = mac_mode
            self._window_pos: Tuple[int, int] = window_pos
            self._frames_per_second: int = frames_per_second
            self._scaling: int = scaling
            self._horizontal_mode: bool = horizontal_mode
            self._stroke_mode: bool = False

            self._shotTrees: list[api_pb2.Shot] = []
            self._active_shot_tree_idx: Optional[int] = None

            ServerHandler._instance = self
        else:
            raise Exception("This class is a singleton!")

    def start_server_window(self):
        self._game_table = GameTable.from_table_state(ff.TableState(), 1)

        width = int(self._game_table.width * self._scaling)
        length = int(self._game_table.length * self._scaling)

        if self._horizontal_mode:
            width, length = length, width

        def _setup():
            size(width, length)
            ellipseMode(CENTER)
            textAlign(CENTER, CENTER)
            if not self._stroke_mode:
                noStroke()

        def _draw():
            background(255)
            self._game_table.draw(self._scaling * 2 if self._mac_mode else self._scaling, self._horizontal_mode,
                                  self._stroke_mode)

            if self._shotTrees:
                self._game_table.draw_shot_tree(self._shotTrees[self._active_shot_tree_idx],
                                                self._scaling * 2 if self._mac_mode else self._scaling,
                                                self._horizontal_mode, self._stroke_mode)

        def _key_released(event):
            if event.key == "RIGHT":
                if self._shotTrees:
                    self._active_shot_tree_idx = (self._active_shot_tree_idx + 1) % len(self._shotTrees)
            elif event.key == "LEFT":
                if self._shotTrees:
                    self._active_shot_tree_idx = (self._active_shot_tree_idx - 1) % len(self._shotTrees)
            elif event.key == "f" or event.key == "F":
                self._stroke_mode = not self._stroke_mode

            # print(self._shotTrees[self._active_shot_tree_idx])

        run(renderer="skia", frame_rate=self._frames_per_second, sketch_draw=_draw, sketch_setup=_setup,
            sketch_key_released=_key_released, window_xpos=self._window_pos[0],
            window_ypos=self._window_pos[1],
            window_title="Cue Canvas Server")

    def update_shots_trees(self, shot_trees: list[api_pb2.Shot]):
        self._shotTrees = shot_trees
        if shot_trees:
            self._active_shot_tree_idx = 0

    def update_table_state(self, table_state: api_pb2.TableState):
        new_table_state: ff.TableState = ff.TableState()
        for ball in table_state.balls:
            new_table_state.setBall(ball.number, ball.state, ball.pos.x, ball.pos.y)
        self._game_table = GameTable.from_table_state(new_table_state, 1)
