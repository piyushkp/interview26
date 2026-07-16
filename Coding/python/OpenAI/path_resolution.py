"""Resolve a shell-style `cd` and return the destination path.

cd(current_dir, new_dir, soft_links=None) simulates changing directories and
returns the normalized absolute path, or None on an illegal move.

Part 1 - traversal:
  '.' stays put, '..' goes to the parent, a leading '/' means new_dir is
  absolute, and rising above the root is illegal (returns None).
Part 2 - home:
  a leading '~' expands to HOME (/home/user); such a path is absolute.
Part 3 - symbolic links:
  soft_links maps an absolute path to a target. The final path is rewritten
  through the links, always preferring the LONGEST matching key, following
  chains of links, and returning None if the links form a cycle.
"""

HOME = "/home/user"     # where a leading '~' expands to
_MAX_LINK_HOPS = 1000   # safety net against self-growing link chains


def _expand_home(path):
    """Expand a leading '~' to HOME ('~' -> HOME, '~/x' -> HOME + '/x')."""
    # Time: O(L) over the L characters of path. Space: O(L) - the new string.
    if path == "~":
        return HOME
    if path.startswith("~/"):
        return HOME + path[1:]   # path[1:] keeps its leading '/'
    return path


def _to_components(path):
    """Split a path on '/', dropping empty pieces (keeps '.' and '..')."""
    # Time: O(L) over the L characters of path. Space: O(L) - the parts list.
    parts = []
    for token in path.split("/"):
        if token != "":
            parts.append(token)
    return parts


def _resolve_stack(base, tokens):
    """Apply tokens to a copy of base, handling '.' and '..'. Returns the
    resulting component list, or None if '..' rises above the root."""
    # b = len(base), t = len(tokens).
    # Time: O(b + t) - copy the base, then one pass over the tokens.
    # Space: O(b + t) - the working stack.
    stack = list(base)
    for token in tokens:
        if token == "." or token == "":
            continue
        if token == "..":
            if not stack:
                return None   # cannot go above the root
            stack.pop()
        else:
            stack.append(token)
    return stack


def _join(components):
    """Join components into an absolute path ('/' when empty)."""
    # Time: O(total characters). Space: O(total characters) - the new string.
    if not components:
        return "/"
    return "/" + "/".join(components)


def _link_match_length(key, path):
    """How many leading components of path the link key covers, or -1 if key
    is not a component-boundary prefix ('/a' matches '/a/b', not '/ab')."""
    # k, p = component counts of key and path.
    # Time: O(k + p) - split both, then compare up to k. Space: O(k + p).
    key_comps = _to_components(key)
    path_comps = _to_components(path)
    if len(key_comps) > len(path_comps):
        return -1
    for i in range(len(key_comps)):
        if key_comps[i] != path_comps[i]:
            return -1
    return len(key_comps)


def _resolve_links(path, soft_links):
    """Rewrite path through soft_links, always replacing the LONGEST matching
    prefix, until no link matches. Returns None if the links form a cycle."""
    # n = number of links, p = path length, d = link-chain depth (paths seen).
    # Time: O(d * n * p) - each step scans every link for the longest match.
    # Space: O(d + p) - the 'seen' set plus one path's components.
    seen = set()
    hops = 0
    while path not in seen:
        seen.add(path)
        hops += 1
        if hops > _MAX_LINK_HOPS:
            return None   # runaway resolution (e.g. '/a' -> '/a/b')
        best_key = None
        best_len = -1
        for key in soft_links:
            match_len = _link_match_length(key, path)
            if match_len > best_len:   # longer prefix wins (more specific)
                best_len = match_len
                best_key = key
        if best_key is None:
            return path   # no link matches -> this is the final path
        remaining = _to_components(path)[best_len:]
        new_comps = _to_components(soft_links[best_key]) + remaining
        stack = _resolve_stack([], new_comps)
        if stack is None:
            return None
        path = _join(stack)
    return None   # revisited a path -> the links form a cycle


# Approach (in plain terms):
#   Think of a path as a stack of folder names. We start from a base stack
#   (the current directory) - unless the new path is absolute or starts with
#   '~', in which case we start fresh from the root or the home folder.
#   Then we read the new path piece by piece:
#     - a normal name is pushed onto the stack (step into that folder),
#     - '.' means stay put,
#     - '..' pops the top folder (go up); popping past the root is illegal,
#       so we return None.
#   For symbolic links we first build this plain path, then keep rewriting it:
#   find the LONGEST link key that matches the front of the path, swap that
#   prefix for the link's target, and repeat (so links pointing to other links
#   keep unwinding). We remember every path we have seen; if one comes back,
#   the links form a loop, so we return None.
def cd(current_dir, new_dir, soft_links=None):
    """Resolve navigating from current_dir to new_dir (see module docstring).
    Returns the destination path, or None on an illegal move or link cycle."""
    # p = total path length, n = number of soft links, d = link-chain depth.
    # Time: O(p + d * n * p). Space: O(p + d).
    target = _expand_home(new_dir)
    if target.startswith("/"):
        base = []   # absolute new_dir -> start from the root
    else:
        start = _expand_home(current_dir)
        base = _resolve_stack([], _to_components(start))
        if base is None:
            return None
    stack = _resolve_stack(base, _to_components(target))
    if stack is None:
        return None
    path = _join(stack)
    if soft_links:
        path = _resolve_links(path, soft_links)
    return path


if __name__ == "__main__":
    # ----- Part 1: standard traversal -----
    print(cd("/foo/bar", "baz"))            # /foo/bar/baz
    print(cd("/foo/../", "./baz"))          # /baz
    print(cd("/", "foo/bar/../../baz"))     # /baz
    print(cd("/", ".."))                    # None  (above root)
    print(cd("/foo", "/bar/qux"))           # /bar/qux  (absolute new_dir)

    # ----- Part 2: home directory (~) -----
    print(cd("/foo/bar", "~"))              # /home/user
    print(cd("/tmp", "~/docs/../pics"))     # /home/user/pics
    print(cd("~", ".."))                    # /home

    # ----- Part 3: symbolic links -----
    print(cd("/foo/bar", "baz", {"/foo/bar": "/abc"}))   # /abc/baz

    cascade = {"/foo/bar": "/abc", "/abc": "/bcd", "/bcd/baz": "/xyz"}
    print(cd("/foo/bar", "baz", cascade))                # /xyz

    longest = {"/foo/bar": "/abc", "/foo/bar/baz": "/xyz"}
    print(cd("/foo/bar", "baz", longest))                # /xyz

    cycle = {"/x": "/y", "/y": "/x"}
    print(cd("/", "x", cycle))                           # None  (cycle)
