"""Catan Tournament 1v1 agent. Team: AI_Reasoning_Group

Playbook: docs/students/CATAN_PLAYBOOK.md
Full rules: games/catan/README.md
Samples: docs/students/sample_observations/catan_*.json
Training: docs/students/TRAINING.md

You may not import catanatron.players. Values learned offline must live in this file.
"""
import random
from collections import Counter

# Learned Q-table from docs/students/train_catan.py (Step 5). Key: "features|ACTION_TYPE".
Q = {"['initial_placement', 0, 0, 0, 1, 0, 0, 'mixed', 0]|BUILD_SETTLEMENT": 1.70031, "['play_turn', 0, 0, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 1.27696, "['play_turn', 1, 0, 0, 1, 1, 0, 'mixed', 1]|BUILD_SETTLEMENT": 1.21088, "['play_turn', 0, 0, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 1.18326, "['play_turn', 0, 0, 0, 1, 1, 0, 'mixed', 1]|BUILD_SETTLEMENT": 1.17391, "['play_turn', 1, 0, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 1.16975, "['play_turn', 1, 0, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 1.12759, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": 1.00831, "['play_turn', 0, 0, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.98756, "['play_turn', 0, 0, 0, 1, 1, 0, 'road', 1]|BUILD_SETTLEMENT": 0.94229, "['initial_placement', 0, 0, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": 0.93751, "['play_turn', 2, 0, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 0.93492, "['play_turn', 2, 0, 0, 1, 1, 0, 'mixed', 2]|BUILD_SETTLEMENT": 0.91582, "['play_turn', 1, 1, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.89482, "['play_turn', 1, 1, 0, 1, 1, 0, 'road', 1]|BUILD_SETTLEMENT": 0.88772, "['play_turn', 2, 1, 0, 1, 1, 0, 'mixed', 1]|BUILD_SETTLEMENT": 0.87561, "['play_turn', 0, 1, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 0.87148, "['play_turn', 1, 0, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.86528, "['play_turn', 1, 1, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 0.85408, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": 0.85204, "['play_turn', 0, 1, 0, 1, 1, 0, 'mixed', 1]|BUILD_SETTLEMENT": 0.84017, "['play_turn', 0, 1, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 0.83305, "['play_turn', 0, 0, 1, 0, 0, 1, 'city', 1]|BUILD_CITY": 0.82694, "['play_turn', 1, 1, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 0.82245, "['play_turn', 2, 0, 0, 1, 0, 0, 'mixed', 1]|BUILD_SETTLEMENT": 0.81, "['play_turn', 1, 2, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 0.76356, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": 0.76155, "['play_turn', 2, 0, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.75131, "['play_turn', 2, 1, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 0.73818, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.73378, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.73071, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.72357, "['play_turn', 1, 1, 0, 1, 1, 0, 'mixed', 1]|BUILD_SETTLEMENT": 0.72073, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.71944, "['play_turn', 2, 0, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 0.70829, "['play_turn', 0, 1, 0, 1, 1, 0, 'road', 1]|BUILD_SETTLEMENT": 0.70732, "['play_turn', 2, 1, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.70643, "['play_turn', 2, 0, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.7035, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.69597, "['move_robber', 0, 2, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": -0.67992, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 1]|END_TURN": -0.67675, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.67225, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": -0.66337, "['play_turn', 1, 1, 0, 1, 1, 0, 'mixed', 2]|BUILD_SETTLEMENT": 0.65791, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": 0.65591, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": 0.65267, "['play_turn', 1, 0, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.65213, "['play_turn', 2, 0, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.63847, "['play_turn', 1, 0, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": 0.621, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.61745, "['play_turn', 2, 1, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.61217, "['play_turn', 2, 0, 0, 1, 0, 1, 'mixed', 2]|BUILD_SETTLEMENT": 0.60923, "['play_turn', 2, 0, 0, 1, 0, 0, 'road', 1]|BUILD_SETTLEMENT": 0.6068, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 1]|MARITIME_TRADE": -0.60243, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 1]|END_TURN": -0.59629, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": -0.59321, "['play_turn', 1, 0, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": 0.58967, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.5845, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": 0.58244, "['play_turn', 1, 0, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": 0.57969, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 1]|END_TURN": -0.57944, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.5765, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 1]|END_TURN": -0.5731, "['play_turn', 0, 0, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.5706, "['play_turn', 0, 1, 0, 1, 1, 0, 'mixed', 2]|BUILD_SETTLEMENT": 0.56992, "['play_turn', 0, 2, 0, 1, 1, 0, 'mixed', 1]|BUILD_SETTLEMENT": 0.56918, "['play_turn', 0, 0, 1, 0, 0, 0, 'mixed', 2]|BUILD_CITY": 0.5669, "['move_robber', 0, 2, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": -0.56642, "['play_turn', 2, 0, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.5647, "['move_robber', 0, 2, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": -0.55261, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 0]|END_TURN": -0.55094, "['play_turn', 2, 0, 0, 1, 0, 0, 'road', 2]|BUILD_SETTLEMENT": 0.5459, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 0]|END_TURN": -0.54257, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.54247, "['play_turn', 2, 1, 0, 1, 0, 0, 'mixed', 1]|BUILD_SETTLEMENT": 0.542, "['play_turn', 0, 1, 0, 1, 1, 0, 'road', 2]|BUILD_SETTLEMENT": 0.53777, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": -0.53753, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 0]|END_TURN": -0.53263, "['move_robber', 0, 2, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": -0.53226, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": 0.52774, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.52728, "['play_turn', 2, 0, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": 0.52287, "['play_turn', 2, 1, 0, 1, 0, 1, 'road', 2]|BUILD_SETTLEMENT": 0.52201, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": 0.52196, "['play_turn', 0, 2, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 0.51922, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.51536, "['play_turn', 2, 1, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.50969, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.50386, "['play_turn', 1, 2, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 0.50307, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 1]|END_TURN": -0.50279, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 2]|END_TURN": -0.49846, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": 0.49823, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 2]|END_TURN": -0.49807, "['play_turn', 2, 0, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": 0.4974, "['play_turn', 2, 1, 0, 1, 0, 1, 'mixed', 2]|BUILD_SETTLEMENT": 0.49064, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.48614, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 1]|END_TURN": -0.48199, "['play_turn', 1, 1, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.48044, "['play_turn', 2, 1, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": 0.47999, "['play_turn', 1, 0, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": 0.47918, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.47703, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.47587, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 1]|END_TURN": -0.47105, "['play_turn', 0, 0, 1, 0, 1, 0, 'city', 1]|BUILD_CITY": 0.46941, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 2]|END_TURN": -0.4687, "['play_turn', 2, 1, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.4674, "['play_turn', 2, 0, 0, 1, 0, 1, 'road', 2]|BUILD_SETTLEMENT": 0.46557, "['play_turn', 1, 2, 0, 1, 1, 0, 'road', 1]|BUILD_SETTLEMENT": 0.46326, "['play_turn', 2, 0, 0, 1, 0, 1, 'mixed', 1]|BUILD_SETTLEMENT": 0.46256, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": -0.46015, "['move_robber', 0, 2, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": -0.45824, "['move_robber', 0, 2, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": -0.45531, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.45354, "['play_turn', 0, 1, 1, 0, 0, 1, 'city', 1]|BUILD_CITY": 0.45134, "['play_turn', 1, 0, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": 0.44937, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": -0.44619, "['play_turn', 1, 2, 0, 1, 1, 1, 'mixed', 2]|BUILD_SETTLEMENT": 0.44362, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 2]|END_TURN": -0.44284, "['move_robber', 1, 2, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": -0.4411, "['play_turn', 2, 2, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.42564, "['play_turn', 2, 2, 1, 0, 0, 0, 'city', 2]|BUILD_CITY": 0.42473, "['play_turn', 1, 0, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": 0.42227, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": -0.42027, "['play_turn', 0, 2, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 0.41537, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.41284, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": -0.41047, "['play_turn', 0, 2, 0, 0, 1, 0, 'city', 1]|END_TURN": -0.41027, "['play_turn', 2, 0, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": 0.40913, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 2]|END_TURN": -0.40887, "['play_turn', 2, 1, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.40667, "['play_turn', 1, 2, 1, 0, 1, 0, 'city', 2]|BUILD_CITY": 0.40607, "['play_turn', 1, 1, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.40465, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.40389, "['play_turn', 0, 0, 1, 0, 1, 0, 'mixed', 2]|BUILD_CITY": 0.4025, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": 0.3985, "['play_turn', 0, 1, 1, 0, 1, 0, 'city', 2]|BUILD_CITY": 0.39689, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 1]|END_TURN": -0.39621, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 1]|MARITIME_TRADE": -0.39102, "['move_robber', 1, 2, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": -0.38843, "['play_turn', 2, 0, 1, 0, 0, 1, 'city', 1]|BUILD_CITY": 0.38515, "['play_turn', 0, 1, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.38331, "['play_turn', 1, 0, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": 0.38293, "['play_turn', 2, 1, 0, 1, 0, 1, 'mixed', 1]|BUILD_SETTLEMENT": 0.38, "['play_turn', 2, 0, 0, 1, 0, 0, 'mixed', 2]|BUILD_SETTLEMENT": 0.38, "['play_turn', 2, 2, 0, 1, 1, 0, 'road', 2]|BUILD_SETTLEMENT": 0.38, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": -0.37974, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.37803, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 0]|END_TURN": -0.37782, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": 0.37744, "['play_turn', 2, 1, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 0.37435, "['play_turn', 1, 0, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.37324, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 0]|END_TURN": -0.37122, "['play_turn', 2, 0, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": 0.36959, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": -0.36834, "['move_robber', 0, 1, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": -0.365, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": 0.36475, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 1]|END_TURN": -0.36472, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 1]|MARITIME_TRADE": -0.36389, "['play_turn', 0, 2, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": -0.36383, "['move_robber', 1, 1, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": -0.36377, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": 0.36041, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": 0.35865, "['play_turn', 2, 1, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": 0.35774, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": -0.35724, "['play_turn', 2, 0, 0, 0, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.35606, "['play_turn', 1, 0, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.35599, "['play_turn', 0, 2, 0, 0, 1, 0, 'city', 1]|MARITIME_TRADE": -0.35395, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": 0.35375, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": 0.35218, "['play_turn', 0, 0, 1, 0, 1, 0, 'city', 2]|BUILD_CITY": 0.34833, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 2]|MARITIME_TRADE": -0.34581, "['move_robber', 0, 1, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": -0.34496, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 1]|MARITIME_TRADE": -0.34476, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 1]|END_TURN": -0.34378, "['move_robber', 1, 0, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": 0.34217, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 0]|END_TURN": -0.3421, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": -0.33812, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 1]|END_TURN": -0.33809, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 0]|END_TURN": -0.33761, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 1]|END_TURN": -0.33468, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 1]|END_TURN": -0.33459, "['play_turn', 0, 0, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.33399, "['play_turn', 0, 0, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": 0.33231, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.33185, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 2]|END_TURN": -0.33102, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 2]|MARITIME_TRADE": -0.33024, "['play_turn', 1, 1, 1, 0, 1, 0, 'city', 2]|BUILD_CITY": 0.3293, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": 0.3292, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": -0.3282, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.32772, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": 0.32755, "['play_turn', 0, 1, 1, 0, 1, 0, 'mixed', 2]|BUILD_CITY": 0.32455, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": -0.32157, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 1]|END_TURN": -0.32014, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.31957, "['play_turn', 1, 1, 1, 0, 0, 1, 'city', 1]|BUILD_CITY": 0.31911, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 0]|END_TURN": 0.31822, "['move_robber', 2, 0, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": 0.31451, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 2]|MARITIME_TRADE": -0.31242, "['play_turn', 2, 1, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": 0.31089, "['play_turn', 2, 0, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": 0.31085, "['play_turn', 1, 0, 1, 0, 0, 1, 'city', 1]|BUILD_CITY": 0.31023, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 1]|END_TURN": 0.31001, "['play_turn', 2, 2, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.30929, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": 0.30917, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": -0.30871, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 1]|END_TURN": -0.3064, "['play_turn', 0, 1, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.30575, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 0]|END_TURN": -0.30303, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.30177, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 1]|END_TURN": -0.30098, "['play_turn', 2, 1, 0, 1, 0, 0, 'road', 1]|BUILD_SETTLEMENT": 0.30034, "['play_turn', 2, 1, 0, 0, 1, 0, 'road', 1]|END_TURN": -0.30026, "['play_turn', 2, 1, 0, 0, 1, 0, 'road', 0]|END_TURN": -0.3, "['move_robber', 1, 2, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": -0.29931, "['move_robber', 1, 0, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": 0.29897, "['play_turn', 1, 0, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": 0.29857, "['play_turn', 1, 0, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.29818, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 1]|END_TURN": -0.29818, "['play_turn', 2, 2, 0, 1, 0, 0, 'road', 1]|BUILD_SETTLEMENT": 0.29768, "['play_turn', 1, 2, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": 0.29758, "['move_robber', 1, 2, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": -0.29706, "['move_robber', 1, 0, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": 0.29678, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.29633, "['play_turn', 2, 0, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": 0.29608, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": 0.29599, "['move_robber', 1, 0, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": 0.29447, "['play_turn', 0, 0, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.29283, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": 0.29017, "['play_turn', 2, 2, 0, 1, 1, 0, 'mixed', 2]|BUILD_SETTLEMENT": 0.2897, "['free_roads', 2, 2, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": 0.28949, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": 0.28892, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.28809, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 0]|END_TURN": -0.28801, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": -0.28799, "['play_turn', 2, 1, 0, 1, 0, 0, 'road', 2]|BUILD_SETTLEMENT": 0.28789, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": -0.2848, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.28464, "['move_robber', 2, 0, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": 0.28454, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": 0.2835, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.28243, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 0]|END_TURN": -0.27993, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 2]|END_TURN": -0.27603, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.27541, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": 0.27461, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 2]|END_TURN": -0.27379, "['play_turn', 2, 2, 0, 1, 1, 0, 'mixed', 1]|BUILD_SETTLEMENT": 0.27335, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": -0.27278, "['move_robber', 2, 0, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": 0.27246, "['play_turn', 2, 2, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.27207, "['play_turn', 1, 2, 0, 1, 1, 0, 'mixed', 1]|BUILD_SETTLEMENT": 0.2718, "['play_turn', 0, 2, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.271, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": -0.27096, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 2]|END_TURN": -0.27061, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 1]|END_TURN": 0.27005, "['play_turn', 0, 1, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.26964, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 1]|END_TURN": -0.26739, "['play_turn', 0, 2, 0, 0, 0, 1, 'mixed', 1]|END_TURN": -0.26669, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 2]|PLAY_KNIGHT_CARD": 0.26522, "['play_turn', 0, 0, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.26456, "['move_robber', 2, 0, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": 0.26288, "['play_turn', 1, 0, 0, 1, 1, 0, 'city', 1]|BUILD_ROAD": 0.26232, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 2]|END_TURN": -0.26191, "['play_turn', 1, 1, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": 0.26115, "['play_turn', 0, 0, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": 0.25918, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": 0.25797, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 2]|END_TURN": -0.2568, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": 0.2558, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": -0.25432, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": -0.25359, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 2]|END_TURN": -0.25288, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 0]|ROLL": -0.252, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 2]|END_TURN": -0.25106, "['play_turn', 1, 2, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": -0.2508, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 0]|END_TURN": -0.25071, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 2]|PLAY_KNIGHT_CARD": 0.2494, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.24939, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": -0.24853, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.24743, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.24665, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.24279, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": 0.24262, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": -0.242, "['play_turn', 0, 0, 1, 0, 0, 0, 'city', 1]|END_TURN": 0.24053, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 0]|MARITIME_TRADE": -0.23936, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": -0.23809, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.23734, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": -0.23589, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": -0.23438, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 2]|MARITIME_TRADE": -0.23405, "['move_robber', 1, 0, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": 0.23343, "['play_turn', 1, 0, 1, 0, 1, 0, 'mixed', 2]|BUILD_CITY": 0.2333, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": -0.23301, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 2]|END_TURN": -0.23255, "['play_turn', 0, 1, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": -0.23132, "['play_turn', 0, 2, 0, 1, 1, 0, 'mixed', 2]|BUILD_SETTLEMENT": 0.22929, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": -0.22911, "['move_robber', 2, 0, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": 0.229, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.22829, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": 0.22707, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.22656, "['play_turn', 2, 1, 0, 0, 1, 0, 'city', 1]|END_TURN": -0.22508, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 1]|END_TURN": -0.22507, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.22493, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": 0.22438, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.22412, "['move_robber', 2, 2, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": -0.2233, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 2]|END_TURN": -0.22314, "['move_robber', 0, 0, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": 0.22301, "['play_turn', 1, 0, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": 0.22233, "['move_robber', 2, 1, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": 0.22174, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.22145, "['play_turn', 1, 2, 0, 0, 1, 0, 'city', 1]|END_TURN": -0.22008, "['play_turn', 0, 0, 0, 0, 1, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": 0.2194, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": 0.2182, "['play_turn', 0, 0, 0, 0, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.2177, "['play_turn', 1, 0, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": 0.21677, "['play_turn', 1, 1, 0, 1, 0, 1, 'road', 2]|BUILD_SETTLEMENT": 0.21626, "['play_turn', 1, 0, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.21626, "['play_turn', 1, 0, 1, 0, 0, 0, 'mixed', 2]|BUILD_CITY": 0.21554, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.21529, "['play_turn', 2, 1, 1, 0, 0, 1, 'city', 1]|BUILD_CITY": 0.21453, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.21436, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": -0.21416, "['play_turn', 1, 0, 0, 1, 0, 0, 'road', 1]|BUILD_SETTLEMENT": 0.21367, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": 0.21214, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 1]|END_TURN": 0.21201, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": 0.21185, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": -0.21137, "['play_turn', 0, 2, 1, 0, 1, 0, 'city', 2]|BUILD_CITY": 0.20986, "['play_turn', 1, 0, 1, 0, 1, 0, 'city', 2]|BUILD_CITY": 0.20949, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": -0.20819, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": -0.20732, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 1]|END_TURN": -0.20582, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 1]|PLAY_MONOPOLY": -0.20534, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 1]|END_TURN": 0.20503, "['play_turn', 1, 2, 1, 0, 1, 0, 'mixed', 2]|BUILD_CITY": 0.20421, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.20365, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.20332, "['play_turn', 2, 1, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": 0.20206, "['play_turn', 1, 2, 0, 0, 1, 0, 'city', 1]|MARITIME_TRADE": -0.20104, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": -0.20021, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 2]|PLAY_KNIGHT_CARD": 0.20001, "['play_turn', 2, 0, 0, 1, 0, 1, 'city', 2]|BUILD_SETTLEMENT": 0.2, "['play_turn', 2, 2, 1, 0, 1, 0, 'city', 2]|BUILD_CITY": 0.2, "['play_turn', 2, 2, 0, 1, 0, 1, 'mixed', 1]|BUILD_SETTLEMENT": 0.2, "['free_roads', 1, 1, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": 0.19967, "['play_turn', 1, 1, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.1995, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 2]|END_TURN": -0.1994, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": -0.1988, "['play_turn', 0, 1, 0, 0, 1, 0, 'city', 1]|END_TURN": -0.19807, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 0]|END_TURN": -0.19649, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 0]|ROLL": 0.196, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 2]|END_TURN": -0.19586, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 0]|END_TURN": -0.19579, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.19556, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.19529, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.19494, "['play_turn', 0, 2, 0, 0, 0, 1, 'city', 1]|END_TURN": -0.19465, "['play_turn', 0, 1, 0, 1, 1, 0, 'city', 1]|BUILD_ROAD": 0.1938, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 0]|ROLL": -0.1934, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 1]|END_TURN": -0.1933, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 0]|END_TURN": 0.19255, "['move_robber', 0, 1, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": -0.19232, "['play_turn', 2, 2, 0, 1, 1, 0, 'road', 1]|BUILD_SETTLEMENT": 0.19116, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 0]|END_TURN": -0.19107, "['play_turn', 1, 2, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.19056, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.19041, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 1]|MARITIME_TRADE": -0.19008, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 0]|END_TURN": 0.18905, "['play_turn', 0, 2, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": -0.18863, "['play_turn', 1, 2, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.18863, "['play_turn', 0, 0, 0, 0, 0, 1, 'road', 1]|MARITIME_TRADE": 0.18777, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": 0.18728, "['play_turn', 1, 2, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.18603, "['play_turn', 0, 2, 1, 0, 0, 1, 'city', 1]|BUILD_CITY": 0.18469, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 0]|MARITIME_TRADE": -0.18423, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 2]|MARITIME_TRADE": -0.18388, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 1]|PLAY_MONOPOLY": -0.18379, "['move_robber', 0, 1, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": -0.18337, "['play_turn', 1, 1, 0, 0, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.18247, "['play_turn', 0, 2, 0, 0, 1, 0, 'city', 2]|MARITIME_TRADE": -0.18223, "['play_turn', 2, 0, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": 0.18147, "['play_turn', 0, 2, 0, 0, 1, 0, 'city', 2]|END_TURN": -0.18133, "['move_robber', 2, 0, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": 0.18102, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 0]|END_TURN": -0.181, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 0]|END_TURN": -0.18, "['play_turn', 0, 1, 1, 0, 0, 0, 'mixed', 2]|BUILD_CITY": 0.17977, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": -0.17954, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 0]|END_TURN": -0.17874, "['play_turn', 0, 2, 0, 0, 0, 1, 'city', 0]|END_TURN": -0.17844, "['play_turn', 1, 1, 1, 1, 1, 1, 'city', 2]|BUILD_CITY": 0.17644, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 1]|END_TURN": 0.17587, "['play_turn', 2, 0, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": 0.17536, "['play_turn', 1, 0, 0, 0, 1, 0, 'road', 1]|END_TURN": 0.17515, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": -0.17502, "['play_turn', 0, 0, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.17384, "['play_turn', 0, 0, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.17349, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.17189, "['play_turn', 0, 1, 0, 0, 1, 1, 'city', 1]|BUILD_ROAD": 0.17185, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": 0.17168, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.1708, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 0]|END_TURN": -0.16844, "['play_turn', 0, 1, 0, 0, 1, 0, 'city', 1]|MARITIME_TRADE": -0.16784, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": -0.16708, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": -0.16704, "['move_robber', 0, 0, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": 0.16702, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 0]|END_TURN": 0.16666, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": 0.16658, "['initial_placement', 0, 0, 0, 0, 1, 0, 'city', 0]|BUILD_ROAD": 0.16632, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 1]|END_TURN": 0.16601, "['move_robber', 1, 2, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": -0.16564, "['play_turn', 1, 2, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.16555, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 0]|END_TURN": 0.16511, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 2]|END_TURN": -0.16367, "['play_turn', 1, 1, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.16356, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": -0.16308, "['play_turn', 2, 0, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": 0.16283, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 1]|END_TURN": 0.16227, "['play_turn', 1, 0, 0, 0, 0, 1, 'mixed', 1]|END_TURN": 0.16153, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": 0.16124, "['play_turn', 2, 2, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.15805, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": -0.15804, "['play_turn', 0, 0, 0, 0, 0, 1, 'mixed', 2]|MARITIME_TRADE": 0.15667, "['play_turn', 1, 1, 1, 0, 1, 0, 'city', 1]|BUILD_CITY": 0.15555, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 1]|MARITIME_TRADE": -0.15525, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 2]|END_TURN": 0.15498, "['play_turn', 1, 0, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": 0.15347, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 2]|END_TURN": -0.15335, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": 0.15324, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": -0.15316, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 1]|END_TURN": 0.15261, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 0]|END_TURN": 0.1512, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 0]|MARITIME_TRADE": -0.15064, "['play_turn', 0, 1, 0, 0, 0, 1, 'mixed', 1]|END_TURN": -0.15017, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 0]|END_TURN": -0.14966, "['play_turn', 1, 1, 1, 0, 0, 0, 'city', 1]|MARITIME_TRADE": -0.1477, "['play_turn', 0, 0, 0, 0, 0, 1, 'mixed', 1]|END_TURN": 0.14644, "['move_robber', 0, 0, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": 0.14552, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 0]|MARITIME_TRADE": -0.14535, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 1]|END_TURN": 0.14413, "['play_turn', 1, 2, 0, 0, 1, 0, 'city', 2]|MARITIME_TRADE": -0.14337, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 0]|MARITIME_TRADE": -0.14308, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": 0.14251, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": 0.14245, "['play_turn', 0, 0, 0, 0, 1, 1, 'road', 1]|BUILD_ROAD": 0.14232, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": 0.14203, "['play_turn', 0, 0, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": 0.14146, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 2]|MARITIME_TRADE": -0.13997, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 1]|END_TURN": -0.13799, "['free_roads', 1, 1, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": 0.13699, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.13602, "['move_robber', 0, 1, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": -0.13559, "['play_turn', 0, 1, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.13536, "['play_turn', 0, 2, 0, 0, 1, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.1353, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": 0.13424, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": -0.13347, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.13334, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 0]|PLAY_MONOPOLY": -0.13305, "['play_turn', 1, 0, 0, 0, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.13297, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": -0.13191, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": -0.13098, "['play_turn', 0, 1, 0, 0, 1, 0, 'city', 2]|END_TURN": -0.1306, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 0]|END_TURN": -0.13044, "['play_turn', 2, 1, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": 0.13001, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": 0.12992, "['play_turn', 0, 2, 0, 1, 1, 0, 'road', 2]|BUILD_SETTLEMENT": 0.12988, "['move_robber', 1, 2, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": -0.12969, "['play_turn', 0, 2, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": -0.12967, "['play_turn', 1, 1, 1, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.1294, "['play_turn', 2, 0, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.12901, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": 0.12874, "['play_turn', 0, 0, 0, 0, 1, 1, 'city', 1]|BUILD_ROAD": 0.12781, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 1]|PLAY_MONOPOLY": 0.12766, "['play_turn', 1, 2, 0, 0, 1, 0, 'city', 2]|END_TURN": -0.12669, "['move_robber', 1, 0, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": 0.12625, "['play_turn', 1, 0, 1, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.12591, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": -0.12475, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": 0.12445, "['play_turn', 1, 1, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": -0.12422, "['play_turn', 1, 2, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": -0.12367, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 0]|MARITIME_TRADE": -0.12293, "['play_turn', 0, 0, 0, 0, 1, 1, 'city', 2]|BUILD_ROAD": 0.12208, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": 0.12125, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 1]|PLAY_MONOPOLY": 0.12112, "['move_robber', 2, 1, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": -0.12098, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.12074, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": -0.12074, "['play_turn', 0, 2, 0, 0, 0, 1, 'city', 2]|BUY_DEVELOPMENT_CARD": 0.1207, "['play_turn', 2, 0, 1, 0, 1, 0, 'city', 2]|BUILD_CITY": 0.12049, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": 0.12024, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": 0.12015, "['play_turn', 0, 2, 0, 0, 0, 1, 'city', 2]|END_TURN": -0.12012, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": -0.12002, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": 0.11976, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": -0.11938, "['play_turn', 0, 2, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.11929, "['play_turn', 0, 1, 0, 0, 1, 0, 'city', 2]|MARITIME_TRADE": -0.11923, "['play_turn', 1, 0, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.11801, "['play_turn', 1, 1, 0, 1, 0, 0, 'road', 1]|BUILD_SETTLEMENT": 0.11788, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.11786, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": 0.1177, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 2]|END_TURN": 0.11513, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.11454, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 0]|MARITIME_TRADE": -0.11441, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 2]|MARITIME_TRADE": -0.11427, "['play_turn', 1, 0, 0, 0, 0, 1, 'road', 1]|BUY_DEVELOPMENT_CARD": 0.11408, "['free_roads', 1, 2, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.11359, "['play_turn', 1, 1, 0, 1, 0, 1, 'city', 2]|BUILD_SETTLEMENT": 0.1135, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 0]|ROLL": -0.11296, "['play_turn', 1, 1, 0, 0, 1, 0, 'city', 2]|END_TURN": -0.11275, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 1]|END_TURN": 0.1126, "['move_robber', 2, 2, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": -0.11213, "['play_turn', 1, 1, 0, 0, 0, 1, 'road', 2]|MARITIME_TRADE": 0.11176, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.11165, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 2]|END_TURN": 0.11156, "['play_turn', 1, 0, 1, 0, 1, 1, 'city', 2]|BUILD_CITY": 0.11143, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 0]|ROLL": 0.11106, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.11074, "['free_roads', 0, 1, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.11058, "['play_turn', 1, 1, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.11028, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": 0.11016, "['free_roads', 0, 2, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.10979, "['play_turn', 0, 1, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.10977, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 1]|END_TURN": -0.10939, "['play_turn', 1, 0, 0, 1, 0, 1, 'road', 2]|BUILD_SETTLEMENT": 0.1085, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": 0.10835, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 2]|END_TURN": -0.10801, "['play_turn', 2, 0, 1, 1, 0, 1, 'mixed', 2]|BUILD_CITY": 0.10724, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 0]|PLAY_MONOPOLY": -0.10463, "['move_robber', 1, 1, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": 0.1046, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": -0.10392, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": -0.10367, "['play_turn', 2, 2, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.10349, "['play_turn', 2, 2, 0, 0, 0, 1, 'mixed', 2]|MARITIME_TRADE": 0.10318, "['play_turn', 2, 1, 0, 0, 0, 1, 'mixed', 1]|END_TURN": 0.10305, "['play_turn', 0, 0, 1, 0, 1, 1, 'city', 2]|BUILD_CITY": 0.10253, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 2]|END_TURN": 0.10211, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": -0.10155, "['move_robber', 2, 1, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": 0.10121, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 1]|END_TURN": 0.10097, "['play_turn', 1, 2, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": -0.10047, "['play_turn', 2, 2, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.1, "['play_turn', 1, 2, 0, 0, 0, 1, 'road', 2]|END_TURN": -0.1, "['play_turn', 0, 1, 0, 0, 0, 1, 'road', 2]|END_TURN": -0.1, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 0]|PLAY_MONOPOLY": -0.1, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 0]|PLAY_MONOPOLY": -0.1, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 0]|MARITIME_TRADE": -0.1, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 0]|PLAY_YEAR_OF_PLENTY": -0.1, "['play_turn', 2, 2, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": -0.1, "['play_turn', 0, 2, 0, 0, 0, 1, 'mixed', 2]|END_TURN": -0.1, "['play_turn', 2, 2, 1, 0, 0, 0, 'mixed', 2]|BUILD_CITY": 0.1, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 2]|END_TURN": -0.1, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 0]|PLAY_MONOPOLY": -0.1, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": -0.1, "['play_turn', 0, 2, 0, 1, 1, 1, 'mixed', 1]|BUILD_SETTLEMENT": 0.1, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.09996, "['play_turn', 0, 2, 0, 0, 1, 1, 'mixed', 1]|END_TURN": -0.09989, "['play_turn', 1, 1, 0, 1, 1, 0, 'city', 2]|BUILD_SETTLEMENT": 0.09894, "['move_robber', 2, 2, 0, 0, 0, 0, 'city', 2]|MOVE_ROBBER": -0.09891, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": -0.09861, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 1]|END_TURN": 0.09817, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 1]|END_TURN": -0.09749, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.09695, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 2]|MARITIME_TRADE": 0.09693, "['play_turn', 0, 1, 1, 0, 1, 1, 'mixed', 2]|BUILD_CITY": 0.09674, "['play_turn', 2, 2, 1, 0, 1, 0, 'mixed', 2]|BUILD_CITY": 0.09635, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 2]|END_TURN": -0.09633, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 0]|END_TURN": 0.0955, "['play_turn', 2, 2, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.09515, "['play_turn', 0, 0, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": 0.09515, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 0]|ROLL": 0.0951, "['play_turn', 1, 0, 0, 0, 1, 0, 'mixed', 1]|END_TURN": 0.09501, "['play_turn', 2, 0, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.09469, "['play_turn', 2, 1, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.09467, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.09459, "['play_turn', 1, 1, 1, 0, 0, 1, 'city', 2]|END_TURN": 0.0942, "['play_turn', 1, 2, 0, 0, 1, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.09377, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": 0.09334, "['free_roads', 0, 1, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.09321, "['move_robber', 2, 1, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": 0.0932, "['play_turn', 1, 1, 1, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": 0.09309, "['move_robber', 2, 1, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": 0.09297, "['play_turn', 1, 1, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": -0.09195, "['play_turn', 0, 0, 1, 0, 0, 0, 'city', 1]|MARITIME_TRADE": 0.09195, "['play_turn', 2, 0, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": 0.08938, "['play_turn', 1, 0, 0, 1, 1, 0, 'mixed', 1]|END_TURN": 0.08752, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": 0.0875, "['free_roads', 1, 2, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.08701, "['play_turn', 0, 1, 0, 0, 1, 1, 'road', 2]|BUILD_ROAD": 0.08675, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": 0.08655, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": 0.08628, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 0]|END_TURN": -0.08582, "['play_turn', 0, 1, 1, 0, 1, 0, 'city', 1]|BUILD_CITY": 0.08573, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": 0.08557, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 0]|MARITIME_TRADE": -0.08553, "['play_turn', 2, 0, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.0855, "['play_turn', 2, 2, 0, 1, 0, 1, 'mixed', 2]|BUILD_SETTLEMENT": 0.08545, "['play_turn', 1, 1, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.08468, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": 0.08438, "['play_turn', 2, 1, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.0839, "['play_turn', 2, 0, 0, 0, 0, 1, 'mixed', 1]|END_TURN": 0.0836, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 0]|PLAY_MONOPOLY": 0.08326, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.08259, "['play_turn', 0, 2, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.08253, "['play_turn', 2, 2, 0, 0, 0, 1, 'mixed', 1]|END_TURN": -0.0825, "['play_turn', 0, 2, 1, 0, 1, 0, 'city', 1]|BUILD_CITY": 0.08239, "['play_turn', 1, 1, 0, 0, 0, 1, 'road', 1]|MARITIME_TRADE": 0.08162, "['play_turn', 0, 0, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.08142, "['play_turn', 0, 1, 0, 0, 0, 1, 'road', 2]|MARITIME_TRADE": 0.0814, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 0]|ROLL": 0.08137, "['play_turn', 2, 2, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": 0.08053, "['move_robber', 0, 0, 0, 0, 0, 0, 'mixed', 0]|MOVE_ROBBER": 0.08046, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": 0.08036, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 0]|END_TURN": -0.08025, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": -0.07978, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 2]|END_TURN": -0.07975, "['play_turn', 2, 1, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": -0.07918, "['play_turn', 0, 2, 0, 1, 1, 1, 'road', 1]|BUY_DEVELOPMENT_CARD": 0.07845, "['play_turn', 1, 0, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.07828, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": -0.07815, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": 0.07802, "['play_turn', 2, 0, 0, 0, 0, 1, 'mixed', 2]|END_TURN": 0.07734, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 0]|END_TURN": -0.07689, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 1]|PLAY_KNIGHT_CARD": -0.07649, "['move_robber', 2, 1, 0, 0, 0, 0, 'mixed', 2]|MOVE_ROBBER": 0.07587, "['move_robber', 1, 1, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": -0.07575, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 0]|END_TURN": 0.07494, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": -0.07457, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": -0.07448, "['play_turn', 0, 0, 0, 0, 0, 1, 'mixed', 1]|PLAY_MONOPOLY": 0.07446, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 1]|ROLL": 0.07311, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 0]|ROLL": 0.07302, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": 0.07267, "['play_turn', 1, 1, 0, 0, 0, 1, 'mixed', 1]|END_TURN": -0.07136, "['play_turn', 2, 1, 0, 0, 0, 1, 'mixed', 1]|PLAY_MONOPOLY": 0.07105, "['play_turn', 1, 0, 1, 0, 0, 0, 'city', 1]|END_TURN": 0.07089, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 1]|END_TURN": 0.07041, "['play_turn', 0, 2, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": -0.06992, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": 0.06978, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": 0.06973, "['play_turn', 1, 0, 0, 1, 1, 1, 'city', 1]|BUILD_ROAD": 0.06885, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 1]|ROLL": 0.06885, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 2]|END_TURN": 0.06847, "['play_turn', 0, 2, 0, 1, 1, 0, 'city', 1]|BUILD_SETTLEMENT": 0.06826, "['play_turn', 2, 0, 0, 0, 0, 1, 'mixed', 2]|MARITIME_TRADE": 0.068, "['play_turn', 2, 1, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.06776, "['play_turn', 0, 1, 1, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.06759, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 1]|ROLL": -0.06694, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 2]|END_TURN": -0.06681, "['play_turn', 1, 1, 0, 0, 1, 0, 'city', 1]|END_TURN": -0.0665, "['play_turn', 1, 2, 1, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.06628, "['play_turn', 0, 2, 0, 0, 0, 1, 'mixed', 1]|PLAY_KNIGHT_CARD": -0.06627, "['play_turn', 0, 2, 1, 0, 1, 0, 'mixed', 2]|BUILD_CITY": 0.06574, "['play_turn', 0, 0, 0, 0, 0, 1, 'mixed', 2]|END_TURN": 0.06562, "['play_turn', 0, 0, 0, 0, 0, 1, 'mixed', 1]|MARITIME_TRADE": 0.0652, "['play_turn', 0, 1, 1, 0, 0, 0, 'city', 1]|END_TURN": 0.06489, "['play_turn', 1, 1, 0, 0, 1, 1, 'road', 2]|BUILD_ROAD": 0.06471, "['play_turn', 0, 1, 0, 0, 1, 1, 'city', 2]|BUILD_ROAD": 0.06455, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": 0.06436, "['play_turn', 0, 0, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": 0.0642, "['move_robber', 1, 1, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": -0.06407, "['move_robber', 2, 0, 0, 0, 0, 0, 'city', 2]|MOVE_ROBBER": 0.06388, "['play_turn', 2, 1, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": 0.06386, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": -0.06294, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 0]|END_TURN": 0.06286, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 2]|END_TURN": -0.06268, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": 0.06179, "['play_turn', 1, 0, 1, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.06173, "['play_turn', 2, 1, 1, 0, 1, 0, 'city', 2]|MARITIME_TRADE": 0.06059, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 2]|MARITIME_TRADE": 0.06054, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 2]|END_TURN": -0.06043, "['play_turn', 0, 2, 0, 1, 1, 0, 'road', 1]|BUILD_SETTLEMENT": 0.06022, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 2]|PLAY_YEAR_OF_PLENTY": 0.05996, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.05982, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": -0.05978, "['play_turn', 0, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": -0.05844, "['play_turn', 1, 0, 0, 0, 1, 0, 'mixed', 0]|END_TURN": 0.05831, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": -0.05812, "['play_turn', 2, 2, 0, 1, 1, 1, 'city', 1]|BUILD_ROAD": 0.05729, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 1]|PLAY_MONOPOLY": -0.05715, "['free_roads', 1, 2, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.05699, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": 0.05693, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": -0.05668, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": -0.05607, "['move_robber', 2, 2, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": -0.05576, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": -0.05527, "['play_turn', 0, 1, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.05506, "['play_turn', 0, 0, 0, 1, 1, 1, 'city', 2]|BUILD_ROAD": 0.05487, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 1]|MARITIME_TRADE": -0.05405, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": 0.0539, "['play_turn', 2, 1, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.05294, "['play_turn', 1, 1, 0, 0, 0, 1, 'mixed', 2]|MARITIME_TRADE": 0.0528, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 0]|END_TURN": 0.05266, "['play_turn', 2, 1, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": 0.05253, "['play_turn', 2, 1, 0, 0, 1, 1, 'city', 1]|BUILD_ROAD": 0.0523, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 0]|BUY_DEVELOPMENT_CARD": -0.05223, "['play_turn', 2, 0, 0, 0, 1, 0, 'mixed', 2]|MARITIME_TRADE": 0.05185, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 0]|PLAY_YEAR_OF_PLENTY": -0.05177, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 1]|ROLL": 0.05175, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 2]|END_TURN": 0.05105, "['play_turn', 1, 0, 0, 0, 0, 1, 'mixed', 2]|MARITIME_TRADE": 0.0509, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 0]|ROLL": -0.05069, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 0]|MARITIME_TRADE": -0.05049, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 0]|END_TURN": 0.04983, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 0]|PLAY_MONOPOLY": -0.04964, "['play_turn', 1, 1, 0, 1, 1, 1, 'road', 1]|BUILD_ROAD": 0.04957, "['play_turn', 1, 0, 0, 0, 1, 0, 'road', 2]|MARITIME_TRADE": 0.04953, "['play_turn', 1, 0, 1, 0, 0, 0, 'city', 1]|MARITIME_TRADE": 0.04933, "['play_turn', 1, 2, 0, 0, 0, 1, 'mixed', 1]|END_TURN": -0.04893, "['play_turn', 0, 2, 0, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.04828, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 0]|END_TURN": 0.04777, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 1]|ROLL": 0.04772, "['play_turn', 1, 1, 0, 0, 1, 1, 'city', 2]|BUILD_ROAD": 0.0475, "['play_turn', 1, 2, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.04736, "['free_roads', 1, 1, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.04721, "['play_turn', 0, 2, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": 0.04676, "['play_turn', 1, 0, 0, 1, 1, 1, 'road', 1]|BUILD_ROAD": 0.04645, "['play_turn', 1, 1, 0, 1, 1, 1, 'city', 1]|BUILD_ROAD": 0.04645, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 0]|PLAY_YEAR_OF_PLENTY": -0.04641, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 0]|END_TURN": -0.04619, "['play_turn', 2, 2, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.04571, "['play_turn', 1, 1, 1, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.04528, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 2]|END_TURN": 0.04502, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 0]|END_TURN": 0.04498, "['play_turn', 2, 2, 0, 0, 0, 1, 'city', 0]|END_TURN": 0.04493, "['move_robber', 2, 2, 0, 0, 0, 0, 'city', 0]|MOVE_ROBBER": -0.04381, "['play_turn', 1, 0, 1, 0, 1, 0, 'city', 2]|MARITIME_TRADE": 0.04345, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.04328, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 2]|END_TURN": 0.0431, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 2]|END_TURN": -0.04288, "['move_robber', 1, 2, 0, 0, 0, 0, 'road', 2]|MOVE_ROBBER": -0.04285, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.04278, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 2]|MARITIME_TRADE": 0.04266, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": 0.04257, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 2]|END_TURN": -0.04238, "['play_turn', 1, 1, 1, 0, 0, 0, 'city', 1]|END_TURN": 0.04237, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 1]|PLAY_MONOPOLY": 0.04228, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 1]|PLAY_MONOPOLY": -0.0419, "['play_turn', 0, 1, 0, 0, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.04181, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 0]|PLAY_YEAR_OF_PLENTY": 0.04165, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 0]|PLAY_MONOPOLY": -0.04151, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": -0.04134, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": 0.04122, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": 0.04056, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 1]|ROLL": -0.04005, "['play_turn', 0, 1, 1, 0, 0, 0, 'city', 1]|MARITIME_TRADE": -0.03999, "['play_turn', 2, 2, 0, 1, 1, 1, 'city', 2]|BUILD_ROAD": 0.03994, "['play_turn', 1, 0, 0, 0, 0, 1, 'road', 2]|MARITIME_TRADE": 0.03967, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 2]|END_TURN": 0.03963, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 0]|ROLL": 0.03963, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 1]|MARITIME_TRADE": 0.03906, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.03896, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 1]|MARITIME_TRADE": -0.03896, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 0]|MARITIME_TRADE": 0.03863, "['play_turn', 0, 2, 1, 0, 0, 0, 'city', 1]|END_TURN": 0.03859, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 0]|PLAY_MONOPOLY": 0.03777, "['play_turn', 0, 1, 0, 0, 0, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.03771, "['play_turn', 2, 0, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.03742, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 2]|END_TURN": -0.03736, "['play_turn', 2, 1, 0, 0, 0, 1, 'road', 1]|BUY_DEVELOPMENT_CARD": 0.03733, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": 0.03729, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": -0.03722, "['play_turn', 1, 1, 0, 0, 1, 0, 'city', 2]|MARITIME_TRADE": 0.03705, "['play_turn', 0, 1, 0, 0, 0, 1, 'road', 1]|MARITIME_TRADE": 0.03697, "['play_turn', 0, 2, 0, 1, 1, 0, 'city', 1]|BUILD_ROAD": -0.03693, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 0]|PLAY_MONOPOLY": -0.03673, "['move_robber', 2, 2, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": -0.03664, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 2]|END_TURN": 0.03638, "['play_turn', 1, 1, 0, 1, 1, 1, 'city', 2]|BUILD_ROAD": 0.03626, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 2]|PLAY_YEAR_OF_PLENTY": 0.03578, "['play_turn', 2, 2, 0, 0, 0, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.03545, "['free_roads', 1, 1, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": 0.03533, "['play_turn', 1, 0, 0, 0, 1, 1, 'city', 2]|BUILD_ROAD": 0.0353, "['free_roads', 1, 2, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.03405, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 1]|PLAY_MONOPOLY": -0.03398, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 0]|PLAY_MONOPOLY": -0.03392, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 2]|END_TURN": 0.03389, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": -0.03358, "['play_turn', 1, 1, 0, 1, 1, 0, 'road', 1]|MARITIME_TRADE": 0.03356, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 0]|PLAY_YEAR_OF_PLENTY": 0.03354, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 0]|MARITIME_TRADE": 0.03305, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 1]|END_TURN": -0.03294, "['play_turn', 1, 2, 0, 1, 1, 1, 'city', 2]|BUILD_ROAD": 0.0329, "['play_turn', 2, 1, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": -0.03289, "['move_robber', 2, 2, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": -0.03265, "['move_robber', 0, 0, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": 0.03241, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 0]|PLAY_MONOPOLY": 0.03235, "['play_turn', 1, 0, 0, 0, 1, 1, 'road', 2]|BUILD_ROAD": 0.03221, "['play_turn', 2, 0, 0, 0, 0, 1, 'road', 2]|END_TURN": 0.03194, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 1]|ROLL": 0.03181, "['free_roads', 0, 2, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.03174, "['free_roads', 0, 2, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.03099, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 0]|PLAY_YEAR_OF_PLENTY": -0.03086, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": -0.03082, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": -0.0308, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": 0.03074, "['play_turn', 1, 1, 0, 0, 1, 1, 'city', 1]|BUILD_ROAD": 0.03053, "['play_turn', 2, 0, 0, 0, 1, 0, 'road', 1]|END_TURN": 0.03032, "['play_turn', 1, 0, 0, 0, 0, 1, 'mixed', 1]|MARITIME_TRADE": 0.03024, "['play_turn', 0, 0, 0, 1, 1, 0, 'mixed', 1]|BUILD_ROAD": 0.03024, "['play_turn', 0, 1, 0, 1, 1, 1, 'road', 1]|BUILD_ROAD": 0.02975, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 0]|MARITIME_TRADE": -0.02972, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": -0.02939, "['play_turn', 0, 1, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.02922, "['play_turn', 2, 0, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.02919, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 2]|PLAY_YEAR_OF_PLENTY": 0.02916, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 2]|MARITIME_TRADE": -0.02906, "['play_turn', 1, 1, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.02901, "['play_turn', 1, 1, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.02899, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.0288, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 1]|PLAY_MONOPOLY": 0.02879, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 0]|ROLL": 0.02871, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 1]|END_TURN": -0.02868, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 2]|PLAY_YEAR_OF_PLENTY": 0.02858, "['play_turn', 2, 0, 0, 1, 1, 0, 'city', 2]|BUILD_ROAD": 0.02853, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": -0.02852, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 1]|PLAY_MONOPOLY": -0.0285, "['play_turn', 0, 0, 0, 1, 1, 0, 'city', 1]|BUILD_ROAD": 0.02847, "['play_turn', 0, 1, 0, 1, 1, 1, 'city', 1]|BUILD_ROAD": 0.02833, "['play_turn', 0, 0, 0, 1, 1, 0, 'mixed', 1]|END_TURN": -0.02832, "['free_roads', 2, 0, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": 0.02825, "['initial_placement', 0, 0, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": 0.028, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 1]|ROLL": -0.02796, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": -0.02772, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 1]|PLAY_KNIGHT_CARD": -0.02767, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 1]|PLAY_MONOPOLY": -0.02764, "['play_turn', 1, 0, 0, 0, 1, 0, 'road', 1]|MARITIME_TRADE": 0.02756, "['move_robber', 1, 2, 0, 0, 0, 0, 'mixed', 2]|MOVE_ROBBER": -0.02755, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": -0.02753, "['free_roads', 0, 2, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": -0.02746, "['free_roads', 0, 1, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": 0.02709, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": -0.02709, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": -0.02698, "['play_turn', 0, 2, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": -0.02683, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 1]|PLAY_ROAD_BUILDING": -0.02653, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 2]|MARITIME_TRADE": 0.02604, "['play_turn', 1, 0, 0, 0, 0, 1, 'city', 1]|PLAY_KNIGHT_CARD": 0.02563, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 2]|END_TURN": 0.02535, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 1]|PLAY_ROAD_BUILDING": -0.02523, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 2]|MARITIME_TRADE": 0.02512, "['play_turn', 1, 0, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.02476, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 1]|END_TURN": 0.02473, "['free_roads', 0, 0, 0, 0, 1, 0, 'road', 1]|BUILD_ROAD": 0.02458, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 2]|END_TURN": 0.02455, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 0]|END_TURN": 0.02441, "['move_robber', 0, 2, 0, 0, 0, 0, 'city', 2]|MOVE_ROBBER": -0.02421, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 1]|PLAY_KNIGHT_CARD": -0.02408, "['play_turn', 0, 1, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": -0.02402, "['play_turn', 1, 0, 0, 1, 1, 0, 'road', 1]|END_TURN": 0.02375, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 1]|ROLL": 0.02344, "['play_turn', 0, 2, 0, 0, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.02344, "['play_turn', 0, 1, 0, 0, 0, 1, 'mixed', 2]|MARITIME_TRADE": 0.02332, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 1]|END_TURN": -0.02325, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 1]|END_TURN": 0.02314, "['play_turn', 1, 0, 0, 0, 1, 1, 'mixed', 2]|BUY_DEVELOPMENT_CARD": 0.02312, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 1]|PLAY_MONOPOLY": 0.0229, "['play_turn', 0, 1, 1, 0, 1, 0, 'mixed', 2]|END_TURN": 0.02281, "['play_turn', 1, 0, 0, 0, 0, 0, 'mixed', 0]|ROLL": 0.02278, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 0]|PLAY_YEAR_OF_PLENTY": -0.0227, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 1]|MARITIME_TRADE": 0.02257, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 1]|END_TURN": 0.02247, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 0]|PLAY_MONOPOLY": 0.02242, "['play_turn', 0, 2, 1, 0, 0, 0, 'city', 2]|END_TURN": 0.02235, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 0]|ROLL": -0.02216, "['play_turn', 2, 2, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": 0.02214, "['free_roads', 2, 2, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.02189, "['play_turn', 2, 1, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.02169, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.02166, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 0]|ROLL": 0.02163, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 0]|PLAY_MONOPOLY": 0.02154, "['play_turn', 0, 0, 0, 1, 1, 0, 'city', 2]|BUILD_ROAD": 0.02154, "['move_robber', 1, 1, 0, 0, 0, 0, 'city', 2]|MOVE_ROBBER": -0.02139, "['play_turn', 2, 1, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.02136, "['play_turn', 1, 1, 0, 0, 0, 1, 'mixed', 2]|END_TURN": 0.02124, "['play_turn', 2, 1, 0, 0, 0, 1, 'city', 1]|PLAY_MONOPOLY": 0.02116, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": -0.0211, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 0]|END_TURN": 0.02108, "['play_turn', 2, 1, 0, 1, 1, 1, 'road', 1]|BUILD_ROAD": 0.02091, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 0]|MARITIME_TRADE": 0.02075, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 1]|PLAY_ROAD_BUILDING": 0.0207, "['play_turn', 1, 2, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": 0.02066, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": 0.02059, "['play_turn', 0, 1, 0, 1, 1, 0, 'mixed', 1]|END_TURN": -0.02046, "['play_turn', 1, 0, 0, 0, 1, 0, 'city', 2]|MARITIME_TRADE": 0.02037, "['play_turn', 1, 2, 0, 0, 0, 1, 'road', 1]|BUY_DEVELOPMENT_CARD": 0.02032, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 0]|PLAY_MONOPOLY": 0.02016, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 1]|END_TURN": 0.02014, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 0]|PLAY_ROAD_BUILDING": -0.02011, "['play_turn', 2, 2, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": -0.01997, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 2]|ROLL": 0.01937, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 0]|MARITIME_TRADE": -0.01937, "['play_turn', 0, 0, 0, 1, 1, 0, 'road', 2]|MARITIME_TRADE": 0.01925, "['play_turn', 2, 0, 0, 1, 1, 0, 'city', 1]|BUILD_ROAD": 0.01903, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 1]|PLAY_MONOPOLY": 0.01884, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 1]|PLAY_MONOPOLY": -0.0188, "['play_turn', 0, 2, 1, 0, 0, 0, 'city', 2]|MARITIME_TRADE": -0.01877, "['play_turn', 1, 0, 0, 0, 1, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.01861, "['free_roads', 1, 0, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": 0.0184, "['move_robber', 1, 0, 0, 0, 0, 0, 'mixed', 2]|MOVE_ROBBER": 0.01825, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 1]|PLAY_ROAD_BUILDING": -0.01817, "['play_turn', 1, 2, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.01791, "['move_robber', 2, 1, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": 0.01791, "['move_robber', 0, 1, 0, 0, 0, 0, 'city', 2]|MOVE_ROBBER": -0.01769, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 1]|MARITIME_TRADE": -0.01766, "['play_turn', 0, 1, 0, 0, 0, 1, 'mixed', 2]|END_TURN": 0.0175, "['play_turn', 2, 2, 0, 0, 1, 1, 'city', 2]|BUILD_ROAD": 0.01749, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 1]|PLAY_ROAD_BUILDING": 0.01749, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": -0.01742, "['free_roads', 1, 2, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": -0.01729, "['move_robber', 2, 0, 0, 0, 0, 0, 'mixed', 2]|MOVE_ROBBER": 0.01719, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 2]|PLAY_KNIGHT_CARD": -0.0171, "['free_roads', 0, 1, 0, 0, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.01694, "['play_turn', 1, 2, 0, 0, 1, 1, 'city', 2]|BUILD_ROAD": 0.01666, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 2]|END_TURN": -0.01644, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": -0.01625, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": 0.01625, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 1]|MARITIME_TRADE": -0.01617, "['play_turn', 0, 2, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": -0.0161, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 2]|PLAY_YEAR_OF_PLENTY": -0.01598, "['move_robber', 0, 1, 0, 0, 0, 0, 'mixed', 2]|MOVE_ROBBER": -0.01584, "['play_turn', 1, 1, 0, 0, 0, 1, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.0156, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 0]|PLAY_YEAR_OF_PLENTY": 0.0156, "['play_turn', 0, 2, 0, 0, 1, 0, 'mixed', 1]|PLAY_ROAD_BUILDING": -0.01548, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 0]|ROLL": 0.01514, "['play_turn', 0, 0, 0, 0, 0, 0, 'mixed', 2]|PLAY_MONOPOLY": -0.0151, "['move_robber', 1, 2, 0, 0, 0, 0, 'city', 2]|MOVE_ROBBER": -0.0146, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 1]|PLAY_MONOPOLY": 0.01422, "['play_turn', 1, 0, 0, 0, 0, 1, 'road', 2]|END_TURN": 0.01421, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 1]|PLAY_MONOPOLY": 0.01414, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 0]|MARITIME_TRADE": 0.01403, "['free_roads', 0, 1, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": -0.01385, "['play_turn', 2, 2, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": -0.01378, "['play_turn', 0, 0, 0, 0, 1, 0, 'city', 1]|END_TURN": 0.01373, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 1]|ROLL": 0.01365, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 1]|PLAY_MONOPOLY": -0.01341, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 1]|END_TURN": -0.01328, "['play_turn', 2, 1, 0, 0, 0, 1, 'city', 1]|END_TURN": 0.01327, "['play_turn', 2, 1, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.01307, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 0]|ROLL": -0.01282, "['play_turn', 0, 2, 0, 0, 0, 1, 'road', 1]|END_TURN": -0.0128, "['play_turn', 1, 2, 0, 0, 0, 1, 'mixed', 2]|END_TURN": 0.01277, "['play_turn', 1, 2, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.01275, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 1]|END_TURN": -0.0126, "['play_turn', 0, 1, 0, 0, 1, 1, 'road', 1]|BUILD_ROAD": 0.01243, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 0]|END_TURN": -0.01239, "['play_turn', 2, 2, 0, 0, 0, 1, 'city', 2]|MARITIME_TRADE": -0.01217, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 1]|MARITIME_TRADE": 0.01203, "['play_turn', 2, 0, 0, 0, 1, 1, 'city', 1]|BUILD_ROAD": 0.01194, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 1]|PLAY_MONOPOLY": -0.01181, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 2]|PLAY_YEAR_OF_PLENTY": -0.01159, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 0]|ROLL": -0.01158, "['play_turn', 0, 1, 0, 1, 1, 1, 'city', 2]|BUILD_ROAD": 0.01156, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": 0.01146, "['play_turn', 2, 1, 0, 0, 1, 0, 'city', 1]|MARITIME_TRADE": -0.01146, "['play_turn', 0, 1, 0, 1, 1, 0, 'road', 2]|BUILD_ROAD": -0.01131, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": -0.01126, "['play_turn', 1, 2, 0, 0, 0, 1, 'mixed', 2]|MARITIME_TRADE": 0.01114, "['play_turn', 0, 0, 1, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.01091, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 0]|PLAY_MONOPOLY": 0.01077, "['free_roads', 2, 1, 0, 0, 1, 0, 'mixed', 1]|BUILD_ROAD": -0.01047, "['free_roads', 0, 0, 0, 0, 1, 0, 'road', 0]|BUILD_ROAD": -0.01019, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 1]|MARITIME_TRADE": 0.01011, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 0]|PLAY_YEAR_OF_PLENTY": 0.00984, "['play_turn', 2, 0, 0, 0, 1, 0, 'mixed', 2]|END_TURN": 0.00977, "['play_turn', 0, 0, 0, 0, 1, 0, 'city', 2]|MARITIME_TRADE": 0.00973, "['play_turn', 1, 1, 0, 0, 1, 0, 'city', 1]|MARITIME_TRADE": -0.00967, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 2]|PLAY_YEAR_OF_PLENTY": -0.00966, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 1]|ROLL": -0.00964, "['play_turn', 0, 1, 0, 1, 1, 0, 'city', 2]|MARITIME_TRADE": -0.00956, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 1]|ROLL": 0.0093, "['play_turn', 1, 2, 0, 0, 1, 1, 'road', 2]|BUILD_ROAD": 0.00925, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 1]|MARITIME_TRADE": -0.00924, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 1]|PLAY_MONOPOLY": -0.00909, "['play_turn', 0, 2, 0, 1, 1, 1, 'mixed', 1]|BUILD_ROAD": -0.00902, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 0]|PLAY_KNIGHT_CARD": 0.009, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 1]|ROLL": -0.00889, "['play_turn', 1, 2, 0, 0, 0, 1, 'city', 1]|PLAY_KNIGHT_CARD": -0.00884, "['play_turn', 0, 2, 0, 0, 0, 0, 'road', 0]|ROLL": -0.00856, "['play_turn', 1, 2, 0, 0, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.00854, "['play_turn', 2, 2, 0, 0, 0, 1, 'city', 2]|END_TURN": -0.00827, "['play_turn', 2, 0, 0, 0, 1, 0, 'city', 1]|MARITIME_TRADE": 0.00821, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 2]|PLAY_YEAR_OF_PLENTY": -0.0081, "['play_turn', 2, 2, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": -0.0081, "['move_robber', 2, 1, 0, 0, 0, 0, 'road', 2]|MOVE_ROBBER": 0.00805, "['play_turn', 2, 2, 0, 0, 0, 1, 'road', 1]|MARITIME_TRADE": 0.00799, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 1]|PLAY_ROAD_BUILDING": -0.00761, "['play_turn', 0, 2, 0, 0, 0, 1, 'mixed', 2]|MARITIME_TRADE": -0.00727, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 0]|MARITIME_TRADE": -0.00722, "['move_robber', 1, 0, 0, 0, 0, 0, 'city', 2]|MOVE_ROBBER": 0.00718, "['play_turn', 0, 1, 0, 0, 0, 0, 'city', 0]|ROLL": 0.00711, "['move_robber', 0, 0, 0, 0, 0, 0, 'road', 2]|MOVE_ROBBER": 0.0071, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 0]|PLAY_MONOPOLY": 0.00707, "['play_turn', 0, 1, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": 0.00702, "['play_turn', 1, 2, 0, 0, 0, 1, 'road', 1]|MARITIME_TRADE": 0.00697, "['play_turn', 0, 2, 0, 1, 1, 0, 'mixed', 2]|BUILD_ROAD": -0.00696, "['play_turn', 1, 2, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.00682, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 0]|ROLL": -0.00677, "['move_robber', 0, 0, 0, 0, 0, 0, 'road', 0]|MOVE_ROBBER": 0.0063, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 1]|PLAY_YEAR_OF_PLENTY": -0.00624, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 0]|MARITIME_TRADE": -0.0062, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 1]|PLAY_KNIGHT_CARD": 0.00606, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 1]|PLAY_MONOPOLY": 0.00605, "['play_turn', 1, 0, 0, 0, 1, 0, 'road', 0]|END_TURN": 0.00604, "['play_turn', 0, 2, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.00602, "['play_turn', 0, 2, 0, 1, 1, 1, 'city', 1]|BUILD_ROAD": 0.00587, "['play_turn', 2, 2, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": 0.00556, "['play_turn', 0, 0, 0, 0, 1, 0, 'city', 2]|END_TURN": 0.0055, "['play_turn', 2, 1, 0, 0, 1, 1, 'city', 2]|BUILD_ROAD": 0.00536, "['play_turn', 0, 2, 0, 0, 0, 1, 'road', 1]|MARITIME_TRADE": 0.00514, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": -0.0051, "['play_turn', 2, 2, 0, 0, 0, 1, 'road', 2]|END_TURN": 0.00507, "['play_turn', 1, 2, 0, 0, 1, 1, 'city', 1]|BUILD_ROAD": -0.00507, "['play_turn', 0, 1, 0, 0, 0, 0, 'road', 1]|ROLL": 0.00507, "['play_turn', 0, 2, 0, 0, 1, 1, 'road', 2]|BUILD_ROAD": -0.00488, "['free_roads', 0, 0, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": 0.00483, "['play_turn', 0, 2, 0, 0, 0, 1, 'road', 1]|BUY_DEVELOPMENT_CARD": -0.00478, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 0]|PLAY_YEAR_OF_PLENTY": -0.00467, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.00466, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 2]|PLAY_YEAR_OF_PLENTY": 0.00463, "['play_turn', 1, 2, 1, 0, 0, 0, 'city', 1]|MARITIME_TRADE": -0.00463, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 0]|PLAY_ROAD_BUILDING": -0.00457, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 0]|END_TURN": -0.00452, "['play_turn', 1, 2, 1, 0, 0, 1, 'city', 2]|MARITIME_TRADE": -0.00451, "['play_turn', 2, 1, 0, 0, 0, 0, 'mixed', 1]|ROLL": 0.0045, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": -0.00443, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 0]|PLAY_MONOPOLY": 0.00434, "['play_turn', 1, 2, 0, 1, 1, 1, 'mixed', 2]|BUILD_ROAD": -0.00408, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 2]|PLAY_MONOPOLY": -0.00386, "['play_turn', 0, 2, 0, 0, 0, 1, 'mixed', 1]|MARITIME_TRADE": -0.00385, "['play_turn', 1, 0, 0, 1, 1, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.00383, "['play_turn', 1, 2, 0, 0, 0, 1, 'mixed', 1]|MARITIME_TRADE": -0.00379, "['play_turn', 0, 1, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": -0.00379, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 2]|MARITIME_TRADE": -0.00379, "['play_turn', 0, 2, 0, 1, 1, 0, 'road', 1]|BUILD_ROAD": -0.00371, "['move_robber', 2, 0, 0, 0, 0, 0, 'road', 2]|MOVE_ROBBER": 0.0037, "['play_turn', 0, 1, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": -0.00366, "['play_turn', 0, 1, 0, 0, 0, 1, 'mixed', 1]|PLAY_KNIGHT_CARD": -0.00366, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 0]|END_TURN": -0.00359, "['play_turn', 0, 0, 0, 0, 1, 1, 'mixed', 2]|END_TURN": 0.00358, "['free_roads', 0, 0, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.00356, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": 0.00354, "['play_turn', 2, 1, 0, 0, 0, 1, 'city', 0]|END_TURN": 0.00345, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 1]|MARITIME_TRADE": 0.00335, "['play_turn', 1, 1, 0, 0, 1, 1, 'mixed', 2]|END_TURN": -0.00331, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 0]|MARITIME_TRADE": -0.00324, "['play_turn', 2, 1, 0, 1, 1, 0, 'city', 2]|BUILD_ROAD": 0.0032, "['play_turn', 1, 2, 0, 0, 0, 1, 'road', 2]|MARITIME_TRADE": -0.00311, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 2]|END_TURN": -0.00288, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 2]|PLAY_KNIGHT_CARD": -0.00287, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 1]|ROLL": 0.00282, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": -0.00276, "['play_turn', 0, 0, 0, 0, 1, 1, 'road', 2]|BUILD_ROAD": 0.00276, "['move_robber', 0, 1, 0, 0, 0, 0, 'city', 1]|MOVE_ROBBER": -0.0027, "['play_turn', 1, 2, 0, 0, 1, 0, 'mixed', 0]|PLAY_ROAD_BUILDING": -0.00248, "['play_turn', 1, 2, 0, 1, 1, 1, 'city', 1]|BUILD_ROAD": -0.00242, "['play_turn', 0, 0, 0, 1, 1, 1, 'road', 2]|END_TURN": 0.00226, "['move_robber', 0, 1, 0, 0, 0, 0, 'road', 2]|MOVE_ROBBER": -0.00217, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 1]|PLAY_KNIGHT_CARD": -0.00217, "['play_turn', 2, 0, 1, 0, 0, 0, 'city', 2]|MARITIME_TRADE": 0.00199, "['play_turn', 2, 0, 0, 0, 1, 0, 'mixed', 1]|END_TURN": 0.00199, "['play_turn', 2, 1, 0, 0, 1, 1, 'mixed', 2]|BUILD_ROAD": 0.00197, "['play_turn', 0, 0, 0, 0, 1, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": 0.00183, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 0]|PLAY_KNIGHT_CARD": -0.00175, "['play_turn', 0, 1, 1, 0, 0, 0, 'city', 2]|MARITIME_TRADE": -0.00163, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.00156, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 0]|PLAY_MONOPOLY": -0.00154, "['play_turn', 2, 2, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.00149, "['play_turn', 0, 0, 0, 0, 0, 1, 'road', 1]|END_TURN": -0.00148, "['free_roads', 1, 1, 0, 0, 1, 0, 'road', 2]|BUILD_ROAD": -0.00144, "['play_turn', 0, 2, 0, 1, 1, 1, 'road', 1]|BUILD_ROAD": -0.00144, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 0]|ROLL": -0.0014, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 1]|PLAY_ROAD_BUILDING": -0.00138, "['move_robber', 1, 1, 0, 0, 0, 0, 'mixed', 1]|MOVE_ROBBER": -0.00136, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.00133, "['play_turn', 1, 2, 0, 0, 0, 0, 'mixed', 2]|PLAY_MONOPOLY": -0.00121, "['play_turn', 1, 1, 0, 0, 0, 0, 'mixed', 2]|MARITIME_TRADE": -0.00117, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 0]|PLAY_MONOPOLY": -0.00115, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 0]|PLAY_KNIGHT_CARD": 0.00108, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 1]|PLAY_ROAD_BUILDING": -0.00106, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 1]|ROLL": -0.00105, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 0]|PLAY_ROAD_BUILDING": -0.00103, "['play_turn', 2, 0, 0, 0, 0, 0, 'road', 1]|ROLL": -0.00099, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 1]|PLAY_MONOPOLY": 0.00094, "['play_turn', 0, 2, 0, 0, 1, 1, 'mixed', 1]|BUILD_ROAD": -0.00091, "['play_turn', 1, 1, 0, 0, 1, 0, 'city', 2]|BUILD_ROAD": -0.0009, "['play_turn', 2, 0, 0, 1, 1, 0, 'mixed', 2]|MARITIME_TRADE": 0.00084, "['play_turn', 2, 0, 0, 0, 0, 0, 'mixed', 2]|PLAY_KNIGHT_CARD": 0.00081, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 2]|ROLL": -0.00081, "['play_turn', 2, 1, 0, 0, 0, 0, 'city', 0]|PLAY_MONOPOLY": 0.00079, "['move_robber', 1, 1, 0, 0, 0, 0, 'road', 1]|MOVE_ROBBER": 0.00063, "['play_turn', 2, 2, 0, 0, 0, 0, 'mixed', 1]|ROLL": -0.0006, "['play_turn', 2, 1, 0, 0, 1, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": 0.0006, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 2]|PLAY_ROAD_BUILDING": -0.00058, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 0]|PLAY_ROAD_BUILDING": -0.00048, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 0]|END_TURN": -0.00048, "['play_turn', 0, 2, 0, 0, 1, 1, 'city', 1]|BUILD_ROAD": 0.00047, "['play_turn', 0, 2, 0, 1, 1, 1, 'road', 2]|BUILD_ROAD": 0.00047, "['play_turn', 1, 1, 0, 0, 1, 0, 'mixed', 1]|PLAY_ROAD_BUILDING": 0.00047, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 1]|ROLL": 0.00044, "['play_turn', 2, 0, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": 0.00037, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 1]|PLAY_MONOPOLY": -0.00031, "['play_turn', 0, 1, 1, 0, 0, 1, 'city', 1]|MARITIME_TRADE": -0.00028, "['play_turn', 1, 1, 1, 0, 1, 0, 'city', 2]|MARITIME_TRADE": -0.00025, "['free_roads', 2, 2, 0, 0, 1, 0, 'mixed', 0]|BUILD_ROAD": -0.00019, "['play_turn', 0, 1, 0, 0, 1, 1, 'mixed', 1]|BUY_DEVELOPMENT_CARD": -0.00018, "['play_turn', 1, 1, 1, 0, 0, 1, 'city', 1]|MARITIME_TRADE": -0.00017, "['play_turn', 0, 2, 0, 0, 1, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": -0.00014, "['play_turn', 1, 1, 0, 0, 0, 0, 'city', 1]|PLAY_MONOPOLY": -0.0001, "['play_turn', 1, 0, 0, 0, 1, 0, 'city', 2]|END_TURN": 5e-05, "['play_turn', 2, 2, 0, 0, 0, 1, 'city', 1]|END_TURN": 5e-05, "['play_turn', 2, 2, 0, 0, 1, 0, 'road', 2]|END_TURN": 4e-05, "['play_turn', 0, 0, 0, 0, 0, 1, 'road', 1]|BUY_DEVELOPMENT_CARD": -4e-05, "['play_turn', 1, 1, 0, 0, 1, 0, 'city', 1]|PLAY_ROAD_BUILDING": -3e-05, "['play_turn', 1, 0, 0, 0, 0, 0, 'road', 2]|PLAY_MONOPOLY": 2e-05, "['play_turn', 0, 0, 0, 1, 1, 0, 'road', 1]|END_TURN": 1e-05, "['play_turn', 1, 0, 0, 0, 0, 1, 'mixed', 2]|END_TURN": 0.0, "['play_turn', 2, 1, 0, 0, 1, 0, 'road', 2]|MARITIME_TRADE": 0.0, "['play_turn', 0, 1, 0, 0, 1, 0, 'mixed', 0]|PLAY_YEAR_OF_PLENTY": 0.0, "['play_turn', 1, 2, 0, 0, 0, 0, 'road', 2]|PLAY_MONOPOLY": 0.0, "['play_turn', 0, 1, 0, 0, 0, 1, 'city', 1]|PLAY_MONOPOLY": 0.0, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 0]|END_TURN": 0.0, "['play_turn', 0, 0, 0, 0, 0, 1, 'city', 2]|PLAY_YEAR_OF_PLENTY": 0.0, "['play_turn', 0, 0, 0, 0, 0, 0, 'city', 2]|PLAY_MONOPOLY": 0.0, "['play_turn', 1, 2, 0, 1, 1, 1, 'city', 2]|MARITIME_TRADE": 0.0, "['play_turn', 1, 2, 1, 0, 1, 0, 'city', 2]|BUILD_ROAD": 0.0, "['play_turn', 0, 0, 0, 0, 0, 0, 'road', 2]|PLAY_KNIGHT_CARD": 0.0, "['play_turn', 1, 0, 0, 1, 1, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": 0.0, "['play_turn', 2, 0, 0, 1, 1, 1, 'city', 1]|BUILD_ROAD": 0.0, "['play_turn', 2, 0, 0, 0, 0, 0, 'city', 0]|PLAY_MONOPOLY": 0.0, "['play_turn', 1, 2, 0, 1, 1, 0, 'road', 1]|END_TURN": 0.0, "['play_turn', 2, 0, 0, 1, 1, 0, 'city', 2]|MARITIME_TRADE": 0.0, "['play_turn', 1, 1, 0, 0, 0, 1, 'road', 2]|BUY_DEVELOPMENT_CARD": 0.0, "['play_turn', 1, 1, 0, 0, 0, 0, 'road', 2]|PLAY_KNIGHT_CARD": 0.0, "['move_robber', 1, 1, 0, 0, 0, 0, 'road', 2]|MOVE_ROBBER": 0.0, "['play_turn', 1, 1, 0, 1, 1, 0, 'mixed', 2]|END_TURN": 0.0, "['play_turn', 2, 1, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": 0.0, "['play_turn', 2, 0, 0, 0, 0, 1, 'city', 1]|MARITIME_TRADE": 0.0, "['play_turn', 2, 0, 0, 1, 1, 1, 'city', 2]|BUILD_ROAD": 0.0, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 2]|PLAY_KNIGHT_CARD": 0.0, "['move_robber', 2, 2, 0, 0, 0, 0, 'road', 2]|MOVE_ROBBER": 0.0, "['play_turn', 2, 1, 0, 0, 1, 0, 'road', 1]|MARITIME_TRADE": 0.0, "['play_turn', 2, 2, 0, 0, 0, 0, 'road', 0]|END_TURN": 0.0, "['play_turn', 1, 0, 0, 0, 0, 0, 'city', 2]|PLAY_KNIGHT_CARD": 0.0, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 2]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 2, 0, 1, 0, 1, 0, 'city', 1]|END_TURN": 0.0, "['play_turn', 2, 1, 0, 0, 0, 0, 'road', 1]|ROLL": 0.0, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 1]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 2]|PLAY_YEAR_OF_PLENTY": 0.0, "['play_turn', 1, 0, 0, 0, 1, 0, 'mixed', 1]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 1, 2, 1, 0, 0, 1, 'city', 1]|BUILD_CITY": 0.0, "['play_turn', 2, 2, 0, 0, 0, 0, 'city', 1]|PLAY_YEAR_OF_PLENTY": 0.0, "['play_turn', 0, 2, 0, 0, 0, 0, 'city', 2]|PLAY_KNIGHT_CARD": 0.0, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 0]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 0, 2, 1, 0, 0, 1, 'city', 1]|BUY_DEVELOPMENT_CARD": 0.0, "['play_turn', 1, 1, 0, 0, 1, 0, 'road', 2]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 0, 1, 1, 0, 1, 0, 'city', 2]|END_TURN": 0.0, "['play_turn', 1, 2, 0, 0, 0, 0, 'city', 2]|PLAY_KNIGHT_CARD": 0.0, "['play_turn', 2, 0, 0, 1, 0, 0, 'road', 2]|MARITIME_TRADE": 0.0, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 0]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 2, 1, 0, 0, 0, 1, 'road', 2]|END_TURN": 0.0, "['play_turn', 0, 0, 0, 0, 1, 0, 'road', 1]|PLAY_YEAR_OF_PLENTY": 0.0, "['play_turn', 1, 2, 0, 0, 1, 0, 'road', 2]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 2, 2, 1, 0, 0, 0, 'city', 1]|BUILD_CITY": 0.0, "['play_turn', 0, 0, 0, 0, 1, 0, 'mixed', 0]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 0, 1, 0, 0, 1, 0, 'road', 2]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 0, 2, 0, 0, 1, 0, 'road', 2]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 0, 1, 0, 0, 0, 0, 'mixed', 2]|PLAY_KNIGHT_CARD": 0.0, "['play_turn', 0, 2, 1, 0, 0, 1, 'city', 2]|BUILD_CITY": 0.0, "['play_turn', 2, 2, 0, 0, 1, 0, 'mixed', 1]|PLAY_ROAD_BUILDING": 0.0, "['play_turn', 0, 2, 0, 0, 1, 0, 'city', 1]|PLAY_ROAD_BUILDING": 0.0, "['free_roads', 0, 2, 0, 0, 1, 0, 'city', 1]|BUILD_ROAD": 0.0}

