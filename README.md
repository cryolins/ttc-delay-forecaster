# TTC Delay Forecaster
Hello! Welcome to my TTC Delay Forecaster project. I started this project as I wanted to analyze some data about what factors influence bus delays in Toronto. I quite like exploring geospatial data and I thought it would be fun to fit it to some ML models!

Currently, there are 3 major versions of the model available in this repository at `/pysrc/models`:

 1. The V1 model was trained with the TTC's Min Gap data column included as a feature. The V1 model performed a 35% improvement over linear baseline (5.1mins->3.3mins). However, Min Gap was dropped in later versions as it was found to be highly correlated with Min Delay since the gap seems to be calculated from delay time.
 2. The V2 model was trained without the Min Gap feature. With such a heavily relied on feature dropped, model performance significantly worsened (3.3mins->14mins mean absolute error), and so logarithmic scaling was also applied due to extra long delay times (hundreds of minutes) to improve performance to ~10mins MAE.
 3. For V3 models, extra long delay times over an hour was dropped from the dataset (<3% of data), as forecasting priorities shifted to shorter delays in less extreme circumstances. V3-1 uses better cleaned and processed data, resulting in slightly better accuracy (4.02mins MAE, ~14% improvement over linear baseline), and is the model that is planned to be deployed (as of 2026-05-06).

I will probably revamp this README as I get further along the project, but thanks for stopping by!
