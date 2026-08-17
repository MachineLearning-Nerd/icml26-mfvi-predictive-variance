
#!/usr/bin/env python3
'''Verify the published MFVI dossier and live repository state.'''

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPOSITORY = 'icml26-mfvi-predictive-variance'
CANONICAL = ('MachineLearning-Nerd', 'MachineLearning-Nerd@users.noreply.github.com')
EXPECTED_BRANCHES = {'main'}
EXPECTED_STATUSES = [
    'verified_scoped_spherical_prior',
    'verified_scoped_empirical_training_distribution',
    'verified_scoped_first_principal_direction',
]
SOURCE_PDF_SHA = '5347414ef5e950966cc90ef9567da99aaa89276b8946259b717af3639a7cab59'
SOURCE_ARCHIVE_SHA = '5a5e8ba755d451526420170011c78e278fa472afc4325acbdc98858c420ef157'
SOURCE_TEX_SHA = '2dfae2872507edad0b225121891ec1f24d76d4bf10a5ab6c1cdb63eeb490b1da'
APPENDIX_TEX_SHA = 'ca1d1d9546159520cb3337ca61b04b42d14516fedeeaa4a7ac21dde6081c57e9'
CONTRACT_SHA = '6b644fa280ddebeac75d0888e13134933ee7fe26366c34cb328b28c381b0cb5b'
OFFICIAL_COMMIT = '98604c6e558127fb756529a2c9339c77ca1a9965'
OFFICIAL_UCI_SHA = '4c0968b190e69064e663732c76d1669b48404fd47bddfa633b0a510eaeb2ac4a'
COLAB_ARCHIVE_SHA = '52a199c2c2bce9b84d312849e088cf44cdeaecd5812503286d33aba5065406b9'
INDEPENDENT_AUDIT_SHA = '57812709227f6a96ac4e035f6de6f8bdaedc3479fefff145e2ae37557b4c3f48'
EVIDENCE_BUNDLE_SHA = '333425cedaaaa2419c061c31a0e89942c8524118101322c0b5558f2ccc774ce4'
ARTIFACT_MANIFEST_SHA = '5c3dd0c8809b35faccc452bd7b4657f358a9e72cc91b6497fa61e15da766f3f4'
LOCAL_READBACK_SHA = 'bfd5a29f0b3b545ab8a79dc80a218eb67e7078c3c1b02fe0422de3601d48c5ba'
PREPUBLISH_SHA = '8d52b9b1a6e0a7ced3fd39b29863267389b9a5b3af59b7281e36d99e37c28207'
OFFICIAL_STDOUT_SHA = '91ef22ef4dd3cff0219083d742d3ce310b1c3256adecbd835f8c573e1ff32db0'
OFFICIAL_TRACE_SHA = '3da7647942ede28be9857242f6a80dc9461ef8975acd39c361b35e0be8b198a3'
OFFICIAL_PROVENANCE_SHA = 'e8276cb41c0ea9e22e11d38534fa0fa344ac2a0378fd109da2d8f85fb8532188'
EXPECTED_UCI = {
    'v1__boston__MEDV.pkl': 'b8dafe36623f3460b812a8b63c24c7a820f6075314bc14eb2327a8c87b07b25a',
    'v1__concrete__ConcreteCompressiveStrength.pkl': 'a5ae2678b6902fe8af36d24422726330f825f4d5fb506bf3e9dbb856df469233',
    'v1__energy__Y1.pkl': '1edb5edc0317eae59b4e04cda1d281c6f263c993b0b9fbecbc282c522d362061',
    'v1__kin8nm___default.pkl': 'daf0910c5d534c39faf3d921881d9965d86c4de7f16c4da2f6101efea46e60fe',
    'v1__naval__kMc.pkl': '3da44b496e450fa1ff4dab65fd873120421fb01bd12a70be1b404f5f0c9c2f2a',
    'v1__power__PE.pkl': '7decad58c92b5926206e7e8ee29dc1dfbf1fc2fccbc082441abe6418bd657687',
    'v1__protein__RMSD.pkl': 'f5b672d6150360ea6489fdcb48f12f2026401235ef30621c4e7a0515aea67981',
    'v1__wine__class.pkl': 'cbc18a58a8112b72989a5c1a8f30f6f9fdba29b83abfdf894a617f6b815f71e2',
    'v1__yacht__residuary_resistance.pkl': '0a86bb49fd52d5484368e281f8ac87718090c2a5c2fcf210b9141cfc85530286',
}
REQUIRED_PATHS = [
    '.gitignore', 'README.md', 'STATUS.md', 'sources.json', 'publication_gate.json',
    'AUTONOMOUS_STATE.json', 'CLAIM_EVIDENCE.md', 'SOURCE_AUDIT.md', 'ENVIRONMENT.md',
    'REPORT.md', 'AUTHOR_THANK_YOU.md', 'CITATION.cff', 'BRANCH_AUDIT.md',
    'branch-audit.md', 'claims.json', 'EVIDENCE_MANIFEST.json', 'verify_final.py',
    'docs/BRANCH_AUDIT.md', 'docs/CLAIM_EVIDENCE.md', 'docs/PUBLICATION_GATE.md',
    'docs/SOURCE_AUDIT.md', 'docs/primary.pdf',
    'outputs/CUMULATIVE_SCIENCE_GATE.json', 'outputs/PUBLICATION_GATE_PASSED.json',
    'outputs/artifact_manifest.json', 'outputs/colab/RG7maF4bGu-colab-results.tar.gz',
    'outputs/colab_synthetic_preflight.json', 'outputs/evidence_bundle.jsonl',
    'outputs/independent_full_audit.json', 'outputs/independent_full_audit_sha256.txt',
    'outputs/independent_full_audit_stdout.json', 'outputs/local_readback_gate.json',
    'outputs/official_uci_provenance.txt', 'outputs/official_uci_sha256.txt',
    'outputs/official_uci_stdout.txt', 'outputs/official_uci_trace_table.tex',
    'outputs/prepublish_gate.json', 'outputs/publication_gate.json',
    'outputs/synthetic_audit.json', 'outputs/synthetic_audit_rerun.json',
    'outputs/synthetic_audit_rerun_stdout.json', 'outputs/synthetic_audit_stdout.json',
    'repro/configs/live_claims.json', 'repro/requirements.txt', 'repro/src/.gitkeep',
    'repro/src/artifact_manifest.py', 'repro/src/build_evidence_bundle.py',
    'repro/src/prepublish_gate.py', 'repro/src/publication_gate.py',
    'repro/src/run_full_gate.sh', 'repro/src/run_independent_uci.sh',
    'repro/src/run_official_uci.sh', 'repro/src/verify_mfvi.py',
    'repro/tests/test_prepublish_gate.py', 'repro/tests/test_verify_mfvi.py',
    'source/arxiv/00README.json', 'source/arxiv/main.tex', 'source/arxiv/app_proofs.tex',
]
DOSSIER_PATHS = {
    'CLAIM_EVIDENCE.md', 'SOURCE_AUDIT.md', 'ENVIRONMENT.md', 'REPORT.md',
    'AUTHOR_THANK_YOU.md', 'CITATION.cff', 'BRANCH_AUDIT.md', 'branch-audit.md',
    'claims.json', 'verify_final.py',
}


