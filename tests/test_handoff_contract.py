"""Offline contract continuity checks; no live model or business outcome claims."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from council.config import Config
from council.context import build_brief
from council.demo import BRIEF
from council.engine import Engine
from council.report import handoff, handoff_identity
from council.schema import validate_brief
from council.store import Store


class HandoffContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store.create(self.root / 'run', copy.deepcopy(BRIEF),
                                  Config(profile='demo'), 'origin-test')
        Engine(self.store).run()
        self.state = self.store.load()

    def test_preserves_every_existing_decision_boundary(self):
        output = handoff(self.state)
        decision = self.state['jobs']['chair']['data']
        for value in self.state['brief']['constraints']:
            self.assertIn(value, output)
        for key in ('action', 'metric', 'pass_threshold', 'fail_threshold', 'timebox', 'cost_ceiling'):
            self.assertIn(f'{key.replace("_", " ").capitalize()}: {decision["next_action"][key]}', output)
        for key in ('stop_conditions', 'revisit_when', 'uncertainties'):
            for value in decision[key]:
                self.assertIn(value, output)
        for dissent in decision['dissent']:
            for value in dissent.values():
                self.assertIn(value, output)
        for reason in decision['rationale']:
            self.assertIn(reason['text'], output)
        for value in decision['handoff']['do_not']:
            self.assertIn(value, output)
        self.assertIn(decision['handoff']['scope'], output)

    def test_criteria_ids_are_scoped_to_exact_reference(self):
        output = handoff(self.state)
        reference = handoff_identity(self.state)['reference']
        self.assertIn(reference, output)
        for index, criterion in enumerate(self.state['jobs']['chair']['data']['handoff']['acceptance_criteria'], 1):
            self.assertIn(f'- AC{index}: {criterion}', output)
        other = copy.deepcopy(self.state)
        other['run_id'] = 'different-run'
        self.assertNotEqual(reference, handoff_identity(other)['reference'])
        self.assertIn('<contract-reference>/AC1', output)

    def test_binding_changes_with_load_bearing_content(self):
        reference = handoff_identity(self.state)['reference']
        paths = [
            ('brief', 'question'), ('brief', 'mode'), ('brief', 'constraints', 0),
            ('brief', 'evidence', 0, 'excerpt'), ('brief', 'evidence', 0, 'source'),
            ('brief', 'evidence', 0, 'retrieved_at'), ('brief', 'evidence', 0, 'provenance'),
            ('jobs', 'chair', 'data', 'recommendation'),
            ('jobs', 'chair', 'data', 'handoff', 'scope'),
            ('jobs', 'chair', 'data', 'handoff', 'acceptance_criteria', 0),
            ('jobs', 'chair', 'data', 'handoff', 'do_not', 0),
            ('jobs', 'chair', 'data', 'stop_conditions', 0),
            ('jobs', 'chair', 'data', 'revisit_when', 0),
            ('jobs', 'chair', 'data', 'dissent', 0, 'view'),
        ]
        paths += [('jobs', 'chair', 'data', 'next_action', key) for key in
                  ('action', 'metric', 'pass_threshold', 'fail_threshold', 'timebox', 'cost_ceiling')]
        for path in paths:
            with self.subTest(path=path):
                changed = copy.deepcopy(self.state)
                node = changed
                for key in path[:-1]:
                    node = node[key]
                node[path[-1]] += ' changed'
                self.assertNotEqual(reference, handoff_identity(changed)['reference'])

    def test_binding_includes_protocol_and_profile(self):
        reference = handoff_identity(self.state)['reference']
        for path in [('protocol_version',), ('config', 'profile'), ('config', 'depth')]:
            with self.subTest(path=path):
                changed = copy.deepcopy(self.state)
                node = changed
                for key in path[:-1]:
                    node = node[key]
                node[path[-1]] = str(node[path[-1]]) + '-changed'
                self.assertNotEqual(reference, handoff_identity(changed)['reference'])

    def test_binding_is_independent_of_json_object_order(self):
        reordered = json.loads(json.dumps(self.state, ensure_ascii=False, sort_keys=True))
        self.assertEqual(handoff_identity(self.state), handoff_identity(reordered))
        self.assertEqual(handoff(self.state), handoff(reordered))

    def test_binding_ignores_runtime_bookkeeping(self):
        changed = copy.deepcopy(self.state)
        changed['calls_used'] += 1
        changed['budget_limit'] += 1
        changed['created_at'] = 'later'
        changed['attempts'].append({'note': 'runtime-only fixture'})
        changed['outcome'] = {'result': 'inconclusive'}
        self.assertEqual(handoff_identity(self.state), handoff_identity(changed))

    def test_report_json_exposes_independently_reproducible_identity(self):
        report = json.loads((self.store.path / 'report.json').read_text(encoding='utf-8'))
        identity = report['handoff_contract']
        self.assertEqual(identity, handoff_identity(self.state))
        def sha(value):
            return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                              separators=(',', ':')).encode('utf-8')).hexdigest()
        self.assertEqual(identity['brief_sha256'], sha(report['brief']))
        self.assertEqual(identity['decision_sha256'], sha(report['decision']))
        payload = {key: value for key, value in identity.items() if key != 'reference'}
        self.assertEqual(identity['reference'], f'origin-test:handoff-v1:{sha(payload)}')

    def test_resume_preserves_identity_and_external_result_receipt(self):
        before = (self.store.path / 'handoff.md').read_bytes()
        calls = self.state['calls_used']
        receipt = self.store.path / 'RESULT.md'
        contents = b'External receipt: not run. Preserve this file.\n'
        receipt.write_bytes(contents)
        Engine(self.store).run()
        self.assertEqual((self.store.path / 'handoff.md').read_bytes(), before)
        self.assertEqual(receipt.read_bytes(), contents)
        self.assertEqual(self.store.load()['calls_used'], calls)

    def test_rendering_does_not_mutate_original_state(self):
        before = copy.deepcopy(self.state)
        handoff_identity(self.state)
        handoff(self.state)
        self.assertEqual(self.state, before)

    def test_empty_optional_sections_do_not_imply_permission(self):
        state = copy.deepcopy(self.state)
        state['brief']['constraints'] = []
        state['brief']['evidence'] = []
        decision = state['jobs']['chair']['data']
        decision['dissent'] = []
        decision['uncertainties'] = []
        for reason in decision['rationale']:
            reason['evidence_ids'] = []
        output = handoff(state)
        self.assertIn('No constraints recorded. This does not grant permission or an allowance.', output)
        self.assertIn('No external evidence was supplied.', output)
        self.assertIn('Agreement is not independent corroboration.', output)
        self.assertIn('None recorded; this is not evidence that none exist.', output)

    def test_synthetic_and_live_renderings_keep_authority_warning(self):
        demo_output = handoff(self.state)
        self.assertIn('SYNTHETIC DEMO', demo_output)
        # Rendering-only fixture: changing this field does NOT simulate a live run.
        live_state = copy.deepcopy(self.state)
        live_state['config']['profile'] = 'codex'
        live_output = handoff(live_state)
        self.assertNotIn('SYNTHETIC DEMO', live_output)
        for output in (demo_output, live_output):
            self.assertIn('PROPOSAL ONLY', output)
            self.assertIn('not approval, a signature or independent verification', output)
            self.assertIn('separate owner authorization', output)
            self.assertIn('not measured results, an authorized budget', output)

    def test_single_agent_rendering_is_not_labelled_council_review(self):
        state = copy.deepcopy(self.state)
        state['config']['depth'] = 'single'
        self.assertIn('Single-agent baseline, not a multi-agent council.', handoff(state))

    def test_stop_and_defer_verdicts_do_not_become_approvals(self):
        for verdict in ('stop', 'defer', 'revise', 'test', 'proceed'):
            with self.subTest(verdict=verdict):
                state = copy.deepcopy(self.state)
                state['jobs']['chair']['data']['decision'] = verdict
                output = handoff(state)
                self.assertIn(f'Decision: {verdict}', output)
                self.assertIn('PROPOSAL ONLY', output)
                self.assertIn('Missing authorization or an unresolved conflict means stop', output)

    def test_evidence_is_run_qualified_without_copying_full_excerpts(self):
        state = copy.deepcopy(self.state)
        state['brief']['evidence'][0]['excerpt'] = 'PRIVATE_RAW_EXCERPT_SENTINEL'
        output = handoff(state)
        for evidence in state['brief']['evidence']:
            self.assertIn(f'origin-test/{evidence["id"]}', output)
            self.assertIn(evidence['source'], output)
        self.assertNotIn('PRIVATE_RAW_EXCERPT_SENTINEL', output)
        self.assertIn('These IDs belong to this run, not the next review.', output)

    def test_receipt_and_handoff_fit_existing_selective_review_intake(self):
        reference = handoff_identity(self.state)['reference']
        receipt = self.root / 'RESULT.md'
        receipt.write_text(f'Contract reference: {reference}\nAC1: not run; no evidence.\n'
                           'Implementation outcome: untested. Economic outcome: unmeasured.\n', encoding='utf-8')
        review_brief = build_brief('Review intent versus implementation versus outcome; do not invent results.',
                                  'technical', ['Read-only review; no external actions.'],
                                  [str(self.store.path / 'handoff.md'), str(receipt)], [])
        validate_brief(review_brief)
        excerpts = '\n'.join(item['excerpt'] for item in review_brief['evidence'])
        self.assertIn(reference, excerpts)
        self.assertIn('not run; no evidence', excerpts)
        self.assertEqual(len(review_brief['evidence']), 2)
        self.assertEqual(self.store.load()['brief'], self.state['brief'])
