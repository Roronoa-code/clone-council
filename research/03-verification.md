# Verification record

Recorded 2026-09-22. **Offline engineering validation, not a live multi-model evaluation.** No API key or subscription model request was used in this build environment.

## Executed locally

Environment: Linux, Python 3.13.5. The four test modules were run separately after implementation changes and all passed:

| Command | Result |
|---|---:|
| `python -m unittest discover -s tests -p test_schema_context.py -v` | 18 passed |
| `python -m unittest discover -s tests -p test_engine.py -v` | 14 passed |
| `python -m unittest discover -s tests -p test_providers.py -v` | 18 passed |
| `python -m unittest discover -s tests -p test_cli_install_report.py -v` | 12 passed |
| **Total** | **62 passed** |

The suite covers strict JSON/schema validation; unknown/duplicate evidence IDs; factual-claim citation requirements; proceed/high-evidence gates; independent first-pass inputs; identity-reduced review; own-answer exclusion in deep audits; all 1/3/5/7-stage depths; mixed routing; bounded retries; permanent failures; cumulative budgets; resume; changed brief/configuration/result rejection; exclusive locks; installation conflict/backup behaviour; recursive-run prevention; and escaped static reports.

Provider tests include **real subprocesses running explicitly named offline fixtures**, not real Codex/Claude executables. They verify stdin/Unicode/metacharacter handling, JSONL and JSON-envelope parsing, zero-exit error envelopes, subscription-auth recognition/rejection, required safety arguments, API/cloud environment stripping, Windows npm-shim resolution, output limits, timeout/cancellation, and Linux child-process-group cleanup. Windows-specific branches are not thereby proven on a real Windows host.

One early process-tree test used an unrealistically short startup deadline in this environment and failed before the child PID file existed. It was replaced with a readiness-synchronised cancellation test, then passed. One combined suite attempt exceeded the surrounding execution tool's time limit; module-level reruns above are the completed results, not an invented all-at-once pass.

## Executed end-to-end and packaging checks

- `python -m council demo`: completed independent opinions, audit, chair, report generation and private checkpoint creation using synthetic fixture data.
- `python -m council resume <completed-demo>`: validated and reused all five completed stages, with no additional invocations.
- Deep-mode demo: completed all seven stages; each peer audit excludes its own original candidate.
- `python -m pip wheel --no-deps --no-build-isolation .`: built `mani_council-0.1.0-py3-none-any.whl` successfully.
- Installed that wheel into a separate target directory; from outside the source checkout, executed a seven-stage demo and installed both native skill resource sets successfully.
- Validated all seven synthetic evaluation briefs against the input contract. **No quality scores or live evaluation outcomes were manufactured.**
- Re-decoded all 1,209 video frames with the included research utility and exported only numerical frame/timing/luminance-change statistics, not the private source footage.

## Explicitly not verified here

`python -m council doctor --profile mixed` correctly reported that neither `codex` nor `claude` was installed in this environment. Therefore this record does **not** claim authenticated live Codex/Claude execution, Windows-native execution, account eligibility/quota, compatibility with every CLI version, correct real-world recommendations, or a measured improvement over one model.

The repository includes a Windows/Linux, Python 3.11/3.13 GitHub Actions matrix. Inspect the actual run before describing it as passed; a workflow file is not execution evidence. CI has no model credentials and does not upload private run artifacts.

## Local live acceptance check

On the owner's machine, using its existing official CLI subscription logins:

1. Run `council doctor --profile mixed`; both entries must report a recognised login. The probe itself makes no model request. Disable provider extra usage/top-ups separately when subscription-only spending is required.
2. Run one small `--profile codex --depth single --max-calls 2` decision and one `--profile claude --depth single --max-calls 2` decision, with a short non-sensitive evidence file.
3. Run the same brief with `--profile mixed --depth quick --max-calls 4`. Inspect provider/session/version metadata, all completed stages, evidence references and the final action.
4. Resume the completed run; invocation count must remain unchanged. Do not weaken flags, bypass nested-session safeguards, or introduce API billing when a compatibility check fails.