def fail(message: str) -> None:
    print(f'FINAL_AUDIT=FAILED {message}', file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode:
        fail(f'command failed: {" ".join(args)}: {result.stderr.strip()}')
    return result.stdout


def current_bytes(path: str) -> bytes:
    local = ROOT / path
    if local.exists():
        return local.read_bytes()
    result = subprocess.run(['git', 'show', f'HEAD:{path}'], cwd=ROOT, check=False, capture_output=True)
    if result.returncode:
        fail(f'required path is unavailable: {path}')
    return result.stdout


def current_json(path: str) -> object:
    try:
        return json.loads(current_bytes(path))
    except json.JSONDecodeError as exc:
        fail(f'invalid JSON in {path}: {exc}')
    return None


def sha256(path: str) -> str:
    return hashlib.sha256(current_bytes(path)).hexdigest()


def verify_git_state() -> tuple[int, int]:
    origin = run('git', 'config', '--get', 'remote.origin.url').strip()
    require(origin in {
        f'https://github.com/MachineLearning-Nerd/{REPOSITORY}.git',
        f'git@github.com:MachineLearning-Nerd/{REPOSITORY}.git',
    }, f'unexpected origin: {origin}')
    require('ref: refs/heads/main\tHEAD' in run('git', 'ls-remote', '--symref', 'origin', 'HEAD'),
            'origin/HEAD is not main')
    remote_heads = {}
    for line in run('git', 'ls-remote', '--heads', 'origin').splitlines():
        commit, ref = line.split('\t', 1)
        require(ref.startswith('refs/heads/'), f'unexpected remote ref: {ref}')
        remote_heads[ref.removeprefix('refs/heads/')] = commit
    require(set(remote_heads) == EXPECTED_BRANCHES, f'remote branches changed: {sorted(remote_heads)}')
    for branch in EXPECTED_BRANCHES:
        require(remote_heads[branch] == run('git', 'rev-parse', f'origin/{branch}').strip(),
                f'origin/{branch} differs from live remote tip')
    local_heads = set(run('git', 'for-each-ref', '--format=%(refname:strip=2)', 'refs/heads').splitlines())
    require(local_heads <= EXPECTED_BRANCHES, f'unexpected local branches: {sorted(local_heads)}')
    require(run('git', 'branch', '--show-current').strip() == 'main', 'current branch is not main')
    refs = run('git', 'for-each-ref', '--format=%(refname)', 'refs').splitlines()
    require(not any('refs/original/' in ref for ref in refs), 'refs/original remains')
    identities = set()
    for line in run('git', 'log', '--all', '--format=%an\t%ae\t%cn\t%ce').splitlines():
        if line.strip():
            identities.add(tuple(line.split('\t')))
    require(identities == {(CANONICAL[0], CANONICAL[1], CANONICAL[0], CANONICAL[1])},
            f'non-canonical reachable identity: {sorted(identities)}')
    require('co-authored-by:' not in run('git', 'log', '--all', '--format=%B').lower(),
            'co-author trailer found')
    commit_count = int(run('git', 'rev-list', '--count', '--all').strip())
    require(commit_count >= 16, f'unexpectedly short history: {commit_count}')
    return len(remote_heads), commit_count


def verify_nested_manifest() -> None:
    manifest = current_json('outputs/artifact_manifest.json')
    require(isinstance(manifest, dict), 'nested artifact manifest is not an object')
    entries = manifest.get('files')
    require(isinstance(entries, list) and len(entries) == 72, 'nested artifact file count changed')
    seen = set()
    for entry in entries:
        require(isinstance(entry, dict), 'nested artifact entry is not an object')
        path, expected = entry.get('path'), entry.get('sha256')
        require(isinstance(path, str) and path not in seen, f'invalid nested path: {path}')
        require(isinstance(expected, str) and len(expected) == 64, f'bad nested hash: {path}')
        seen.add(path)
        require((ROOT / path).is_file(), f'nested artifact missing: {path}')
        require(sha256(path) == expected, f'nested artifact hash mismatch: {path}')
    require(sha256('outputs/artifact_manifest.json') == ARTIFACT_MANIFEST_SHA, 'artifact manifest hash changed')


def verify_evidence_manifest() -> None:
    manifest = current_json('EVIDENCE_MANIFEST.json')
    require(isinstance(manifest, dict), 'evidence manifest is not an object')
    require(manifest.get('schema_version') == 1 and manifest.get('hash_algorithm') == 'sha256',
            'unsupported evidence manifest schema')
    entries = manifest.get('entries')
    require(isinstance(entries, list) and len(entries) == 82, 'evidence manifest entry count changed')
    seen = set()
    for entry in entries:
        require(isinstance(entry, dict), 'evidence entry is not an object')
        path, expected = entry.get('path'), entry.get('sha256')
        require(isinstance(path, str) and path not in seen, f'invalid or duplicate evidence path: {path}')
        require(not Path(path).is_absolute() and '..' not in Path(path).parts, f'unsafe evidence path: {path}')
        require(isinstance(expected, str) and len(expected) == 64, f'bad evidence hash: {path}')
        seen.add(path)
        require((ROOT / path).is_file(), f'evidence path missing: {path}')
        require(sha256(path) == expected, f'evidence hash mismatch: {path}')
    require(DOSSIER_PATHS <= seen, 'dossier files are missing from evidence manifest')
    require('AUTONOMOUS_STATE.json' not in seen and 'EVIDENCE_MANIFEST.json' not in seen,
            'state or manifest would create a hash cycle')


def verify_source_and_claims() -> None:
    sources = current_json('sources.json')
    require(isinstance(sources, dict), 'sources.json is not an object')
    paper = sources.get('paper', {})
    require(paper.get('openreview_id') == 'RG7maF4bGu' and paper.get('arxiv_id') == '2606.25745'
            and paper.get('arxiv_version') == 'v1' and paper.get('official_claim_count') == 3,
            'paper source pin changed')
    contract = sources.get('challenge_contract', {})
    require(contract.get('local_path') == 'repro/configs/live_claims.json'
            and contract.get('local_sha256') == CONTRACT_SHA, 'challenge contract pin changed')
    require(sha256('repro/configs/live_claims.json') == CONTRACT_SHA, 'challenge contract bytes changed')
    arxiv = sources.get('arxiv_source', {})
    source_files = [path for path in (ROOT / 'source/arxiv').rglob('*') if path.is_file()]
    require(arxiv.get('local_root') == 'source/arxiv' and arxiv.get('file_count') == 30
            and len(source_files) == 30, 'source file count changed')
    require(arxiv.get('main_tex_sha256') == SOURCE_TEX_SHA
            and arxiv.get('appendix_tex_sha256') == APPENDIX_TEX_SHA,
            'source TeX pins changed')
    require(sha256('source/arxiv/main.tex') == SOURCE_TEX_SHA
            and sha256('source/arxiv/app_proofs.tex') == APPENDIX_TEX_SHA,
            'source TeX bytes changed')
    require(arxiv.get('author_executable_files') == [], 'author executable boundary changed')
    artifact = sources.get('source_artifact', {})
    require(artifact.get('path') == 'docs/primary.pdf' and artifact.get('sha256') == SOURCE_PDF_SHA
            and artifact.get('pages') == 22 and sha256('docs/primary.pdf') == SOURCE_PDF_SHA,
            'paper PDF pin changed')
    require(sources.get('primary_source_tar_sha256') == SOURCE_ARCHIVE_SHA
            and sources.get('official_repository_commit') == OFFICIAL_COMMIT
            and sources.get('official_uci_script_sha256') == OFFICIAL_UCI_SHA,
            'external provenance pins changed')
    require(sources.get('uci_data_sha256') == EXPECTED_UCI, 'UCI input pins changed')
    retained = sources.get('retained_artifacts', {})
    require(retained.get('colab_archive', {}).get('sha256') == COLAB_ARCHIVE_SHA
            and retained.get('independent_full_audit_sha256') == INDEPENDENT_AUDIT_SHA
            and retained.get('local_readback_gate_sha256') == LOCAL_READBACK_SHA
            and retained.get('prepublish_gate_sha256') == PREPUBLISH_SHA,
            'retained artifact pins changed')
    claims = current_json('claims.json')
    require(isinstance(claims, dict) and claims.get('repository') == f'MachineLearning-Nerd/{REPOSITORY}',
            'claims repository mismatch')
    rows = claims.get('claims')
    require(isinstance(rows, list) and len(rows) == 3
            and [row.get('status') for row in rows] == EXPECTED_STATUSES,
            'claim statuses changed')
    require(claims.get('official_code', {}).get('commit') == OFFICIAL_COMMIT
            and claims.get('official_code', {}).get('status') == 'externally_pinned_not_vendored'
            and claims.get('publication_allowed') is False, 'claim boundary changed')
    state = current_json('AUTONOMOUS_STATE.json')
    require(isinstance(state, dict) and state.get('phase') == 'published_and_verified', 'state is not final')
    require(state.get('publication_allowed') is False and state.get('branch_set') == ['main'],
            'state publication or branch boundary changed')
    require(state.get('claim_statuses') == dict(zip(['C1', 'C2', 'C3'], EXPECTED_STATUSES)),
            'state claim statuses changed')
    checkpoint = state.get('last_known_git_commit')
    require(isinstance(checkpoint, str) and len(checkpoint) == 40, 'state checkpoint is not a full SHA')
    run('git', 'cat-file', '-e', checkpoint)
    run('git', 'merge-base', '--is-ancestor', checkpoint, 'HEAD')


def verify_gate_and_results() -> None:
    gate_paths = ['publication_gate.json', 'outputs/publication_gate.json',
                  'outputs/PUBLICATION_GATE_PASSED.json', 'outputs/CUMULATIVE_SCIENCE_GATE.json']
    gates = [current_json(path) for path in gate_paths]
    require(all(gate == gates[0] for gate in gates[1:]), 'publication gate copies differ')
    gate = gates[0]
    require(gate.get('status') == 'SCOPED_PASS' and gate.get('strict_status') == 'NOT_READY'
            and gate.get('overall_status') == 'VERIFIED_SCOPED_WITH_FULL_SCALE_RETAINED_ARTIFACTS'
            and gate.get('official_claim_count') == 3 and gate.get('local_claim_units') == 3
            and gate.get('publication_gate_passed') is True and gate.get('score_forecast') is None,
            'publication gate status changed')
    require(gate.get('claim_outcomes') == ['VERIFIED_SCOPED_SPHERICAL_PRIOR',
            'VERIFIED_SCOPED_EMPIRICAL_TRAINING_DISTRIBUTION',
            'VERIFIED_SCOPED_FIRST_PRINCIPAL_DIRECTION'], 'publication claim outcomes changed')
    source = gate.get('source', {})
    require(source.get('arxiv') == '2606.25745' and source.get('source_files') == 30
            and source.get('pdf_sha256') == SOURCE_PDF_SHA and source.get('source_sha256') == SOURCE_ARCHIVE_SHA
            and source.get('main_tex_sha256') == SOURCE_TEX_SHA
            and source.get('appendix_tex_sha256') == APPENDIX_TEX_SHA
            and source.get('official_repository_commit') == OFFICIAL_COMMIT
            and source.get('official_uci_script_sha256') == OFFICIAL_UCI_SHA,
            'gate source pins changed')
    require(gate.get('artifact_manifest') == {'files': 72, 'sha256': ARTIFACT_MANIFEST_SHA},
            'gate artifact manifest changed')
    require(gate.get('evidence_bundle') == {'bytes': 23633, 'records': 21, 'sha256': EVIDENCE_BUNDLE_SHA},
            'gate evidence bundle changed')
    full = gate.get('full_scale_evidence', {})
    require(full.get('synthetic_systems') == 144 and full.get('uci_datasets') == 9
            and full.get('independent_full_audit_sha256') == INDEPENDENT_AUDIT_SHA
            and full.get('colab_archive_sha256') == COLAB_ARCHIVE_SHA
            and full.get('local_readback_gate_sha256') == LOCAL_READBACK_SHA
            and full.get('prepublish_gate_sha256') == PREPUBLISH_SHA
            and full.get('minimum_synthetic_empirical_gap') == 5.725297700025641e-8
            and full.get('minimum_synthetic_first_pc_gap') == 9.375506445419605e-7
            and full.get('minimum_uci_empirical_gap') == 1.035265794912767e-14
            and full.get('minimum_uci_first_pc_gap') == 4.6049666600837724e-8,
            'full-scale gate summary changed')
    limitations = ' '.join(gate.get('limitations', [])).lower()
    require('machine-checked' in limitations and 'does not rerun' in limitations
            and 'externally pinned' in limitations, 'gate limitations changed')
    audit = current_json('outputs/independent_full_audit.json')
    method = audit.get('methodology', {})
    require(audit.get('paper') == 'RG7maF4bGu' and audit.get('mode') == 'full'
            and audit.get('pass') is True and method.get('uses_author_posterior_code') is False,
            'independent audit boundary changed')
    synthetic = audit.get('synthetic', {})
    require(synthetic.get('pass') is True and synthetic.get('system_count') == 144
            and synthetic.get('minimum_empirical_gap') == 5.725297700025641e-8
            and synthetic.get('minimum_first_pc_gap') == 9.375506445419605e-7
            and synthetic.get('axis_aligned_equality_control', {}).get(
                'empirical_mfvi_minus_exact_predictive_variance') == 0.0
            and synthetic.get('nonspherical_prior_scope_control', {}).get(
                'first_pc_mfvi_minus_exact_predictive_variance') == -0.039114482356105526,
            'synthetic audit results changed')
    uci = audit.get('uci', {})
    require(uci.get('pass') is True and uci.get('dataset_count') == 9
            and uci.get('minimum_empirical_gap') == 1.035265794912767e-14
            and uci.get('minimum_first_pc_gap') == 4.6049666600837724e-8
            and len(uci.get('rows', [])) == 9, 'UCI audit results changed')
    require(all(row.get('empirical_mfvi_minus_exact_predictive_variance', -1) >= 0 for row in uci['rows'])
            and all(row.get('first_pc_mfvi_minus_exact_predictive_variance', -1) >= 0 for row in uci['rows'])
            and all(row.get('mfvi_minus_exact_posterior_trace', 1) <= 0 for row in uci['rows']),
            'UCI claim inequalities changed')
    synthetic_record = current_json('outputs/synthetic_audit.json')
    require(synthetic_record.get('paper') == 'RG7maF4bGu' and synthetic_record.get('pass') is True
            and synthetic_record.get('synthetic', {}).get('system_count') == 144,
            'synthetic record changed')
    for path in ['outputs/local_readback_gate.json', 'outputs/prepublish_gate.json']:
        record = current_json(path)
        require(record.get('paper') == 'RG7maF4bGu'
                and record.get('publication_gate_passed') is True
                and record.get('official_claim_count') == 3
                and record.get('maximum_points') == 6
                and '4 passed' in record.get('tests', ''), f'{path} changed')
        require(record.get('official_run_provenance', {}).get('official_repository_commit') == OFFICIAL_COMMIT
                and record.get('official_run_provenance', {}).get('uci_tr_inequ_sha256') == OFFICIAL_UCI_SHA,
                f'{path} provenance changed')
    require(sha256('outputs/independent_full_audit.json') == INDEPENDENT_AUDIT_SHA
            and sha256('outputs/evidence_bundle.jsonl') == EVIDENCE_BUNDLE_SHA
            and len(current_bytes('outputs/evidence_bundle.jsonl').splitlines()) == 21,
            'retained audit or evidence bundle changed')
    require(sha256('outputs/colab/RG7maF4bGu-colab-results.tar.gz') == COLAB_ARCHIVE_SHA,
            'Colab archive changed')
    require(sha256('outputs/local_readback_gate.json') == LOCAL_READBACK_SHA
            and sha256('outputs/prepublish_gate.json') == PREPUBLISH_SHA,
            'readback gate hashes changed')
    require(sha256('outputs/official_uci_stdout.txt') == OFFICIAL_STDOUT_SHA
            and sha256('outputs/official_uci_trace_table.tex') == OFFICIAL_TRACE_SHA
            and sha256('outputs/official_uci_provenance.txt') == OFFICIAL_PROVENANCE_SHA,
            'official retained output hashes changed')
    provenance = current_bytes('outputs/official_uci_provenance.txt').decode().splitlines()
    require(provenance == [
        f'official_repository_commit={OFFICIAL_COMMIT}',
        f'uci_tr_inequ_sha256={OFFICIAL_UCI_SHA}',
    ], 'official provenance contents changed')
    with tarfile.open(ROOT / 'outputs/colab/RG7maF4bGu-colab-results.tar.gz', 'r:gz') as archive:
        members = {member.name for member in archive.getmembers()}
    require({'outputs/independent_full_audit.json', 'outputs/official_uci_stdout.txt',
             'outputs/official_uci_trace_table.tex', 'outputs/prepublish_gate.json'} <= members,
            'retained Colab members changed')


def verify_hygiene() -> None:
    readme = current_bytes('README.md').decode().lower()
    for phrase in ['clean-room', 'full-scale', 'does not run all nine official datasets',
                   'thank you', 'citation', 'not an official implementation']:
        require(phrase in readme, f'README boundary phrase missing: {phrase}')
    tracked = run('git', 'ls-files').splitlines()
    require(not any(path == '.trackio' or path.startswith('.trackio/')
                    or path == 'logbook.json' or path.endswith('/logbook.json')
                    or '__pycache__' in path or path.startswith('.venv/') for path in tracked),
            'stale private or generated state is tracked')
    executable_suffixes = {'.py', '.ipynb', '.sh', '.r', '.R', '.jl'}
    author_files = [path for path in tracked if path.startswith('source/arxiv/')
                    and Path(path).suffix in executable_suffixes]
    require(not author_files, f'author executable appeared in source snapshot: {author_files}')


def main() -> None:
    branches, commits = verify_git_state()
    for path in REQUIRED_PATHS:
        require((ROOT / path).is_file(), f'required path missing: {path}')
    verify_source_and_claims()
    verify_gate_and_results()
    verify_nested_manifest()
    verify_evidence_manifest()
    verify_hygiene()
    print('FINAL_AUDIT=VERIFIED '
          f'branches={branches} commits={commits} '
          'claims=C1:verified_scoped_spherical_prior,'
          'C2:verified_scoped_empirical_training_distribution,'
          'C3:verified_scoped_first_principal_direction publication_allowed=false')


if __name__ == '__main__':
    main()
