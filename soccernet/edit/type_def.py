from typing import List, Dict, Tuple
from typing_extensions import TypedDict

# ピッチサイズ
pitch_width = 105
pitch_length = 68

# フレーム数
max_frame = 750

# 座標
Location = List[float]

# 入力用データ
class BBoxPitch(TypedDict):
    x_bottom_left: float
    y_bottom_left: float
    x_bottom_right: float
    y_bottom_right: float
    x_bottom_middle: float
    y_bottom_middle: float
class Entry(TypedDict):
    bbox_pitch: BBoxPitch
    track_id: float
    jersey: str
    role: str
    team: str
Data = Dict[str, List[Entry]]

# 各ファイル用データ
Frame = Dict[int, Tuple[int, int]] #dict{data_num, (start_frame, end_frame)}
Edit = Dict[Tuple[int, int], List[Tuple[float, str, str]]] #dict{(start_frame, end_frame), list[(track_id, jersey, team)]}
Delete = Dict[int, List[Tuple[int, float]]] #dict{data_num, list[(frame_num, track_id)]}
Formation = List[List[str]] #list[list[jersey]]
Formations = Dict[Tuple[int, int], Formation] #dict{(data_num, start_frame), formation}

# 各選手情報（座標、関係性）保存用データ
Relation = Dict[str, Location]
class PlayerInfo(TypedDict):
    position: Tuple[int, int]
    location: Location
    relation: Relation
PlayerList = Dict[str, PlayerInfo]
PlayerLists = Dict[Tuple[int, int], PlayerList]

# 座標時系列データ（座標補間用）データ
Trajectory = Dict[str, List[Tuple[float, Location]]] #dict{jersey, list[(time, location)]}
Trajectories = Dict[Tuple[int, int], Trajectory] #dict{(data_num, start_frame), trajectory}

# 出力用データ
class SimpleInfo(TypedDict):
    location: Location
    jersey: str
    team: str
SimpleData = Dict[str, List[SimpleInfo]]

# GS-HOTA計算用データ
FrameMatchIds = List[Tuple[float, float]]

__all__ = [
    "pitch_width", "pitch_length", "max_frame",
    "BBoxPitch", "Entry", "Data",
    "Frame", "Edit", "Delete", "Formation", "Formations",
    "Relation", "PlayerInfo", "PlayerList", "PlayerLists",
    "Trajectory", "Trajectories",
    "SimpleInfo", "SimpleData"
]