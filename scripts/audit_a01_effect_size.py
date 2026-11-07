#!/usr/bin/env python3
"""Published-correlation arithmetic and an ideal Gaussian score fixture only."""

from __future__ import annotations

import json
import math
from statistics import NormalDist


def partial_correlation(r_xy: float, r_xz: float, r_yz: float) -> float:
    return (r_xy - r_xz * r_yz) / math.sqrt((1 - r_xz**2) * (1 - r_yz**2))


def gaussian_information(r: float) -> float:
    return -0.5 * math.log1p(-r**2)


def known_parameter_score_power(r: float, n: int, alpha: float = 0.05) -> float:
    if r == 0:
        raise ValueError("identical known models give zero score variance; the normal approximation is undefined")
    normal = NormalDist()
    return normal.cdf(gaussian_information(r) * math.sqrt(n) / abs(r) - normal.inv_cdf(1 - alpha))


def main() -> None:
    r = partial_correlation(0.223, 0.282, 0.382)
    gain = gaussian_information(r)
    normal = NormalDist()
    print(json.dumps({
        "source": "Cannizzo & Mattei 1992, Table 4, printed p645, DOI 10.1086/172092",
        "source_correlations": {"duration_following_gap": 0.223, "duration_preceding_gap": 0.282,
                                "adjacent_gaps": 0.382},
        "partial_r": r,
        "ideal_gaussian_gain_nats": gain,
        "n_for_2n_gain_equal_8": 4 / gain,
        "known_parameter_score_difference_variance": r**2,
        "ideal_iid_score_fixture": [{"n": n, "two_n_gain": 2 * n * gain,
                                     "normal_approx_one_sided_power_alpha_0_05": known_parameter_score_power(r, n)}
                                    for n in (55, 400, 470)],
        "score_fixture_continuous_n_for_power_0_8": ((normal.inv_cdf(0.95) + normal.inv_cdf(0.8)) * abs(r) / gain)**2,
        "assumptions": "known correct Gaussian models, iid forecasts; baseline Y~N(0,1), expanded Y|X~N(rX,1-r^2)",
        "scope": "conditional arithmetic illustration; not a prior bound, pipeline power calculation or estimate from real photometry",
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
