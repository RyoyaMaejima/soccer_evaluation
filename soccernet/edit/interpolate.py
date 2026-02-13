from typing import List, Dict, Tuple
from edit.type_def import *
import edit.convert_take as con
import edit.create as cre
import edit.math_func as mf

# 複数ある背番号の統合
def integrate_jerseis(data_list: List[Data]) -> None:
    for data_num, data in enumerate(data_list):
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
            seen: Dict[Tuple[str, str], Entry] = {}
            new_frame_data : List[Entry] = []

            for entry in frame_data:
                location, track_id, jersey, team = con.take_entry_info(entry)
                if location == "":
                    continue
                if jersey == "":
                    new_frame_data.append(entry)
                    continue

                if (jersey, team) not in seen:
                    seen[(jersey, team)] = entry
                    new_frame_data.append(entry)
                else:
                    prev = seen[(jersey, team)]
                    p_location, p_track_id, p_jersey, p_team = con.take_entry_info(prev)
                    ave_loc = mf.calc_average(p_location, location)
                    con.set_location(prev, ave_loc)
            
            frame_data[:] = new_frame_data

# 座標時系列データの更新
def update_trajectories(data_list: List[Data], trajectories: Trajectories, e_team: str) -> None:
    trajectory : Trajectory = {}
    for data_num, data in enumerate(data_list):
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
            if (data_num, frame_num) in trajectories:
                trajectory = trajectories[(data_num, frame_num)]
            
            time = con.conver_num_to_time(data_num, frame_num)
            for entry in frame_data:
                location, track_id, jersey, team = con.take_entry_info(entry)
                if location == "":
                    continue
                if jersey == "" or team != e_team:
                    continue
                if jersey in trajectory:
                    trajectory[jersey].append((time, location))
                else:
                    print(f"{jersey}, {team} not found in trajectory at {data_num}")

# 現フレームにない背番号を取得
def get_none_jerseis(frame_data: List[Entry], trajectory: Trajectory, e_team: str) -> List[str]:
    cur_jerseis = []
    for entry in frame_data:
        location, track_id, jersey, team = con.take_entry_info(entry)
        if location == "":
            continue
        if jersey == "" or team == "nan":
            continue
        if team == e_team:
            cur_jerseis.append(jersey)
    none_jerseis = [j for j in trajectory.keys() if j not in cur_jerseis]
    return none_jerseis

# 指定した時間における座標の取得
def take_loc_info_by_time(time: float, trajectory: Trajectory) -> Dict[str, List[float]]:
    loc_info: Dict[str, List[float]] = {}
    for jersey, records in trajectory.items():
        for t, loc in records:
            if t == time:
                loc_info[jersey] = loc
    return loc_info

# 他の選手との関係性による座標予測
def predict_location_by_relation(time: float, o_time: float, trajectory: Trajectory, e_jersey: str) -> List[float]:
    loc_info = take_loc_info_by_time(time, trajectory)
    o_loc_info = take_loc_info_by_time(o_time, trajectory)
    common = set(loc_info.keys()) & set(o_loc_info.keys())
    if common:
        c_jersey = next(iter(common))
        sub_vector = mf.calc_sub(o_loc_info[e_jersey], o_loc_info[c_jersey])
        return mf.calc_add(loc_info[c_jersey], sub_vector)
    else:
        return o_loc_info[e_jersey]
    
# 線形補間による座標予測
def predict_location_by_interpolate(time: float, trajectory: Trajectory, e_jersey: str) -> List[float]:
    pred_loc = []
    records = trajectory[e_jersey]
    for i in range(len(records) - 1):
        t1, loc1 = records[i]
        t2, loc2 = records[i + 1]
        if t1 <= time <= t2:
            pred_loc = mf.calc_linear(time, t1, loc1, t2, loc2)
            break
    return pred_loc

# 座標予測
def predict_location(time: float, trajectory: Trajectory, e_jersey: str) -> List[float]:
    records = trajectory[e_jersey]
    if records == []:
        pred_loc = []
    elif time < records[0][0]:
        pred_loc = predict_location_by_relation(time, records[0][0], trajectory, e_jersey)
    elif time > records[-1][0]:
        pred_loc = predict_location_by_relation(time, records[-1][0], trajectory, e_jersey)
    else:
        pred_loc = predict_location_by_interpolate(time, trajectory, e_jersey)
    if pred_loc == []:
        print(f"{e_jersey} not found at {time}")
    
    return pred_loc

# データに予測座標をいれたエントリーを追加
def add_entry_to_data(
    data_list: List[Data], trajectories_left: Trajectories, trajectories_right: Trajectories
) -> None:
    trajectory_left: Trajectory = {}
    trajectory_right: Trajectory = {}
    for data_num, data in enumerate(data_list):
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
            if (data_num, frame_num) in trajectories_left:
                trajectory_left = trajectories_left[(data_num, frame_num)]
            if (data_num, frame_num) in trajectories_right:
                trajectory_right= trajectories_right[(data_num, frame_num)]
            
            none_jerseis_left = get_none_jerseis(frame_data, trajectory_left, "left")
            none_jerseis_right = get_none_jerseis(frame_data, trajectory_right, "right")
            time = con.conver_num_to_time(data_num, frame_num)
            entries: List[Entry] = []
            
            for jersey in none_jerseis_left:
                pred_loc = predict_location(time, trajectory_left, jersey)
                if pred_loc != []:
                    bbox = cre.create_bbox(e_x_bottom_middle=pred_loc[0], e_y_bottom_middle=pred_loc[1])
                    entry = cre.create_entry(e_bbox=bbox, e_jersey=jersey, e_team="left")
                    entries.append(entry)
            for jersey in none_jerseis_right:
                pred_loc = predict_location(time, trajectory_right, jersey)
                if pred_loc != []:
                    bbox = cre.create_bbox(e_x_bottom_middle=pred_loc[0], e_y_bottom_middle=pred_loc[1])
                    entry = cre.create_entry(e_bbox=bbox, e_jersey=jersey, e_team="right")
                    entries.append(entry)
            frame_data.extend(entries)