PIPS = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
RESOURCES = ("WOOD", "BRICK", "SHEEP", "WHEAT", "ORE")
BUILD_COSTS = {
    "BUILD_ROAD": {"WOOD": 1, "BRICK": 1},
    "BUILD_SETTLEMENT": {"WOOD": 1, "BRICK": 1, "SHEEP": 1, "WHEAT": 1},
    "BUILD_CITY": {"WHEAT": 2, "ORE": 3},
    "BUY_DEVELOPMENT_CARD": {"SHEEP": 1, "WHEAT": 1, "ORE": 1},
}

# Prefer VP and productive builds; trades only when they unlock something.
PRIORITY = [
    "BUILD_CITY",
    "BUILD_SETTLEMENT",
    "PLAY_KNIGHT_CARD",
    "PLAY_YEAR_OF_PLENTY",
    "PLAY_MONOPOLY",
    "PLAY_ROAD_BUILDING",
    "BUY_DEVELOPMENT_CARD",
    "BUILD_ROAD",
    "MARITIME_TRADE",
    "ROLL",
    "MOVE_ROBBER",
    "END_TURN",
]


# When True, act may override the heuristic if Q has a clear preference.
USE_Q = True
# Minimum Q advantage over the heuristic action before we override.
Q_MARGIN = 0.05


