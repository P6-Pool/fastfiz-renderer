from typing import Tuple, Set

from p5 import *
import fastfiz as ff
from vectormath import Vector2
import os
import time
from .GameTable import GameTable
from sys import platform


class GameHandler:
    _instance = None
    ShotDecider = Callable[[ff.TableState], Optional[ff.ShotParams]]
    Game = Tuple[ff.TableState, ShotDecider]

    def __init__(
        self,
        window_pos: Tuple[int, int] = (100, 100),
        frames_per_second: int = 60,
        scaling: int = 200,
        horizontal_mode: bool = False,
        flipped: bool = False,
        screenshot_dir: str = ".",
    ):
        if GameHandler._instance is None:
            self._game_number: int = 0
            self._games: list[GameHandler.Game] = []
            self._game_table: Optional[GameTable] = None
            self._table_state: Optional[ff.TableState] = None
            self._start_ball_positions: dict[int, Tuple[float, float]] = dict()
            self._shot_decider: Optional[GameHandler.ShotDecider] = None

            self._renderer = "skia"
            self._mac_mode: bool = platform == "darwin" and self._renderer == "skia"
            self._window_pos: Tuple[int, int] = window_pos
            self._frames_per_second: int = frames_per_second
            self._scaling: int = scaling
            self._horizontal_mode: bool = horizontal_mode
            self._flipped: bool = flipped
            self._stroke_mode: bool = False
            self._grab_mode: bool = False
            self._shot_speed_factor: float = 1

            self._ss_dir: str = screenshot_dir
            self._ss_buffer: Optional[p5.core.graphics.Graphics] = None
            self._ss_scaling: int = 2000

            GameHandler._instance = self
        else:
            raise Exception("This class is a singleton!")

    def play_eight_ball_games(
        self,
        shot_deciders: list[ShotDecider],
        shot_speed_factor: float = 1,
        auto_play: bool = False,
    ):
        games: list[GameHandler.Game] = []
        for decider in shot_deciders:
            game_state: ff.GameState = ff.GameState.RackedState(ff.GT_EIGHTBALL)
            table_state: ff.TableState = game_state.tableState()
            games.append((table_state, decider))

        self.play_games(games, shot_speed_factor, auto_play)

    def play_games(
        self, games: list[Game], shot_speed_factor: float = 1, auto_play: bool = False
    ):
        if not games:
            raise Exception("No games provided!")

        self._games = games
        self._verify_table_dimensions()
        self._shot_speed_factor = shot_speed_factor
        self._handle_next_game()

        shot_requester = self._handle_shoot if auto_play else None
        width = int(self._game_table.width * self._scaling)
        length = int(self._game_table.length * self._scaling)

        ss_width = int(self._game_table.width * self._ss_scaling)
        ss_length = int(self._game_table.length * self._ss_scaling)

        if self._horizontal_mode:
            width, length = length, width
            ss_width, ss_length = ss_length, ss_width

        def _setup():
            size(width, length)
            self._ss_buffer = create_graphics(ss_width, ss_length)
            ellipseMode(CENTER)
            if not self._stroke_mode:
                noStroke()

        def _draw():
            background(255)
            self._game_table.update(shot_requester)
            self._game_table.draw(
                self._scaling * 2 if self._mac_mode else self._scaling,
                self._horizontal_mode,
                self._flipped,
                self._stroke_mode,
                1 if self._stroke_mode else 4,
                canvas=p5.renderer
            )

        def _key_released(event):
            if event.key == "RIGHT":
                self._handle_shoot()
            elif event.key == "r" or event.key == "R":
                self._handle_restart()
            elif event.key == "n" or event.key == "N":
                print(f"{self._game_number}: Game skipped")
                self._handle_next_game()
            elif event.key == "s" or event.key == "S":
                self._handle_screenshot()
            elif event.key == "f" or event.key == "F":
                self._stroke_mode = not self._stroke_mode
            elif event.key == "g" or event.key == "G":
                self._grab_mode = not self._grab_mode

        def _mouse_pressed(_):
            if self._grab_mode:
                scaling = self._scaling * 2 if self._mac_mode else self._scaling
                moused_over_ball = None

                for ball in self._game_table.game_balls:
                    if ball.is_mouse_over(
                        scaling,
                        Vector2(self._game_table.board_pos, self._game_table.board_pos),
                    ):
                        moused_over_ball = ball
                        break

                if moused_over_ball:
                    moused_over_ball.is_being_dragged = True
                    return

        def _mouse_released(_):
            if self._grab_mode:
                for ball in self._game_table.game_balls:
                    self._table_state.setBall(
                        ball.number, ball.state, ball.position.x, ball.position.y
                    )
                    ball.is_being_dragged = False

        def _mouse_dragged(_):
            if self._grab_mode:
                for ball in self._game_table.game_balls:
                    if ball.is_being_dragged:
                        new_pos = Vector2(mouse_x, mouse_y) / self._scaling
                        if self._mac_mode:
                            new_pos /= 2
                        ball.position = new_pos - Vector2(
                            self._game_table.board_pos, self._game_table.board_pos
                        )
                        return

        run(
            renderer=self._renderer,
            frame_rate=self._frames_per_second,
            sketch_draw=_draw,
            sketch_setup=_setup,
            sketch_key_released=_key_released,
            sketch_mouse_dragged=_mouse_dragged,
            sketch_mouse_released=_mouse_released,
            sketch_mouse_pressed=_mouse_pressed,
            window_xpos=self._window_pos[0],
            window_ypos=self._window_pos[1],
            window_title="Cue Canvas",
        )

    def _handle_screenshot(self):
        os.makedirs(self._ss_dir, exist_ok=True)

        self._ss_buffer.background(255)

        self._game_table.draw(
            self._ss_scaling,
            self._horizontal_mode,
            self._flipped,
            self._stroke_mode,
            3 if self._stroke_mode else 10,
            canvas=self._ss_buffer.renderer,
        )

        save_canvas(os.path.join(self._ss_dir, time.strftime("%Y-%m-%d_%T") + ".png"), self._ss_buffer)

    def _handle_next_game(self):
        if self._games:
            self._table_state, self._shot_decider = self._games.pop(0)
            self._game_table = GameTable.from_table_state(
                self._table_state, self._shot_speed_factor
            )
            self._game_number += 1
            self._load_start_balls()
        else:
            print("No more games left")
            exit()

    def _handle_restart(self):
        for ball_number, pos in self._start_ball_positions.items():
            self._table_state.setBall(ball_number, ff.Ball.STATIONARY, pos[0], pos[1])
        self._game_table = GameTable.from_table_state(
            self._table_state, self._shot_speed_factor
        )

    def _handle_shoot(self):
        if self._table_state.getBall(ff.Ball.CUE).isPocketed():
            print(f"{self._game_number}: Cue ball pocketed")
            self._handle_next_game()

        params = self._shot_decider(self._table_state)

        if params is None:
            print(f"{self._game_number}: No more shots left")
            self._handle_next_game()
        elif (
            self._table_state.isPhysicallyPossible(params)
            != ff.TableState.OK_PRECONDITION
        ):
            print(f"{self._game_number}: Shot not possible")
            self._handle_next_game()
        else:
            shot = self._table_state.executeShot(params)
            self._game_table.add_shot(params, shot, lambda: None)

    def _verify_table_dimensions(self):
        widths: Set[float] = {
            table.TABLE_WIDTH
            for table in [
                table_state.getTable()
                for table_state in [game[0] for game in self._games]
            ]
        }
        lengths: Set[float] = {
            table.TABLE_LENGTH
            for table in [
                table_state.getTable()
                for table_state in [game[0] for game in self._games]
            ]
        }

        if len(widths) > 1 or len(lengths) > 1:
            raise Exception("Games must have the same table width and length!")

    def _load_start_balls(self):
        for i in range(ff.Ball.CUE, ff.Ball.FIFTEEN + 1):
            ball = self._table_state.getBall(i)
            pos = ball.getPos()
            self._start_ball_positions[ball.getID()] = (pos.x, pos.y)
