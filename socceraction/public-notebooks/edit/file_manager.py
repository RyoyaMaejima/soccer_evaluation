import os
import json
import shlex
from typing import List, Dict, Tuple
from edit.type_def import *

class FileManager:
    def __init__(self, data_path: str):
        self.data_path = data_path

    #　入力ファイル読み込み
    def load_files(self) -> Tuple[SimpleData, SimpleData]:
        data_1 : SimpleData = {}
        file_path = os.path.join(self.data_path, f"1/simple_data.json")
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                data_1 = json.load(file)
        else:
            print(f"{file_path} not found")
        print(f"Loaded {file_path}")

        data_2 : SimpleData = {}
        file_path = os.path.join(self.data_path, f"2/simple_data.json")
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                data_2 = json.load(file)
        else:
            print(f"{file_path} not found")
        print(f"Loaded {file_path}")
        return data_1, data_2
    
    # ファイル読み込み(AnyInfos)
    def load_any_file(self) -> Tuple[List[str], DeleteRanges]:
        file_path = os.path.join(self.data_path, f"AnyInfos.txt")

        team_names : TeamNames = {}
        delete_ranges : DeleteRanges = []
        mode = "none"
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                elif line == "fin":
                    break
                else:
                    parts = shlex.split(line)
                    if len(parts) == 1:
                        mode = parts[0]
                    else:
                        if mode == "team":
                            team_names["left"] = parts[0]
                            team_names["right"] = parts[1]
                        elif mode == "delete":
                            start_action_num = int(parts[0])
                            end_action_num = int(parts[1])
                            delete_ranges.append((start_action_num, end_action_num))
        
        return team_names, delete_ranges
    
    # ファイル読み込み(PlayerInfos)
    def load_player_file(self) -> Tuple[PlayerNames, PlayerInfos]:
        file_path = os.path.join(self.data_path, f"PlayerInfos.txt")

        player_names : PlayerNames = {}
        player_infos : PlayerInfos = {}
        team_name = ""
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                elif line == "fin":
                    break
                else:
                    parts = shlex.split(line)
                    if parts[0] == "team":
                        team_name = parts[1]
                        if team_name not in player_names:
                            player_names[team_name] = {}
                    else:
                        player_name = parts[0]
                        jersey = parts[1]
                        position = parts[2]
                        rating = float(parts[3])
                        player_names[team_name][jersey] = player_name
                        player_infos[player_name] = {
                            "team_name": team_name,
                            "jersey": jersey,
                            "position": position,
                            "rating": rating
                        }
        
        return player_names, player_infos
    
    # ファイル読み込み(CornerInfos)
    def load_corner_file(self) -> CornerInfos:
        file_path = os.path.join(self.data_path, f"CornerInfos.txt")

        corner_infos : CornerInfos = {}
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                elif line == "fin":
                    break
                else:
                    parts = shlex.split(line)
                    if parts[0] == "num":
                        start_action_num = int(parts[1])
                        end_action_num = int(parts[2])
                    elif parts[0] == "player":
                        player_name = parts[1]
                    elif parts[0] == "loc":
                        location = [float(parts[1]), float(parts[2])]
                        corner_infos[(start_action_num, end_action_num)] = (player_name, location)
        
        return corner_infos
    
    # ファイル読み込み(SubStitutions)
    def load_substitution_file(self) -> SubStitutions:
        file_path = os.path.join(self.data_path, f"Substitutions.txt")

        substitutions : SubStitutions = []
        in_player_name = ""
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                elif line == "fin":
                    break
                else:
                    parts = shlex.split(line)
                    if parts[0] == "in":
                        in_player_name = parts[1]
                    else:
                        out_player_name = parts[0]
                        substitutions.append((in_player_name, out_player_name))
        
        return substitutions