def act(observation):
    """H+Q policy: start from the heuristic; override only when Q clearly disagrees.

    If the clock is nearly empty, skip scoring and use the fast heuristic.
    During offline training time_remaining_s may be None — treat that as plenty of time.
    """
    actions = observation["actions"]
    if not actions:
        raise ValueError("no legal actions")

    remaining = observation.get("time_remaining_s")
    if remaining is not None and remaining < 0.35:
        return {"action": heuristic_policy(observation)}

    heur_id = heuristic_policy(observation)
    if not USE_Q or not Q:
        return {"action": heur_id}

    features = state_features(observation)
    scored = []
    for action in actions:
        key = _q_key(features, action["type"])
        if key in Q:
            scored.append((Q[key], action["id"]))

    if not scored:
        return {"action": heur_id}

    best_q, best_id = max(scored, key=lambda t: (t[0], t[1] == heur_id))
    heur_action = _action_by_id(observation, heur_id)
    heur_key = _q_key(features, heur_action["type"]) if heur_action else None
    heur_q = Q.get(heur_key, None) if heur_key else None

    # Override only when the Q-best action beats the heuristic action by a margin.
    if best_id != heur_id and (heur_q is None or best_q >= heur_q + Q_MARGIN):
        return {"action": best_id}
    return {"action": heur_id}


