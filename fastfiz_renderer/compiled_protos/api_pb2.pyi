from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShotType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CUE_STRIKE: _ClassVar[ShotType]
    POCKET: _ClassVar[ShotType]
    RAIL: _ClassVar[ShotType]
    STRIKE: _ClassVar[ShotType]
    KISS_LEFT: _ClassVar[ShotType]
    KISS_RIGHT: _ClassVar[ShotType]
    BALL_BOTH: _ClassVar[ShotType]
CUE_STRIKE: ShotType
POCKET: ShotType
RAIL: ShotType
STRIKE: ShotType
KISS_LEFT: ShotType
KISS_RIGHT: ShotType
BALL_BOTH: ShotType

class ShowShotsRequest(_message.Message):
    __slots__ = ("tableState", "shots")
    TABLESTATE_FIELD_NUMBER: _ClassVar[int]
    SHOTS_FIELD_NUMBER: _ClassVar[int]
    tableState: TableState
    shots: _containers.RepeatedCompositeFieldContainer[Shot]
    def __init__(self, tableState: _Optional[_Union[TableState, _Mapping]] = ..., shots: _Optional[_Iterable[_Union[Shot, _Mapping]]] = ...) -> None: ...

class ShowGamesRequest(_message.Message):
    __slots__ = ("games",)
    GAMES_FIELD_NUMBER: _ClassVar[int]
    games: _containers.RepeatedCompositeFieldContainer[Game]
    def __init__(self, games: _Optional[_Iterable[_Union[Game, _Mapping]]] = ...) -> None: ...

class Game(_message.Message):
    __slots__ = ("turnHistory",)
    TURNHISTORY_FIELD_NUMBER: _ClassVar[int]
    turnHistory: _containers.RepeatedCompositeFieldContainer[GameTurn]
    def __init__(self, turnHistory: _Optional[_Iterable[_Union[GameTurn, _Mapping]]] = ...) -> None: ...

class GameTurn(_message.Message):
    __slots__ = ("turnType", "agentName", "tableStateBefore", "tableStateAfter", "gameShot", "shotResult")
    TURNTYPE_FIELD_NUMBER: _ClassVar[int]
    AGENTNAME_FIELD_NUMBER: _ClassVar[int]
    TABLESTATEBEFORE_FIELD_NUMBER: _ClassVar[int]
    TABLESTATEAFTER_FIELD_NUMBER: _ClassVar[int]
    GAMESHOT_FIELD_NUMBER: _ClassVar[int]
    SHOTRESULT_FIELD_NUMBER: _ClassVar[int]
    turnType: str
    agentName: str
    tableStateBefore: TableState
    tableStateAfter: TableState
    gameShot: GameShot
    shotResult: str
    def __init__(self, turnType: _Optional[str] = ..., agentName: _Optional[str] = ..., tableStateBefore: _Optional[_Union[TableState, _Mapping]] = ..., tableStateAfter: _Optional[_Union[TableState, _Mapping]] = ..., gameShot: _Optional[_Union[GameShot, _Mapping]] = ..., shotResult: _Optional[str] = ...) -> None: ...

class GameShot(_message.Message):
    __slots__ = ("shotParams", "decision", "ballTarget", "pocketTarget", "cuePos")
    SHOTPARAMS_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    BALLTARGET_FIELD_NUMBER: _ClassVar[int]
    POCKETTARGET_FIELD_NUMBER: _ClassVar[int]
    CUEPOS_FIELD_NUMBER: _ClassVar[int]
    shotParams: ShotParams
    decision: str
    ballTarget: str
    pocketTarget: str
    cuePos: Point
    def __init__(self, shotParams: _Optional[_Union[ShotParams, _Mapping]] = ..., decision: _Optional[str] = ..., ballTarget: _Optional[str] = ..., pocketTarget: _Optional[str] = ..., cuePos: _Optional[_Union[Point, _Mapping]] = ...) -> None: ...

class ShotParams(_message.Message):
    __slots__ = ("a", "b", "phi", "theta", "v")
    A_FIELD_NUMBER: _ClassVar[int]
    B_FIELD_NUMBER: _ClassVar[int]
    PHI_FIELD_NUMBER: _ClassVar[int]
    THETA_FIELD_NUMBER: _ClassVar[int]
    V_FIELD_NUMBER: _ClassVar[int]
    a: float
    b: float
    phi: float
    theta: float
    v: float
    def __init__(self, a: _Optional[float] = ..., b: _Optional[float] = ..., phi: _Optional[float] = ..., theta: _Optional[float] = ..., v: _Optional[float] = ...) -> None: ...

class TableState(_message.Message):
    __slots__ = ("balls",)
    BALLS_FIELD_NUMBER: _ClassVar[int]
    balls: _containers.RepeatedCompositeFieldContainer[Ball]
    def __init__(self, balls: _Optional[_Iterable[_Union[Ball, _Mapping]]] = ...) -> None: ...

class Ball(_message.Message):
    __slots__ = ("pos", "number", "state")
    POS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    pos: Point
    number: int
    state: int
    def __init__(self, pos: _Optional[_Union[Point, _Mapping]] = ..., number: _Optional[int] = ..., state: _Optional[int] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class Shot(_message.Message):
    __slots__ = ("type", "next", "branch", "posB1", "ghostBall", "leftMost", "rightMost", "b1", "b2", "id")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    POSB1_FIELD_NUMBER: _ClassVar[int]
    GHOSTBALL_FIELD_NUMBER: _ClassVar[int]
    LEFTMOST_FIELD_NUMBER: _ClassVar[int]
    RIGHTMOST_FIELD_NUMBER: _ClassVar[int]
    B1_FIELD_NUMBER: _ClassVar[int]
    B2_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    type: ShotType
    next: Shot
    branch: Shot
    posB1: Point
    ghostBall: Point
    leftMost: Point
    rightMost: Point
    b1: int
    b2: int
    id: int
    def __init__(self, type: _Optional[_Union[ShotType, str]] = ..., next: _Optional[_Union[Shot, _Mapping]] = ..., branch: _Optional[_Union[Shot, _Mapping]] = ..., posB1: _Optional[_Union[Point, _Mapping]] = ..., ghostBall: _Optional[_Union[Point, _Mapping]] = ..., leftMost: _Optional[_Union[Point, _Mapping]] = ..., rightMost: _Optional[_Union[Point, _Mapping]] = ..., b1: _Optional[int] = ..., b2: _Optional[int] = ..., id: _Optional[int] = ...) -> None: ...
