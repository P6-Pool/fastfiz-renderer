from typing import Tuple, Optional
from p5 import *
import fastfiz as ff
from ..compiled_protos import api_pb2
from vectormath import Vector2

from fastfiz_renderer.GameTable import GameTable


class ShowGameServiceHandler:
    _instance = None

    def __init__(self, mac_mode=False, window_pos: Tuple[int, int] = (100, 100), frames_per_second: int = 60,
                 scaling: int = 200, horizontal_mode: bool = False, flipped: bool = False, auto_play: bool = False):

        if ShowGameServiceHandler._instance is None:
            self._game_table: Optional[GameTable] = None

            self._mac_mode: bool = mac_mode
            self._window_pos: Tuple[int, int] = window_pos
            self._frames_per_second: int = frames_per_second
            self._scaling: int = scaling
            self._horizontal_mode: bool = horizontal_mode
            self._stroke_mode: bool = False
            self._flipped: bool = flipped
            self._auto_play: bool = auto_play

            self._turn_history: list[api_pb2.GameTurn] = []
            self._active_turn_idx: Optional[int] = None

            self._table_state: Optional[ff.TableState] = None
            self._org_table_state: Optional[api_pb2.TableState] = None
            self._highlighted_ball: Optional[str] = None
            self._highlighted_pocket: Optional[str] = None
            self._shot_params: Optional[api_pb2.ShotParams] = None

            self._shot_available: bool = False

            ShowGameServiceHandler._instance = self
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
                                  self._stroke_mode,
                                  [self._highlighted_ball],
                                  [self._highlighted_pocket],
                                  self._shot_params
                                  )

        def _key_released(event):
            if event.key == "RIGHT":
                self._handle_shift_turn(True)
            elif event.key == "LEFT":
                self._handle_shift_turn(False)
            elif event.key == "f" or event.key == "F":
                self._stroke_mode = not self._stroke_mode
            elif event.key == "a" or event.key == "A":
                self._auto_play = not self._auto_play
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

    def _handle_shift_turn(self, is_next):
        if self._turn_history:
            if is_next:
                self._active_turn_idx += 1 if self._active_turn_idx < len(self._turn_history) - 1 else 0
            else:
                self._active_turn_idx -= 1 if self._active_turn_idx > 0 else 0

            turn = self._turn_history[self._active_turn_idx]

            if turn.turnType != "TT_BREAK":
                self._highlighted_ball = turn.gameShot.ballTarget
                self._highlighted_pocket = self._turn_history[self._active_turn_idx].gameShot.pocketTarget
            else:
                self._highlighted_ball = None
                self._highlighted_pocket = None
            self._shot_params = turn.gameShot.shotParams
            self.update_table_state(turn.tableStateBefore)
            print(f"{self._active_turn_idx + 1} / {len(self._turn_history)} - {turn.agentName} - {turn.gameShot.decision} - {turn.turnType} - {turn.shotResult}")

    def update_turn_history(self, turn_history: list[api_pb2.GameTurn]):
        self._turn_history = turn_history
        if turn_history:
            self._active_turn_idx = 0

            turn = self._turn_history[self._active_turn_idx]
            self._shot_params = turn.gameShot.shotParams
            self.update_table_state(turn.tableStateBefore)
            self._handle_shoot()
            print(f"{self._active_turn_idx + 1} / {len(self._turn_history)} - {turn.agentName} - {turn.gameShot.decision} - {turn.turnType} - {turn.shotResult}")

    def update_table_state(self, table_state: api_pb2.TableState):
        new_table_state: ff.TableState = ff.TableState()

        for ball in table_state.balls:
            new_table_state.setBall(ball.number, ball.state, ball.pos.x, ball.pos.y)
        self._game_table = GameTable.from_table_state(new_table_state, 1)
        self._org_table_state = table_state
        self._table_state = new_table_state
        self._shot_available = True

    def _handle_shoot(self):
        if self._turn_history and self._shot_available:
            gt = self._turn_history[self._active_turn_idx]
            gs = gt.gameShot

            if gs.decision != "DEC_CONCEDE":
                params = gs.shotParams
                params = ff.ShotParams(params.a, params.b, params.theta, params.phi, params.v)

                shot = self._table_state.executeShot(params)

                self._game_table.add_shot(params, shot, lambda: self._handle_shot_finished())
                self._shot_available = False
                self._shot_params = None

    def _handle_shot_finished(self):
        if self._active_turn_idx < len(self._turn_history) - 1:
            self._handle_shift_turn(True)
            if self._auto_play:
                self._handle_shoot()
