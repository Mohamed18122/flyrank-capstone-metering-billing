from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPricing:
    input_per_million: int
    cached_input_per_million: int
    output_per_million: int


PRICING = TokenPricing(
    input_per_million=500,
    cached_input_per_million=50,
    output_per_million=1500,
)


def calculate_token_cost(
    input_tokens: int,
    cached_input_tokens: int,
    output_tokens: int,
    reasoning_tokens: int,
) -> int:
    if input_tokens < 0:
        raise ValueError("input_tokens cannot be negative")

    if cached_input_tokens < 0:
        raise ValueError("cached_input_tokens cannot be negative")

    if output_tokens < 0:
        raise ValueError("output_tokens cannot be negative")

    if reasoning_tokens < 0:
        raise ValueError("reasoning_tokens cannot be negative")

    if cached_input_tokens > input_tokens:
        raise ValueError(
            "cached_input_tokens cannot exceed input_tokens"
        )

    fresh_input_tokens = input_tokens - cached_input_tokens
    billable_output_tokens = output_tokens + reasoning_tokens

    cost_cents = (
        fresh_input_tokens * PRICING.input_per_million
        + cached_input_tokens * PRICING.cached_input_per_million
        + billable_output_tokens * PRICING.output_per_million
    ) // 1_000_000

    return cost_cents