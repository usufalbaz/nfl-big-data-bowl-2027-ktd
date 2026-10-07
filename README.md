# 🏈 The Kinetic Translation Deficit (KTD)
### NFL Big Data Bowl 2027 Submission | Sensor Tracking from Combine to Regular Season

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-NFL%20Big%20Data%20Bowl%202027-20BEFF.svg?logo=kaggle)](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Executive Summary
Every spring, NFL front offices invest millions of dollars in draft capital based on physical testing at the **NFL Scouting Combine**. However, traditional stopwatch timings (such as the 40-yard dash and 3-cone drill) evaluate athletes in a sterile environment: in shorts, without pads, without contact, and executing pre-planned trajectories.

**The Kinetic Translation Deficit (KTD)** is an applied biomechanical framework leveraging **10 Hz RFID player tracking data** to measure how efficiently collegiate prospects translate Combine movement mechanics into live regular-season NFL game separation.

---

## 🔬 Mathematical Formulation

### 1. Combine Kinematic Extraction (The Isolated Cut)
Focusing on isolated movement primitives (e.g., 90° cuts during `SPEED_OUT` routes), we extract kinematic inflection points at 10 Hz:

$$\Delta S_{\text{Combine}} = S_{\text{max}} - S_{\text{cut\_min}}$$

Where:
* $S_{\text{max}}$ is the prospect's peak entry velocity (yards/second).
* $S_{\text{cut\_min}}$ is the instantaneous minimum velocity at the apex of the route break.

### 2. In-Game Operational Translation
In regular-season games, receivers execute identical route concepts (`OUT` routes) under physical load (pads, helmet) and defensive press/man coverage:

$$\text{KTD Score} = \frac{\Delta S_{\text{Combine}}}{\overline{\text{Separation}}_{\text{Game}} + \epsilon}$$

Where:
* $\overline{\text{Separation}}_{\text{Game}}$ is the mean separation in yards generated at the exact frame of pass release (`separation_at_pass_forward`).
* $\epsilon = 0.01$ prevents division-by-zero artifacts.

### Theoretical Interpretation:
* **Low KTD (< 1.5):** *Resilient Separators (Draft Steals)* — Prospects whose deceleration-to-burst mechanics efficiently translate into in-game separation regardless of raw straight-line speed.
* **High KTD (> 2.5):** *Scripted Sprinters (Draft Busts)* — Prospects with elite track speed whose cutting explosiveness completely degrades against live NFL defenders.

---

## 📊 Baseline Findings: Evaluated on 106 Wide Receivers

| Prospect Name | Draft Pick | Combine Peak Speed (yd/s) | Game Separation (yds) | KTD Score | Historical Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ricky White** | Round 7 (Pick 238) | 7.21 | **6.63** | **0.99** | 🌟 Elite Draft Steal |
| **Devontez Walker** | Round 4 (Pick 113) | 7.63 | **5.83** | **1.14** | 🌟 High-Value Separator |
| **Jacolby George** | Undrafted (UDFA) | 7.04 | **5.91** | **1.18** | 🌟 Hidden Gem |
| **Jalin Hyatt** | Round 3 (Pick 73) | 6.26 | **4.71** | **1.23** | 🌟 Resilient Explosiveness |
| **Justin Shorter** | Round 5 (Pick 150) | 6.56 | **4.22** | **1.35** | 🌟 Day 3 Value |

---

## 📁 Project Repository Architecture
data/
└── ktd_wr_metrics.csv       # Extracted kinematic dataset (106 prospects)
src/
├── __init__.py
└── ktd_metrics.py           # Core kinematic calculation pipeline
notebooks/
└── 01_combine_to_game.ipynb # Kaggle research notebook
requirements.txt             # Environment dependencies
LICENSE                      # MIT Open Source License
README.md                    # Project documentation

---

## 🛠️ Tech Stack & Methods
* **Tracking Analytics:** 10 Hz Spatiotemporal Kinematics (Next Gen Stats & Combine RFID)
* **Languages & Tooling:** Python 3.10+, Pandas, NumPy, SciPy, Matplotlib
* **Target Audience:** NFL Front Offices, Pro Scouting Personnel, Sports Science Directors

---

## 🏆 Actionability for NFL Front Offices
NFL General Managers and Analytics Directors can deploy the KTD metric to:
1. Identify Day 3 and undrafted prospects whose in-game separation traits outclass their raw combine 40-yard dash times.
2. Avoid costly high-round draft busts who rely purely on unpadded, straight-line track speed.
