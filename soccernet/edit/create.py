from typing import List, Dict, Tuple
from edit.type_def import *
import edit.convert_take as con

# BBox作成
def create_bbox(
    e_x_bottom_left : float = 0.0, e_y_bottom_left : float = 0.0, e_x_bottom_right : float = 0.0,
    e_y_bottom_right : float = 0.0, e_x_bottom_middle : float = 0.0, e_y_bottom_middle : float = 0.0
) -> BBoxPitch:
    bbox : BBoxPitch = {
        "x_bottom_left" : e_x_bottom_left,
        "y_bottom_left" : e_y_bottom_left,
        "x_bottom_right" : e_x_bottom_right,
        "y_bottom_right" : e_y_bottom_right,
        "x_bottom_middle" : e_x_bottom_middle,
        "y_bottom_middle" : e_y_bottom_middle
    }
    return bbox

# エントリー作成
def create_entry(
    e_bbox : BBoxPitch = None, e_track_id : float = 0.0,
    e_jersey : str = "", e_role : str = "player", e_team : str = ""
) -> Entry:
    entry : Entry = {
        "bbox_pitch": e_bbox,
        "track_id" : e_track_id,
        "jersey" : e_jersey,
        "role" : e_role,
        "team" : e_team
    }
    return entry

# 試合データの作成
def create_player_lists(formations_left : Formations, formations_right : Formations):
    player_lists_left : PlayerLists = {}
    player_lists_right : PlayerLists = {}

    for (data_num, start_frame), formation in formations_left.items():
        player_list : PlayerList = {}
        line_num = -len(formation)
        for jerseis in formation:
            side_num = len(jerseis)
            for jersey in jerseis:
                player_list[jersey] = {
                    "position": (line_num, side_num),
                    "location": [],
                    "relation": {},
                }
                side_num -= 1
            line_num += 1
        player_lists_left[(data_num, start_frame)] = player_list
    
    for (data_num, start_frame), formation in formations_right.items():
        player_list : PlayerList = {}
        line_num = len(formation)
        for jerseis in formation:
            side_num = 1
            for jersey in jerseis:
                player_list[jersey] = {
                    "position": (line_num, side_num),
                    "location": [],
                    "relation": {},
                }
                side_num += 1
            line_num -= 1
        player_lists_right[(data_num, start_frame)] = player_list

    return player_lists_left, player_lists_right

# 座標時系列データの作成
def create_trajectories(
    formations_left : Formations, formations_right : Formations, replay_frames : Frame
) -> Tuple[Trajectories, Trajectories]:
    trajectories_left : Trajectories = {}
    trajectories_right : Trajectories = {}
    formation_left : Formation = []
    formation_right : Formation = []

    for data_num, (start_frame, end_frame) in replay_frames.items():
        trajectory : Trajectory = {}
        if (data_num, start_frame) in formations_left:
            formation_left = formations_left[(data_num, start_frame)]
        for jerseis in formation_left:
            for jersey in jerseis:
                trajectory[jersey] = []
        trajectories_left[(data_num, start_frame)] = trajectory

    for data_num, (start_frame, end_frame) in replay_frames.items():
        trajectory : Trajectory = {}
        if (data_num, start_frame) in formations_right:
            formation_right = formations_right[(data_num, start_frame)]
        for jerseis in formation_right:
            for jersey in jerseis:
                trajectory[jersey] = []
        trajectories_right[(data_num, start_frame)] = trajectory
    
    return trajectories_left, trajectories_right

# 座標変換
def coordinate_location(location: List[float], period_num: int) -> List[float]:
    if period_num == 1:
        location[0] *= -1
    else:
        location[1] *= -1
    location[0] += pitch_width / 2
    location[1] += pitch_length / 2
    return location

# 単純化データ作成
def create_simple_data(data_list: List[Data], period_num: int) -> SimpleData:
    simple_data : SimpleData = {}
    for data_num, data in enumerate(data_list):
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
            time = con.conver_num_to_time(data_num, frame_num)
            for entry in frame_data:
                location, track_id, jersey, team = con.take_entry_info(entry)
                if location == "":
                    continue
                if time not in simple_data:
                    simple_data[time] = []
                location = coordinate_location(location, period_num)
                simple_data[time].append({
                    "location": location,
                    "jersey": jersey,
                    "team": team
                })
    return simple_data