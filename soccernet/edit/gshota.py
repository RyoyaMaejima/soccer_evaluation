import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Dict, Tuple
from edit.type_def import BBoxPitch, Entry, Data, FrameMatchIds
import edit.math_func as mf
import edit.convert_take as con

class GSHOTA:
    def __init__(self, alpha=0.5, tau=5.0):
        self.alpha = alpha
        self.tau = tau

    # ID類似度スコア
    def calc_id_sim(self, entry1 : Entry, entry2 : Entry):
        location1, track_id1, jersey_number1, team1 = con.take_entry_info(entry1)
        location2, track_id2, jersey_number2, team2 = con.take_entry_info(entry2)
        if (jersey_number1 == jersey_number2) and (team1 == team2):
            return 1
        else:
            return 0
        
    # 類似度スコア
    def cal_sim(self, entry1 : Entry, entry2 : Entry):
        location1, track_id1, jersey_number1, team1 = con.take_entry_info(entry1)
        location2, track_id2, jersey_number2, team2 = con.take_entry_info(entry2)
        return mf.calc_location_sim(location1, location2, self.tau) * self.calc_id_sim(entry1, entry2)
    
    # ハンガリアン法でマッチング
    def match_gt_pred(self, frame_data_gt : List[Entry], frame_data_pred : List[Entry]):
        n_gt = len(frame_data_gt)
        n_pred= len(frame_data_pred)
        sim_matrix = np.zeros((n_gt, n_pred))

        for i in range(n_gt):
            for j in range(n_pred):
                sim_matrix[i, j] = self.calc_id_sim(frame_data_gt[i], frame_data_pred[j])
        
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
    def calc_track_id_count(self, data : Data, e_track_id):
        count = 0
        for frame_num in range(1, 750 + 1):
            frame_id = con.convert_num_to_id(data, frame_num)
            if frame_id not in data:
                continue

            frame_data = data[frame_id]
            for entry in frame_data:
                location, track_id, jersey_number, team = con.take_entry_info(entry)
                if track_id == e_track_id:
                    count += 1
                    break
        
        return count
    
    # GS-HOTAの計算
    def calc_gs_hota(self, data_num, data_gt : Data, data_pred : Data):
        match_ids : FrameMatchIds = []
        total_matches = 0
        total_gt = 0
        total_pred = 0
        for frame_num in range(1, 750 + 1):
            frame_id = con.convert_num_to_id(data_num, frame_num)
            if frame_id not in data_pred:
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
            total_frames = self.calc_track_id_count(data_gt, track_id_gt)
            track_consistency.append(consistent_frames / total_frames)
        ass_a = np.mean(track_consistency)

        gshota = mf.cal_root(det_a * ass_a)
        return gshota, det_a, ass_a