import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from edit.type_def import *
import edit.create as cre
from scipy.stats import pearsonr, spearmanr

# ゲームIDの指定
def specify_game_id(action_locations : pd.DataFrame, game_id : float) -> pd.DataFrame:
    game_locations = action_locations[action_locations["game_id"] == game_id]
    return game_locations

# 各グリッドのVAEPスコアを集計
def get_vaep_map(team_actions : pd.DataFrame, is_off : bool) -> pd.DataFrame:
    x = team_actions["start_x"].values
    y = team_actions["start_y"].values
    if is_off:
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
def calc_location_value(
    game_actions : pd.DataFrame, heatmap : np.ndarray, team_id : float, player_range : Tuple[int, int]
) -> Tuple[float, float]:
    start_id, end_id = player_range
    active_actions = game_actions[(game_actions["action_id"] >= start_id) & (game_actions["action_id"] <= end_id)]
    team_actions = active_actions[active_actions["team_id"] == team_id]

    team_map_off = get_vaep_map(team_actions, True)
    team_map_def = get_vaep_map(team_actions, False)
    loc_value_map_off = team_map_off * heatmap
    loc_value_map_def = team_map_def * heatmap
    return np.sum(loc_value_map_off), np.sum(loc_value_map_def)

# 全選手の座標スコアを計算
def calc_all_location_value(
    game_actions : pd.DataFrame, heatmaps : Heatmaps, names_ids : NameIds, player_ranges : PlayerRanges, gamma : float, 
) -> pd.DataFrame:
    loc_values_list = []
    for player_name, (player_id, team_id) in names_ids.items():
        heatmap = heatmaps[player_id]
        player_range = player_ranges[player_id]
        loc_value_off, loc_value_def = calc_location_value(game_actions, heatmap, team_id, player_range)
        loc_value = loc_value_off + gamma * loc_value_def
        pd_entry = cre.create_pd_entry_eval(player_id, player_name, loc_value, loc_value_off, loc_value_def)
        loc_values_list.append(pd_entry)
    
    return pd.DataFrame(loc_values_list)

# 選手の除外
def delete_players(playersR : pd.DataFrame, delete_names : List[str]) -> pd.DataFrame:
    playersR = playersR[~playersR["player_name"].isin(delete_names)]
    return playersR

# アクションスコアに座標スコアを追加
def add_location_value_to_playersR(playersR : pd.DataFrame, loc_values : pd.DataFrame) -> pd.DataFrame:
    playersR = playersR.merge(loc_values[["player_id", "location_value", "off_location_value", "def_location_value"]], on="player_id", how="left")
    return playersR

# 選手情報の追加
def add_player_infos(playersR : pd.DataFrame, player_infos : PlayerInfos) ->pd.DataFrame:
    playersR["position"] = playersR["player_name"].map(
        lambda name: player_infos[name]["position"] if name in player_infos else None
    )
    playersR["rating"] = playersR["player_name"].map(
        lambda name: player_infos[name]["rating"] if name in player_infos else None
    )
    return playersR

# βの算出
def calc_beta(playersR_list : List[pd.DataFrame]) -> float:
    playersR_all = pd.concat(playersR_list, ignore_index=True)
    std_a = playersR_all["vaep_value"].std()
    std_l = playersR_all["location_value"].std()
    beta = std_a / std_l
    return beta

# トータルスコアの計算
def calc_total_score(playersR_list : List[pd.DataFrame], beta : float) -> None:
    for playersR in playersR_list:
        playersR["total_value"] = playersR["vaep_value"] + beta * playersR["location_value"]

# 得点者フラグの付与
def calc_is_scorer(playersR_list : List[pd.DataFrame], scorer : List[List[str]]) -> None:
    for i, playersR in enumerate(playersR_list):
        playersR["is_scorer"] = playersR["player_name"].isin(scorer[i])

# 分布の計算
def calc_distribution(playersR_list : List[pd.DataFrame]) -> Tuple[float, float, float, float]:
    playersR_all = pd.concat(playersR_list, ignore_index=True)
    scorer_all = playersR_all[playersR_all["is_scorer"]]
    nonscorer_all = playersR_all[~playersR_all["is_scorer"]]

    mu_G = scorer_all["rating"].mean()
    std_G = scorer_all["rating"].std(ddof=0)
    mu_N = nonscorer_all["rating"].mean()
    std_N = nonscorer_all["rating"].std(ddof=0)
    return mu_G, std_G, mu_N, std_N

# 分布正規化
def batch_normalization(playersR_list : List[pd.DataFrame]) -> None:
    mu_G, std_G, mu_N, std_N = calc_distribution(playersR_list)
    for playersR in playersR_list:
        playersR["rating_dist_align"] = playersR["rating"]
        mask = playersR["is_scorer"]
        playersR.loc[mask, "rating_dist_align"] = (
            mu_N + (std_N / std_G) * (playersR.loc[mask, "rating"] - mu_G)
        )

# 相関係数の計算
def calc_corr(playersR : pd.DataFrame, value1, value2) -> Tuple[float, float]:
    pearson_corr, _ = pearsonr(playersR[value1], playersR[value2])
    spearman_corr, _ = spearmanr(playersR[value1], playersR[value2])
    return pearson_corr, spearman_corr