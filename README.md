# Marketing Data Platform

This project tells the story of a marketing team that wants one clear view of performance across multiple channels, without spending hours stitching reports together by hand. Instead of jumping between disconnected exports, the pipeline brings everything into one flow: generate or ingest campaign data, clean it, store it in a database, run analysis queries, and then publish a dashboard you can actually use to make decisions.

At a high level, it starts with campaign-level daily metrics from five channels: `Search_Google`, `Social_FB`, `Social_IG`, `Display_Programmatic`, and `Email_Newsletter`. Each row tracks impressions, clicks, cost, and conversions. From there, the cleaning step standardizes types, removes nulls and duplicates, and computes performance metrics that matter in real marketing conversations: CTR (how often people click after seeing an ad), CPC (how much each click costs), and CPA (how much each conversion costs).

Once the data is clean, it gets loaded into a local SQLite database so analysis is fast and repeatable. SQL then answers practical questions: where most of the budget is going, which channel gets the best click-through rate, how clicks move over time, and which campaign gives the most efficient acquisition cost. In this dataset, `Search_Google` comes out as the highest total cost channel at about `$164K`, it also leads average CTR at `3.96%`, and `Email_Newsletter` has the lowest average CPA at `$8.11`.

The dashboard layer is built with Plotly and outputs an interactive HTML file. It includes KPI cards for average CTR and CPA, a line chart for click trend over time, and a bar chart that compares spend by campaign. It is simple, but it gives a quick executive read of both scale and efficiency in one place.

The stack is intentionally lightweight: Python orchestrates everything, pandas handles transformations, SQLite stores the analytical table, SQL drives business questions, and Plotly handles presentation. The point is not just to make a chart, but to show an end-to-end analytics workflow that can be rerun, extended, and productionized.

To run the whole pipeline, install dependencies and execute one command:

```bash
python3 -m pip install pandas numpy plotly
python3 scripts/run_pipeline.py
```

That command runs the full chain from data generation through dashboard creation. If you prefer, you can also run each script separately from the `scripts/` directory in the same order.

What this project really demonstrates is how much cleaner decision-making becomes when the data flow is standardized. Instead of one-off analysis, you get a repeatable pipeline that makes channel performance easier to compare, easier to explain, and easier to act on.
