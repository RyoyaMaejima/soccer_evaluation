import pandas as pd
from typing import List, Dict, Tuple
from edit.type_def import SimpleInfo, PlayerInfo, LocationData
import edit.math_func as mf

# 時刻を文字列に変換
def convert_time_to_string(time : float) -> str:
    time = int(time * 100) / 100
    return f"{time:.2f}"

# 情報の取り出し
def take_simple_info(simple_info : SimpleInfo) -> Tuple[List[float], str, str]:
    location = simple_info["location"]
    jersey = simple_info["jersey"]
    team = simple_info["team"]

    return location, jersey, team

# 選手情報の取り出し
def take_player_info(player_info : PlayerInfo) -> Tuple[str, str, str, float]:
    team_name = player_info["team_name"]
    jersey = player_info["jersey"]
    position = player_info["position"]
    rating = player_info["rating"]

    return team_name, jersey, position, rating

# 描画用情報の取り出し
def take_plot_data(Location_data : LocationData) -> Tuple[List[str], List[List[float]], List[str], List[str]]:
    player_names = []
    locations = []
    jerseis = []
    team_names = []
    for player_name, simple_info in Location_data.items():
        location, jersey_number, team_name = take_simple_info(simple_info)
        if not mf.calc_is_nan_location(location):
            player_names.append(player_name)
            locations.append(location)
            jerseis.append(jersey_number)
            team_names.append(team_name)
        
    return player_names, locations, jerseis, team_names