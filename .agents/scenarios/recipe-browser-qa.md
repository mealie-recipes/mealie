# Scenario: seeded recipe browser QA

Purpose: exercise a complete browser-only QA path with deterministic data.

```sh
.agents/hooks/resume
.agents/hooks/seed
.agents/hooks/qa
.agents/hooks/collect
```

Verify that the seeded “Agent QA Recipe” loads for the default administrator. Review
`.agents/artifacts/browser-qa/recipe.png`, `console.json`, `page-errors.json`, `network.json`, and
`network-failures.json`. Report failed requests and console/page errors even when the page looks
correct. Running the scenario again must reuse the recipe instead of creating another one.
