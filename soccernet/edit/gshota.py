import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Dict, Tuple
from edit.type_def import *
import edit.convert_take as con
import edit.math_func as mf

class GSHOTA:
    def __init__(self, alpha=0.5, tau=5.0):
        self.alpha = alpha
        self.tau = tau

    # ID類似度スコア
    def calc_id_sim(self, entry1 : Entry, entry2 : Entry) -> int:
        location1, track_id1, jersey1, team1 = con.take_entry_info(entry1)
        location2, track_id2, jersey2, team2 = con.take_entry_info(entry2)
        if (jersey1 == jersey2) and (team1 == team2):
            return 1
        else:
            return 0
        
    # 類似度スコア
    def calc_sim(self, entry1 : Entry, entry2 : Entry) -> float:
        location1, track_id1, jersey1, team1 = con.take_entry_info(entry1)
        location2, track_id2, jersey2, team2 = con.take_entry_info(entry2)
        return mf.calc_location_sim(location1, location2, self.tau) * self.calc_id_sim(entry1, entry2)
    
    # ハンガリアン法でマッチング
    def match_gt_pred(self, frame_data_gt : List[Entry], frame_data_pred : List[Entry]) -> FrameMatchIds:
        n_gt = len(frame_data_gt)
        n_pred= len(frame_data_pred)
        sim_matrix = np.zeros((n_gt, n_pred))

        for i in range(n_gt):
            for j in range(n_pred):
                sim_matrix[i, j] = self.calc_sim(frame_data_gt[i], frame_data_pred[j])
        
        cost_matrix = 1 - sim_matrix
        gt_idx, pred_idx = linear_sum_assignment(cost_matrix)
        frame_matche_ids : FrameMatchIds = []
        for i , j in zip(gt_idx, pred_idx):
            if sim_matrix[i, j] >= self.alpha:
                track_id_gt = frame_data_gt[i]["track_id"]
                track_id_pred = frame_data_pred[j]["track_id"]
                frame_matche_ids.append((track_id_gt, track_id_pred))
        
        return frame_matche_ids
    
    # track_idの出現数を数える
    def calc_track_id_count(self, data : Data, data_num : int, e_track_id : str) -> int:
        count = 0
        for frame_num, frame_data in con.iterate_frame_datas(data, data_num, 1, max_frame):
            for entry in frame_data:
                location, track_id, jersey, team = con.take_entry_info(entry)
                if track_id == e_track_id:
                    count += 1
                    break
        return count
    
    # GS-HOTAの計算
    def calc_gs_hota(self, data_gt : Data, data_pred : Data, data_num : int) -> Tuple[float, float, float]:
        match_ids : FrameMatchIds = []
        total_matches = 0
        total_gt = 0
        total_pred = 0
        for frame_num in range(1, max_frame + 1):
            frame_id = con.convert_num_to_id(data_num, frame_num)
            if frame_id not in data_gt or frame_id not in data_pred:
                continue

            frame_data_gt = data_gt[frame_id]
            frame_data_pred = data_pred[frame_id]

            frame_matche_ids = self.match_gt_pred(frame_data_gt, frame_data_pred)
            match_ids.extend(frame_matche_ids)
            total_matches += len(frame_matche_ids)
            total_gt += len(frame_data_gt)
            total_pred += len(frame_data_pred)

        tp = total_matches
        fn = total_gt - tp
        fp = total_pred - tp
        det_a = tp / (tp + fn + fp )

        track_consistency = []
        for (track_id_gt, track_id_pred) in set(match_ids):
            consistent_frames = match_ids.count((track_id_gt, track_id_pred))
            total_frames = self.calc_track_id_count(data_gt, data_num, track_id_gt)
            track_consistency.append(consistent_frames / total_frames)
        ass_a = np.mean(track_consistency)

        gshota = mf.cal_root(det_a * ass_a)
        return gshota, det_a, ass_a