#!/usr/bin/env python3
"""One-time removal of the two PI-authorized sibling entries, after preservation.
Requires an explicit execute flag; never removes refs, branches, repositories,
original raw data or symlink targets. Run only from the original checkout.
"""
import argparse
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

import ctr34_support as m

ROOT, P = m.ROOT, m.P
EXPECTED = Path('/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026')


def active_local_processes(targets):
    hits, denied, own_denied, inspected = [], [], [], 0
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            uid = proc.stat().st_uid
            inspected += 1
            for kind in ['cwd', 'root', 'exe']:
                try:
                    path = os.readlink(proc / kind)
                    if any(path == t or path.startswith(t + '/') for t in targets):
                        hits.append(dict(pid=int(proc.name), kind=kind, path=path))
                except FileNotFoundError:
                    pass
            for fd in (proc / 'fd').iterdir():
                try:
                    path = os.readlink(fd)
                    if any(path == t or path.startswith(t + '/') for t in targets):
                        hits.append(dict(pid=int(proc.name), kind='open_fd', path=path))
                except FileNotFoundError:
                    pass
            for line in (proc / 'maps').read_text().splitlines():
                fields = line.split(None, 5)
                path = fields[-1] if len(fields) == 6 else ''
                if any(path == t or path.startswith(t + '/') for t in targets):
                    hits.append(dict(pid=int(proc.name), kind='mapped_file', path=path))
        except PermissionError:
            denied.append(int(proc.name))
            if uid == os.getuid():
                try:
                    comm = (proc / 'comm').read_text().strip()
                    executable = (proc / 'cmdline').read_bytes().split(b'\0')[0].decode(errors='replace')
                    own_denied.append(dict(pid=int(proc.name), comm=comm, executable=executable,
                        known_session_daemon=comm in ['systemd', '(sd-pam)', 'sshd']))
                except FileNotFoundError:
                    pass
        except (FileNotFoundError, ProcessLookupError):
            pass
    return dict(checked_utc=m.now(), scope='local Linux /proc cwd, root, exe, open fds and maps; no NAS-client-wide activity claim',
                inspected_processes=inspected, scanner_pid_excluded=os.getpid(), active_references=hits, own_uid_inaccessible=own_denied,
                unknown_worker_processes=[r for r in own_denied if not r['known_session_daemon']],
                other_uid_inaccessible_count=len(denied)-len(own_denied),
                limitation='other-user process details require privileges and are not asserted; no privilege changes made')


