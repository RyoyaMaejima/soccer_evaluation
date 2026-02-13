from typing import List, Dict, Tuple
from edit.type_def import *
import edit.convert_take as con
import edit.math_func as mf

# team反転
def reverse_team(data_list: List[Data], reverse_numbers: List[int]) -> None:
    for data_num in reverse_numbers:
        data = data_list[data_num]
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
            for entry in frame_data:
                location, track_id, jersey, team = con.take_entry_info(entry)
                if team == "left":
                    entry["team"] = "right"
                elif team == "right":
                    entry["team"] = "left"

# フィルタリング（手動）
def filter_data_manual(data_list: List[Data], filter_frames: Frame) -> None:
    for data_num, (start_frame, end_frame) in filter_frames.items():
        data = data_list[data_num]
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, start_frame, end_frame):
            for entry in frame_data:
                entry["bbox_pitch"] = ""

# フィルタリング判定
def calc_is_filter(frame_data: List[Entry]) -> bool:
    player_num = 0
    pitch_x_range = pitch_width / 2
    pitch_y_range = pitch_length / 2 + 5
    for entry in frame_data:
        location, track_id, jersey, team = con.take_entry_info(entry)
        if location == "":
            continue
        if mf.calc_order_of_abs(location[0], pitch_x_range) or mf.calc_order_of_abs(location[1], pitch_y_range):
            return True
        player_num += 1
    return player_num < 5

# フィルタリング（自動）
def filter_data_auto(data_list: List[Data]) -> None:
    for data_num, data in enumerate(data_list):
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
            if calc_is_filter(frame_data):
                for entry in frame_data:
                    entry["bbox_pitch"] = ""

# data内のtrack_idの出現回数
def calc_track_counts(data: Data, data_num: int) -> Dict[float, int]:
    track_counts: Dict[float, int] = {}
    for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
        for entry in frame_data:
            location, track_id, jersey, team = con.take_entry_info(entry)
            track_counts[track_id] = track_counts.get(track_id, 0) + 1
    return track_counts

# track_id削除
def delete_track_id(data: Data, data_num: int, start_frame: int, end_frame: int, e_track_id: float) -> None:
    for frame_num, frame_data in con.iterate_frame_datas(data, data_num, start_frame, end_frame):
        for entry in frame_data:
            location, track_id, jersey, team = con.take_entry_info(entry)
            if track_id == e_track_id:
                frame_data.remove(entry)

# 一度しか出現しないtrack_idを削除
def delete_once_track_id(data_list: List[Data], edit_numbers: List[Edit]) -> None:
    for data_num, data in enumerate(data_list):
        edit_ids = []
        for (start_frame, end_frame), edit_infos in edit_numbers[data_num].items():
            for track_id, jersey_number, team in edit_infos:
                edit_ids.append(track_id)
        
        track_counts = calc_track_counts(data, data_num)
        for track_id, count in track_counts.items():
            if count == 1 and track_id not in edit_ids:
                delete_track_id(data, data_num, 1, max_frame, track_id)

# 特定フレームのtrack_idを削除
def delete_track_id_by_frame(data_list: List[Data], delete_numbers: Delete) -> None:
    for data_num, frame_track_ids in delete_numbers.items():
        data = data_list[data_num]
        for frame_num, track_id in frame_track_ids:
            delete_track_id(data, data_num, frame_num, frame_num, track_id)