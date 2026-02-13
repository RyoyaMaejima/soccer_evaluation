import os
import json
import shutil
import shlex
from typing import List, Dict, Tuple
from edit.type_def import *
import edit.convert_take as con
import edit.create as cre

class FileManager:
    def __init__(self, data_path: str):
        self.data_path= data_path

    # 入力ファイル読み込み
    def load_files(self, data_file : str, start_file_num: int, end_file_num: int) -> List[Data]:
        data_list : List[Data] = []
        files = os.path.join(self.data_path, data_file)
        for file_num in range(start_file_num, end_file_num + 1):
            file_name = con.convert_num_to_file_name(file_num)
            file_path = os.path.join(files, file_name)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    data = json.load(file)
                    data_list.append(data)
            else:
                print(f"{file_name} not found")
        
        print(f"Loaded {len(data_list)} files")
        return data_list
    
    # 正解ファイル読み込み
    def load_label_file(self) -> List[Data]:
        data_list : List[Data] = []
        file_path = os.path.join(self.data_path, f"Labels-GameState.json")
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                file_data = json.load(file)
                data : Data = {}
                for ann in file_data["annotations"]:
                    if "bbox_pitch" not in ann:
                        continue
                    attributes = ann["attributes"]
                    entry = cre.create_entry(
                        e_bbox=ann["bbox_pitch"], e_track_id=ann["track_id"], e_jersey=attributes["jersey"],
                        e_role=attributes["role"], e_team=attributes["team"])
                    if ann["image_id"] not in data:
                        data[ann["image_id"]] = []
                    data[ann["image_id"]].append(entry)
                data_list.append(data)
        else:
            print(f"Label data not found")
        
        return data_list
    
    # ファイル保存(単体)
    def save_file(self, file_path, data):
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    
    # ファイル保存
    def save_files(self, data_list : List[Data]):
        files = os.path.join(self.data_path, f"edit_datas")
        if os.path.exists(files):
            shutil.rmtree(files)
            print(f"Existed files deleted")
        os.makedirs(files, exist_ok=True)
        
        for data_num in range(len(data_list)):
            data = data_list[data_num]
            file_name = con.convert_num_to_file_name(data_num)
            file_path = os.path.join(files, file_name)
            self.save_file(file_path, data)
        
        print(f"Data saved to {files}")

    # ファイル読み込み(AnyNumbers)
    def load_any_file(self) -> Tuple[List, Frame, Frame]:
        file_path = os.path.join(self.data_path, f"AnyNumbers.txt")

        reverse_numbers = []
        set_frames : Frame = {}
        replay_frames : Frame = {}
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
                        if mode == "reverse":
                            for part in parts:
                                reverse_numbers.append(int(part))
                        elif mode == "set":
                            data_num = int(parts[0])
                            start_frame = int(parts[1])
                            end_frame = int(parts[2])
                            set_frames[data_num] = (start_frame, end_frame)
                        elif mode == "replay":
                            data_num = int(parts[0])
                            start_frame = int(parts[1])
                            end_frame = int(parts[2])
                            replay_frames[data_num] = (start_frame, end_frame)

        return reverse_numbers, set_frames, replay_frames

    # ファイル読み込み(FilterFrames)
    def load_filter_file(self) -> Frame:
        file_path = os.path.join(self.data_path, f"FilterNumbers.txt")
        
        filter_frames : Frame = {}
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                elif line == "fin":
                    break
                else:
                    parts = shlex.split(line)
                    data_num = int(parts[0])
                    start_frame = int(parts[1])
                    end_frame = int(parts[2])
                    filter_frames[data_num] = (start_frame, end_frame)
        
        return filter_frames

    # ファイル読み込み(Formations)
    def load_formation_file(self) -> Tuple[Formations, Formations]:
        file_path = os.path.join(self.data_path, f"Formations.txt")

        formations_0 : Formations = {}
        formations_1 : Formations = {}
        formation_num = 0
        data_num = 0
        start_frame = 1
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                elif line == "fin":
                    break
                else:
                    parts = shlex.split(line)
                    if parts[0] == "formation":
                        formation_num = int(parts[1])
                    elif parts[0] == "start":
                        data_num = int(parts[1])
                        start_frame = int(parts[2])
                    else:
                        jerseis = []
                        for part in parts:
                            jerseis.append(part.strip('"'))
                        if formation_num == 0:
                            if (data_num, start_frame) not in formations_0:
                                formations_0[(data_num, start_frame)] = []
                            formations_0[(data_num, start_frame)].append(jerseis)
                        elif formation_num == 1:
                            if (data_num, start_frame) not in formations_1:
                                formations_1[(data_num, start_frame)] = []
                            formations_1[(data_num, start_frame)].append(jerseis)
        
        return formations_0, formations_1

    # ファイル読み込み(EditNumbers)
    def load_edit_file(self) -> List[Edit]:
        file_path = os.path.join(self.data_path, f"EditNumbers.txt")

        edit_numbers : List[Edit] = []
        start_frame = 1
        end_frame = max_frame
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
                        edit_numbers.append({})
                        start_frame = 1
                        end_frame = max_frame
                    elif parts[0] == "start":
                        start_frame = int(parts[1])
                    elif parts[0] == "end":
                        end_frame = int(parts[1])
                    else:
                        track_id = float(parts[0])
                        jersey = parts[1]
                        if len(parts) == 2:
                            team = "nan" if jersey == "" else ""
                        else:
                            team = parts[2]
                        edit_number = edit_numbers[-1]
                        if (start_frame, end_frame) not in edit_number:
                            edit_number[(start_frame, end_frame)] = []
                        edit_number[(start_frame, end_frame)].append((track_id, jersey, team))

        print(f"Loaded {len(edit_numbers)} in edit file")
        return edit_numbers

    # ファイル読み込み(DeleteNumbers)
    def load_delete_file(self) -> Delete:
        file_path = os.path.join(self.data_path, f"DeleteNumbers.txt")

        delete_numbers : Delete = {}
        data_num = 0
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
                        data_num = int(parts[0])
                        if data_num not in delete_numbers:
                            delete_numbers[data_num] = []
                    else:
                        frame_num = int(parts[0])
                        track_id = float(parts[1])
                        delete_numbers[data_num].append((frame_num, track_id))
        
        return delete_numbers