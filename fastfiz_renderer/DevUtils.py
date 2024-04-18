from math import fabs
from random import random
from typing import Optional, Callable
import vectormath as vmath

import fastfiz as ff


class DevTableStates:
    @staticmethod
    def get_one_ball_state():
        game_state: ff.GameState = ff.GameState.RackedState(ff.GT_EIGHTBALL)
        table_state: ff.TableState = game_state.tableState()
        for i in range(ff.Ball.ONE, ff.Ball.FIFTEEN + 1):
            table_state.setBall(i, ff.Ball.NOTINPLAY, 0, 0)
        return table_state

    @staticmethod
    def get_two_ball_state():
        game_state: ff.GameState = ff.GameState.RackedState(ff.GT_EIGHTBALL)
        table_state: ff.TableState = game_state.tableState()
        for i in range(ff.Ball.TWO, ff.Ball.FIFTEEN + 1):
            table_state.setBall(i, ff.Ball.NOTINPLAY, table_state.getBall(i).getPos())
        return table_state


class DevShotDeciders:
    @staticmethod
    def get_from_shot_params_list(shot_params_list: list[ff.ShotParams]) -> Callable[
        [ff.TableState], Optional[ff.ShotParams]]:
        def decider(_: ff.TableState) -> Optional[ff.ShotParams]:
            if shot_params_list:
                return shot_params_list.pop(0)
            else:
                return None

        return decider

    @staticmethod
    def biased_north_shot_decider(_: ff.TableState) -> ff.ShotParams:
        shot_params = ff.ShotParams()
        shot_params.v = 1.5
        shot_params.a = 0
        shot_params.b = 0
        shot_params.phi = 260 + random() * 20
        shot_params.theta = 11
        return shot_params

    @staticmethod
    def north_shot_decider(_: ff.TableState) -> ff.ShotParams:
        shot_params = ff.ShotParams()
        shot_params.v = 1.5
        shot_params.a = 0
        shot_params.b = 0
        shot_params.phi = 270
        shot_params.theta = 11
        return shot_params

    @staticmethod
    def hole_shot_decider(_: ff.TableState) -> ff.ShotParams:
        shot_params = ff.ShotParams()
        shot_params.v = 1
        shot_params.a = 0
        shot_params.b = 0
        shot_params.phi = 45
        shot_params.theta = 11
        return shot_params

class MathUtils:

    EPSILON = 1.0E-11
    VELOCITY_EPSILON = 1E-10

    @staticmethod
    def vec_mag(vec: vmath.Vector3) -> float:
        return (vec.x ** 2 + vec.y ** 2 + vec.z ** 2) ** 0.5

    @staticmethod
    def vec_norm(vec: vmath.Vector3) -> vmath.Vector3:
        mag = MathUtils.vec_mag(vec)
        assert mag > 0
        return vmath.Vector3([vec.x / mag, vec.y / mag, vec.z / mag]) 
        
    
    @staticmethod
    def vec_rotate(vec: vmath.Vector3, cos_phi: float, sin_phi: float) -> vmath.Vector3:
        return vmath.Vector3([vec.x * cos_phi - vec.y * sin_phi, vec.x * sin_phi + vec.y * cos_phi, vec.z])
    
    @staticmethod
    def vec_to_point(vec: vmath.Vector3) -> vmath.Vector2:
        return vmath.Vector2([vec.x, vec.y])
    
    @staticmethod
    def point_rotate(point: vmath.Vector2, cos_phi: float, sin_phi: float) -> vmath.Vector2:
        return vmath.Vector2([point.x * cos_phi - point.y * sin_phi, point.x * sin_phi + point.y * cos_phi])
    
    @staticmethod
    def fequal(a: float, b: float) -> bool:
        return (fabs(a - b) < MathUtils.EPSILON)
    
    @staticmethod
    def vzero(a: float) -> bool:
        return (fabs(a) < MathUtils.VELOCITY_EPSILON)