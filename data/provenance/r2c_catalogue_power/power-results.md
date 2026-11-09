# R2c power results

Score-level synthetic planning only. Rates have two-sided exact 95% binomial intervals; each row uses 2,000 independently seeded trials. Nominal gain refers to a perfect-marker individual-star oracle; achieved fitted gains are reported separately.

## Independent-observation core at nominal gain 0.010

| Test forecasts | Known-rule power | Fitted-rule power | Exact 95% interval, fitted | Fitted mean conditional gain |
|---:|---:|---:|---|---:|
| 400 | 0.4045 | 0.4125 | [0.3908, 0.4344] | 0.009037 |
| 800 | 0.6180 | 0.6005 | [0.5786, 0.6221] | 0.009069 |
| 1100 | 0.7515 | 0.7110 | [0.6906, 0.7308] | 0.009034 |
| 1600 | 0.8590 | 0.8005 | [0.7823, 0.8178] | 0.009010 |
| 2200 | 0.9445 | 0.8630 | [0.8471, 0.8778] | 0.009027 |

## One-at-a-time robustness at nominal gain 0.010, N=1,100

| Case | Fitted power | Exact 95% interval | Overall 90% coverage | Positive-coefficient coverage | Identity fraction |
|---|---:|---|---:|---:|---:|
| stars3 | 0.6580 | [0.6367, 0.6788] | 0.8910 | 0.8906 | 0.0040 |
| stars7 | 0.7040 | [0.6835, 0.7239] | 0.8880 | 0.8878 | 0.0015 |
| development40 | 0.6405 | [0.6190, 0.6616] | 0.8955 | 0.8925 | 0.0280 |
| reliability08 | 0.6245 | [0.6029, 0.6458] | 0.9025 | 0.9023 | 0.0025 |
| heterogeneous05 | 0.5760 | [0.5540, 0.5978] | 0.9145 | 0.9142 | 0.0035 |
| correlated-blocks | 0.3945 | [0.3730, 0.4163] | 0.9005 | 0.8995 | 0.0095 |
| serial-blocks | 0.4500 | [0.4280, 0.4721] | 0.7295 | 0.7265 | 0.0110 |
| imbalanced | 0.6450 | [0.6236, 0.6660] | 0.8975 | 0.8974 | 0.0010 |

## No-effect generator at N=1,100

| Case | Rejection rate | Exact 95% interval | Overall 90% coverage | Positive-coefficient coverage | Identity fraction |
|---|---:|---|---:|---:|---:|
| core-g0.0000-n1100 | 0.0095 | [0.0057, 0.0148] | 0.9435 | 0.8878 | 0.4965 |
| null-correlated-blocks | 0.0150 | [0.0101, 0.0213] | 0.9490 | 0.9004 | 0.4880 |
| null-serial-blocks | 0.0520 | [0.0427, 0.0627] | 0.8610 | 0.7277 | 0.4895 |

Known-rule null coefficients are exactly zero: rejection rate zero and 100% interval coverage by identity, with no nonidentity denominator. That is not evidence of calibrated 90% uncertainty. The serial-block scenario deliberately violates independence between the proposed star-by-block clusters. Its apparent power is inflated by intervals that are too narrow.

The study does not simulate extraction, missed events, censoring, state-filter estimation, observer behaviour or uncertain class qualification. It assumes known population mark standardization and unit working predictive variance. Effect heterogeneity varies positive amplitudes only; negative or zero-effect subpopulations are not modelled. Neither these rates nor catalogue metadata certify the eventual multi-star test.
