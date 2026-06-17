import random
from app.config import config


class CaseManager:
    """Case management and rewards system"""
    
    @staticmethod
    def get_case_price(case_type: str) -> int:
        """Get case price in stars"""
        return config.CASE_PRICES.get(case_type, 10)
    
    @staticmethod
    def open_case(case_type: str) -> float:
        """Open case and get reward"""
        if case_type not in config.CASE_REWARDS:
            return random.randint(5, 50)
        
        min_reward, max_reward = config.CASE_REWARDS[case_type]
        reward = random.randint(min_reward, max_reward)
        return float(reward)
    
    @staticmethod
    def get_case_info(case_type: str) -> dict:
        """Get case information"""
        return {
            'type': case_type,
            'price': CaseManager.get_case_price(case_type),
            'min_reward': config.CASE_REWARDS.get(case_type, (5, 50))[0],
            'max_reward': config.CASE_REWARDS.get(case_type, (5, 50))[1],
        }
    
    @staticmethod
    def get_all_cases() -> list:
        """Get all available cases"""
        cases = []
        for case_type in config.CASE_PRICES.keys():
            cases.append(CaseManager.get_case_info(case_type))
        return cases


class RankSystem:
    """User rank and level system"""
    
    RANKS = [
        {'level': 1, 'name': 'Bronze', 'min_earned': 0},
        {'level': 2, 'name': 'Silver', 'min_earned': 500},
        {'level': 3, 'name': 'Gold', 'min_earned': 1500},
        {'level': 4, 'name': 'Platinum', 'min_earned': 5000},
        {'level': 5, 'name': 'Diamond', 'min_earned': 15000},
    ]
    
    @staticmethod
    def get_rank(total_earned: float) -> dict:
        """Get user rank based on total earned"""
        for i in range(len(RankSystem.RANKS) - 1, -1, -1):
            if total_earned >= RankSystem.RANKS[i]['min_earned']:
                return RankSystem.RANKS[i]
        return RankSystem.RANKS[0]
    
    @staticmethod
    def get_next_rank_requirement(current_earned: float) -> dict:
        """Get next rank requirements"""
        current_rank = RankSystem.get_rank(current_earned)
        for rank in RankSystem.RANKS:
            if rank['level'] > current_rank['level']:
                return {
                    'name': rank['name'],
                    'level': rank['level'],
                    'needed': rank['min_earned'] - current_earned
                }
        return None