# ---------------------------------------------------------------------------------
# Step 4 — public log inference (certain deductions only)
# ---------------------------------------------------------------------------------


def estimate_opponent_resources(observation):
    """Reconstruct a lower-bound estimate of the opponent's hand from the public log.

    Certain: dice payouts to buildings we have seen, spends on builds/trades/dev buys,
    cards we stole from them, cards they stole from us, Year of Plenty / Monopoly they played.
    Uncertain (we do not invent certainty): which cards they discarded, which unknown
    card was stolen when we were not involved, composition of their bank trades beyond
    the public give/receive.
    """
    board = observation["board"]
    log = observation.get("log") or []
    tiles_by_number = {}
    tile_resource = {}
    for tile in board["tiles"]:
        key = _tile_key(tile["tile"])
        tile_resource[key] = tile.get("resource")
        num = tile.get("number")
        if num:
            tiles_by_number.setdefault(num, []).append(key)

    # Ownership evolves with the log. Start empty; initial placements appear as BUILD_*.
    settlements = {"me": set(), "opponent": set()}
    cities = {"me": set(), "opponent": set()}
    hand = Counter()
    rolls_seen = 0
    free_roads_left = 0  # PLAY_ROAD_BUILDING grants two free roads
    robber = None
    for tile in board["tiles"]:
        if tile.get("resource") is None and tile.get("number") is None:
            robber = _tile_key(tile["tile"])  # desert default before first MOVE_ROBBER
            break

    for entry in log:
        player = entry.get("player")
        kind = entry.get("type")
        if kind == "BUILD_SETTLEMENT":
            settlements[player].add(entry["node"])
            # Initial placements (before any roll) are free; later settlements cost.
            if player == "opponent" and rolls_seen > 0:
                hand -= Counter(BUILD_COSTS["BUILD_SETTLEMENT"])
        elif kind == "BUILD_CITY":
            node = entry["node"]
            settlements[player].discard(node)
            cities[player].add(node)
            if player == "opponent":
                hand -= Counter(BUILD_COSTS["BUILD_CITY"])
        elif kind == "BUILD_ROAD":
            if player == "opponent" and rolls_seen > 0:
                if free_roads_left > 0:
                    free_roads_left -= 1
                else:
                    hand -= Counter(BUILD_COSTS["BUILD_ROAD"])
        elif kind == "PLAY_ROAD_BUILDING" and player == "opponent":
            free_roads_left += 2
        elif kind == "BUY_DEVELOPMENT_CARD":
            if player == "opponent":
                hand -= Counter(BUILD_COSTS["BUY_DEVELOPMENT_CARD"])
        elif kind == "MARITIME_TRADE" and player == "opponent":
            hand[entry["give"]] -= entry["give_count"]
            hand[entry["receive"]] += 1
        elif kind == "PLAY_YEAR_OF_PLENTY" and player == "opponent":
            hand += Counter(entry.get("resources") or [])
        elif kind == "PLAY_MONOPOLY" and player == "opponent":
            # Exact gain unknown without our past hand; do not invent a number.
            pass
        elif kind == "ROLL":
            rolls_seen += 1
            dice = entry.get("dice") or [0, 0]
            total = sum(dice)
            if total == 7:
                continue
            for tkey in tiles_by_number.get(total, []):
                if tkey == robber:
                    continue
                res = tile_resource.get(tkey)
                if not res:
                    continue
                nodes = set()
                for tile in board["tiles"]:
                    if _tile_key(tile["tile"]) == tkey:
                        nodes = set(tile["nodes"])
                        break
                for node in nodes & settlements["opponent"]:
                    hand[res] += 1
                for node in nodes & cities["opponent"]:
                    hand[res] += 2
        elif kind == "MOVE_ROBBER":
            robber = _tile_key(entry["tile"])
            stole_from = entry.get("stole_from")
            stolen = entry.get("stolen_resource")
            if player == "opponent" and stole_from == "me" and stolen:
                hand[stolen] += 1
            elif player == "me" and stole_from == "opponent" and stolen:
                hand[stolen] -= 1
        elif kind == "DISCARD" and player == "opponent":
            # Count known, composition unknown — do not guess which cards.
            pass

        for r in list(hand):
            if hand[r] < 0:
                hand[r] = 0

    # Align total with public card count when our estimate overshoots
    public_count = observation["opponent"].get("resource_cards")
    if public_count is not None:
        while sum(hand.values()) > public_count:
            # Drop from the most plentiful estimated resource
            rich = max(RESOURCES, key=lambda r: hand[r])
            if hand[rich] <= 0:
                break
            hand[rich] -= 1

    return {r: int(hand[r]) for r in RESOURCES}


