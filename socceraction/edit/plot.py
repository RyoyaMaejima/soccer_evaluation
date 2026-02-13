import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
from edit.type_def import LocationData, Heatmaps
import edit.convert_take as con
import edit.fns as fns
import edit.eval_func as ef

def nice_time(row):
    minute = int((row.period_id-1)*45 +row.time_seconds // 60)
    second = int(row.time_seconds % 60)
    return f"{minute}m{second}s"

# 描画
def plot_action_data(
    actions : pd.DataFrame, game : pd.DataFrame, location_data_list : List[LocationData], action_num : int
) -> None:
    # Select the 5 actions
    shot = action_num
    a = actions[shot:shot+1].copy()

    # Print the game date and timestamp
    g = game.iloc[0]
    minute = int((a.period_id.values[0]-1) * 45 + a.time_seconds.values[0] // 60)
    game_info = f"{g.game_date} {g.home_team_name} {g.home_score}-{g.away_score} {g.away_team_name} {minute + 1}'"
    print(game_info)

    # Plot the actions
    a["nice_time"] = a.apply(nice_time, axis=1)
    labels = a[["nice_time", "type_name", "player_name", "team_name"]]

    location_data : LocationData = location_data_list[action_num]
    o_player_names, o_locations, o_jerseis, o_team_names = con.take_plot_data(location_data)
    o_player_names = np.array(o_player_names)
    o_locations = np.array(o_locations)
    o_jerseis = np.array(o_jerseis)
    o_team_names = np.array(o_team_names)
    ax = fns.actions_with_players(
        location=a[["start_x", "start_y", "end_x", "end_y"]],
        action_type=a.type_name,
        team=a.team_name,
        result=a.result_name == "success",
        label=labels,
        labeltitle=["time", "actiontype", "player", "team"],
        zoom=False,
        figsize=6,
        o_locations=o_locations,
        o_team_names=o_team_names,
        o_names=o_jerseis
    )

# ヒートマップの描画
def plot_heatmaps(heatmap : np.ndarray, player_id : float) -> None:
    plt.figure(figsize=(8, 5))
    sns.heatmap(
        np.flipud(heatmap.T),
        cmap="Reds", cbar=True,
        xticklabels=False, yticklabels=False
    )
    plt.title(f"Heatmap for id: {player_id}")
    plt.xlabel("Pitch X")
    plt.ylabel("Pitch Y")
    plt.show()

# βの割合を変えながら実行してグラフ化
def plot_corr_by_beta(playersR_list : List[pd.DataFrame], value1, value2) -> float:
    beta_values = np.linspace(0, 0.2, 1000)

    all_pearson_corrs = []
    all_spearman_corrs = []

    # 各DataFrameについて相関計算
    for idx, playersR in enumerate(playersR_list):
        pearson_corrs = []
        spearman_corrs = []
        for beta in beta_values:
            playersR_tmp = ef.calc_total_score(playersR.copy(), beta)
            pearson_corr, spearman_corr = ef.calc_corr(playersR_tmp, value1, value2)
            pearson_corrs.append(pearson_corr)
            spearman_corrs.append(spearman_corr)
        all_pearson_corrs.append(pearson_corrs)
        all_spearman_corrs.append(spearman_corrs)

    all_spearman_corrs = np.array(all_spearman_corrs)
    all_pearson_corrs = np.array(all_pearson_corrs)

    mean_spearman_corrs = np.mean(all_spearman_corrs, axis=0)
    mean_pearson_corrs = np.mean(all_pearson_corrs, axis=0)
    mean_corrs = mean_spearman_corrs + mean_pearson_corrs

    max_index = np.argmax(mean_corrs)
    beta_max = beta_values[max_index]
    max_corr = mean_corrs[max_index]

    print(f"平均Spearman相関が最大: beta = {beta_max:.4f}, 相関 = {max_corr:.4f}")

    # グラフ描画
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

# アクションスコアと座標スコアのグラフ
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