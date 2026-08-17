# Normalized branch audit

The final repository has one published branch:

| Branch | Role | Final state |
| --- | --- | --- |
| <code>main</code> | Canonical paper/source pins, independent audit, retained full-scale artifacts, tests, and publication gate | Default and only public branch |

The former repository also exposed only <code>main</code>. No branch carried a
distinct implementation or result. There are no experiment, author-code,
queue, or <code>orx/</code> branches.

All reachable commits use:

    MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>

The final-state verifier checks the live remote branch set, default branch,
canonical history identity, and stale-ref hygiene.
