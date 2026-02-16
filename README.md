# soccer_evaluation
Soccer Player Evaluation Using Video-Derived Tracking Data

## Overview

*(Please insert the abstract of the journal paper here.)*

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
   Positional discrepancies between action data coordinates and estimated tracking coordinates were corrected using parallel translation.

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
