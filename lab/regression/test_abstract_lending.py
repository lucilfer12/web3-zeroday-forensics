from lab.models.abstract_lending import Position, invariant_no_unchecked_self_health_transition

def test_healthy_position_stays_healthy_for_safe_transition():
    before=Position(collateral=10_000, debt=5_000)
    after=Position(collateral=9_000, debt=5_000)
    assert invariant_no_unchecked_self_health_transition(before, after)

def test_invariant_detects_bad_health_transition():
    before=Position(collateral=10_000, debt=7_000)
    after=Position(collateral=4_000, debt=7_000)
    assert before.healthy()
    assert not invariant_no_unchecked_self_health_transition(before, after)
