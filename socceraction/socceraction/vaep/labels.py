"""Implements the label tranformers of the VAEP framework."""

import pandas as pd  # type: ignore
from pandera.typing import DataFrame

import socceraction.spadl.config as spadl
from socceraction.spadl.schema import SPADLSchema


def scores(actions: DataFrame[SPADLSchema], nr_actions: int = 10) -> pd.DataFrame:
    """Determine whether the team possessing the ball scored a goal within the next x actions.

    Parameters
    ----------
    actions : pd.DataFrame
        The actions of a game.
    nr_actions : int, default=10  # noqa: DAR103
        Number of actions after the current action to consider.

    Returns
    -------
    pd.DataFrame
        A dataframe with a column 'scores' and a row for each action set to
        True if a goal was scored by the team possessing the ball within the
        next x actions; otherwise False.
    """
    # merging goals, owngoals and team_ids

    goals = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("success")
    )
    owngoals = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("owngoal")
    )
    y = pd.concat([goals, owngoals, actions["team_id"]], axis=1)
    y.columns = ["goal", "owngoal", "team_id"]

    # adding future results
    for i in range(1, nr_actions):
        for c in ["team_id", "goal", "owngoal"]:
            shifted = y[c].shift(-i)
            shifted[-i:] = y[c].iloc[len(y) - 1]
            y["%s+%d" % (c, i)] = shifted

    res = y["goal"]
    for i in range(1, nr_actions):
        gi = y["goal+%d" % i] & (y["team_id+%d" % i] == y["team_id"])
        ogi = y["owngoal+%d" % i] & (y["team_id+%d" % i] != y["team_id"])
        res = res | gi | ogi

    return pd.DataFrame(res, columns=["scores"])


def concedes(actions: DataFrame[SPADLSchema], nr_actions: int = 10) -> pd.DataFrame:
    """Determine whether the team possessing the ball conceded a goal within the next x actions.

    Parameters
    ----------
    actions : pd.DataFrame
        The actions of a game.
    nr_actions : int, default=10  # noqa: DAR103
        Number of actions after the current action to consider.

    Returns
    -------
    pd.DataFrame
        A dataframe with a column 'concedes' and a row for each action set to
        True if a goal was conceded by the team possessing the ball within the
        next x actions; otherwise False.
    """
    # merging goals,owngoals and team_ids
    goals = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("success")
    )
    owngoals = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("owngoal")
    )
    y = pd.concat([goals, owngoals, actions["team_id"]], axis=1)
    y.columns = ["goal", "owngoal", "team_id"]

    # adding future results
    for i in range(1, nr_actions):
        for c in ["team_id", "goal", "owngoal"]:
            shifted = y[c].shift(-i)
            shifted[-i:] = y[c].iloc[len(y) - 1]
            y["%s+%d" % (c, i)] = shifted

    res = y["owngoal"]
    for i in range(1, nr_actions):
        gi = y["goal+%d" % i] & (y["team_id+%d" % i] != y["team_id"])
        ogi = y["owngoal+%d" % i] & (y["team_id+%d" % i] == y["team_id"])
        res = res | gi | ogi

    return pd.DataFrame(res, columns=["concedes"])


def goal_from_shot(actions: DataFrame[SPADLSchema]) -> pd.DataFrame:
    """Determine whether a goal was scored from the current action.

    This label can be use to train an xG model.

    Parameters
    ----------
    actions : pd.DataFrame
        The actions of a game.

    Returns
    -------
    pd.DataFrame
        A dataframe with a column 'goal' and a row for each action set to
        True if a goal was scored from the current action; otherwise False.
    """
    goals = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("success")
    )

    return pd.DataFrame(goals, columns=["goal_from_shot"])

# add existing model
def recoveries(actions: DataFrame[SPADLSchema], nr_actions: int = 10) -> pd.DataFrame:

    # merging tackles, interceptions and team_ids
    tackles = actions["type_name"].str.contains("tackle") & (
        actions["result_id"] == spadl.results.index("success")
    )
    interceptions = actions["type_name"].str.contains("interception") & (
        actions["result_id"] == spadl.results.index("success")
    )
    y = pd.concat([tackles, interceptions, actions["team_id"]], axis=1)
    y.columns = ["tackle", "interception", "team_id"]

    # adding future results
    for i in range(nr_actions):
        for c in ["team_id", "tackle", "interception"]:
            shifted = y[c].shift(-i)
            shifted[-i:] = y[c][len(y) - 1]
            y['%s+%d' % (c, i)] = shifted

    res = y["tackle"] | y["interception"]
    for i in range(1, nr_actions):
        ti = y["tackle+%d" % i] & (y["team_id+%d" % i] == y["team_id"])
        ii = y["interception+%d" % i] & (y["team_id+%d" % i] == y["team_id"])
        res = res | ti | ii

    return pd.DataFrame(res, columns=["recoveries"])

