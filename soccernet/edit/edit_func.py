import copy
from typing import List, Dict, Tuple
from edit.type_def import *
import edit.convert_take as con
import edit.math_func as mf

# 位置関係の計算
def update_relation(frame_data: List[Entry], entry: Entry, relation: Relation) -> None:
    location, track_id, jersey, team = con.take_entry_info(entry)
    if location == "":
        return
    for other in frame_data:
        o_location, o_track_id, o_jersey, o_team = con.take_entry_info(other)
        if o_location == "" or o_jersey == "":
            continue
        if team == o_team and jersey != o_jersey:
            relation[o_jersey] = mf.calc_sub(location, o_location)

# 各選手情報の更新
def update_player_list(data_num: int, frame_data: List[Entry], player_list: PlayerList, e_team: str, is_loc: bool) -> None:
    for entry in frame_data:
        location, track_id, jersey, team = con.take_entry_info(entry)
        if location == "":
            continue
        if jersey == "" or team != e_team:
            continue
        if jersey in player_list:
            player_list[jersey]["location"] = location
            if not is_loc:
                update_relation(frame_data, entry, player_list[jersey]["relation"])
        else:
            print(f"{data_num}: {jersey}, {team} not found")

# 背番号の予測（座標由来）
def predict_jersey_by_location(
    entry: Entry, relation: Relation, player_list: PlayerList, max_distance: float, nan_data: List[Entry]
) -> str:
    best_distance = max_distance
    best_jersey = ""
    location, track_id, jersey, team = con.take_entry_info(entry)

    for p_jersey, p_info in player_list.items():
        if p_jersey in relation or p_info["relation"] == {}:
            continue
        p_location = p_info["location"]
        distance = mf.calc_distance(location, p_location)
        if distance < best_distance:
            best_distance = distance
            best_jersey = p_jersey
    
    for nan in nan_data:
        n_location, n_track_id, n_jersey, n_team = con.take_entry_info(nan)
        distance = mf.calc_distance(location, n_location)
        if distance < best_distance:
            best_distance = distance
            best_jersey = "none"
    
    return best_jersey

# 順番の一致を判定
def calc_is_order(jersey: str, o_jersey: str, sub_vector: List[float], player_list: PlayerList) -> bool:
    position = player_list[jersey]["position"]
    o_position = player_list[o_jersey]["position"]
    if position[0] == o_position[0]:
        return (sub_vector[1] > 0) == (position[1] > o_position[1])
    else:
        return (sub_vector[0] > 0) == (position[0] > o_position[0])
    
# 背番号の予測（関係性由来）
def predict_jersey_by_relation(
    entry: Entry, relation: Relation, player_list: PlayerList, min_match: float, min_order: float
) -> str:
    best_match = -1.0
    best_jersey = ""
    location, track_id, jersey, team = con.take_entry_info(entry)

    for p_jersey, p_info in player_list.items():
        if p_jersey in relation or p_info["relation"] == {}:
            continue
        p_relation = p_info["relation"]

        m = 0.0
        num = 0
        order_score = 0.0
        for o_jersey, sub_vector in relation.items():
            if o_jersey in p_relation:
                mm = mf.calc_cos(sub_vector, p_relation[o_jersey])
                m += mm
                num += 1
                if calc_is_order(p_jersey, o_jersey, sub_vector, player_list):
                    order_score += 1.0
        if num == 0:
            continue
        m /= num
        order_score /= num
        if m > (min_match / num) and m > best_match and order_score > min_order:
            best_match = m
            best_jersey = p_jersey

    return best_jersey

# 座標由来で予測するかを判定
def calc_is_loc(data_num: int, frame_num: int, set_frames: Frame) -> bool:
    if data_num in set_frames:
        start_frame, end_frame = set_frames[data_num]
        return start_frame <= frame_num <= end_frame
    else:
        return False
    
# exist_frame_numの計算
def calc_exist_frame_num(data : Data, data_num : int) -> int:
    for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
        for entry in frame_data:
            location, track_id, jersey, team = con.take_entry_info(entry)
            if location == "":
                break
            else:
                return frame_num
    return 0

# 背番号が無いデータの取得
def get_nan_data(data_list: List[Data], data_num: int) -> List[Entry]:
    nan_data: List[Entry] = []
    if data_num == 0:
        return nan_data
    data = data_list[data_num - 1]
    for frame_num, frame_data in con.iterate_frame_datas(data, data_num - 1, max_frame, max_frame):
        for entry in frame_data:
            location, track_id, jersey, team = con.take_entry_info(entry)
            if location == "":
                continue
            if team == "nan":
                nan_data.append(entry)
    return nan_data

