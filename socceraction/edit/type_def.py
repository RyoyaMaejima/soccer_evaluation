import numpy as np
from typing import List, Dict, Tuple
from typing_extensions import TypedDict

columns = [
    "game_id", "period_id", "team_id", "player_id",
    "location_x", "location_y", "action_id"
]

# ピッチサイズ
pitch_width = 105
pitch_length = 68
grid_x = 50
grid_y = 34

# 時間間隔
time_interval = 0.04

# チームの色
team_colors = {"Liverpool" : "red", "Chelsea" : "blue", "Manchester United" : "red", "Manchester City" : "blue"}

# 座標
Location = List[float]

# 入力用データ
class SimpleInfo(TypedDict):
    location: Location
    jersey: str
    team: str
SimpleData = Dict[str, List[SimpleInfo]]

# 選手情報
class PlayerInfo(TypedDict):
    team_name: str
    jersey: str
    position: str
    rating: float

# 各ファイル用データ
TeamNames = Dict[str, str] #dict{team_side, team_name}
DeleteRanges = List[Tuple[int, int]] #list[(start_action_num, end_action_num)]
PlayerNames = Dict[str, Dict[str, str]] #dict{team, dict{jersey, player_name}}
PlayerInfos = Dict[str, PlayerInfo]
CornerInfos = Dict[Tuple[int, int], Tuple[str, Location]] #dict{(start_action_num, end_action_num), (player_name, location)}
SubStitutions = List[Tuple[str, str]] #list[(in_player_name, out_player_name)]

# アクションデータ合体用データ
LocationData = Dict[str, SimpleInfo] #dict{player_name, simple_info}

# 出場選手情報
FieldPlayers = Dict[int, List[str]] #dict{action_num, list(player_name)}

# 選手名とIDの対応
NameIds = Dict[str, Tuple[float, float]] #dict{player_name, (player_id, team_id)}

# ヒートマップ
Heatmaps = Dict[float, np.ndarray]

# 選手の出場範囲
PlayerRanges = Dict[float, Tuple[int, int]] #dict{player_id, (start_action_id, end_action_id)}

__all__ = [
    "pitch_width", "pitch_length", "grid_x", "grid_y", "time_interval", "team_colors",
    "SimpleInfo", "SimpleData", "PlayerInfo", 
    "TeamNames", "DeleteRanges", "PlayerNames", "PlayerInfos", "CornerInfos", "SubStitutions",
    "LocationData", "FieldPlayers",
    "NameIds", "Heatmaps", "PlayerRanges",    
]