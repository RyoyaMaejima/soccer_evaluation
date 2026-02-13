from typing import List, Dict, Tuple
from edit.type_def import Entry, Data

# 番号から文字列への変換
def num_to_str(num : int) -> str:
    return f"trim_{num:03d}"
    # return f"021"

# 番号からファイル名への変換
def convert_num_to_file_name(file_num : int) -> str:
    return f"{num_to_str(file_num)}.json"

# 番号からフレームIDへの変換
def convert_num_to_id(data_num : int, frame_num : int) -> str:
    return f"2{num_to_str(data_num)}{frame_num:06d}"

# フレームIDをもとに対応するdataを返す
def iterate_frame_datas(data: Data, data_num: int, start_frame: int, end_frame: int):
    for frame_num in range(start_frame, end_frame + 1):
        frame_id = convert_num_to_id(data_num, frame_num)
        if frame_id in data:
            yield frame_num, data[frame_id]

# 番号から画像パスへの変換
def convert_num_to_path(data_num : int, frame_num : int) -> str:
    return f"images/{num_to_str(data_num)}/{frame_num:06d}.jpg"

# 番号から時間への変換
def conver_num_to_time(data_num : int, frame_num : int) -> float:
    return data_num * 30 + (frame_num / 750) * 30

# 数値リストを文字列に変換
def convert_list_to_string(numbers : List[int]) -> str:
    if not numbers:
        return "None"
    
    numbers = sorted(set(numbers))
    ranges = []
    start = numbers[0]
    end = numbers[0]
    
    for number in numbers[1:]:
        if number == end + 1:
            end = number
        else:
            ranges.append(f"{start}" if start == end else f"{start}~{end}")
            start = end = number
    ranges.append(f"{start}" if start == end else f"{start}~{end}")
    return ",".join(ranges)

# 時刻を文字列に変換
def convert_time_to_string(time) -> str:
    time = int(time * 100) / 100
    return f"{time:.2f}"

# 情報の取り出し
def take_entry_info(entry : Entry) -> Tuple[List[float], float, str, str]:
    bbox = entry["bbox_pitch"]
    if bbox == "":
        location = ""
    else:
        location = [bbox["x_bottom_middle"], bbox["y_bottom_middle"]]
    track_id = entry["track_id"]
    jersey = entry["jersey"]
    team = entry["team"]
    
    return location, track_id, jersey, team

# 座標の設定
def set_location(entry: Entry, e_location: List[float]) -> None:
    bbox = entry["bbox_pitch"]
    if bbox != "":
        bbox["x_bottom_middle"] = e_location[0]
        bbox["y_bottom_middle"] = e_location[1]