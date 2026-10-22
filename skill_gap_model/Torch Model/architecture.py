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
]

with (Path(__file__).resolve().parent / "catalog.json").open(encoding="utf-8") as catalog_file:
    _catalog = json.load(catalog_file)

SKILL_NAMES = _catalog["skill_names"]
LEARNING_ACTIVITIES = _catalog["learning_activities"]


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
    """MLP that predicts continuous skill mastery in binary."""
    def __init__(self, input_dim, hidden=(96, 48, 24), dropout=0.25):
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
            nn.Linear(prev, 12),
            nn.ReLU(),
            nn.Linear(12, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.head(self.backbone(x)).squeeze(-1)
