import pandas as pd
import numpy as np
import copy
from typing import List, Dict, Tuple
from edit.type_def import *
import edit.convert_take as con

# ある時刻から最も近いフレームを取得
def get_frame_by_time(simple_data : SimpleData, time : float) -> str:
    time = round(time / time_interval) * time_interval
    frame_time = con.convert_time_to_string(time)
    if frame_time in simple_data:
        return frame_time
    else:
        before_time = time - time_interval
        after_time = time + time_interval
        while before_time >= 0:
            frame_time = con.convert_time_to_string(before_time)
            if frame_time in simple_data:
                return frame_time
            frame_time = con.convert_time_to_string(after_time)
            if frame_time in simple_data:
                return frame_time
            before_time -= time_interval
            after_time += time_interval
        return ""

# simple_info作成
def create_simple_info(location, jersey, team) -> SimpleInfo:
    simple_info : SimpleInfo = {
        "location" : location,
        "jersey" : jersey,
        "team" : team
    }
    return simple_info

# アクションデータに入れる用の座標データを作成
def create_location_data(
    actions : pd.DataFrame, simple_data_1 : SimpleData, simple_data_2 : SimpleData, team_names : TeamNames, player_names : PlayerNames
) -> List[LocationData]:
    location_data_list : List[LocationData] = []
    simple_data : SimpleData = {}

    for action_num in range(len(actions)):
        a = actions.iloc[action_num]
        a_time = a.time_seconds
        period_id = a.period_id
        if period_id == 1:
            simple_data = simple_data_1
        elif period_id == 2:
            simple_data = simple_data_2
        
        location_data : LocationData = {}
        frame_time = get_frame_by_time(simple_data, a_time)
        if frame_time != "":
            simple_info_list = simple_data[frame_time]
            for simple_info in simple_info_list:
                location, jersey, team = con.take_simple_info(simple_info)
                if (team == "left" and period_id == 1) or (team == "right" and period_id == 2):
                    team_name = team_names["left"]
                else:
                    team_name = team_names["right"]
                player_name = player_names[team_name][jersey]
                location_data[player_name] = create_simple_info(location, jersey, team_name)
        else:
            print(f"action_num: {action_num}, time: {a_time} not found in simple_data")
        location_data_list.append(location_data)

    return location_data_list

# キーパー情報の作成
def create_keepers(player_infos : PlayerInfos) -> List[str]:
    keepers : List[str] = []
    for player_name, player_info in player_infos.items():
        team_name, jersey, position, rating = con.take_player_info(player_info)
        if position == "GK":
            keepers.append(player_name)
    return keepers

# ベンチ情報の作成
def create_benches(substitutions : SubStitutions) -> List[str]:
    benches : List[str] = []
    for (in_player_name, out_player_name) in substitutions:
        benches.append(in_player_name)
    return benches

# 選手が初めて出るaction_numの取得
def get_player_in_num(location_data_list : List[LocationData], e_player_name : str) -> int:
    for action_num, location_data in enumerate(location_data_list):
        for player_name, simple_info in location_data.items():
            if player_name == e_player_name:
                return action_num
    return -1

# フィールド選手情報の作成
def create_field_players(
    location_data_list : List[LocationData], player_infos : PlayerInfos, substitutions : SubStitutions
) -> FieldPlayers:
    field_players : FieldPlayers = {}
    
    keepers = create_keepers(player_infos)
    benches = create_benches(substitutions)
    field_player : List[str] = [p for p in player_infos.keys() if p not in (keepers + benches)]
    field_players[0] = copy.deepcopy(field_player)

    for (in_player_name, out_player_name) in substitutions:
        field_player.remove(out_player_name)
        field_player.append(in_player_name)
        action_num = get_player_in_num(location_data_list, in_player_name)
        field_players[action_num] = copy.deepcopy(field_player)
    
    return field_players

# １行分のデータフレーム作成
def create_pd_entry(
    game_id : float, period_id :float, action_id : float, team_id : float, player_id : float, location : List[float]
):
    return {
        "game_id": game_id,
        "period_id": period_id,
        "team_id": team_id,
        "player_id": player_id,
        "location_x": location[0],
        "location_y": location[1],
        "action_id": action_id
    }

# アクションデータと同じ形式の座標データを作成
def create_action_locations(actions : pd.DataFrame, location_data_list : List[LocationData]) -> pd.DataFrame:
    team_to_id = actions.drop_duplicates(subset=["team_id", "team_name"])[["team_name", "team_id"]]
    team_to_id_dict = dict(zip(team_to_id["team_name"], team_to_id["team_id"]))
    player_to_id = actions.drop_duplicates(subset=["player_id", "player_name"])[["player_name", "player_id"]]
    player_to_id_dict = dict(zip(player_to_id["player_name"], player_to_id["player_id"]))

    action_locations : pd.DataFrame = {}
    action_locations_list = []
    for action_num in range(len(actions)):
        a = actions.iloc[action_num]
        game_id = a["game_id"]
        period_id = a["period_id"]
        action_id = a["action_id"]

        location_data = location_data_list[action_num]
        for player_name, simple_info in location_data.items():
            location, jersey, team_name = con.take_simple_info(simple_info)
            team_id = team_to_id_dict[team_name]
            player_id = player_to_id_dict[player_name]
            pd_entry = create_pd_entry(game_id, period_id, action_id, team_id, player_id, location)
            action_locations_list.append(pd_entry)

    action_locations[game_id] = pd.DataFrame(action_locations_list)
    return action_locations

# 選手名とIDの対応情報作成
def create_name_ids(players : pd.DataFrame, game_locations : pd.DataFrame) -> NameIds:
    name_ids : NameIds = {}
    for player_id, group in game_locations.groupby("player_id"):
        player_name = players.loc[players["player_id"] == player_id, ["nickname", "player_name"]].apply(
            lambda x: x.iloc[0] if x.iloc[0] else x.iloc[1], axis=1
        ).values[0]
        team_id = group["team_id"].values[0]
        name_ids[player_name] = (player_id, team_id)
    return name_ids

# ヒートマップ作成
def create_heatmaps(game_locations : pd.DataFrame) -> Heatmaps:
    player_locations : Dict[float, Tuple[np.ndarray, np.ndarray]] = {}
    for player_id, group in game_locations.groupby("player_id"):
        group = group.dropna(subset=["location_x", "location_y"])
        x = group["location_x"].values
        y = group["location_y"].values
        player_locations[player_id] = (x, y)

    heatmaps : Heatmaps = {}
    for player_id, (x, y) in player_locations.items():
        heatmap, _, _ = np.histogram2d(
            x, y,
            bins=[grid_x, grid_y],
            range=[[0, pitch_width], [0, pitch_length]]
        )
        heatmaps[player_id] = heatmap
    
    return heatmaps

# 各選手の出場範囲情報を作成
def create_player_ranges(game_locations : pd.DataFrame) -> PlayerRanges:
    player_ranges : PlayerRanges = {}
    for player_id, group in game_locations.groupby("player_id"):
        action_ids = group["action_id"].values
        start_id = np.min(action_ids)
        end_id = np.max(action_ids)
        player_ranges[player_id] = (start_id, end_id)
    
    return player_ranges

# １行分のデータフレーム作成（評価用）
def create_pd_entry_eval(
    player_id : float, player_name : str, loc_value : float, loc_value_off : float, loc_value_def : float
):
    return {
        "player_id" : player_id,
        "player_name" : player_name,
        "location_value" : loc_value,
        "off_location_value": loc_value_off,
        "def_location_value": loc_value_def
    }