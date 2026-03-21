import math

# 加算
def calc_add(loc1, loc2):
    return [loc1[0] + loc2[0], loc1[1] + loc2[1]]

# 減算
def calc_sub(loc1, loc2):
    return [loc1[0] - loc2[0], loc1[1] - loc2[1]]

# スカラー倍
def calc_scalar(f, loc):
    return[f * loc[0], f * loc[1]]

# ルート
def cal_root(f):
    return math.sqrt(f)

# ベクトルの大きさ
def calc_norm(loc):
    return math.sqrt(loc[0]**2 + loc[1]**2)

# 距離
def calc_distance(loc1, loc2):
    return calc_norm(calc_sub(loc1, loc2))

# 絶対値の大小比較（左が大きいか）
def calc_order_of_abs(f1, f2):
    return math.fabs(f1) > math.fabs(f2)

# 内積
def calc_dot(loc1, loc2):
    return loc1[0] * loc2[0] + loc1[1] * loc2[1]

# コサイン類似度
def calc_cos(loc1, loc2):
    dot_product = calc_dot(loc1, loc2)
    norm_loc1 = calc_norm(loc1)
    norm_loc2 = calc_norm(loc2)
    return dot_product / (norm_loc1 * norm_loc2)

# ２つのベクトルの平均
def calc_average(loc1, loc2):
    return calc_scalar(0.5, calc_add(loc1, loc2))

# ２つのベクトルの間の時間を線形補間
def calc_linear(time, t1, loc1, t2, loc2):
    ratio = (time - t1) / (t2 - t1)
    return calc_add(loc1, calc_scalar(ratio, calc_sub(loc2, loc1)))

# 位置ベースの類似度スコア
def calc_location_sim(loc1, loc2, tau):
    dis = calc_distance(loc1, loc2)
    return math.exp(math.log(0.05) * dis**2 / tau**2)