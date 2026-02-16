# soccer_evaluation
Soccer Player Evaluation Using Video-Derived Tracking Data

## Overview
In soccer, quantitatively evaluating players' contributions based on match data is an important research challenge. In recent years, methods that assess player contributions by analyzing action data, such as passes and shots, have been widely adopted. However, these approaches primarily rely on information from the player in possession of the ball and therefore fail to sufficiently capture off-the-ball contributions, such as movement and positioning when a player does not have possession. In addition, tracking data that record the movements of all players throughout a match are available only for limited teams and leagues, making them difficult to obtain. To address these issues, this study proposes a method for generating tracking data based on player location and identification information estimated from match videos using SoccerNet-GSR. Furthermore, by integrating the generated tracking data with conventional action-based player evaluation models, we develop a novel player evaluation framework that enables the assessment of player contributions from both action-based and location-based perspectives. Experimental results demonstrate that the proposed model allows for a more multifaceted evaluation of players compared to existing models, and an improvement in correlation with player ratings from WhoScored.com is also observed. In addition, through an accuracy evaluation of the tracking data, we quantitatively show that the data generated in this study estimate player locations and identities with higher accuracy than existing methods. Finally, an analysis of the relationship between action-based and location-based evaluation values reveals a positive correlation between the two, indicating that the proposed method captures characteristics related to players' playstyles and roles.

---

## Repository Structure

This repository consists of two main components:

- `soccernet`  
  Predicts player coordinates and identity information from match videos.

- `socceraction`  
  Evaluates players using both action data and tracking data.

---

## soccernet

This module is built upon the official implementation of:  
https://github.com/SoccerNet/sn-gamestate

Using the outputs of the original model, we applied the following post-processing steps to construct higher-quality tracking data:

1. **Jersey Number Correction**  
   Incorrect jersey numbers were corrected using a combination of manual annotation and automatic correction based on spatial (coordinate) information.

2. **Interpolation of Off-Screen Players**  
   When players moved outside the camera frame, their coordinates were estimated using linear interpolation based on previous and subsequent frames.

Implementation details are available in:

- `soccernet/edit`
- `soccernet/DataEdit.ipynb`

---

## socceraction

This module is built upon:  
https://github.com/ML-KULeuven/socceraction

The tracking data obtained after steps (1) and (2) were further processed to align with StatsBomb action data:

3. **Temporal Alignment**  
   Only video segments corresponding to the timestamps of action data were extracted.

4. **Spatial Alignment**  
   Locational discrepancies between action data coordinates and estimated tracking coordinates were corrected using parallel translation.

After applying steps (1)–(4), the refined tracking data and action data were jointly used to evaluate players using our proposed evaluation metric.

Implementation details are available in:

- `socceraction/public-notebooks/edit`
- `socceraction/public-notebooks/4-compute-vaep-values-and-top-players.ipynb`

---

## Acknowledgements

This repository builds upon the following open-source projects:

- SoccerNet Game State Reconstruction  
  https://github.com/SoccerNet/sn-gamestate

- socceraction  
  https://github.com/ML-KULeuven/socceraction

We sincerely thank the authors for making their code publicly available.
