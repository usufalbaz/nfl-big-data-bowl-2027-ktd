"""
Kinetic Translation Deficit (KTD) Pipeline Module
=================================================
This module provides a production-grade framework for extracting high-frequency
10 Hz spatiotemporal kinematics from NFL Scouting Combine tracking data and
quantifying translation efficiency against regular-season game separation.

Author: NFL Big Data Bowl 2027 Research Team
License: MIT
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class KTDProcessor:
    """
    Kinematic Translation Deficit processor for tracking sensor data.
    
    Attributes:
        epsilon (float): Regularization constant to prevent zero-division.
    """

    def __init__(self, epsilon: float = 0.01) -> None:
        """
        Initializes the KTDProcessor with numerical stability parameters.

        Args:
            epsilon (float, optional): Small float to avoid division by zero. Defaults to 0.01.
        """
        self.epsilon = epsilon

    def extract_combine_cut_kinematics(
        self,
        combine_tracking_df: pd.DataFrame,
        drill_filter: str = "SPEED_OUT"
    ) -> pd.DataFrame:
        """
        Extracts high-frequency kinematic inflection points during Combine route cuts.

        For each prospect attempt, this function isolates the route break point,
        measuring peak entry speed, instantaneous cut apex minimum velocity,
        and kinematic speed retention.

        Args:
            combine_tracking_df (pd.DataFrame): 10 Hz tracking data from Combine drills.
            drill_filter (str, optional): Substring filter for target drill. Defaults to "SPEED_OUT".

        Returns:
            pd.DataFrame: Aggregated prospect-level Combine kinematic features.
        """
        # Filter for target drill mechanics
        target_drills = combine_tracking_df[
            combine_tracking_df["drill_name"].str.contains(drill_filter, na=False)
        ]

        prospect_records: List[Dict[str, float]] = []

        for nfl_id, trajectory in target_drills.groupby("nfl_id"):
            max_velocity = float(trajectory["s"].max())
            min_cut_velocity = float(trajectory["s"].min())
            mean_velocity = float(trajectory["s"].mean())
            speed_drop = max_velocity - min_cut_velocity

            # Velocity retention ratio (elastic conservation)
            retention_ratio = (
                (min_cut_velocity / max_velocity) if max_velocity > 0 else 0.0
            )

            prospect_records.append({
                "nfl_id": int(nfl_id),
                "combine_peak_speed": round(max_velocity, 4),
                "combine_apex_min_speed": round(min_cut_velocity, 4),
                "combine_speed_drop": round(speed_drop, 4),
                "combine_velocity_retention": round(retention_ratio, 4),
                "combine_mean_speed": round(mean_velocity, 4),
            })

        return pd.DataFrame(prospect_records)

    def extract_game_separation_metrics(
        self,
        player_play_df: pd.DataFrame,
        route_target: str = "OUT"
    ) -> pd.DataFrame:
        """
        Aggregates regular-season game operational separation for identical route concepts.

        Args:
            player_play_df (pd.DataFrame): In-game play-by-play player performance records.
            route_target (str, optional): Target route concept. Defaults to "OUT".

        Returns:
            pd.DataFrame: Aggregated prospect operational metrics across regular-season snaps.
        """
        matched_plays = player_play_df[player_play_df["route_ran"] == route_target]

        game_summary = (
            matched_plays.groupby("nfl_id")
            .agg(
                routes_run_count=("route_ran", "count"),
                avg_game_separation=("separation_at_pass_forward", "mean"),
                avg_expected_points_added=("expected_points_added", "mean"),
                avg_yards_after_catch=("yards_after_catch", "mean"),
            )
            .reset_index()
        )

        return game_summary

    def compute_ktd_metric(
        self,
        combine_features: pd.DataFrame,
        game_features: pd.DataFrame,
        metadata_df: Optional[pd.DataFrame] = None,
        career_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Synthesizes Combine kinematics and game operational separation into the KTD Score.

        Formula:
            KTD = combine_speed_drop / (avg_game_separation + epsilon)

        Args:
            combine_features (pd.DataFrame): Combine kinematic outputs.
            game_features (pd.DataFrame): In-game separation metrics.
            metadata_df (Optional[pd.DataFrame], optional): Demographic/draft pick metadata.
            career_df (Optional[pd.DataFrame], optional): Career longevity and accolade metrics.

        Returns:
            pd.DataFrame: Master dataset ranked by Kinetic Translation Deficit.
        """
        master_df = combine_features.merge(game_features, on="nfl_id", how="left")

        # Impute missing separation for prospects with zero targeted snaps using empirical median
        median_sep = master_df["avg_game_separation"].median()
        master_df["avg_game_separation"] = master_df["avg_game_separation"].fillna(median_sep)

        # Compute official KTD Score
        master_df["KTD_Score"] = (
            master_df["combine_speed_drop"]
            / (master_df["avg_game_separation"] + self.epsilon)
        ).round(3)

        if metadata_df is not None:
            master_df = master_df.merge(metadata_df, on="nfl_id", how="left")

        if career_df is not None:
            master_df = master_df.merge(career_df, on="nfl_id", how="left")

        # Sort prospects by translation resilience (Ascending: Low KTD = Elite Translation)
        return master_df.sort_values("KTD_Score", ascending=True).reset_index(drop=True)