class EditFunc:
    def __init__(self, start_data_num: int, end_data_num: int):
        self.start_data_num = start_data_num
        self.end_data_num = end_data_num

    # 背番号削除
    def delete_jersey_number(self, data_list: List[Data]) -> None:
        for data_num in range(self.start_data_num, self.end_data_num + 1):
            data = data_list[data_num]
            for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
                for entry in frame_data:
                    entry["jersey"] = ""
    
    # track_idによる補正
    def edit_data(
        self, data: Data, data_num: int, start_frame: int, end_frame: int,
        is_overwrite: bool, e_track_id: float, e_jersey: str, e_team: str
    ) -> None:
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, start_frame, end_frame):
            for entry in frame_data:
                location, track_id, jersey, team = con.take_entry_info(entry)
                if location == "":
                    continue
                if (jersey != "" or team == "nan") and not is_overwrite:
                    continue
                if track_id == e_track_id:
                    entry["jersey"] = e_jersey
                    if e_team != "":
                        entry["team"] = e_team
    
    # 手動補正
    def edit_data_manual(self, data_list: List[Data], edit_numbers: List[Edit]) -> None:
        for data_num in range(self.start_data_num, self.end_data_num + 1):
            data = data_list[data_num]
            for (start_frame, end_frame), edit_infos in edit_numbers[data_num].items():
                for track_id, jersey_number, team in edit_infos:
                    self.edit_data(data, data_num, start_frame, end_frame, True, track_id, jersey_number, team)
    
    # 自動補正
    def edit_data_auto(
        self, data_list: List[Data], player_lists_left: PlayerLists, player_lists_right: PlayerLists,
        min_match: float, max_distance: float, min_order: float, set_frames: Frame
    ) -> None:
        prev_player_lists_left: PlayerLists = {}
        prev_player_lists_right: PlayerLists = {}
        player_list_left: PlayerList = {}
        player_list_right: PlayerList = {}

        # 途中から補正した場合の処理
        for (dnum, fnum), player_list in player_lists_left.items():
            if dnum < self.start_data_num:
                player_list_left = player_lists_left[(dnum, fnum)]
        for (dnum, fnum), player_list in player_lists_right.items():
            if dnum < self.start_data_num:
                player_list_right = player_lists_right[(dnum, fnum)]

        for data_num in range(self.start_data_num, self.end_data_num + 1):
            if data_num == self.end_data_num:
                prev_player_lists_left = copy.deepcopy(player_lists_left)
                prev_player_lists_right = copy.deepcopy(player_lists_right)

            data = data_list[data_num]
            exist_frame_num = calc_exist_frame_num(data, data_num)
            for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
                if (data_num, frame_num) in player_lists_left:
                    player_list_left = player_lists_left[(data_num, frame_num)]
                if (data_num, frame_num) in player_lists_right:
                    player_list_right = player_lists_right[(data_num, frame_num)]

                is_loc = calc_is_loc(data_num, frame_num, set_frames)
                update_player_list(data_num, frame_data, player_list_left, "left", is_loc)
                update_player_list(data_num, frame_data, player_list_right, "right", is_loc)

                for entry in frame_data:
                    location, track_id, jersey, team = con.take_entry_info(entry)
                    if location == "":
                        continue
                    if jersey != "" or team == "nan":
                        continue
                    if entry["role"] == "goalkeeper":
                        self.edit_data(data, data_num, 1, max_frame, False, track_id, "", "nan")
                        continue
                    
                    relation : Relation = {}
                    update_relation(frame_data, entry, relation)
                    player_list = player_list_left if team == "left" else player_list_right
                    if frame_num == exist_frame_num:
                        nan_data = get_nan_data(data_list, data_num)
                        pred_jersey = predict_jersey_by_location(entry, relation, player_list, max_distance, nan_data)
                    elif relation == {} or is_loc:
                        pred_jersey = predict_jersey_by_location(entry, relation, player_list, max_distance, [])
                    else:
                        pred_jersey = predict_jersey_by_relation(entry, relation, player_list, min_match, min_order)
                    if pred_jersey == "none":
                        self.edit_data(data, data_num, 1, max_frame, False, track_id, "", "nan")
                    elif pred_jersey != "":
                        self.edit_data(data, data_num, 1, max_frame, False, track_id, pred_jersey, "")
        
        player_lists_left.clear()
        player_lists_left.update(prev_player_lists_left)
        player_lists_right.clear()
        player_lists_right.update(prev_player_lists_right)