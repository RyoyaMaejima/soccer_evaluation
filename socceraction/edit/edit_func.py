import pandas as pd
from typing import List, Dict, Tuple
from edit.type_def import *
import edit.convert_take as con
import edit.create as cre
import edit.math_func as mf

# 座標補正（平行移動）
def edit_location_by_translation(a_loc : List[float], pred_loc : List[float], location_data : LocationData) -> None:
    sub_vector = mf.calc_sub(a_loc, pred_loc)
    for player_name, simple_info in location_data.items():
        simple_info["location"] = mf.calc_add(simple_info["location"], sub_vector)

# アクション範囲内かどうかを判定
def calc_is_in_ranges(action_num: int, delete_ranges: DeleteRanges) -> bool:
    for delete_range in delete_ranges:
        if delete_range[0] <= action_num <= delete_range[1]:
            return False
    return True

# 自動補正
def edit_data_auto(actions : pd.DataFrame, location_data_list : List[LocationData], delete_ranges: DeleteRanges) -> None:
    for action_num in range(len(actions)):
        a = actions.iloc[action_num]
        a_time = a.time_seconds
        a_loc = [a["start_x"], a["start_y"]]
        a_player_name = a["player_name"]

        location_data = location_data_list[action_num]
        if a_player_name in location_data:
            pred_loc = location_data[a_player_name]["location"]
            if calc_is_in_ranges(action_num, delete_ranges):
                edit_location_by_translation(a_loc, pred_loc, location_data)

# コーナー情報の追加
def add_corner_infos(location_data_list : List[LocationData], player_infos : PlayerInfos, corner_infos : CornerInfos) -> None:
    for (start_action_num, end_action_num), (player_name, location) in corner_infos.items():
        team_name, jersey, position, rating = con.take_player_info(player_infos[player_name])
        simple_info = cre.create_simple_info(location, jersey, team_name)
        for action_num in range(start_action_num, end_action_num + 1):
            location_data = location_data_list[action_num]
            location_data[player_name] = simple_info

# 座標が欠損している選手の情報を取得
def get_lack_players(location_data_list : List[LocationData], field_players : FieldPlayers) -> FieldPlayers:
    lack_players : FieldPlayers = {}
    field_player = field_players[0]
    for action_num, location_data in enumerate(location_data_list):
        if action_num in field_players:
            field_player = field_players[action_num]
        for player_name in field_player:
            if player_name not in location_data:
                if action_num not in lack_players:
                    lack_players[action_num] = []
                lack_players[action_num].append(player_name)
    return lack_players

# 欠損選手の補間
def interpolate_data(location_data_list : List[LocationData], field_players : FieldPlayers) -> None:
    lack_players : FieldPlayers = get_lack_players(location_data_list, field_players)
    for action_num, player_names in lack_players.items():
        for player_name in player_names:
            location_data = location_data_list[action_num]
            for prev_action_num in range(action_num, -1, -1):
                prev_location_data = location_data_list[prev_action_num]
                if player_name in prev_location_data:
                    p_location, p_jersey, p_team_name = con.take_simple_info(prev_location_data[player_name])
                    common =  set(location_data.keys()) & set(prev_location_data.keys())
                    if common:
                        c_player = next(iter(common))
                        sub_vector = mf.calc_sub(p_location, prev_location_data[c_player]["location"])
                        pred_loc = mf.calc_add(location_data[c_player]["location"], sub_vector)
                        location_data[player_name] = cre.create_simple_info(pred_loc, p_jersey, p_team_name)

# アクション数の削減
def reduct_actions(location_data_list : List[LocationData], delete_ranges : DeleteRanges) -> None:
    for delete_range in delete_ranges:
        for action_num in range(delete_range[0], delete_range[1] + 1):
            location_data = location_data_list[action_num]
            for player_name, simple_info in location_data.items():
                simple_info["location"] = mf.create_nan_location()