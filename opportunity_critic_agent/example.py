from opportunity_critic import (
    CurrentProposal,
    Evidence,
    InvestmentCandidate,
    OpportunityCriticAgent,
)


def main() -> None:
    current = InvestmentCandidate(
        ticker="NEXA",
        name="Nexa Renewables",
        expected_return=0.18,
        downside_risk=0.12,
        conviction=0.62,
        liquidity_score=0.72,
        catalyst_score=0.58,
        valuation_score=0.54,
        evidence=(
            Evidence("quarterly results", "margin expansion is improving", "mixed"),
            Evidence("technical analyst", "breakout confirmed on volume", "mixed"),
        ),
        notes="Clean energy momentum idea.",
    )
    proposal = CurrentProposal(
        action="buy",
        candidate=current,
        thesis="Buy clean energy momentum with improving margins.",
    )
    alternatives = [
        InvestmentCandidate(
            ticker="TPOW",
            name="Tata Power",
            expected_return=0.24,
            downside_risk=0.09,
            conviction=0.78,
            liquidity_score=0.86,
            catalyst_score=0.76,
            valuation_score=0.68,
            evidence=(
                Evidence("fundamental analyst", "earnings revisions are positive", "strong"),
                Evidence("macro analyst", "power demand tailwinds remain supportive", "strong"),
                Evidence("risk analyst", "drawdown profile is below current proposal", "mixed"),
            ),
            notes="Cleaner risk-adjusted power-sector exposure.",
        ),
        InvestmentCandidate(
            ticker="AREN",
            name="Adani Green",
            expected_return=0.29,
            downside_risk=0.24,
            conviction=0.51,
            liquidity_score=0.70,
            catalyst_score=0.82,
            valuation_score=0.39,
            evidence=(
                Evidence("sentiment analyst", "strong retail momentum", "mixed"),
                Evidence("risk analyst", "high volatility and valuation risk", "weak"),
            ),
            notes="Higher upside but materially higher drawdown risk.",
        ),
    ]

    critique = OpportunityCriticAgent().critique(proposal, alternatives)
    print(critique.committee_message)
    print(f"Verdict: {critique.verdict.value}")
    print("Debate questions:")
    for question in critique.questions_for_debate:
        print(f"- {question}")


if __name__ == "__main__":
    main()