def opponent_likely_rich_resource(observation):
    """Best monopoly / steal target from the public estimate."""
    est = estimate_opponent_resources(observation)
    # If everything is zero, fall back to resources their buildings touch
    if sum(est.values()) == 0:
        _, resources, _ = _node_info(observation["board"])
        opp = observation["opponent"]
        touched = Counter()
        for node in opp.get("settlements", []) + opp.get("cities", []):
            for res in resources.get(node, set()):
                weight = 2 if node in opp.get("cities", []) else 1
                touched[res] += weight
        if touched:
            return max(touched, key=touched.get)
        return "ORE"
    return max(est, key=est.get)


# ---------------------------------------------------------------------------------
# Board / resource helpers
# ---------------------------------------------------------------------------------


def _vp_bucket(vp):
    if vp <= 2:
        return 0
    if vp <= 4:
        return 1
    if vp <= 6:
        return 2
    return 3


def _hand_bucket(n):
    if n <= 3:
        return 0
    if n <= 7:
        return 1
    return 2


def _resource_shape(resources):
    road = resources.get("WOOD", 0) + resources.get("BRICK", 0)
    city = resources.get("WHEAT", 0) + resources.get("ORE", 0)
    if road >= city + 2:
        return "road"
    if city >= road + 2:
        return "city"
    return "mixed"


