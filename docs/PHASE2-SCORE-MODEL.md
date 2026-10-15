# Phase 2 – Score model (provisional)

This is an offline proposal, not a user-approved final product rule.

## Classic assessment

The default migration profile preserves the reference strict operators:

```text
good iff temperature > 10 °C
       and wind < 15 km/h
       and precipitation <= 0 mm
```

Missing any of those three values produces `unknown`, never a positive result.
The profile makes all three limits configurable. The historical dashboard wind
object bug is not reproduced: normalized wind is a scalar in km/h.

## Weighted score

The initial weights are:

| Factor | Weight | Curve |
|---|---:|---|
| temperature / feels-like fallback | 30 | 100 in ideal band, linear to 0 at acceptable limits |
| wind | 20 | 100 below configured limit, linear to 0 at 2.5× limit |
| gusts | 15 | 100 below configured limit, linear to 0 at 1.75× limit |
| precipitation amount | 20 | 100 at configured maximum, linear to 0 at 3 mm |
| precipitation probability | 10 | 100 below configured maximum, 0 at 100% |
| feels-like | 5 | ideal/acceptable temperature curve |

The implementation returns factor scores and used weight. Missing factors are
excluded from the numerator but the result is multiplied by the fraction of
available weight. That makes incomplete data conservative: it cannot yield a
false 100. Quality is `partial` when any configured factor is missing.

The provisional status is `good` at score >= 70 only when quality is good;
partial data is `unknown`, even if its numeric score is retained for diagnosis.
The classic result and score are intentionally separate and may disagree.

## Window aggregation

Every forecast slot intersecting a ride window is assessed. The combined score
is the minimum slot score and the combined status is only `good` if every slot
is good. A missing interval makes the window unknown. No interpolation is
performed.

## Approval gate

Before production use, confirm the weights, acceptable bands, rain semantics,
partial-data policy and score threshold with the owner. These values remain
documented as provisional until that gate.
