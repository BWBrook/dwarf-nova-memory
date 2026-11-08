"""Bounded A10c synthetic streams.

This module adds the slow shared-state stress family and the independent
evaluation reference stream.  The established A10b stream remains the source
of truth for its existing cases; no real-era cadence is read here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Any, Mapping, Sequence

from . import injection_truth as _timing
from . import injection_truth_v2 as _v2
from .forecast_experiment import CASES, ERAS, crop_stratum, source_strata
from .injection_observe import simulate_rows
from .joint_benchmark import generate_observations
from .phase_cadence import PhaseCadenceConfig, phase_aligned_schedule
from .x4_benchmark import seed_for


SLOW_CASES = ("slow_090", "slow_098")
_SLOW_PHI = {"slow_090": 0.90, "slow_098": 0.98}
_SLOW_LOADING_SQUARED = 0.13
_SLOW_LOADING = math.sqrt(_SLOW_LOADING_SQUARED)
_SLOW_PROCESS = "newARsharedGaussianstate"


@dataclass(frozen=True)
class _Block:
    index: int
    source: Mapping[str, Any]
    synthetic_start: float
    synthetic_stop: float


def _block_plan(inputs: Mapping[str, Any]) -> tuple[_Block, ...]:
    strata = source_strata(inputs)
    sources = [strata[e] for e in ERAS] * 2
    first = strata[ERAS[0]]
    sources.append(crop_stratum(first, first["start"], first["start"] + 8 * 365.25))
    cursor = 1000.5
    result = []
    for index, source in enumerate(sources):
        shift = cursor - float(source["start"])
        if abs(shift - round(shift)) > 1e-7:
            raise ValueError("translation must preserve native-JD night bins")
        shift = int(round(shift))
        stop = float(source["stop"]) + shift
        result.append(_Block(index, source, cursor, stop))
        cursor = math.ceil(stop + 30 - 0.5) + 0.5
    return tuple(result)


def _slow_latent_draws(
    count: int, phi: float, seed: int, *, burn_in: int = 1000
) -> tuple[tuple[float, float], ...]:
    """Draw (duration, gap) Gaussian copula scores for the shared state.

    The returned scores have marginal standard-normal distributions.  Their
    contemporaneous correlation is the declared ``lambda**2``; the state is
    the only serial term and the two innovations are independent.
    """
    if count < 0:
        raise ValueError("count must be non-negative")
    if not math.isfinite(phi) or not 0.0 < phi < 1.0:
        raise ValueError("phi must lie strictly between zero and one")
    if burn_in < 0:
        raise ValueError("burn_in must be non-negative")
    rng = random.Random(_timing._stream_seed(seed, "slow-shared-state"))
    state = 0.0
    for _ in range(burn_in):
        state = phi * state + math.sqrt(1.0 - phi * phi) * rng.gauss(0.0, 1.0)
    draws = []
    for _ in range(count):
        state = phi * state + math.sqrt(1.0 - phi * phi) * rng.gauss(0.0, 1.0)
        duration = _SLOW_LOADING * state + math.sqrt(1.0 - _SLOW_LOADING_SQUARED) * rng.gauss(0.0, 1.0)
        gap = _SLOW_LOADING * state + math.sqrt(1.0 - _SLOW_LOADING_SQUARED) * rng.gauss(0.0, 1.0)
        draws.append((duration, gap))
    return tuple(draws)


def _slow_timing(
    durations: Sequence[float],
    gaps: Sequence[float],
    start: float,
    stop: float,
    seed: int,
    phi: float,
) -> tuple[list[tuple[float, float, float, float, float, float]], dict[str, Any]]:
    """Generate renewal timings with the frozen shared-state construction."""
    duration_values = _timing._validated_marginal(durations, "duration_marginal")
    gap_values = _timing._validated_marginal(gaps, "gap_marginal")
    start_value, stop_value = float(start), float(stop)
    if not math.isfinite(start_value) or not math.isfinite(stop_value) or stop_value <= start_value:
        raise ValueError("stop must be finite and greater than start")
    latent_rng = random.Random(_timing._stream_seed(seed, "slow-shared-state"))
    state = 0.0
    for _ in range(1000):
        state = phi * state + math.sqrt(1.0 - phi * phi) * latent_rng.gauss(0.0, 1.0)
    phase_rng = random.Random(_timing._stream_seed(seed, "phase"))
    phase = phase_rng.random() or 0.5
    draws: list[tuple[float, float, float, float, float, float]] = []
    onset = None
    previous_end = None
    previous_gap = None
    for index in range(1_000_000):
        state = phi * state + math.sqrt(1.0 - phi * phi) * latent_rng.gauss(0.0, 1.0)
        latent_duration = _SLOW_LOADING * state + math.sqrt(1.0 - _SLOW_LOADING_SQUARED) * latent_rng.gauss(0.0, 1.0)
        latent_gap = _SLOW_LOADING * state + math.sqrt(1.0 - _SLOW_LOADING_SQUARED) * latent_rng.gauss(0.0, 1.0)
        duration = _timing._empirical_quantile(duration_values, latent_duration)
        gap = _timing._empirical_quantile(gap_values, latent_gap)
        if index == 0:
            onset = start_value - 1000.0 - phase * (duration + gap)
        else:
            assert previous_end is not None and previous_gap is not None
            onset = previous_end + previous_gap
        end = onset + duration
        if onset >= start_value - (max(duration_values) + max(gap_values)):
            draws.append((onset, end, duration, gap, latent_duration, latent_gap))
        if onset > stop_value:
            break
        previous_end = end
        previous_gap = gap
    else:
        raise RuntimeError("slow-state renewal did not reach the stream stop")
    diagnostics = {
        "slow_state": _SLOW_PROCESS,
        "slow_state_phi": phi,
        "slow_state_loading": _SLOW_LOADING,
        "slow_state_loading_squared": _SLOW_LOADING_SQUARED,
        "slow_state_marginal_copula_correlation": _SLOW_LOADING_SQUARED,
        "slow_state_marginal_rank_correlation": _SLOW_LOADING_SQUARED,
        "slow_state_direct_duration_to_gap": 0.0,
        "slow_state_serial_terms": "shared state only",
        "slow_state_burn_in_cycles": 1000,
        "calendar_warmup_days": 1000.0,
        "random_phase": phase,
    }
    return draws, diagnostics


def _slow_history(inputs, configuration, source, seed, case):
    if case not in SLOW_CASES:
        raise ValueError("unknown slow-state case")
    if configuration.get("family") != "v2":
        raise ValueError("slow-state cases require the v2 waveform family")
    phi = _SLOW_PHI[case]
    timing, diagnostics = _slow_timing(
        inputs["durations"], inputs["gaps"], source["start"], source["stop"], seed, phi
    )
    base_events = _timing._build_events(timing, min(float(x) for x in inputs["gaps"]),
                                        random.Random(_timing._stream_seed(seed, "shape")))
    shape = _v2.ShapeConfig(**configuration["shape_config"])
    shape_rng = random.Random(_v2._shape_seed(seed))
    events = tuple(_v2._smooth_event(event, shape_rng, shape) for event in base_events)
    diagnostics = {**diagnostics, "shape_family": "asymmetric_half_gaussian_flat_peak_v2"}
    return _v2.TruthSeries("null", float(source["start"]), float(source["stop"]), int(seed),
                           False, events, diagnostics, shape.quiet_magnitude)


def _slow_observed_block(inputs, configuration, source, seed, case):
    history = _slow_history(inputs, configuration, source, seed, case)
    schedule, cadence = phase_aligned_schedule(
        source["days"], inputs["phase_profiles"], history, source["start"], source["stop"],
        seed_for(seed, "cadence"), config=PhaseCadenceConfig(**configuration["cadence_config"])
    )
    model = {
        who: {**params, "sigma": params["sigma"] * configuration["noise_multiplier"]}
        for who, params in inputs["brightness_model"].items()
    }
    rows = simulate_rows(
        schedule, history.evaluate([float(r["JD"]) for r in schedule]), model,
        seed_for(seed, "measurement")
    )
    truth = [dict(event) for event in _v2.truth_catalogue(history, 10.0)
             if source["start"] <= event["onset"] and event["end"] < source["stop"]]
    return rows, truth, {"cadence": {k: v for k, v in cadence.items() if k != "events"},
                         "case": case, "slow_state": history.diagnostics}


def _render_blocks(inputs, configuration, case, replicate, namespace, blocks):
    rows, truth, metadata = [], [], []
    process_label = case if case in ("structured", "alternative") + SLOW_CASES else "null"
    offset_seed = seed_for(namespace, configuration["pair_id"], replicate, "observer-offsets")
    for block in blocks:
        seed = seed_for(namespace, configuration["pair_id"], process_label, replicate,
                        "block", block.index)
        if case in SLOW_CASES:
            observed, events, info = _slow_observed_block(inputs, configuration, block.source, seed, case)
        else:
            observed, events, info = _old_observed_block(
                inputs, configuration, block.source, seed, case, offset_seed
            )
        shift = block.synthetic_start - float(block.source["start"])
        shift = int(round(shift))
        for row in observed:
            rows.append({**row, "JD": str(float(row["JD"]) + shift),
                         "obsID": f"synthetic-block-{block.index}-{row.get('obsID', '')}"})
        for event in events:
            truth.append({**event, "id": f"block-{block.index}-{event['id']}", "block": block.index,
                          **{key: event[key] + shift for key in ("onset", "end", "peak_t")}})
        metadata.append({"block": block.index, "source_era": block.source["stratum"], "seed": seed,
                         "source_start": block.source["start"], "source_stop": block.source["stop"],
                         "synthetic_start": block.synthetic_start, "synthetic_stop": block.synthetic_stop,
                         **info})
    rows.sort(key=lambda row: float(row["JD"]))
    truth.sort(key=lambda event: event["onset"])
    return rows, truth, metadata


def _old_observed_block(inputs, configuration, source, seed, case, offset_seed):
    process = case if case in ("structured", "alternative") else "null"
    actual_inputs = inputs
    if case == "offset":
        actual_inputs = {**inputs, "brightness_model": {
            who: {**params, "offset": params["offset"] + random.Random(
                seed_for(offset_seed, "persistent-observer", who)).gauss(0, .2)}
            for who, params in inputs["brightness_model"].items()}}
    rows, history, _generator, cadence, contamination = generate_observations(
        actual_inputs, configuration, source, seed, process=process, gross=case == "gross"
    )
    truth = [dict(event) for event in _generator.truth_catalogue(history, 10.0)
              if source["start"] <= event["onset"] and event["end"] < source["stop"]]
    return rows, truth, {"cadence": {k: v for k, v in cadence.items() if k != "events"},
                         "contamination": contamination, "case": case}


def development_stream(inputs, configuration, case, replicate, base):
    """Return one seven-block development stream under the A10b timeline."""
    if case not in CASES + SLOW_CASES:
        raise ValueError(f"unknown development case: {case}")
    if case in SLOW_CASES and configuration.get("family") != "v2":
        raise ValueError("slow-state cases are available only for v2")
    if case in CASES:
        from .forecast_experiment import chronological_stream
        rows, truth, metadata = chronological_stream(inputs, configuration, case, replicate, base)
        metadata = {**metadata, "eval_start": metadata["blocks"][3]["synthetic_start"]}
        return rows, truth, metadata
    blocks = _block_plan(inputs)
    rows, truth, block_metadata = _render_blocks(
        inputs, configuration, case, replicate, base, blocks
    )
    train_cutoff = block_metadata[2]["synthetic_stop"]
    return rows, truth, {
        "training_cutoff": train_cutoff,
        "eval_start": block_metadata[3]["synthetic_start"],
        "stop": block_metadata[-1]["synthetic_stop"],
        "blocks": block_metadata,
        "adaptive": None,
        "time_basis": "artificial relative days; integer translations of pre1960 patterns",
        "slow_state": {"case": case, "phi": _SLOW_PHI[case],
                       "loading_squared": _SLOW_LOADING_SQUARED},
    }


def reference_stream(inputs, configuration, case, replicate, base, reference_id,
                     training_context, metadata=None):
    """Replay the four-block evaluation pattern with independent random streams."""
    if case not in ("null", "alternative"):
        raise ValueError("reference_stream supports only null and alternative")
    if not isinstance(training_context, Sequence) or isinstance(training_context, (str, bytes)):
        raise ValueError("training_context must be a sequence of rows")
    all_blocks = _block_plan(inputs)
    blocks = all_blocks[3:]
    expected_metadata = {
        "training_cutoff": all_blocks[2].synthetic_stop,
        "eval_start": blocks[0].synthetic_start,
        "stop": blocks[-1].synthetic_stop,
    }
    if metadata is not None:
        for key, expected in expected_metadata.items():
            if key not in metadata:
                raise ValueError(f"reference metadata lacks {key}")
            try:
                observed = float(metadata[key])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"reference metadata {key} must be finite numeric") from exc
            if not math.isfinite(observed) or observed != expected:
                raise ValueError(f"reference metadata {key} does not match the artificial timeline")
    reference_seed_namespace = f"{base}|reference|{reference_id}"
    rows, truth, block_metadata = _render_blocks(
        inputs, configuration, case, replicate, reference_seed_namespace, blocks
    )
    block_metadata = [{**block, "reference_id": str(reference_id)} for block in block_metadata]
    cutoff = all_blocks[2].synthetic_stop
    context = []
    for index, row in enumerate(training_context):
        if not isinstance(row, Mapping):
            raise ValueError(f"training_context[{index}] must be a mapping")
        if "JD" not in row:
            raise ValueError(f"training_context[{index}] lacks JD")
        jd = float(row["JD"])
        if not math.isfinite(jd):
            raise ValueError("training_context JD must be finite")
        if jd <= cutoff and jd >= cutoff - 400.0:
            context.append(dict(row))
    rows = context + [
        {**row, "obsID": f"reference-{reference_id}-block-{block['block']}-{row.get('obsID', '')}"}
        for block in block_metadata
        for row in rows
        if float(row["JD"]) >= block["synthetic_start"]
        and float(row["JD"]) < block["synthetic_stop"]
    ]
    rows.sort(key=lambda row: float(row["JD"]))
    obs_ids = [str(row.get("obsID", "")) for row in rows]
    if len(obs_ids) != len(set(obs_ids)):
        raise ValueError("reference stream produced duplicate observation IDs")
    for event in truth:
        event["id"] = f"ref-{reference_id}-{event['id']}"
        event["reference_id"] = str(reference_id)
    if len({str(event["id"]) for event in truth}) != len(truth):
        raise ValueError("reference stream produced duplicate truth IDs")
    return rows, truth, {
        "training_cutoff": cutoff,
        "eval_start": block_metadata[0]["synthetic_start"],
        "stop": block_metadata[-1]["synthetic_stop"],
        "blocks": block_metadata,
        "reference_id": str(reference_id),
        "reference_seed_namespace": reference_seed_namespace,
        "training_context_window": [cutoff - 400.0, cutoff],
        "training_context_rows": len(context),
        "issuance_filter": {"start": block_metadata[0]["synthetic_start"],
                             "rule": "filter only evaluation issuances by issue_time"},
        "source_metadata": metadata,
    }


__all__ = ["development_stream", "reference_stream", "SLOW_CASES", "_slow_latent_draws"]