def _action_types(observation):
    return {a["type"] for a in observation["actions"]}


def _action_by_id(observation, action_id):
    for action in observation["actions"]:
        if action["id"] == action_id:
            return action
    return None


def _q_key(features, action_type):
    return f"{features}|{action_type}"


def _tile_key(tile):
    return tuple(tile) if isinstance(tile, (list, tuple)) else tile


def _node_info(board):
    """Per-node pip total, resource set, and whether a port touches the node."""
    production = {}
    resources = {}
    for tile in board["tiles"]:
        pips = PIPS.get(tile.get("number"), 0)
        res = tile.get("resource")
        for node in tile["nodes"]:
            production[node] = production.get(node, 0) + pips
            resources.setdefault(node, set())
            if res:
                resources[node].add(res)
    ports = {}
    for port in board.get("ports", []):
        for node in port["nodes"]:
            ports[node] = port.get("resource")  # None => 3:1
    return production, resources, ports


def _node_score(node, production, resources, ports, prefer_missing=None):
    score = float(production.get(node, 0))
    kinds = resources.get(node, set())
    score += 1.5 * len(kinds)
    if node in ports:
        score += 2.0 if ports[node] is None else 1.5
    if prefer_missing:
        score += 2.0 * len(kinds & prefer_missing)
    # Mild preference for balanced numbers already in production via pips.
    return score


