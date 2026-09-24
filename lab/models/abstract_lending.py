"""Safe toy lending model used to test invariants without chain access or exploit transactions."""
from dataclasses import dataclass

@dataclass
class Position:
    collateral: int
    debt: int
    liquidation_factor_bps: int = 7500

    def healthy(self) -> bool:
        return self.collateral * 10_000 >= self.debt * self.liquidation_factor_bps

    def donate_collateral(self, amount: int) -> None:
        if amount < 0 or amount > self.collateral:
            raise ValueError('invalid donation')
        self.collateral -= amount


def invariant_no_unchecked_self_health_transition(before: Position, after: Position) -> bool:
    """A caller must not reach a liquidation-triggering state through a donated collateral transition without an explicit risk check."""
    return before.healthy() and (after.healthy() or after.debt == 0)
