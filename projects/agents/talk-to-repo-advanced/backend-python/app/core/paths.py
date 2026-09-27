"""
Shared, safe path resolution for reading files out of a cloned repo.

The original version checked `full_path.startswith(base)` on an
*unnormalized* joined path — `os.path.join(base, "../../etc/passwd")`
still starts with `base` as a string, even though it resolves outside it.
That's a real directory-traversal bug. This version resolves both paths
with `os.path.realpath` first and checks *containment*, which is the
correct way to do this check.
"""

import os

REPO_ROOT = "/tmp"


def safe_repo_path(repo_id: str, relative_path: str) -> str | None:
    """
    Resolve `relative_path` inside the cloned repo for `repo_id`.
    Returns the real, absolute path if it's safely contained within the
    repo's directory, or None if it escapes it (traversal attempt,
    symlink out of the sandbox, etc.).
    """
    base = os.path.realpath(os.path.join(REPO_ROOT, f"repo_{repo_id}"))
    candidate = os.path.realpath(os.path.join(base, relative_path))

    # os.path.commonpath handles the "/tmp/repo_abc" vs "/tmp/repo_abcxyz"
    # prefix-collision case that a naive startswith() check gets wrong too.
    try:
        if os.path.commonpath([base, candidate]) != base:
            return None
    except ValueError:
        # commonpath raises if paths are on different drives (Windows) or
        # otherwise incomparable — treat as unsafe.
        return None

    return candidate
