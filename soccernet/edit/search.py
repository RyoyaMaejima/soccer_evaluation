from typing import List, Dict, Tuple
from edit.type_def import max_frame, Data, Edit
import edit.convert_take as con
import edit.math_func as mf

# track_idによるフレーム検索
def search_frame(data : Data, data_num: int, e_track_id: float) -> None:
    frame_list = []
    e_jersey = ""
    for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
        for entry in frame_data:
            location, track_id, jersey, team = con.take_entry_info(entry)
            if location != "" and track_id == e_track_id:
                e_jersey = jersey
                frame_list.append(frame_num)
    
    print(f"({e_track_id}, {e_jersey}): {con.convert_list_to_string(frame_list)}")

# データがないフレームの検索
def search_none_frame(data : Data, data_num: int) -> None:
    frame_list = []
    for frame_num in range(1, max_frame + 1):
        frame_id = con.convert_num_to_id(data_num, frame_num)
        if frame_id in data:
            frame_data = data[frame_id]
        else:
            frame_list.append(frame_num)
            continue
        for entry in frame_data:
            location, track_id, jersey, team = con.take_entry_info(entry)
            if location == "":
                frame_list.append(frame_num)
                break
    
    print(f"none frame: {con.convert_list_to_string(frame_list)}")

# フレーム内のtrack_idの検索
def search_track_id(data : Data, data_num: int, frame_num: int) -> None:
    frame_id = con.convert_num_to_id(data_num, frame_num)
    if frame_id not in data:
        print(f"{frame_id} not found")
        return
    
    frame_data = data[frame_id]
    track_ids = []
    for entry in frame_data:
        location, track_id, jersey, team = con.take_entry_info(entry)
        if location == "":
            continue
        track_ids.append(track_id)
    print(f"track_id : {track_ids}")

# 選手が複数いるフレームの検索
def search_multiple_frame(data_list: List[Data], max_distance: float) -> None:
    for data_num, data in enumerate(data_list):
        is_multi = False
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
            track_locs : Dict[Tuple[str, str], Tuple[str, List[float]]] = {}
            for entry in frame_data:
                location, track_id, jersey, team = con.take_entry_info(entry)
                if location == "" or jersey == "" or team == "nan":
                    continue
                if not (jersey, team) in track_locs:
                    track_locs[(jersey, team)] = (track_id, location)
                elif mf.calc_distance(location, track_locs[(jersey, team)][1]) >= max_distance:
                    if not is_multi:
                        is_multi = True
                        print(f"data_num: {data_num}")
                    print(f"{frame_num}: {jersey}, {team} (track_id: {track_locs[(jersey, team)][0], {track_id}})")
                    break

# フレーム検索（複数）
def search_frames(data: Data, data_num: int, edit_numbers: List[Edit]) -> None:
    edit_number = edit_numbers[data_num]
    for (start_frame, end_frame), edit_infos in edit_number.items():
        print(f"start {start_frame}")
        for (track_id, jersey, team) in edit_infos:
            search_frame(data, data_num, track_id)