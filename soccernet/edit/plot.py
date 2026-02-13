import matplotlib.pyplot as plt
import cv2
import os
from typing import List, Dict, Tuple
from edit.type_def import Data
import edit.convert_take as con

class Plot:
    def __init__(self, data_path: str):
        self.data_path = data_path
    
    # 画像を表示
    def plot_picture(self, data_num: int, frame_num: int):
        picture_path = os.path.join(self.data_path, con.convert_num_to_path(data_num, frame_num))
        return cv2.imread(picture_path)
    
    # フレーム描画
    def plot_frame_data(
        self, data: Data, data_num: int, frame_num: int, lims: List[List[float]], colors: List[str]
     ) -> None:
        frame_id = con.convert_num_to_id(data_num, frame_num)
        if frame_id not in data:
            print(f"{frame_id} not found")
            return
        
        fig, axs = plt.subplots(1, 2, figsize=(20, 6), dpi=100)
        axs[0].set_title(f"Frame Number: {frame_num}")
        axs[0].set_xlim(lims[0][0], lims[0][1])
        axs[0].set_ylim(lims[1][0], lims[1][1])
        axs[0].set_xlabel("X Coordinate")
        axs[0].set_ylabel("Y Coordinate")
        axs[0].grid(True)
    
        frame_data = data[frame_id]
        for entry in frame_data:
            location, track_id, jersey, team = con.take_entry_info(entry)
            if location == "":
                continue
            x, y = location
            if team == "left":
                color = colors[0]
            elif team == "right":
                color = colors[1]
            else:
                color = "black"
            axs[0].scatter(x, y, c=color, s=100)
            axs[0].text(x + 0.5, y + 0.5, f'[{track_id}]#{jersey}', color=color)
        
        image = self.plot_picture(data_num, frame_num)
        if image is not None:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            axs[1].imshow(img_rgb)
            axs[1].set_title("Visualization Image")
            axs[1].axis("off")
        
        plt.tight_layout()
        plt.show()

    # 画像を開く
    def display_picture(self, data_num: int, frame_num: int) -> None:
        return os.path.join(self.data_path, con.convert_num_to_path(data_num, frame_num))