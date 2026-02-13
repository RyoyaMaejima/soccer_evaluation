import pandas as pd
from typing import List, Dict, Tuple

# 選手名の一部からあてはまる選手を検索
def search_players(actions : pd.DataFrame, keyword : str) -> None:
    unique_names = actions["player_name"].dropna().unique()
    matched_names = [name for name in unique_names if keyword.lower() in name.lower()]
    for filename in matched_names:
        print(filename)

# 後半の検索
def search_second_half(actions : pd.DataFrame) -> None:
    for action_num in range(len(actions)):
        a = actions.iloc[action_num]
        if a["period_id"] == 2:
            print(action_num)
            return