def _owned_resources(me):
    have = set()
    production, resources, _ = None, None, None
    # Settlements/cities imply resources from adjacent tiles — caller passes board.
    return have


def _my_resource_kinds(observation):
    """Resources my settlements/cities currently touch."""
    production, resources, _ports = _node_info(observation["board"])
    me = observation["me"]
    kinds = set()
    for node in me.get("settlements", []) + me.get("cities", []):
        kinds |= resources.get(node, set())
    return kinds


def _edge_key(edge):
    return tuple(sorted(edge))


def _road_toward_score(edge, production, resources, ports, my_nodes, occupied):
    """Prefer roads that reach a high-value empty node we do not already own."""
    a, b = edge
    score = 0.0
    for node in (a, b):
        if node in my_nodes or node in occupied:
            continue
        score = max(score, _node_score(node, production, resources, ports))
    # Slight bonus for extending from our network
    if a in my_nodes or b in my_nodes:
        score += 0.5
    return score


def _occupied_nodes(observation):
    occupied = set()
    for side in ("me", "opponent"):
        player = observation[side]
        occupied.update(player.get("settlements", []))
        occupied.update(player.get("cities", []))
    return occupied


def _my_nodes(observation):
    me = observation["me"]
    return set(me.get("settlements", [])) | set(me.get("cities", []))


