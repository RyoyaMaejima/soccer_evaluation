import MathFunctions as mf
import PlotFunctions as pf
import os
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from typing_extensions import TypedDict

# データ構造体定義
class LocationInfo(TypedDict):
    location: List[float]
    jersey_number: str
    team: str
Data = Dict[str, List[LocationInfo]]

PlayerNames = Dict[str, Dict[str, str]]
Formations = Dict[int, List[str]]
BenchDatas = Dict[int, Dict[str, LocationInfo]]

ActionRanges = List[Tuple[int, int]]

InterNumbers = Dict[Tuple[int, int], Dict[str, LocationInfo]]

LocationData = Dict[str, LocationInfo]

LackNumbers = Dict[int, List[str]]

def nice_time(row):
    minute = int((row.period_id-1)*45 +row.time_seconds // 60)
    second = int(row.time_seconds % 60)
    return f"{minute}m{second}s"

# ファイル読み込み
def load_json_file(file_path):
    data = {}
    if os.path.isfile(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        print(f"{file_path} not found")
    
    print(f"Loaded {file_path}")
    return data

# ファイル読み込み(PlayerNames)
def load_name_file(name_file):
    player_names : PlayerNames = {}
    team_name = ""
    formations : Formations = {}
    formation : List[str] = []
    formation_num = 0
    iskeeper = False

    with open(name_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            elif line == "fin":
                formations[formation_num] = formation.copy()
                break
            elif line.startswith("team"):
                team_name = line.split(' ', 1)[1].strip('"')
            elif line.isdigit():
                formations[formation_num] = formation.copy()
                formation_num = int(line)
            elif line.startswith("out"):
                formation.remove(line.split(' ', 1)[1].strip('"'))
            elif line == "keeper":
                iskeeper = True
            else:
                parts = line.split(' ', 1)
                jersey_number = parts[0].strip('"')
                player_name = parts[1].strip('"')
                if team_name not in player_names:
                    player_names[team_name] = {}
                player_names[team_name][jersey_number] = player_name
                
                if not iskeeper:
                    formation.append(player_name)

    return player_names, formations

# ファイル読み込み(InterNumbers)
def load_inter_file(inter_file):
    inter_numbers : InterNumbers = {}
    team_name = ""
    start_num = end_num = 0
    jersey_number = ""
    player_name = ""
    location = []

    with open(inter_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            elif line == "fin":
                break
            elif line.startswith("team"):
                team_name = line.split(' ', 1)[1].strip('"')
            elif line.startswith("num"):
                start_num = int(line.split()[1])
                end_num = int(line.split()[2])
                if (start_num, end_num) not in inter_numbers:
                    inter_numbers[(start_num, end_num)] = {}
            elif line.startswith("player"):
                player_name = line.split(' ', 1)[1].strip('"')
            elif line.startswith("jersey"):
                jersey_number = line.split()[1].strip('"')
            else:
                parts = line.split()
                location = [float(parts[1]), float(parts[2])]
                inter_numbers[(start_num, end_num)][player_name] = {
                    "location" : location,
                    "jersey_number" : jersey_number,
                    "team" : team_name
                }
    
    return inter_numbers

# ファイル読み込み(AnyInfos)
def load_any_file(any_file):
    team_names = []
    action_ranges : ActionRanges = []
    mode = "none"

    with open(any_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            elif line == "fin":
                break
            elif len(line.split()) == 1:
                mode = line
            else:
                if mode == "team":
                    team_name = line.split(' ', 1)[1].strip('"')
                    team_names.append(team_name)
                elif mode == "delete":
                    parts = line.split()
                    action_ranges.append((int(parts[0]), int(parts[1])))
    
    return team_names, action_ranges

# 時刻を文字列に変換
def convert_time_to_string(time):
    time = int(time * 100) / 100
    return f"{time:.2f}"

# 情報の取り出し
def take_loc_info(loc_info : LocationInfo):
    location = loc_info["location"]
    jersey_number = loc_info["jersey_number"]
    team = loc_info["team"]

    return location, jersey_number, team

# 描画用情報の取り出し
def take_plot_data(Location_data : LocationData):
    player_names = []
    locations = []
    jersey_numbers = []
    team_names = []
    for player_name, loc_info in Location_data.items():
        location, jersey_number, team_name = take_loc_info(loc_info)
        if not mf.is_nan_location(location):
            player_names.append(player_name)
            locations.append(location)
            jersey_numbers.append(jersey_number)
            team_names.append(team_name)
        
    return player_names, locations, jersey_numbers, team_names

# ある時刻から最も近いフレームの検索
def search_frame_by_time(data : Data, time):
    time = round(time / 0.04) * 0.04
    frame_time = convert_time_to_string(time)
    if frame_time in data:
        return frame_time
    else:
        before_time = time - 0.04
        after_time = time + 0.04
        while before_time >= 0:
            frame_time = convert_time_to_string(before_time)
            if frame_time in data:
                return frame_time
            frame_time = convert_time_to_string(after_time)
            if frame_time in data:
                return frame_time
            before_time -= 0.04
            after_time += 0.04
        return ""
    
# 選手が初めて出る番号の検索
def search_play_in_number(location_data_list : List[LocationData], start_action_num, end_action_num, e_player_name):
    for action_num in range(start_action_num, end_action_num + 1):
        location_data = location_data_list[action_num]
        for player_name, loc_info in location_data.items():
            if player_name == e_player_name:
                print(action_num)
                return
    print("None")
    
# 全選手の座標が無い番号の検索
def search_lack_number(location_data_list : List[LocationData], start_action_num, end_action_num, formations : Formations):
    lack_numbers : LackNumbers = {}
    formation = formations[0]
    for action_num in range(start_action_num, end_action_num + 1):
        if action_num in formations:
            formation = formations[action_num]
        location_data = location_data_list[action_num]
        for player_name in formation:
            if player_name not in location_data:
                if action_num not in lack_numbers:
                    lack_numbers[action_num] = []
                lack_numbers[action_num].append(player_name)
    
    for action_num, player_names in lack_numbers.items():
        print(f"action_num: {action_num}")
        for player_name in player_names:
            print(f"{player_name} not found")
    return lack_numbers

# 描画
def plot_action_data(actions, game, location_data_list : List[LocationData], action_num, player_names : PlayerNames, team_name):
    # Select the 5 actions
    shot = action_num
    a = actions[shot:shot+1].copy()

    # Print the game date and timestamp
    g = game.iloc[0]
    minute = int((a.period_id.values[0]-1) * 45 + a.time_seconds.values[0] // 60)
    game_info = f"{g.game_date} {g.home_team_name} {g.home_score}-{g.away_score} {g.away_team_name} {minute + 1}'"
    print(game_info)

    # Plot the actions
    a["nice_time"] = a.apply(nice_time, axis=1)
    labels = a[["nice_time", "type_name", "player_name", "team_name"]]

    location_data : LocationData = location_data_list[action_num]
    o_player_names, o_locations, o_jersey_numbers, o_team_names = take_plot_data(location_data)
    o_player_names = np.array(o_player_names)
    o_locations = np.array(o_locations)
    o_jersey_numbers = np.array(o_jersey_numbers)
    o_team_names = np.array(o_team_names)
    ax = pf.actions_with_players(
        location=a[["start_x", "start_y", "end_x", "end_y"]],
        e_team_name=team_name,
        action_type=a.type_name,
        team= a.team_name,
        result= a.result_name == "success",
        label=labels,
        labeltitle=["time", "actiontype", "player", "team"],
        zoom=False,
        figsize=6,
        o_locations=o_locations,
        o_teams=o_team_names,
        o_names=o_jersey_numbers
    )

# 座標情報作成
def create_loc_info(location, e_jersey_number, e_team):
    loc_info : LocationInfo = {
        "location" : location,
        "jersey_number" : e_jersey_number,
        "team" : e_team
    }
    return loc_info

# ベンチ情報の作成
def create_bench_datas(player_names : PlayerNames, formations : Formations):
    loc_data : LocationData = {}
    for team_name, player_list in player_names.items():
        for jersey_number, player_name in player_list.items():
            nan_loc = mf.create_nan_location()
            loc_data[player_name] = create_loc_info(nan_loc, jersey_number, team_name)
    # print(loc_data)
            
    bench_datas : BenchDatas = {}
    for action_num, formation in formations.items():
        bench_datas[action_num] = {}
        for player_name, loc_info in loc_data.items():
            if player_name not in formation:
                bench_datas[action_num][player_name] = loc_info
    
    return bench_datas

# アクションデータに入れる用の座標データを作成
def create_location_data(actions, start_action_num, end_action_num, data_1 : Data, data_2 : Data, player_names : PlayerNames, e_team_names):
    location_data_list : List[LocationData] = []
    data : Data = {}
    isfirst = True
    for action_num in range(start_action_num, end_action_num + 1):
        a = actions.iloc[action_num]
        action_time = a.time_seconds
        if a.period_id == 1:
            isfirst = True
            data = data_1
        else:
            isfirst = False
            data = data_2

        location_data : LocationData = {}
        frame_time = search_frame_by_time(data, action_time)
        if frame_time != "":
            loc_info_list = data[frame_time]
            for loc_info in loc_info_list:
                location, jersey_number, team = take_loc_info(loc_info)
                if (team == "left" and isfirst) or (team == "right" and not isfirst):
                    team_name = e_team_names[0]
                else:
                    team_name = e_team_names[1]
                player_name = player_names[team_name][jersey_number]
                location_data[player_name] = create_loc_info(location, jersey_number, team_name)
        else:
            print(f"action_num: {action_num}, time: {action_time} none in data")

        location_data_list.append(location_data)
    return location_data_list

# 座標補正（平行移動）
def edit_location_translation(action_loc, predict_loc, location_data : LocationData):
    sub_vector = mf.calc_sub(action_loc, predict_loc)
    for player_name, loc_info in location_data.items():
        loc_info["location"] = mf.calc_add(loc_info["location"], sub_vector)

# 座標補正（回転）
def edit_location_rotation(action_loc, predict_loc, location_data : LocationData):
    pitch_center = [105 / 2, 68 / 2]
    action_loc = mf.calc_sub(action_loc, pitch_center)
    predict_loc = mf.calc_sub(predict_loc, pitch_center)
    scale, theta = mf.calc_rotate_angle(action_loc, predict_loc)
    for player_name, loc_info in location_data.items():
        convert_loc = mf.calc_sub(loc_info["location"], pitch_center)
        convert_loc = mf.calc_rotate_location(convert_loc, scale, theta)
        loc_info["location"] = mf.calc_add(convert_loc, pitch_center)

# 自動補正
def edit_data_auto(actions, location_data_list : List[LocationData], start_action_num, end_action_num):
    for action_num in range(start_action_num, end_action_num + 1):
        a = actions.iloc[action_num]
        action_time = a.time_seconds
        action_loc = [a["start_x"], a["start_y"]]
        action_player_name = a["player_name"]
        location_data = location_data_list[action_num]

        if action_player_name in location_data:
            predict_loc = location_data[action_player_name]["location"]
            if not (a.period_id == 2 and action_time > 2799):
                edit_location_translation(action_loc, predict_loc, location_data)
            # edit_location_rotation(action_loc, predict_loc, location_data)
    
    return location_data_list

# 補間情報の適用
def apply_inter_data(location_data_list : List[LocationData], inter_numbers : InterNumbers):
    for (start_num, end_num), inter_info_list in inter_numbers.items():
        for player_name, inter_info in inter_info_list.items():
            for action_num in range(start_num, end_num + 1):
                location_data = location_data_list[action_num]
                location_data[player_name] = inter_info
    
    return location_data_list

# 欠損選手の補間
def interpolate_data(location_data_list : List[LocationData], lack_numbers : LackNumbers):
    for action_num, player_names in lack_numbers.items():
        for player_name in player_names:
            location_data = location_data_list[action_num]
            for prev_action_num in range(action_num, -1, -1):
                prev_location_data = location_data_list[prev_action_num]
                if player_name in prev_location_data:
                    p_location, p_jersey_number, p_team_name = take_loc_info(prev_location_data[player_name])
                    common_players = set(location_data.keys()) & set(prev_location_data.keys())
                    if common_players:
                        common_player = next(iter(common_players))
                        sub_vector = mf.calc_sub(p_location, prev_location_data[common_player]["location"])
                        pred_location = mf.calc_add(location_data[common_player]["location"], sub_vector)
                        location_data[player_name] = create_loc_info(pred_location, p_jersey_number, p_team_name)
    
    return location_data_list

# ベンチ情報の追加
def add_bench_datas(location_data_list : List[LocationData], bench_datas : BenchDatas, start_action_num, end_action_num):
    bench_data = bench_datas[0]
    for action_num in range(start_action_num, end_action_num + 1):
        if action_num in bench_datas:
            bench_data = bench_datas[action_num]
        location_data = location_data_list[action_num]
        for player_name, loc_info in bench_data.items():
            location_data[player_name] = loc_info
    return location_data_list

# アクション数の削減
def reduct_actions(location_data_list : List[LocationData], action_range):
    for action_num in range(action_range[0], action_range[1] + 1):
        location_data = location_data_list[action_num]
        for player_name, loc_info in location_data.items():
            loc_info["location"] = mf.create_nan_location()
    return location_data_list

# データフレーム作成
def create_data_frame(game_id, period_id, action_id, team_id, player_id, location):
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
def create_location_data_as_pd(actions, location_data_list : List[LocationData], start_action_num, end_action_num):
    team_to_id = actions.drop_duplicates(subset=["team_id", "team_name"])[["team_name", "team_id"]]
    team_to_id_dict = dict(zip(team_to_id["team_name"], team_to_id["team_id"]))
    name_to_id = actions.drop_duplicates(subset=["player_id", "player_name"])[["player_name", "player_id"]]
    name_to_id_dict = dict(zip(name_to_id["player_name"], name_to_id["player_id"]))

    action_locations = {}
    action_location_list = []
    for action_num in range(start_action_num, end_action_num + 1):
        a = actions.iloc[action_num]
        game_id = a["game_id"]
        period_id = a["period_id"]
        action_location = [a["start_x"], a["start_y"]]
        action_id = a["action_id"]
        action_player_name = a["player_name"]
        location_data = location_data_list[action_num]
        
        for player_name, loc_info in location_data.items():
            location, jersey_number, team_name = take_loc_info(loc_info)
            team_id = team_to_id_dict[team_name]
            player_id = name_to_id_dict[player_name]
            pd_entry = create_data_frame(game_id, period_id, action_id, team_id, player_id, location)
            action_location_list.append(pd_entry)
    
    action_locations[game_id] = pd.DataFrame(action_location_list)
    return action_locations

# アクションデータに座標データを追加
def add_locations_to_actions(actions, action_locations : pd.DataFrame):
    loc_cols = ["team_id", "location_x", "location_y", "action_id"]
    locations = action_locations[loc_cols].copy()
    locations["player_idx"] = locations.groupby(["team_id", "action_id"]).cumcount()

    locations_pivot = locations.pivot_table(
        index=["team_id", "action_id"],
        columns="player_idx",
        values=["location_x", "location_y"]
    )
    locations_pivot.columns = [f"{col}_p{idx}" for col, idx in locations_pivot.columns]
    locations_pivot = locations_pivot.reset_index()
    actions = actions.merge(locations_pivot, on=["team_id", "action_id"], how="left")
    return actions