from typing import Tuple

from p5 import *
import fastfiz as ff
from ..compiled_protos import api_pb2
from vectormath import Vector2

from fastfiz_renderer.GameTable import GameTable


class ShowShotsServiceHandler:
    _instance = None

    def __init__(self, mac_mode=False, window_pos: Tuple[int, int] = (100, 100), frames_per_second: int = 60,
                 scaling: int = 200, horizontal_mode: bool = False, flipped=False):
        if ShowShotsServiceHandler._instance is None:
            self._game_table: Optional[GameTable] = None

            self._mac_mode: bool = mac_mode
            self._window_pos: Tuple[int, int] = window_pos
            self._frames_per_second: int = frames_per_second
            self._scaling: int = scaling
            self._horizontal_mode: bool = horizontal_mode
            self._stroke_mode: bool = False
            self._flipped: bool = flipped

            self._shotTrees: list[api_pb2.Shot] = []
            self._active_shot_tree_idx: Optional[int] = None

            self._table_state: Optional[ff.TableState] = None
            self._org_table_state: Optional[api_pb2.TableState] = None
            self._shot_vel = 2

            ShowShotsServiceHandler._instance = self
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
            self._game_table.update(None)
            self._game_table.draw(self._scaling * 2 if self._mac_mode else self._scaling, self._horizontal_mode,
                                  self._flipped,
                                  self._stroke_mode)

            if self._shotTrees:
                self._game_table.draw_shot_tree(self._shotTrees[self._active_shot_tree_idx],
                                                self._scaling * 2 if self._mac_mode else self._scaling,
                                                self._horizontal_mode, self._flipped, self._stroke_mode)

        def _key_released(event):
            if event.key == "RIGHT":
                if self._shotTrees:
                    self.update_table_state(self._org_table_state)
                    self._active_shot_tree_idx = (self._active_shot_tree_idx + 1) % len(self._shotTrees)
                    print(f"{self._active_shot_tree_idx + 1} / {len(self._shotTrees)}")
            elif event.key == "LEFT":
                if self._shotTrees:
                    self.update_table_state(self._org_table_state)
                    self._active_shot_tree_idx = (self._active_shot_tree_idx - 1) % len(self._shotTrees)
                    print(f"{self._active_shot_tree_idx + 1} / {len(self._shotTrees)}")
            elif event.key == "f" or event.key == "F":
                self._stroke_mode = not self._stroke_mode
            elif event.key == "UP":
                self._handle_shoot()
            elif event.key == "r" or event.key == "R":
                self.update_table_state(self._org_table_state)
            elif event.key in [str(val) for val in range(1, 10)]:
                self._shot_vel = int(event.key.name)
                self.update_table_state(self._org_table_state)

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
        self._org_table_state = table_state
        self._table_state = new_table_state

    def _handle_shoot(self):
        target: Vector2 = Vector2(self._shotTrees[self._active_shot_tree_idx].ghostBall.x, self._shotTrees[self._active_shot_tree_idx].ghostBall.y)
        source: Vector2 = Vector2(self._shotTrees[self._active_shot_tree_idx].posB1.x, self._shotTrees[self._active_shot_tree_idx].posB1.y)

        diff: Vector2 = target - source
        x_axis: Vector2 = Vector2(1, 0)

        angle = (math.acos(diff.dot(x_axis) / (diff.length * x_axis.length)) * 180 / math.pi) + 180 % 360

        if diff.y < 0:
            angle = 360 - angle

        a = 0
        b = 0
        theta = 11
        phi = angle
        vel = self._shot_vel
        params = ff.ShotParams(a, b, theta, phi, vel)

        if self._table_state.isPhysicallyPossible(params) != ff.TableState.OK_PRECONDITION:
            print("Shot not possible")
        else:
            shot = self._table_state.executeShot(params)
            self._game_table.add_shot(params, shot)