def _tile_pips(board):
    out = {}
    for tile in board["tiles"]:
        out[_tile_key(tile["tile"])] = PIPS.get(tile.get("number"), 0)
    return out


def _opponent_nodes_on_tile(board, tile_coord, opponent):
    nodes = set()
    key = _tile_key(tile_coord)
    for tile in board["tiles"]:
        if _tile_key(tile["tile"]) == key:
            nodes = set(tile["nodes"])
            break
    opp = set(opponent.get("settlements", [])) | set(opponent.get("cities", []))
    return nodes & opp


def _can_afford_after_trade(resources, trade):
    """Return new resource counts if we apply a maritime trade, else None."""
    have = Counter(resources)
    give, n, recv = trade["give"], trade["give_count"], trade["receive"]
    if have[give] < n:
        return None
    have[give] -= n
    have[recv] += 1
    return have


def _unlocks_build(have, action_types):
    """Which valuable builds become affordable with this hand."""
    unlocked = []
    for kind, cost in BUILD_COSTS.items():
        if kind not in action_types and kind.startswith("BUILD"):
            # action may not be listed until resources match; check affordability
            pass
        if all(have.get(r, 0) >= c for r, c in cost.items()):
            unlocked.append(kind)
    return unlocked


def _affordable_builds(resources):
    have = resources if isinstance(resources, Counter) else Counter(resources)
    return [
        kind
        for kind, cost in BUILD_COSTS.items()
        if all(have.get(r, 0) >= c for r, c in cost.items())
    ]


def _missing_for(cost, resources):
    have = resources if isinstance(resources, dict) else dict(resources)
    return {r: c - have.get(r, 0) for r, c in cost.items() if have.get(r, 0) < c}


# ---------------------------------------------------------------------------------
# Required algorithms
# ---------------------------------------------------------------------------------


def state_features(observation):
    """Coarse, deterministic abstraction for tabular Q-learning."""
    me = observation["me"]
    opp = observation["opponent"]
    types = _action_types(observation)
    resources = me.get("resources") or {}
    return [
        observation.get("phase", "?"),
        _vp_bucket(me.get("victory_points", me.get("visible_victory_points", 0))),
        _vp_bucket(opp.get("visible_victory_points", 0)),
        int("BUILD_CITY" in types),
        int("BUILD_SETTLEMENT" in types),
        int("BUILD_ROAD" in types),
        int("BUY_DEVELOPMENT_CARD" in types),
        _resource_shape(resources),
        _hand_bucket(me.get("resource_cards", sum(resources.values()) if resources else 0)),
    ]


def action_value(observation, action_id):
    """Q-table lookup by state features + action type; missing keys are 0.0."""
    action = _action_by_id(observation, action_id)
    if action is None:
        return 0.0
    key = _q_key(state_features(observation), action["type"])
    return float(Q.get(key, 0.0))


def q_update(q, reward, best_next_q, alpha, gamma):
    """One Q-learning update. Returns the new value for Q(s, a)."""
    return q + alpha * (reward + gamma * best_next_q - q)


def heuristic_policy(observation):
    """Strong baseline: scored placement, robber, builds, unlock-only trades."""
    actions = observation["actions"]
    if not actions:
        raise ValueError("no legal actions")

    phase = observation.get("phase")
    production, resources, ports = _node_info(observation["board"])

    if phase == "initial_placement":
        return _pick_initial(observation, actions, production, resources, ports)

    if phase == "move_robber":
        return _pick_robber(observation, actions)

    if phase == "free_roads":
        return _pick_road(observation, actions, production, resources, ports)

    # play_turn (and any other)
    return _pick_play_turn(observation, actions, production, resources, ports)


# ---------------------------------------------------------------------------------
# Heuristic decisions
# ---------------------------------------------------------------------------------


def _pick_initial(observation, actions, production, resources, ports):
    if actions[0]["type"] == "BUILD_SETTLEMENT":
        have = _my_resource_kinds(observation)
        prefer = set(RESOURCES) - have
        return max(
            actions,
            key=lambda a: _node_score(a["node"], production, resources, ports, prefer),
        )["id"]
    # Road after settlement: point toward best empty neighbour
    occupied = _occupied_nodes(observation)
    my_nodes = _my_nodes(observation)
    return max(
        actions,
        key=lambda a: _road_toward_score(
            a["edge"], production, resources, ports, my_nodes, occupied
        ),
    )["id"]


def _pick_robber(observation, actions):
    tile_pips = _tile_pips(observation["board"])
    opp = observation["opponent"]
    est = estimate_opponent_resources(observation)
    # Prefer stealing when they likely still hold cards
    likely_cards = sum(est.values())
    public_cards = opp.get("resource_cards", 0)

    def score(a):
        s = 0.0
        if a.get("steal_from") == "opponent":
            s += 20.0
            s += 2.0 * max(likely_cards, public_cards)
        s += tile_pips.get(_tile_key(a["tile"]), 0)
        if _opponent_nodes_on_tile(observation["board"], a["tile"], opp):
            s += 5.0
        return s

    return max(actions, key=score)["id"]


def _pick_road(observation, actions, production, resources, ports):
    occupied = _occupied_nodes(observation)
    my_nodes = _my_nodes(observation)
    return max(
        actions,
        key=lambda a: _road_toward_score(
            a["edge"], production, resources, ports, my_nodes, occupied
        ),
    )["id"]


def _pick_settlement(actions, production, resources, ports, prefer_missing):
    return max(
        actions,
        key=lambda a: _node_score(a["node"], production, resources, ports, prefer_missing),
    )["id"]


def _pick_city(actions, production, resources, ports):
    # Cities upgrade settlements; prefer highest production settlement node
    return max(
        actions,
        key=lambda a: _node_score(a["node"], production, resources, ports),
    )["id"]


def _trade_unlocks_something(observation, trade):
    """True if this maritime trade newly enables a build or buy_dev this turn."""
    me_res = observation["me"].get("resources") or {}
    before = set(_affordable_builds(me_res))
    after_hand = _can_afford_after_trade(me_res, trade)
    if after_hand is None:
        return False
    after = set(_affordable_builds(after_hand))
    valuable = {"BUILD_CITY", "BUILD_SETTLEMENT", "BUY_DEVELOPMENT_CARD", "BUILD_ROAD"}
    return bool((after - before) & valuable)


def _pick_trade(observation, actions):
    useful = [a for a in actions if _trade_unlocks_something(observation, a)]
    if not useful:
        return None
    # Prefer trades that unlock city, then settlement, then road/dev
    rank = {
        "BUILD_CITY": 4,
        "BUILD_SETTLEMENT": 3,
        "BUY_DEVELOPMENT_CARD": 2,
        "BUILD_ROAD": 1,
    }

    def score(a):
        me_res = observation["me"].get("resources") or {}
        before = set(_affordable_builds(me_res))
        after = set(_affordable_builds(_can_afford_after_trade(me_res, a)))
        gained = after - before
        return max((rank.get(g, 0) for g in gained), default=0)

    return max(useful, key=score)["id"]


def _pick_dev_play(observation, actions, kind):
    if kind == "PLAY_MONOPOLY":
        # Blend what we need with what the log says they likely hold
        me_res = observation["me"].get("resources") or {}
        est = estimate_opponent_resources(observation)
        missing = _missing_for(BUILD_COSTS["BUILD_CITY"], me_res)
        if not missing:
            missing = _missing_for(BUILD_COSTS["BUILD_SETTLEMENT"], me_res)
        rich = opponent_likely_rich_resource(observation)

        def mono_score(a):
            res = a.get("resource")
            score = float(est.get(res, 0)) * 3.0
            if res == rich:
                score += 2.0
            if res in missing:
                score += 4.0 + missing[res]
            return score

        return max(actions, key=mono_score)["id"]

    if kind == "PLAY_YEAR_OF_PLENTY":
        me_res = observation["me"].get("resources") or {}
        # Prefer the listed option whose resources most help city then settlement
        def yop_score(a):
            gained = Counter(a.get("resources") or [])
            trial = Counter(me_res) + gained
            score = 0
            if "BUILD_CITY" in _affordable_builds(trial):
                score += 10
            if "BUILD_SETTLEMENT" in _affordable_builds(trial):
                score += 6
            if "BUY_DEVELOPMENT_CARD" in _affordable_builds(trial):
                score += 3
            return score

        return max(actions, key=yop_score)["id"]

    return actions[0]["id"]


def _pick_play_turn(observation, actions, production, resources, ports):
    types = _action_types(observation)
    prefer = set(RESOURCES) - _my_resource_kinds(observation)
    me = observation["me"]
    vp = me.get("victory_points", 0)
    vps_to_win = observation.get("vps_to_win", 7)

    # Endgame: if a build wins or reaches 6+, prioritise VP actions hard
    urgent_city = vp >= vps_to_win - 2
    urgent_settle = vp >= vps_to_win - 1

    for kind in PRIORITY:
        options = [a for a in actions if a["type"] == kind]
        if not options:
            continue

        if kind == "BUILD_CITY":
            return _pick_city(options, production, resources, ports)

        if kind == "BUILD_SETTLEMENT":
            return _pick_settlement(options, production, resources, ports, prefer)

        if kind == "BUILD_ROAD":
            # Skip random roads if we are one VP from a settlement we cannot yet place
            # and a trade might be better — but if road is offered, take best direction.
            return _pick_road(observation, options, production, resources, ports)

        if kind == "MARITIME_TRADE":
            trade_id = _pick_trade(observation, options)
            if trade_id is not None:
                return trade_id
            continue  # do not trade for no reason

        if kind == "BUY_DEVELOPMENT_CARD":
            # Prefer city/settlement path when ore-poor late; still buy if offered
            if urgent_settle and "BUILD_SETTLEMENT" not in types and "BUILD_CITY" not in types:
                return options[0]["id"]
            if urgent_city and "BUILD_CITY" in types:
                continue
            return options[0]["id"]

        if kind in ("PLAY_KNIGHT_CARD", "PLAY_ROAD_BUILDING"):
            return options[0]["id"]

        if kind in ("PLAY_YEAR_OF_PLENTY", "PLAY_MONOPOLY"):
            return _pick_dev_play(observation, options, kind)

        if kind in ("ROLL", "END_TURN", "MOVE_ROBBER"):
            return options[0]["id"]

    return actions[0]["id"]
