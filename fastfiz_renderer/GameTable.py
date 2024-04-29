from typing import Tuple

import fastfiz as ff
from p5 import *
import vectormath as vmath
import fastfiz_renderer.compiled_protos.api_pb2 as api_pb2

from .GameBall import GameBall


class GameTable:
    def __init__(self, width: float, length: float, side_pocket_width: float, corner_pocket_width: float,
                 rolling_friction_const: float, sliding_friction_const: float, gravitational_const: float,
                 game_balls: list[GameBall], shot_speed_factor: float):
        self.wood_width = width / 10
        self.rail_width = width / 30
        self.width = width + 2 * self.wood_width + 2 * self.rail_width
        self.length = length + 2 * self.wood_width + 2 * self.rail_width
        self.board_width = width
        self.board_length = length
        self.side_pocket_width = side_pocket_width
        self.corner_pocket_width = corner_pocket_width
        self.board_pos = self.rail_width + self.wood_width

        self.wood_color = (103, 92, 80)
        self.rail_color = (0, 46, 30)
        self.board_color = (21, 88, 67)
        self.pocket_color = (32, 30, 31)
        self.pocket_marking_color = (77, 70, 62)
        self.board_marking_color = (62, 116, 99)
        self.white_color = (255, 255, 255)
        self.black_color = (0, 0, 0)
        self.red_color = (255, 0, 0)
        self.blue_color = (0, 0, 255)

        self.rolling_friction_const = rolling_friction_const
        self.sliding_friction_const = sliding_friction_const
        self.gravitational_const = gravitational_const
        self.game_balls = game_balls

        self._shot_queue: list[Tuple[ff.ShotParams, ff.Shot, Callable[None, None]]] = []
        self._active_shot: Optional[Tuple[ff.ShotParams, ff.Shot, Callable[None, None]]] = None
        self._active_shot_start_time: float = 0
        self._shot_speed_factor = shot_speed_factor

    @classmethod
    def from_table_state(cls, table_state: ff.TableState, shot_speed_factor: float):
        game_balls = []

        for i in range(ff.Ball.CUE, ff.Ball.FIFTEEN + 1):
            ball: ff.Ball = table_state.getBall(i)
            pos = ball.getPos()
            game_balls.append(GameBall(ball.getRadius(), ball.getID(), vmath.Vector2(pos.x, pos.y), ball.getState()))

        table: ff.Table = table_state.getTable()

        return cls(table.TABLE_WIDTH, table.TABLE_LENGTH, table.SIDE_POCKET_WIDTH, table.CORNER_POCKET_WIDTH,
                   table.MU_ROLLING, table.MU_SLIDING, table.g, game_balls, shot_speed_factor)

    def draw(self, scaling=200, horizontal_mode=False, flipped=False, stroke_mode=False, stroke_weight=2,
             highlighted_balls: list[str] = [], highlighted_pockets: list[str] = [],
             shot_params: Optional[api_pb2.ShotParams] = None, canvas=None):

        if canvas:
            old_canvas = p5.renderer
            p5.renderer = canvas

        push()

        if horizontal_mode:
            rotate(PI / 2)
            translate(0, -int(self.length * scaling))

        if flipped:
            translate(0, int(self.length * scaling))
            scale(1, -1)

        strokeWeight(stroke_weight)
        noStroke() if not stroke_mode else stroke(*self.black_color)

        # Wood
        fill(*self.wood_color) if not stroke_mode else fill(*self.white_color)
        rect(0, 0, self.width * scaling, self.length * scaling)

        # Pocket markings
        marking_width = (self.wood_width * 2 + self.rail_width * 2) * scaling
        fill(*self.pocket_marking_color) if not stroke_mode else fill(*self.white_color)
        square(0, 0, marking_width)
        square(0, self.length / 2 * scaling - marking_width / 2, marking_width)
        square(0, self.length * scaling - marking_width, marking_width)

        square(self.width * scaling - marking_width, 0, marking_width)
        square(self.width * scaling - marking_width, self.length / 2 * scaling - marking_width / 2, marking_width)
        square(self.width * scaling - marking_width, self.length * scaling - marking_width, marking_width)

        # Rails
        push()
        translate(int(self.wood_width * scaling), int(self.wood_width * scaling))
        fill(*self.rail_color) if not stroke_mode else fill(*self.white_color)
        rect(0, 0, (self.board_width + self.rail_width * 2) * scaling,
             (self.board_length + self.rail_width * 2) * scaling)
        pop()

        # Board
        push()
        translate(int(self.board_pos * scaling),
                  int(self.board_pos * scaling))
        fill(*self.board_color) if not stroke_mode else fill(*self.white_color)
        rect(0, 0, self.board_width * scaling, self.board_length * scaling)
        pop()

        push()
        translate(0, int(self.board_pos * scaling))

        # Arc
        stroke(*self.board_marking_color) if not stroke_mode else stroke(*self.black_color)
        noFill()
        arc(
            self.width / 2 * scaling,
            self.board_length * scaling / 8 * 6,
            self.board_width * scaling / 2,
            self.board_width * scaling / 2,
            0,
            PI)
        noStroke() if not stroke_mode else stroke(*self.black_color)

        # Left-right markings
        for i in range(1, 8):
            fill(*GameBall.ball_colors[ff.Ball.CUE]) if not stroke_mode else fill(*self.black_color)
            circle(self.wood_width * scaling / 2, self.board_length * scaling / 8 * i, self.wood_width / 10 * scaling)
            circle((self.wood_width * 1.5 + self.board_width + self.rail_width * 2) * scaling,
                   self.board_length * scaling / 8 * i, self.wood_width / 10 * scaling)

            # Lines
            if i == 2 or i == 6:
                stroke(*self.board_marking_color) if not stroke_mode else stroke(*self.black_color)
                line(self.board_pos * scaling,
                     self.board_length * scaling / 8 * i,
                     (self.wood_width + self.board_width + self.rail_width) * scaling - 1,
                     self.board_length * scaling / 8 * i)
                noStroke() if not stroke_mode else stroke(*self.black_color)

            # Middle dots
            if i == 2 or i == 6:
                fill(*self.board_marking_color) if not stroke_mode else fill(*self.white_color)
                circle(self.width / 2 * scaling, self.board_length * scaling / 8 * i, ceil(scaling / 100) * 3)
        pop()

        # Top-bottom markings
        push()
        translate(int(self.board_pos * scaling), 0)
        fill(*GameBall.ball_colors[ff.Ball.CUE]) if not stroke_mode else fill(*self.black_color)
        for i in range(1, 4):
            circle(self.board_width * scaling / 4 * i, self.wood_width / 2 * scaling, self.wood_width / 10 * scaling)
            circle(self.board_width * scaling / 4 * i,
                   (self.wood_width * 1.5 + self.rail_width * 2 + self.board_length) * scaling,
                   self.wood_width / 10 * scaling)
        pop()

        def draw_side_pocket(rotation_angle, rotation_point, highlighted):
            push()
            translate(*rotation_point)
            rotate(rotation_angle)
            fill(*self.board_color) if not stroke_mode else fill(*self.white_color)
            noStroke()
            rect(
                0,
                -self.rail_width * scaling,
                self.side_pocket_width * scaling,
                self.side_pocket_width * scaling)
            noStroke() if not stroke_mode else stroke(*self.black_color)
            fill(*self.pocket_color) if not stroke_mode else fill(*self.black_color)
            circle((self.side_pocket_width / 2) * scaling, -self.corner_pocket_width / 2 * scaling,
                   self.corner_pocket_width * scaling)

            if highlighted:
                fill(*GameBall.ball_colors[0]) if not stroke_mode else fill(*self.white_color)
                circle((self.side_pocket_width / 2) * scaling, -self.corner_pocket_width / 2 * scaling,
                       self.corner_pocket_width / 4 * scaling)

            a = self.wood_width - (self.board_pos - self.corner_pocket_width / 2)
            c = self.corner_pocket_width / 2
            b = math.sqrt(c ** 2 - a ** 2)

            # triangle(
            #     (b + self.side_pocket_width / 2) * scaling, -self.rail_width * scaling,
            #     self.side_pocket_width * scaling, -self.rail_width * scaling,
            #     self.side_pocket_width * scaling, 0
            # )
            # triangle(
            #     (self.side_pocket_width / 2 - b) * scaling, -self.rail_width * scaling,
            #     0, -self.rail_width * scaling,
            #     0, 0
            # )

            fill(*self.rail_color) if not stroke_mode else fill(*self.white_color)
            beginShape()
            vertex(self.side_pocket_width * scaling, 0)
            vertex((b + self.side_pocket_width / 2) * scaling, -self.rail_width * scaling),
            vertex(self.side_pocket_width * scaling, -self.rail_width * scaling)
            endShape()

            beginShape()
            vertex(0, 0)
            vertex((self.side_pocket_width / 2 - b) * scaling, -self.rail_width * scaling)
            vertex(0, -self.rail_width * scaling)
            endShape()
            pop()

        def draw_corner_pocket(rotation_angle, rotation_point, highlighted):
            push()
            translate(*rotation_point)
            rotate(rotation_angle)
            noStroke()
            fill(*self.board_color) if not stroke_mode else fill(*self.white_color)
            rect(
                0, 0,
                self.corner_pocket_width * scaling,
                self.corner_pocket_width * scaling)
            noStroke() if not stroke_mode else stroke(*self.black_color)
            fill(*self.pocket_color) if not stroke_mode else fill(*self.black_color)
            circle(self.corner_pocket_width * scaling / 2, 0, self.corner_pocket_width * scaling)

            if highlighted:
                fill(*GameBall.ball_colors[0]) if not stroke_mode else fill(*self.white_color)
                circle(self.corner_pocket_width * scaling / 2, 0, self.corner_pocket_width / 4 * scaling)

            line(0, 0, 0, self.corner_pocket_width * scaling / 2)
            line(self.corner_pocket_width * scaling, 0, self.corner_pocket_width * scaling,
                 self.corner_pocket_width * scaling / 2)

            pop()

        offset = math.sqrt(self.corner_pocket_width ** 2 / 2)

        SE_highlighted = "SE" in highlighted_pockets
        E_highlighted = "E" in highlighted_pockets
        NE_highlighted = "NE" in highlighted_pockets
        NW_highlighted = "NW" in highlighted_pockets
        W_highlighted = "W" in highlighted_pockets
        SW_highlighted = "SW" in highlighted_pockets

        draw_corner_pocket(PI / 4 * 1, (
            (self.wood_width + 2 * self.rail_width + self.board_width - offset) * scaling,
            self.wood_width * scaling), SE_highlighted)  # SE
        draw_side_pocket(PI / 4 * 2, ((self.width - self.wood_width - self.rail_width) * scaling, (
                self.board_pos + self.board_length / 2 - self.side_pocket_width / 2) * scaling), E_highlighted)  # E
        draw_corner_pocket(PI / 4 * 3, (
            (self.width - self.wood_width) * scaling, (self.length - self.wood_width - offset) * scaling),
                           NE_highlighted)  # NE
        draw_side_pocket(PI / 4 * 6, (self.board_pos * scaling, (
                self.board_pos + self.board_length / 2 + self.side_pocket_width / 2) * scaling), W_highlighted)  # W
        draw_corner_pocket(PI / 4 * 5,
                           ((self.wood_width + offset) * scaling, (self.length - self.wood_width) * scaling),
                           NW_highlighted)  # NW
        draw_corner_pocket(PI / 4 * 7, (self.wood_width * scaling, (self.wood_width + offset) * scaling),
                           SW_highlighted)  # SW

        if shot_params:
            stroke(*self.board_marking_color) if not stroke_mode else stroke(*self.black_color)
            strokeWeight(8)
            for ball in self.game_balls:
                if ball.number == 0 and ball.state == 1:
                    push()
                    translate((ball.position.x + self.rail_width + self.wood_width) * scaling,
                              (ball.position.y + self.rail_width + self.wood_width) * scaling)
                    push()
                    rotate(shot_params.phi * PI / 180)
                    length = GameBall.RADIUS * scaling + shot_params.v * 20
                    line(0, 0, length, 0)
                    pop()
                    pop()
                    break
            strokeWeight(stroke_weight)

        noStroke() if not stroke_mode else stroke(*self.black_color)

        # Balls
        push()
        translate(int(self.board_pos * scaling),
                  int(self.board_pos * scaling))
        for ball in self.game_balls:
            ball.draw(scaling, horizontal_mode, flipped, stroke_mode, highlighted_balls)
        pop()

        pop()

        if canvas:
            p5.renderer = old_canvas

    def draw_shot_tree(self, shot_tree: api_pb2.Shot, scaling=200, horizontal_mode=False, flipped=False,
                       stroke_weight=2, canvas=None, depth=1):
        if canvas:
            old_canvas = p5.renderer
            p5.renderer = canvas

        push()

        if horizontal_mode:
            rotate(PI / 2)
            translate(0, -int(self.length * scaling))

        if flipped:
            translate(0, int(self.length * scaling))
            scale(1, -1)

        translate(int(self.board_pos * scaling),
                  int(self.board_pos * scaling))

        strokeWeight(stroke_weight)
        noFill()

        # Leftmost
        lm = shot_tree.leftMost
        stroke(*self.red_color)
        circle(lm.x * scaling, lm.y * scaling, GameBall.RADIUS * 2 * scaling)

        # Rightmost
        rm = shot_tree.rightMost
        stroke(*self.blue_color)
        circle(rm.x * scaling, rm.y * scaling, GameBall.RADIUS * 2 * scaling)

        # GhostBall
        rm = shot_tree.rightMost
        stroke(*self.black_color)
        circle(shot_tree.ghostBall.x * scaling, shot_tree.ghostBall.y * scaling, GameBall.RADIUS * 2 * scaling)

        if shot_tree.next.IsInitialized():
            # Lines
            stroke(*self.red_color)
            line(rm.x * scaling, rm.y * scaling, shot_tree.next.leftMost.x * scaling,
                 shot_tree.next.leftMost.y * scaling)
            stroke(*self.blue_color)
            line(lm.x * scaling, lm.y * scaling, shot_tree.next.rightMost.x * scaling,
                 shot_tree.next.rightMost.y * scaling)

            # Id tag
            stroke(*self.black_color)
            push()
            text_x_pos = shot_tree.ghostBall.x * scaling + (shot_tree.next.ghostBall.x - shot_tree.ghostBall.x) * scaling / 2
            text_y_pos = shot_tree.ghostBall.y * scaling + (shot_tree.next.ghostBall.y - shot_tree.ghostBall.y) * scaling / 2

            mag = math.sqrt(text_x_pos**2 + text_y_pos**2)

            offset_x = text_y_pos / mag * (scaling * 0.08)
            offset_y = -text_x_pos / mag * (scaling * 0.08)

            text_x_pos += offset_x
            text_y_pos += offset_y

            translate(int(text_x_pos), int(text_y_pos))
            if horizontal_mode:
                rotate(-PI / 2)

            if flipped:
                scale(1, -1)

            text_align(CENTER, CENTER)
            ts = int(scaling / 30)
            textSize(ts)
            fill(*GameBall.ball_colors[ff.Ball.EIGHT])
            noStroke()
            text(str(shot_tree.next.id), 0, ts * 0.80)
            pop()

            pop()
            self.draw_shot_tree(shot_tree.next, scaling, horizontal_mode, flipped, stroke_weight, canvas, depth=depth+1)
        else:
            pop()

        if canvas:
            p5.renderer = old_canvas

    def update(self, shot_requester: Optional[Callable[None, None]]):
        if self._active_shot is None:
            if self._shot_queue:
                self._active_shot = self._shot_queue.pop(0)
                self._active_shot_start_time = time.time()
            else:
                if shot_requester:
                    shot_requester()
                return

        time_since_shot_start = (time.time() - self._active_shot_start_time) * self._shot_speed_factor

        if time_since_shot_start > self._active_shot[1].getDuration():
            for ball in self.game_balls:
                ball.force_to_end_of_shot_pos(self._active_shot[1])
            self._active_shot[2]()
            self._active_shot = None
            return

        else:
            for ball in self.game_balls:
                ball.update(time_since_shot_start, self._active_shot[1], self.sliding_friction_const,
                            self.rolling_friction_const,
                            self.gravitational_const)

    def add_shot(self, params: ff.ShotParams, shot: ff.Shot, callback: Callable[None, None]):
        self._shot_queue.append((params, shot, callback))