These are explicit future acceptance checks for the local installation, not steps claimed to have happened in this build environment.

## Clone experiment — 2026-09-23

The record above is preserved from upstream. This section records new work in `Roronoa-code/clone-council` only, not changes to the original Council repository.

### Exact baseline

Upstream `main` was pinned to `af5d94a16decad673b056d9156dabdedbec37f5f`. The clone baseline commit `6f6320b2cbba3118837250d951c791ec6450dde4`, preserved on `baseline/council-main`, has the same Git tree SHA: `7d4c0b1abeecf1655abd339cbafe918cd1185870`. This verifies tracked paths, modes and contents, not mirrored Git history, issues, secrets or repository settings.

The first temporary bootstrap push was rejected because its workflow token lacked permission to create `.github/workflows/ci.yml`. The connected GitHub tool copied that workflow; the runner then copied the remaining source without changing workflows. The connected tool removed the temporary bootstrap, and the resulting tree was verified identical. No permission restriction was weakened, no original-repository write was made, and no temporary bootstrap workflow remains in the baseline or implementation.

### Tested implementation

Code/test commit: `3b1ff5aaa518010108ac6c20b2fa95f962bb043f`.

[Completed CI run 35920308544](https://github.com/Roronoa-code/clone-council/actions/runs/35920308544) ran the unchanged Offline reliability workflow. All four job results and their build/test/smoke/clean-worktree steps were inspected and reported success:

| Matrix job | Job ID | Result |
|---|---:|---|
| Ubuntu / Python 3.11 | 107382269276 | success |
| Ubuntu / Python 3.13 | 107382269544 | success |
| Windows / Python 3.11 | 107382269716 | success |
| Windows / Python 3.13 | 107382269526 | success |

The suite contains the original 62 tests plus 15 new handoff-contract tests. Detailed logs inspected for Ubuntu 3.11 report `Ran 77 tests` / `OK`. Detailed Windows 3.13 logs report `Ran 77 tests` / `OK (skipped=1)`, with the existing Linux-only process-group inspection test skipped. The new handoff tests all passed in those logs; the other two matrix jobs also reported successful complete-suite steps.

All four jobs built and installed the package, ran the test suite, then ran the installed package from outside the checkout: a seven-stage synthetic deep demo, completed-run resume, and native-skill installation for both hosts. The inspected smoke logs show all seven validated stages reused on resume, without new provider invocations. The final tracked-worktree checks passed. These are GitHub-hosted checks, not a claim of a complete local checkout test run in the editing container; that container was used only for patch construction and syntax checks.

The patch changes one runtime file, `council/report.py`. It adds a reproducible decision/brief-bound handoff reference, preserves the full proposal and acceptance criteria, and exposes the identity in report.json. Tests cover content changes, JSON key ordering, run/protocol/profile separation, unchanged resume, preserved external receipts, all verdict authority warnings, evidence namespacing, original-state immutability and compatibility with existing selective context intake. Templates and the guide describe the external result/review loop. No prompts, decision schema, engine, provider routing, workflow, budget enforcement or packaged skill resources were changed.

This verification-only append was made after that CI run; it does not change the tested runtime or tests. The commit message skips redundant CI for this documentation record. Test evidence remains tied to the code/test commit above.

### Limits of this verification

No live Codex/Claude model was invoked, no local account/subscription compatibility was established, and no procurement, customer or trading experiment was conducted. The tests establish engineering behaviour, not superior decisions, revenue or a benefit over a complete manual handoff. The reference is a content fingerprint, not an approval signature or tamper-proof control. RESULT.md checking and project-state ownership remain with the external coordinator; there is no automatic receipt parser, autonomous project manager or new execution authority. The linked comparison procedure in `docs/project-review.md` must be evaluated separately before adding more architecture.
