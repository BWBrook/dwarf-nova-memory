# Independent R2 model-control score audit

Status: passed; tolerance 1e-09; 0 failures.

All nine histories: 6,480 evaluation base/marked scores agree within 2.49e-14; 3,240 paired gains within 4.88e-15. Aggregate means and MC SEs agree within 6.25e-17.

Independent direct Gaussian covariance conditioning replaces the candidate B2 Kalman recursion. B0/B1 transforms, missing-history conventions and mark scaling are reconstructed. SciPy lognormal density/survival/CDF scores verify all outcome kinds in retained training objectives (maximum objective error 1.71e-12).

There are 3,240 independent zero-counterfactual predictions and 2,220 exact saved zero/missing pairs. Routes and availability checks agree. Input hashes are in summary.json. No candidate scoring/prediction function was imported; no fit or simulation was run. This is a numerical audit of finite synthetic controls, not calibration or identification.