def main(execute=False):
    assert ROOT == EXPECTED and ROOT.resolve() == ROOT and not ROOT.is_symlink()
    subprocess.run(['findmnt', '-T', str(ROOT), '-n', '-t', 'nfs,nfs4'], check=True, capture_output=True)
    before = json.loads((P / 'provenance/ctr36_worktrees_before.json').read_text())
    targets = [str(ROOT) + s for s in ['-ctr33', '-ctr34']]
    assert [r['path'] for r in before] == targets
    assert not (P / 'provenance/ctr36_deletion_receipt.json').exists(), 'Removal already recorded; inspect receipt instead of repeating.'
    preservation = json.loads((P / 'provenance/ctr36_author_preservation.json').read_text())
    assert m.sha(P / preservation['archive']) == preservation['sha256']
    validation = json.loads((P / 'provenance/ctr36_input_validation.json').read_text())
    assert validation['status'] == 'pass' and validation['eligible_validation_pairs'] == 0
    recovery = json.loads((P / 'provenance/ctr36_recovery_manifest.json').read_text())
    assert all(m.sha(ROOT / r['destination']) == r['final_sha256'] for r in recovery['files'])
    for record in before:
        path = Path(record['path'])
        assert path.resolve() == path and not path.is_symlink()
        assert subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip() == record['head']
        assert not subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain'], text=True)
        # No payload is removed from a raw-data directory; only links and .gitkeep may occur.
        raw = path / 'data/raw'
        assert all(f.is_symlink() or f.name == '.gitkeep' for f in raw.iterdir()), raw
        current = set()
        for directory, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                current.add(str((Path(directory) / name).relative_to(path)))
            dirs[:] = [d for d in dirs if not (Path(directory) / d).is_symlink()]
        assert current == {r['path'] for r in record['entries']}, 'Directory changed after preservation inventory'
        for entry in record['entries']:
            f = path / entry['path']
            s = f.lstat()
            assert s.st_size == entry['size'] and s.st_mtime_ns == entry['mtime_ns'], f
            if entry['kind'] == 'symlink':
                assert f.is_symlink() and os.readlink(f) == entry['target']
            if entry.get('sha256'):
                assert m.sha(f) == entry['sha256'], f
    process_check = active_local_processes(targets + [str(ROOT)])
    m.dump('provenance/ctr36_process_predelete.json', process_check)
    assert not process_check['active_references'] and not process_check['unknown_worker_processes'], process_check
    if not execute:
        print('Preconditions passed. No removal without --execute-authorized-removal.')
        return
    commands = []
    for record in before:
        # This single force permits known ignored files and data symlinks. Git's
        # directory removal unlinks symlinks; it does not traverse their targets.
        cmd = ['git', 'worktree', 'remove', '--force', record['path']]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        commands.append(dict(command=cmd, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr,
                             finished_utc=m.now()))
        m.dump('provenance/ctr36_removal_commands.json', commands)
        if result.returncode:
            raise RuntimeError(result.stderr)
        assert not os.path.lexists(record['path'])
    listing = subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], cwd=ROOT, text=True)
    assert all(t not in listing and not os.path.lexists(t) for t in targets)
    assert m.raw_snapshot() == json.loads((P / 'provenance/ctr36_raw_before.json').read_text())
    original = json.loads((P / 'provenance/ctr36_original_tracked.json').read_text())
    assert all(m.sha(ROOT / name) == digest for name, digest in original.items())
    refs = {}
    for record in before:
        refs[record['branch']] = subprocess.check_output(['git', 'rev-parse', record['branch']], cwd=ROOT, text=True).strip()
        assert refs[record['branch']] == record['head']
        subprocess.run(['git', 'cat-file', '-e', record['head'] + '^{commit}'], cwd=ROOT, check=True)
    # Exact v5 bytes and original environment remain available after link removal.
    assert m.sha(P / 'outputs/official-srf-v5.xlsx') == recovery['v5_cache_sha256']
    assert (ROOT / '.venv/bin/python').exists()
    m.dump('provenance/ctr36_deletion_receipt.json', dict(completed_utc=m.now(), task='CTR-36',
           authorization='CTR-35 assignment and saved plan revision 0d32d61e-8645-4dff-9cc4-1f40d66833e0; not a new approval',
           before=[{k:r[k] for k in ['path','realpath','kind','head','branch','status_porcelain','ignored']} for r in before],
           after=[dict(path=t, lexists=os.path.lexists(t), registered=t in listing) for t in targets],
           commands=commands, remaining_worktrees=listing, retained_branch_heads=refs,
           original_tracked_files_unchanged=True, original_raw_path_size_mtime_unchanged=True,
           source_archive_sha256=preservation['sha256'], v5_sha256=recovery['v5_cache_sha256'],
           symlink_handling='git worktree remove --force unlinks entries without following symlink targets; data/raw contained symlinks and .gitkeep only',
           process_check=process_check, no_raw_dataset_payload_removed=True,
           discarded_ignored_content='reproducible package caches, Quarto/Python/pytest caches; no unique source work; v5 reference cache separately preserved',
           remote_refs_prs_tasks_changed=False))
    print('Removed both exact sibling worktrees; original files/raw data and branch histories retained.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-authorized-removal', action='store_true')
    main(parser.parse_args().execute_authorized_removal)
