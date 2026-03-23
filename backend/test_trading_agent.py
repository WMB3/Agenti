import asyncio
import json
from ingestion.models import Signal, MarketResolution
from polymarket_service import PolymarketTradingAgent

async def test_agent():
    agent = PolymarketTradingAgent()

    # 1. Test Low Confidence (Rejected)
    low_conf_signal = Signal(
        market_id="0xlowconf",
        outcome="YES",
        amount=100.0,
        max_price=0.5,
        confidence_score=0.6
    )
    print("\n--- Test Low Confidence ---")
    result = await agent.process_signal(low_conf_signal)
    print(json.dumps(result.model_dump(), indent=2))
    assert result.status == "REJECTED"

    # 2. Test High Slippage (Rejected)
    # Default midpoint is 0.50, slippage limit 2%. 0.6 is 20% away.
    slippage_signal = Signal(
        market_id="0xslippage",
        outcome="NO",
        amount=100.0,
        max_price=0.6,
        confidence_score=0.9
    )
    print("\n--- Test High Slippage ---")
    result = await agent.process_signal(slippage_signal)
    print(json.dumps(result.model_dump(), indent=2))
    assert result.status == "REJECTED"

    # 3. Test Successful Execution
    success_signal = Signal(
        market_id="0xsuccess",
        outcome="YES",
        amount=50.0, # Within 10% of 1000
        max_price=0.505, # < 2% of 0.50
        confidence_score=0.8
    )
    print("\n--- Test Successful Execution ---")
    result = await agent.process_signal(success_signal)
    print(json.dumps(result.model_dump(), indent=2))
    assert result.status == "EXECUTED"
    assert "Buy 50.0 shares" in result.action

    # 4. Test High Risk (Rejected)
    # Wallet balance 1000, max position 10% (100).
    high_risk_signal = Signal(
        market_id="0xhighrisk",
        outcome="YES",
        amount=150.0, # Exceeds 10%
        max_price=0.505,
        confidence_score=0.8
    )
    print("\n--- Test High Risk (Position Size) ---")
    result = await agent.process_signal(high_risk_signal)
    print(json.dumps(result.model_dump(), indent=2))
    assert result.status == "REJECTED"
    assert "exceeds max position size" in result.reasoning

    # 5. Test Drawdown limit
    print("\n--- Test Daily Drawdown Limit ---")
    agent.wallet_balance = 900.0 # 10% drawdown from 1000.0
    result = await agent.process_signal(success_signal)
    print(json.dumps(result.model_dump(), indent=2))
    assert result.status == "REJECTED"
    assert "Daily drawdown" in result.reasoning

    # 6. Test Redemption
    resolution = MarketResolution(
        market_id="0xresolved",
        token_id="0xtoken123",
        outcome="YES"
    )
    print("\n--- Test Redemption ---")
    result = await agent.redeem_positions(resolution)
    print(json.dumps(result.model_dump(), indent=2))
    assert result.status == "EXECUTED"
    assert "Redeem Positions" in result.action

if __name__ == "__main__":
    asyncio.run(test_agent())
