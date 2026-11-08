"""Candidate-blind observations for the A04i joint benchmark."""

import random

from dnmem.injection_observe import simulate_rows
from dnmem.injection_truth import LatentCoefficients
from dnmem.x4_benchmark import gross_errors, seed_for


def generate_observations(inputs, configuration, stratum, seed, process="null", *, offset=False, gross=False):
    family = configuration["family"]
    if family == "v2":
        from dnmem import injection_truth_v2 as generator
    elif family == "v4":
        from dnmem import injection_truth_v4 as generator
    else:
        raise ValueError("unknown A04i waveform family")
    if process not in ("null", "structured", "alternative"):
        raise ValueError("unknown timing process")
    kwargs = {"shape_config": generator.ShapeConfig(**configuration["shape_config"]),
              "process": "alternative" if process != "null" else "null"}
    if process == "structured":
        kwargs["coefficients"] = LatentCoefficients(partial_duration_gap=0)
    start, stop = float(stratum["start"]), float(stratum["stop"])
    history = generator.generate_events(inputs["durations"], inputs["gaps"], start, stop,
                                        seed_for(seed, "truth"), **kwargs)
    if configuration["phase"] == "phase":
        from dnmem.phase_cadence import PhaseCadenceConfig, phase_aligned_schedule
        schedule, cadence = phase_aligned_schedule(
            stratum["days"], inputs["phase_profiles"], history, start, stop,
            seed_for(seed, "cadence"), config=PhaseCadenceConfig(**configuration["cadence_config"]))
    elif configuration["phase"] == "random":
        schedule = stratum["schedule"]
        cadence = {"scope": "original schedule; no phase alignment", "no_match_fraction": 0.0}
    else:
        raise ValueError("unknown A04i cadence")
    model = {who: {**p, "sigma": p["sigma"] * configuration["noise_multiplier"]}
             for who, p in inputs["brightness_model"].items()}
    if offset:
        model = {who: {**p, "offset": p["offset"] + random.Random(
                        seed_for(seed, "offset", who)).gauss(0, .2)} for who, p in model.items()}
    rows = simulate_rows(schedule, generator.magnitudes_at(history, [float(r["JD"]) for r in schedule]),
                         model, seed_for(seed, "measurement"))
    contamination = {}
    if gross:
        rows, contamination = gross_errors(rows, generator.truth_catalogue(history, 10),
                                           seed_for(seed, "gross-errors"))
    return rows, history, generator, cadence, contamination
