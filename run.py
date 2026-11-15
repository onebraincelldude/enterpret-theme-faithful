"""theme-faithful: faithfulness eval for feedback-clustering agents.

The agent receives raw verbatims and returns themes: {name, summary, members[]}.
Checks per case:
  1. Support: each theme summary must share at least one support term with its theme spec
     AND every must_include verbatim must be a member (the summary's evidence base).
  2. Assignment: no must_not_include verbatim may be a member of that theme.
  3. Coverage: every verbatim must be assigned to exactly one theme.
Exit code 1 = eval blocks the agent.
"""
import json, sys

def load_agent(path):
    if not path:
        return demo_agent
    import importlib.util
    s = importlib.util.spec_from_file_location("agent", path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m.run

def demo_agent(verbatims):
    """Naive agent: misclusters a dashboard verbatim under the export-bug theme, writes an
    unsupported summary claim, and drops one verbatim entirely."""
    return [
        {"name": "csv-export-broken", "summary": "CSV export is broken and slow dashboards make it worse", "members": ["v1", "v3", "v2"]},
        {"name": "dark-mode-request", "summary": "Users want dark mode for night work", "members": ["v5", "v6"]}
    ]

def main():
    spec = json.load(open("cases.json"))
    agent = load_agent(sys.argv[1] if len(sys.argv) > 1 else None)
    unsupported = misassigned = 0
    for c in spec["cases"]:
        verbatims = c["verbatims"]
        themes = agent(verbatims)
        by_name = {t["name"]: t for t in themes}
        assigned = [m for t in themes for m in t["members"]]
        for name, ts in c["themes"].items():
            t = by_name.get(name)
            if not t:
                unsupported += 1
                print(f"[{c['id']}/{name}] THEME MISSING - UNSUPPORTED")
                continue
            summary = t["summary"].lower()
            members = set(t["members"])
            has_term = any(term in summary for term in ts["support_terms"])
            missing_evidence = [v for v in ts["must_include"] if v not in members]
            if not has_term or missing_evidence:
                unsupported += 1
                print(f"[{c['id']}/{name}] UNSUPPORTED summary (term match: {has_term}, missing evidence: {missing_evidence})")
            else:
                print(f"[{c['id']}/{name}] summary supported")
            bad_members = [v for v in ts["must_not_include"] if v in members]
            if bad_members:
                misassigned += len(bad_members)
                print(f"[{c['id']}/{name}] MISASSIGNED verbatims: {bad_members}")
        all_ids = [v["id"] for v in verbatims]
        dupes = {m for m in assigned if assigned.count(m) > 1}
        missing = [i for i in all_ids if i not in assigned]
        coverage = len([i for i in all_ids if i in assigned]) / len(all_ids)
        if dupes or missing:
            print(f"[{c['id']}] COVERAGE gaps: unassigned {missing or '[]'} double-assigned {sorted(dupes) or '[]'}")
    gates = spec["gates"]
    ok = unsupported <= gates["max_unsupported_summaries"] and misassigned <= gates["max_misassigned"] and coverage >= gates["min_coverage"]
    print(f"\nunsupported summaries {unsupported} (gate {gates['max_unsupported_summaries']}), misassigned {misassigned} (gate {gates['max_misassigned']}), coverage {coverage:.2f} (gate {gates['min_coverage']})")
    print("AGENT:", "PASS" if ok else "BLOCKED")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
