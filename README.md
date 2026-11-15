# theme-faithful
Faithfulness eval for feedback-clustering agents: every theme summary must be supported by
its member verbatims, every verbatim must be assigned to exactly one theme, and no verbatim
may contradict its theme. Gates in `cases.json`; any agent callable via
`python run.py my_agent.py` (exposing `run(verbatims)` returning themes with summaries and
member ids). `python run.py` runs the naive demo agent, which the eval blocks.
