from math import fabs
from cv2 import norm
from p5 import *
import fastfiz as ff
from pygame import Vector2
import vectormath as vmath
from .DevUtils import MathUtils as mu


class GameBall:
    RADIUS = 0.028575

    ball_colors = {
        0: (227, 228, 230),  # White
        1: (234, 220, 93),  # Yellow
        2: (56, 121, 171),  # Blue
        3: (219, 72, 65),  # Red
        4: (137, 133, 171),  # Purple
        5: (230, 140, 72),  # Orange
        6: (75, 133, 88),  # Green
        7: (165, 67, 67),  # Dark red
        8: (32, 30, 31),  # Black
    }

    def __init__(self, radius: float, number: int, position: vmath.Vector2, velocity: vmath.Vector3, spin: vmath.Vector3, state: int):
        self.radius = radius
        self.number = number
        self.position = position
        self.velocity = velocity
        self.spin = spin
        self.state = state
        self.color = GameBall.ball_colors[number if number <= 8 else number - 8]
        self.striped = number > 8
        self.is_being_dragged = False

        self.white_color = (255, 255, 255)
        self.black_color = (0, 0, 0)

    def draw(self, scaling=200, horizontal_mode=False, flipped=False, stroke_mode=False):
        dont_draw_states = [ff.Ball.NOTINPLAY, ff.Ball.POCKETED_NE, ff.Ball.POCKETED_E, ff.Ball.POCKETED_SE,
                            ff.Ball.POCKETED_SW, ff.Ball.POCKETED_W, ff.Ball.POCKETED_NW]

        if self.state in dont_draw_states:
            return

        if self.is_being_dragged:
            stroke(*self.black_color)
            strokeWeight(4)

        fill(*self.color) if not stroke_mode else fill(*self.white_color)
        circle(self.position.x * scaling, self.position.y * scaling, GameBall.RADIUS * scaling * 2)

        if self.is_being_dragged:
            noStroke() if not stroke_mode else strokeWeight(1)

        if self.striped and not stroke_mode:
            fill(*GameBall.ball_colors[ff.Ball.CUE])
            circle(self.position.x * scaling, self.position.y * scaling, 0.02 * scaling)

        if stroke_mode:
            push()
            translate(self.position.x * scaling, self.position.y * scaling)

            if horizontal_mode:
                rotate(-PI / 2)

            if flipped:
                scale(1, -1)

            ts = int(scaling / 30)
            textSize(ts)
            fill(*GameBall.ball_colors[ff.Ball.EIGHT])
            text(str(self.number), 0, ts * 0.8)
            pop()

    def update(self, time_since_shot_start: float, shot: ff.Shot, sliding_friction_const: float,
               rolling_friction_const: float, gravitational_const: float):
        relevant_states = self._get_relevant_ball_states_from_shot(shot)

        if not relevant_states:
            return

        cur_state: _BallState = relevant_states[0]

        if cur_state.e_time > time_since_shot_start:
            return

        for state in relevant_states:
            if cur_state.e_time < state.e_time <= time_since_shot_start:
                cur_state = state

        time_since_event_start = time_since_shot_start - cur_state.e_time

        def calc_sliding_displacement(delta_time: float) -> vmath.Vector2:
            rotational_velocity: vmath.Vector3 = GameBall.RADIUS * vmath.Vector3(0, 0, cur_state.ang_vel.z).cross(
                cur_state.ang_vel)
            relative_velocity = cur_state.vel + vmath.Vector2(rotational_velocity.x, rotational_velocity.y)
            self.velocity = cur_state.vel - delta_time * gravitational_const * sliding_friction_const * relative_velocity.normalize()
            return cur_state.vel * delta_time - 0.5 * sliding_friction_const * gravitational_const * delta_time ** 2 * relative_velocity.normalize()

        def calc_rolling_displacement(delta_time: float) -> vmath.Vector2:
            self.velocity = cur_state.vel - gravitational_const * rolling_friction_const *  delta_time * cur_state.vel.copy().normalize()
            return cur_state.vel * delta_time - 0.5 * rolling_friction_const * gravitational_const * delta_time ** 2 * cur_state.vel.copy().normalize()

        displacement = vmath.Vector2(0, 0)

        if cur_state.state == ff.Ball.ROLLING:
            displacement = calc_rolling_displacement(time_since_event_start)
        if cur_state.state == ff.Ball.SLIDING:
            displacement = calc_sliding_displacement(time_since_event_start)

        self.position = displacement + cur_state.pos
        self.state = cur_state.state

    def fastfiz_update(self, shot: ff.Shot, old_time: float, new_time: float, sliding_friction_const: float, 
                       rolling_friction_const: float, spinning_friction_const: float, gravitational_const: float):
        if not (self.state == ff.Ball.SPINNING or self.state == ff.Ball.ROLLING or self.state == ff.Ball.SLIDING):
            return
        
        r: vmath.Vector2 = self.position
        v: vmath.Vector3 = self.velocity
        w: vmath.Vector3 = self.spin
        t: float = new_time - old_time
        mu_sp: float = spinning_friction_const
        mu_r: float = rolling_friction_const
        mu_s: float = sliding_friction_const
        u_o: vmath.Vector3
        v_norm: vmath.Vector3
        new_r: vmath.Vector2 = r
        new_v: vmath.Vector3 = v
        new_w: vmath.Vector3 = w

        cos_phi: float = 1.0 
        sin_phi: float = 0.0

        if (mu.vec_mag(v) > 0):
            v_norm = mu.vec_norm(v)
            cos_phi = v_norm.x
            sin_phi = v_norm.y

            v = mu.vec_rotate(v, cos_phi, -sin_phi)
            w = mu.vec_rotate(w, cos_phi, -sin_phi)
        
        if (self.state == ff.Ball.SPINNING):
            new_w.x = 0
            new_w.y = 0
            new_w.z = self.update_spinning(w.z, t, mu_sp, gravitational_const, False)
        elif (self.state == ff.Ball.SLIDING):
            mu_s = sliding_friction_const
            u_o = mu.vec_norm((v.sum(vmath.Vector3(0, 0, 1).cross(w) * self.radius)))
            new_r.x = mu.vec_mag(v) * t - (0.5) * mu_s * gravitational_const * t * t * u_o.x
            new_r.y = -(0.5) * mu_s * gravitational_const * t * t * u_o.y
            new_v = v.sum(u_o * (-mu_s * gravitational_const * t))
            new_w = w.sum(u_o.cross(vmath.Vector3(0, 0, 1)) * 
                          (-(5.0 * mu_s * gravitational_const) / (2.0 * self.radius) * t))
            new_r = mu.point_rotate(new_r, cos_phi, sin_phi)
            new_r = new_r.sum(r)
            new_v = mu.vec_rotate(new_v, cos_phi, sin_phi)
            new_w = mu.vec_rotate(new_w, cos_phi, sin_phi)
        elif (self.state == ff.Ball.ROLLING):
            v_norm = mu.vec_norm(v)

            mu_r = rolling_friction_const
            new_r = (v * t).sum(v_norm * (-(0.5) * mu_r * gravitational_const * t * t))
            new_v = v.sum(v_norm * (-mu_r * gravitational_const * t))
            new_w = w * (mu.vec_mag(new_v) / mu.vec_mag(v))
            new_w.z = self.update_spinning(w.z, t, mu_sp, gravitational_const, False)

            new_r = mu.point_rotate(new_r, cos_phi, sin_phi)
            new_r = new_r.sum(r)
            new_v = mu.vec_rotate(new_v, cos_phi, sin_phi)
            new_w = mu.vec_rotate(new_w, cos_phi, sin_phi)
        else:
            return
        
        if (mu.fequal(new_v.x, 0)):
            new_v.x = 0
        if (mu.fequal(new_v.y, 0)):
            new_v.y = 0
        if (mu.fequal(new_v.z, 0)):
            new_v.z = 0
        if (mu.fequal(new_w.x, 0)):
            new_w.x = 0
        if (mu.fequal(new_w.y, 0)):
            new_w.y = 0
        if (mu.fequal(new_w.z, 0)):
            new_w.z = 0
        
        self.position = new_r
        self.velocity = new_v
        self.spin = new_w
        self.state = self.update_state()

    def update_state(self):
        new_state: int
        u: vmath.Vector3 = self.velocity.sum(((vmath.Vector3(0, 0, 1)).cross(self.spin)) * self.radius)
        new_v: vmath.Vector3 = self.velocity
        new_w: vmath.Vector3 = self.spin

        if not mu.vzero(mu.vec_mag(self.velocity)):
            if not mu.vzero(mu.vec_mag(u)):
                new_state = ff.Ball.SLIDING
            else:
                new_state = ff.Ball.ROLLING
        else:
            if not mu.vzero(mu.vec_mag(self.spin.z)):
                new_state = ff.Ball.SPINNING
                new_w.x = 0
                new_w.y = 0
            else:
                new_state = ff.Ball.STATIONARY
                new_v = vmath.Vector3(0, 0, 0)
                new_w = vmath.Vector3(0, 0, 0)    
        
        self.state = new_state
        self.velocity = new_v
        self.spin = new_w

    def update_spinning(self, w_z: float, t: float, mu_sp: float, gravitional_const: float, isSliding: bool):
        if mu.fequal(w_z, 0):
            return 0
        new_w_z: float = w_z - 5 * mu_sp * gravitional_const * t / (2 * self.radius) * (1 if w_z > 0 else -1) * (0.25 if isSliding else 1)
        if (new_w_z * w_z) <= 0.0:
            new_w_z = 0
        return new_w_z
        

    def force_to_end_of_shot_pos(self, shot: ff.Shot):
        relevant_states = self._get_relevant_ball_states_from_shot(shot)
        if relevant_states:
            self.velocity = vmath.Vector2(0, 0)
            self.position = relevant_states[-1].pos
            self.state = relevant_states[-1].state

    def is_mouse_over(self, scaling: int, offset: vmath.Vector2):
        virtual_pos = vmath.Vector2(mouse_x, mouse_y) / scaling - offset
        d = dist((self.position.x, self.position.y, 0), (virtual_pos.x, virtual_pos.y, 0))
        hovered = d < GameBall.RADIUS
        return hovered

    def _get_relevant_ball_states_from_shot(self, shot: ff.Shot):
        relevant_states: list[_BallState] = []

        for event in shot.getEventList():
            event: ff.Event
            if event.getBall1() == self.number:
                new_ball_event = _BallState.from_event_and_ball(event, event.getBall1Data())
                relevant_states.append(new_ball_event)
            elif event.getBall2() == self.number:
                new_ball_event = _BallState.from_event_and_ball(event, event.getBall2Data())
                relevant_states.append(new_ball_event)

        return relevant_states


class _BallState:
    def __init__(self, e_time: float, pos: vmath.Vector2, vel: vmath.Vector2, ang_vel: vmath.Vector3, state: int,
                 state_str: str,
                 event_course: int):
        self.e_time = e_time
        self.pos = pos
        self.vel = vel
        self.ang_vel = ang_vel
        self.state = state
        self.state_str = state_str
        self.event_course = event_course

    @classmethod
    def from_event_and_ball(cls, event: ff.Event, ball: ff.Ball):
        e_time = event.getTime()
        pos = ball.getPos()
        vel = ball.getVelocity()
        ang_vel = ball.getSpin()
        state = ball.getState()
        state_str = ball.getStateString()
        event_course = event.getType()
        return cls(e_time, vmath.Vector2([pos.x, pos.y]), vmath.Vector2([vel.x, vel.y]),
                   vmath.Vector3([ang_vel.x, ang_vel.y, ang_vel.z]), state, state_str, event_course)

    def __str__(self):
        return (f"Time: {self.e_time:.3f},\t "
                f"Pos: ({self.pos.x:.3f}, {self.pos.y:.3f}),\t "
                f"Vel: ({self.vel.x:.3f}, {self.vel.y:.3f}),\t "
                f"State: {self.state_str}")
