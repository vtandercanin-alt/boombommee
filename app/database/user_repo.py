from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models.models import User, CaseOpening, Referral, Transaction, Leaderboard
from datetime import datetime


class UserRepository:
    """User database operations"""
    
    @staticmethod
    async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str = None, first_name: str = None):
        """Get or create user"""
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalars().first()
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                stars_balance=0,
                total_earned=0
            )
            session.add(user)
            await session.commit()
        else:
            # Update user info if provided
            if username and not user.username:
                user.username = username
            if first_name and not user.first_name:
                user.first_name = first_name
            await session.commit()
        
        return user
    
    @staticmethod
    async def get_user(session: AsyncSession, telegram_id: int):
        """Get user by telegram_id"""
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def update_balance(session: AsyncSession, telegram_id: int, amount: float):
        """Update user stars balance"""
        user = await UserRepository.get_user(session, telegram_id)
        if user:
            user.stars_balance += amount
            user.total_earned += max(0, amount)  # Track only positive amounts
            user.updated_at = datetime.utcnow()
            await session.commit()
        return user
    
    @staticmethod
    async def add_case_opening(session: AsyncSession, user_id: int, case_type: str, amount_spent: float, reward: float):
        """Record case opening"""
        user = await UserRepository.get_user(session, user_id)
        if not user:
            return None
        
        profit = reward - amount_spent
        user.cases_opened += 1
        
        case_opening = CaseOpening(
            user_id=user_id,
            case_type=case_type,
            amount_spent=amount_spent,
            reward=reward,
            profit=profit
        )
        
        session.add(case_opening)
        user.stars_balance += profit
        user.total_earned += max(0, reward)
        await session.commit()
        
        return case_opening
    
    @staticmethod
    async def get_leaderboard(session: AsyncSession, limit: int = 10):
        """Get top users by total earned"""
        query = select(User).where(User.is_active == True).order_by(desc(User.total_earned)).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def add_referral(session: AsyncSession, referrer_id: int, referee_id: int, commission: float = 0):
        """Add referral"""
        referral = Referral(
            referrer_id=referrer_id,
            referee_id=referee_id,
            commission=commission
        )
        session.add(referral)
        await session.commit()
        return referral
    
    @staticmethod
    async def add_transaction(session: AsyncSession, user_id: int, trans_type: str, amount: float, description: str = None):
        """Add transaction record"""
        transaction = Transaction(
            user_id=user_id,
            transaction_type=trans_type,
            amount=amount,
            description=description
        )
        session.add(transaction)
        await session.commit()
        return transaction
    
    @staticmethod
    async def get_user_stats(session: AsyncSession, telegram_id: int):
        """Get user statistics"""
        user = await UserRepository.get_user(session, telegram_id)
        if not user:
            return None
        
        # Get referral count
        referral_query = select(func.count(Referral.id)).where(Referral.referrer_id == telegram_id)
        referral_result = await session.execute(referral_query)
        referral_count = referral_result.scalars().first() or 0
        
        return {
            'user_id': user.telegram_id,
            'username': user.username,
            'first_name': user.first_name,
            'stars_balance': user.stars_balance,
            'total_earned': user.total_earned,
            'cases_opened': user.cases_opened,
            'referral_count': referral_count,
            'referral_earnings': user.referral_earnings,
            'level': user.level,
            'rank': user.rank,
            'created_at': user.created_at
        }
