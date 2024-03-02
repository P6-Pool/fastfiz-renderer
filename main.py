import os

from DevUtils import DevShotDeciders, DevTableStates
from GameHandler import GameHandler


def main():
    os.environ['SDL_VIDEO_WINDOW_POS'] = "100, 100"

    shot_decider = DevShotDeciders.get_north_shot_decider

    game_handler = GameHandler()
    game_handler.play_eight_ball(shot_decider, frames_per_second=120)
    # game_handler.play_game_from_table_state(DevTableStates.get_one_ball_state(), shot_decider)


if __name__ == '__main__':
    main()