def losts(actions: DataFrame[SPADLSchema], nr_actions: int = 10) -> pd.DataFrame:

    # merging tackles, interceptions and team_ids
    tackles = actions["type_name"].str.contains("tackle") & (
        actions["result_id"] == spadl.results.index("success")
    )
    interceptions = actions["type_name"].str.contains("interception") & (
        actions["result_id"] == spadl.results.index("success")
    )
    y = pd.concat([tackles, interceptions, actions["team_id"]], axis=1)
    y.columns = ["tackle", "interception", "team_id"]

    # adding future results
    for i in range(nr_actions):
        for c in ["team_id", "tackle", "interception"]:
            shifted = y[c].shift(-i)
            shifted[-i:] = y[c][len(y) - 1]
            y['%s+%d' % (c, i)] = shifted

    res = 0
    for i in range(1, nr_actions):
        ti = y["tackle+%d" % i] & (y["team_id+%d" % i] != y["team_id"])
        ii = y["interception+%d" % i] & (y["team_id+%d" % i] != y["team_id"])
        res = res | ti | ii

    return pd.DataFrame(res, columns=["losts"])

def attacked(actions: DataFrame[SPADLSchema], nr_actions: int = 10) -> pd.DataFrame:

    # merging crosses, shots and team_ids
    crosses = actions["type_name"].str.contains("cross") & (
        actions["result_id"] == spadl.results.index("success")
    )
    shots = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("success")
    )
    owngoals = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("owngoal")
    )
    y = pd.concat([crosses, shots, owngoals, actions["team_id"]], axis=1)
    y.columns = ["cross", "shot", "owngoal", "team_id"]

    # adding future results
    for i in range(1, nr_actions):
        for c in ["team_id", "cross", "shot", "owngoal"]:
            shifted = y[c].shift(-i)
            shifted[-i:] = y[c][len(y) - 1]
            y["%s+%d" % (c, i)] = shifted

    res = y["owngoal"]
    for i in range(1, nr_actions):
        cri = y["cross+%d" % i] & (y["team_id+%d" % i] != y["team_id"])
        si = y["shot+%d" % i] & (y["team_id+%d" % i] != y["team_id"])
        ogi = y["owngoal+%d" % i] & (y["team_id+%d" % i] == y["team_id"])
        res = res | cri | si | ogi
    
    return pd.DataFrame(res, columns=["attacked"])

def attacks(actions: DataFrame[SPADLSchema], nr_actions: int = 10) -> pd.DataFrame:

    # merging crosses, shots and team_ids
    crosses = actions["type_name"].str.contains("cross") & (
        actions["result_id"] == spadl.results.index("success")
    )
    shots = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("success")
    )
    owngoals = actions["type_name"].str.contains("shot") & (
        actions["result_id"] == spadl.results.index("owngoal")
    )
    y = pd.concat([crosses, shots, owngoals, actions["team_id"]], axis=1)
    y.columns = ["cross", "shot", "owngoal", "team_id"]

    # adding future results
    for i in range(1, nr_actions):
        for c in ["team_id", "cross", "shot", "owngoal"]:
            shifted = y[c].shift(-i)
            shifted[-i:] = y[c][len(y) - 1]
            y["%s+%d" % (c, i)] = shifted

    res = y["cross"] | y["shot"]
    for i in range(1, nr_actions):
        cri = y["cross+%d" % i] & (y["team_id+%d" % i] == y["team_id"])
        si = y["shot+%d" % i] & (y["team_id+%d" % i] == y["team_id"])
        ogi = y["owngoal+%d" % i] & (y["team_id+%d" % i] != y["team_id"])
        res = res | cri | si | ogi
    
    return pd.DataFrame(res, columns=["attacks"])
