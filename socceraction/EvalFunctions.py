import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
from typing_extensions import TypedDict
from scipy.stats import pearsonr, spearmanr

columns = [
    "game_id", "period_id", "team_id", "player_id",
    "location_x", "location_y", "action_id"
]

# ピッチサイズ
pitch_width = 105
pitch_length = 68
grid_x = 50
grid_y = 34

# データ構造体定義
class PlayerInfo(TypedDict):
    player_name : str
    team_id : int
PlayerNames = Dict[float, PlayerInfo]

Heatmaps = Dict[float, np.ndarray]
ActionRanges = Dict[float, Tuple[int, int]]

PlayerRating = Dict[str, float]

# ファイル読み込み(KeeperNames)
def load_keeper_file(name_file):
    keeper_names = []
    iskeeper = False

    with open(name_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            elif line == "fin":
                break
            elif line.startswith("team"):
                continue
            elif line == "keeper":
                iskeeper = True
            else:
                if iskeeper:
                    parts = line.split(' ', 1)
                    keeper_name = parts[1].strip('"')
                    keeper_names.append(keeper_name)

    return keeper_names

# ファイル読み込み(ベンチ)
def load_bench_file(name_file):
    bench_names = []
    isbench = False

    with open(name_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            elif line.startswith("team"):
                continue
            elif line.isdigit():
                isbench = True
            elif line.startswith("out"):
                continue
            elif line == "keeper":
                isbench = False
            else:
                if isbench:
                    parts = line.split(' ', 1)
                    bench_name = parts[1].strip('"')
                    bench_names.append(bench_name)
    
    return bench_names

# ファイル読み(PlayerRating)
def load_rating_file(rating_file):
    player_rating : PlayerRating = {}

    with open(rating_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            elif line == 'fin':
                break
            else:
                parts = line.split(' ', 1)
                rating = float(parts[0].strip('"'))
                player_name = parts[1].strip('"')
                player_rating[player_name] = rating
    
    return player_rating

# ファイル読み(Position)
def load_position_file(rating_file):
    positions : Dict[str, str] = {}

    with open(rating_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            elif line == 'fin':
                break
            else:
                parts = line.split(' ', 1)
                position = parts[0].strip('"')
                player_name = parts[1].strip('"')
                positions[player_name] = position
    
    return positions

# ゲームIDの指定
def specify_game_id(action_locations : pd.DataFrame, game_id):
    game_locations = action_locations[action_locations["game_id"] == game_id]
    return game_locations

# player情報の作成
def create_player_names(players : pd.DataFrame, game_locations : pd.DataFrame):
    player_names : PlayerNames = {}
    for player_id, group in game_locations.groupby("player_id"):
        player_name = players.loc[players["player_id"] == player_id, ["nickname", "player_name"]].apply(lambda x: x.iloc[0] if x.iloc[0] else x.iloc[1], axis=1).values[0]
        team_id = group["team_id"].values[0]
        player_names[player_id] = {
            "player_name" : player_name,
            "team_id" : team_id
        }
    
    return player_names

# ヒートマップ作成
def create_heatmaps(game_locations : pd.DataFrame):
    player_locations : Dict[float, Tuple[np.ndarray, np.ndarray]] = {}
    for player_id, group in game_locations.groupby("player_id"):
        group = group.dropna(subset=["location_x", "location_y"])
        x = group["location_x"].values
        y = group["location_y"].values
        player_locations[player_id] = (x, y)

    heatmaps : Heatmaps = {}
    for player_id, (x, y) in player_locations.items():
        heatmap, _, _ = np.histogram2d(
            x, y,
            bins=[grid_x, grid_y],
            range=[[0, pitch_width], [0, pitch_length]]
        )
        heatmaps[player_id] = heatmap
    
    return heatmaps

# ヒートマップの可視化
def plot_heatmap(heatmap : np.ndarray, id):
    plt.figure(figsize=(8, 5))
    sns.heatmap(
        np.flipud(heatmap.T),
        cmap="Reds", cbar=True,
        xticklabels=False, yticklabels=False
    )
    plt.title(f"Heatmap for id: {id}")
    plt.xlabel("Pitch X")
    plt.ylabel("Pitch Y")
    plt.show()

# 出場時間（action_id）の範囲を取得
def get_action_ranges(game_locations : pd.DataFrame):
    action_ranges : ActionRanges = {}
    for player_id, group in game_locations.groupby("player_id"):
        action_ids = group["action_id"].values
        start_id = np.min(action_ids)
        end_id = np.max(action_ids)
        action_ranges[player_id] = (start_id, end_id)
    
    return action_ranges

# 各グリッドのVAEPスコアを集計
def create_vaep_map(team_actions : pd.DataFrame, isoff):
    x = team_actions["start_x"].values
    y = team_actions["start_y"].values
    if isoff:
        vaep = team_actions["offensive_value"].values
    else:
        vaep = team_actions["defensive_value"].values
    vaep_map, _, _ = np.histogram2d(
        x, y,
        bins=[grid_x, grid_y],
        range=[[0, pitch_width], [0, pitch_length]],
        weights=vaep
    )
    return vaep_map

# 各選手の座標スコアを計算
def calc_location_value(game_actions : pd.DataFrame, heatmap : np.ndarray, team_id, action_range : Tuple[int, int]):
    start_id, end_id = action_range
    active_actions = game_actions[(game_actions["action_id"] >= start_id) & (game_actions["action_id"] <= end_id)]
    team_actions = active_actions[active_actions["team_id"] == team_id]
    # opp_actions = active_actions[active_actions["team_id"] != team_id]
    team_map_off = create_vaep_map(team_actions, True)
    team_map_def = create_vaep_map(team_actions, False)
    # opp_map_off = create_vaep_map(opp_actions, True)
    # opp_map_def = create_vaep_map(opp_actions, False)

    # loc_value_map_off = (team_map_off - opp_map_def) * heatmap
    loc_value_map_off = team_map_off * heatmap
    # loc_value_map_def = (team_map_def - opp_map_off) * heatmap
    loc_value_map_def = team_map_def * heatmap
    return np.sum(loc_value_map_off), np.sum(loc_value_map_def)

# データフレーム作成
def create_data_frame(player_id, player_name, loc_value, loc_value_off, loc_value_def):
    return {
        "player_id" : player_id,
        "player_name" : player_name,
        "location_value" : loc_value,
        "off_location_value": loc_value_off,
        "def_location_value": loc_value_def
    }

# 選手の座標スコアを計算
def calc_all_location_value(gamma, game_actions : pd.DataFrame, player_names : PlayerNames, heatmaps : Heatmaps, action_ranges : ActionRanges):
    loc_values = []
    for player_id, player_info in player_names.items():
        heatmap = heatmaps[player_id]
        action_range = action_ranges[player_id]
        loc_value_off, loc_value_def = calc_location_value(game_actions, heatmap, player_info["team_id"], action_range)
        loc_value = loc_value_off + gamma * loc_value_def
        pd_entry = create_data_frame(player_id, player_info["player_name"], loc_value, loc_value_off, loc_value_def)
        loc_values.append(pd_entry)

    return pd.DataFrame(loc_values)

# アクションデータと座標スコアを合体する
def add_location_value_to_playersR(playersR : pd.DataFrame, loc_values : pd.DataFrame):
    playersR = playersR.merge(loc_values[["player_id", "location_value", "off_location_value", "def_location_value"]], on="player_id", how="left")
    return playersR

# トータルスコアの計算
def calc_total_score(playersR : pd.DataFrame, a):
    playersR["total_value"] = playersR["vaep_value"] + a * playersR["location_value"]
    return playersR

# 選手の除外
def delete_player(playersR : pd.DataFrame, player_names):
    playersR = playersR[~playersR["player_name"].isin(player_names)]
    return playersR

# 選手採点値の追加
def add_player_rating(playersR : pd.DataFrame, player_rating : PlayerRating):
    playersR["player_rating"] = playersR["player_name"].map(player_rating)
    return playersR

# ポジションの追加
def add_positions(playersR : pd.DataFrame, positions : Dict[str, str]):
    playersR["position"] = playersR["player_name"].map(positions)
    return playersR

# 相関係数の計算
def calc_corr(playersR : pd.DataFrame, value1, value2):
    pearson_corr, _ = pearsonr(playersR[value1], playersR[value2])
    spearman_corr, _ = spearmanr(playersR[value1], playersR[value2])
    return pearson_corr, spearman_corr

# アクション評価値と座標スコアのグラフ
def plot_value(playersR : pd.DataFrame):
    plt.figure(figsize=(8, 6))
    plt.scatter(playersR["vaep_value"], playersR["location_value"], alpha=0.7)

    for i, row in playersR.iterrows():
        plt.text(
            row["vaep_value"] + 0.01,
            row["location_value"] + 0.01,
            row["player_name"],
            fontsize=8
        )
    plt.xlabel("Action Value")
    plt.ylabel("Location Value")
    plt.title("Action Value and Location Value")
    plt.grid(True)
    plt.show()

# 割合を変えながら実行してグラフ化
def plot_corr(playersR : pd.DataFrame, value1, value2):
    a_values = np.linspace(0, 1, 1000)
    pearson_corrs = []
    spearman_corrs = []
    for a in a_values:
        playersR = calc_total_score(playersR, a)
        pearson_corr, spearman_corr = calc_corr(playersR, value1, value2)
        pearson_corrs.append(pearson_corr)
        spearman_corrs.append(spearman_corr)

    pearson_corrs = np.array(pearson_corrs)
    spearman_corrs = np.array(spearman_corrs)
    max_index = np.argmax(spearman_corrs)
    a_max = a_values[max_index]
    print(f"max: a = {a_max}")

    # グラフ描画
    plt.plot(a_values, pearson_corrs, label="pearson_corr")
    plt.plot(a_values, spearman_corrs, label="spearman_corr")
    plt.xlabel("a")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_corr_list(playersR_list, value1, value2):
    """
    playersR_list: DataFrame または DataFrame のリスト（1つまたは複数対応）
    value1, value2: 相関を取る列名
    """

    # 単一DataFrameの場合にリスト化
    if isinstance(playersR_list, pd.DataFrame):
        playersR_list = [playersR_list]

    beta_values = np.linspace(0, 0.2, 1000)

    all_pearson_corrs = []
    all_spearman_corrs = []

    # 各DataFrameについて相関計算
    for idx, playersR in enumerate(playersR_list):
        pearson_corrs = []
        spearman_corrs = []
        for beta in beta_values:
            playersR_tmp = calc_total_score(playersR.copy(), beta)
            pearson_corr, spearman_corr = calc_corr(playersR_tmp, value1, value2)
            pearson_corrs.append(pearson_corr)
            spearman_corrs.append(spearman_corr)
        all_pearson_corrs.append(pearson_corrs)
        all_spearman_corrs.append(spearman_corrs)

    # NumPy配列に変換（形: [playersR数, a_values数]）
    all_spearman_corrs = np.array(all_spearman_corrs)
    all_pearson_corrs = np.array(all_pearson_corrs)

    # 各aにおけるSpearman平均を計算
    mean_spearman_corrs = np.mean(all_spearman_corrs, axis=0)
    mean_pearson_corrs = np.mean(all_pearson_corrs, axis=0)
    mean_corrs = mean_spearman_corrs + mean_pearson_corrs

    # 平均Spearman相関が最大のaを探索
    max_index = np.argmax(mean_corrs)
    beta_max = beta_values[max_index]
    max_corr = mean_corrs[max_index]

    print(f"平均Spearman相関が最大: beta = {beta_max:.4f}, 相関 = {max_corr:.4f}")

    # --- グラフ描画 ---
    # 各playersRの個別相関
    for i in range(len(playersR_list)):
        plt.plot(beta_values, all_spearman_corrs[i], alpha=0.4, label=f"spearman(match{i+1})")
        plt.plot(beta_values, all_pearson_corrs[i], alpha=0.3, linestyle="--", label=f"pearson(match{i+1})")

    plt.axvline(beta_max, color="red", linestyle="--", label=f"maxβ={beta_max:.4f}")

    plt.xlabel("β")
    plt.ylabel("correlation")
    plt.legend()
    plt.grid(True)
    plt.show()

    return beta_max

# 平均値算出
def calc_average(playersR : pd.DataFrame, col):
    mean_val = playersR[col].mean()
    print(mean_val)
    return mean_val