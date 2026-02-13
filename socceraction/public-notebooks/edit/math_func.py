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

# ベクトルの大きさ
def calc_norm(loc):
    return math.hypot(loc[0], loc[1])

# ベクトルの角度
def calc_angle(loc):
    return math.atan2(loc[1], loc[0])

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

# 一致する回転角度を計算
def calc_rotate_angle(loc1, loc2):
    r1 = calc_norm(loc1)
    r2 = calc_norm(loc2)
    theta1 = calc_angle(loc1)
    theta2 = calc_angle(loc2)
    scale = r1 / r2 if r2 != 0 else 1
    delta_theta = theta1 - theta2
    return scale, delta_theta

# 回転座標を計算
def calc_rotate_location(loc, scale, delta_theta):
    r = calc_norm(loc)
    theta = calc_angle(loc)
    r *= scale
    theta += delta_theta
    return [r * math.cos(theta), r * math.sin(theta)]

# 無効座標の作成
def create_nan_location():
    return [math.nan, math.nan]

# 無効座標の判定
def calc_is_nan_location(loc):
    return math.isnan(loc[0]) or math.isnan(loc[1])