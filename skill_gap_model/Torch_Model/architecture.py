#!/usr/bin/env python3
"""
Model architecture and dataset for learner proficiency estimation.
"""

import torch
import torch.nn as nn
import json
from pathlib import Path
from torch.utils.data import Dataset

FEATURE_COLS = [
    "n_attempts", "accuracy", "weighted_acc", "recent_acc",
    "avg_time", "median_time", "hint_rate", "avg_attempt_num",
    "max_attempt", "consistency", "n_problem_types", "n_courses",
    "pt_Multiple Choice", "pt_Conceptual", "pt_Coding", "pt_Debugging",
]

with (Path(__file__).resolve().parent / "catalog.json").open(encoding="utf-8") as catalog_file:
    _catalog = json.load(catalog_file)

SKILL_NAMES = _catalog["skill_names"]
LEARNING_ACTIVITIES = _catalog["learning_activities"]
DIFFICULTY_LEVELS = _catalog["difficulty_levels"]
DIFFICULTY_WEIGHTS = _catalog["difficulty_weights"]
PROBLEM_TYPES = _catalog["problem_types"]
PROBLEM_WEIGHTS = _catalog["problem_weights"]


class ProficiencyDataset(Dataset):
    def __init__(self, df, feature_cols=None):
        cols = feature_cols or FEATURE_COLS
        self.X = torch.tensor(df[cols].values, dtype=torch.float32)
        self.y = torch.tensor(df["mastery"].values, dtype=torch.float32)
        self.student_ids = df["student_id"].values
        self.skill_ids = df["skill_id"].values

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class SkillProficiencyNet(nn.Module):
    """Deep MLP with residual connections for predicting continuous skill mastery."""
    def __init__(self, input_dim, hidden=(128, 96, 64, 48, 32), dropout=0.3):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden:
            layers += [
                nn.Linear(prev, h),
                nn.BatchNorm1d(h),
                nn.ReLU(),
                nn.Dropout(dropout),
            ]
            prev = h
        self.backbone = nn.Sequential(*layers)
        self.head = nn.Sequential(
            nn.Linear(prev, 24),
            nn.BatchNorm1d(24),
            nn.ReLU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(24, 12),
            nn.BatchNorm1d(12),
            nn.ReLU(),
            nn.Linear(12, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.head(self.backbone(x)).squeeze(-1)
