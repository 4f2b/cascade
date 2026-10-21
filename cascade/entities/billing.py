from typing import Optional, List, Dict, Any
from enum import IntEnum


class PremiumType(IntEnum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
    NITRO_BASIC = 3


class PaymentSourceType(IntEnum):
    CARD = 1
    PAYPAL = 2
    GOOGLE_PLAY = 3
    APPLE_APP_STORE = 4
    VIRTUAL_CURRENCY = 5


class SubscriptionStatus(IntEnum):
    ACTIVE = 1
    ENDING = 2
    INACTIVE = 3


class PaymentSource:
    def __init__(self, data: Dict[str, Any]):
        self.id: int = int(data['id'])
        self.type: PaymentSourceType = PaymentSourceType(data['type'])
        self.invalid: bool = data.get('invalid', False)
        self.default: bool = data.get('default', False)
        self.billing_address: Dict = data.get('billing_address', {})
        self.brand: Optional[str] = data.get('brand')
        self.last_4: Optional[str] = data.get('last_4')
        self.expires_month: Optional[int] = data.get('expires_month')
        self.expires_year: Optional[int] = data.get('expires_year')
        self.email: Optional[str] = data.get('email')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'type': int(self.type),
            'invalid': self.invalid,
            'default': self.default
        }


class Subscription:
    def __init__(self, data: Dict[str, Any]):
        self.id: int = int(data['id'])
        self.type: int = data.get('type', 0)
        self.status: SubscriptionStatus = SubscriptionStatus(data['status'])
        self.current_period_start: str = data.get('current_period_start', '')
        self.current_period_end: str = data.get('current_period_end', '')
        self.canceled_at: Optional[str] = data.get('canceled_at')
        self.trial_id: Optional[int] = int(data['trial_id']) if data.get('trial_id') else None
        self.trial_ends_at: Optional[str] = data.get('trial_ends_at')
        self.payment_source_id: Optional[int] = int(data['payment_source_id']) if data.get('payment_source_id') else None
        self.plan_id: Optional[int] = int(data['plan_id']) if data.get('plan_id') else None

    @property
    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE

    @property
    def is_ending(self) -> bool:
        return self.status == SubscriptionStatus.ENDING

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'status': int(self.status),
            'current_period_start': self.current_period_start,
            'current_period_end': self.current_period_end
        }


class GiftCode:
    def __init__(self, data: Dict[str, Any]):
        self.code: str = data['code']
        self.sku_id: int = int(data.get('sku_id', 0))
        self.store_listing_id: Optional[int] = int(data['store_listing_id']) if data.get('store_listing_id') else None
        self.uses: int = data.get('uses', 0)
        self.max_uses: int = data.get('max_uses', 1)
        self.redeemed: bool = data.get('redeemed', False)
        self.expires_at: Optional[str] = data.get('expires_at')
        self.subscription_plan: Optional[Dict] = data.get('subscription_plan')

    @property
    def url(self) -> str:
        return f'https://discord.gift/{self.code}'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'uses': self.uses,
            'max_uses': self.max_uses,
            'redeemed': self.redeemed
        }
