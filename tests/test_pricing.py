import pytest

from app.services.pricing import calculate_token_cost


def test_token_cost_without_cached_or_reasoning():
    cost = calculate_token_cost(
        input_tokens=1_000_000,
        cached_input_tokens=0,
        output_tokens=0,
        reasoning_tokens=0,
    )

    assert cost == 500


def test_cached_input_is_cheaper():
    cost = calculate_token_cost(
        input_tokens=1_000_000,
        cached_input_tokens=500_000,
        output_tokens=0,
        reasoning_tokens=0,
    )

    assert cost == 275


def test_reasoning_tokens_count_as_output():
    cost = calculate_token_cost(
        input_tokens=0,
        cached_input_tokens=0,
        output_tokens=500_000,
        reasoning_tokens=500_000,
    )

    assert cost == 1500


def test_cached_input_cannot_exceed_input():
    with pytest.raises(ValueError):
        calculate_token_cost(
            input_tokens=100,
            cached_input_tokens=200,
            output_tokens=0,
            reasoning_tokens=0,
        )