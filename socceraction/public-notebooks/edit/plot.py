import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
from edit.type_def import beta_range, LocationData
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

def plot_value(playersR: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 6))
    plt.scatter(playersR["vaep_value"], playersR["location_value"], alpha=0.7)

    id_name_map = {}

    for idx, (i, row) in enumerate(playersR.iterrows(), start=1):
        id_name_map[idx] = row["player_name"]

        plt.text(
            row["vaep_value"] + 0.01,
            row["location_value"] + 0.01,
            str(idx),
            fontsize=8
        )

    plt.xlabel("Action Value")
    plt.ylabel("Location Value")
    plt.title("Action Value and Location Value")
    plt.grid(True)
    plt.show()

    # 対応表を文字列として出力
    mapping_str = "\n".join([f"{k} & {v}" for k, v in id_name_map.items()])
    print("番号と選手名の対応")
    print(mapping_str)
