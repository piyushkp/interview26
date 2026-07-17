"""Resolve a shell-style `cd` and return the destination path.

The problem builds up in three parts, solved here as three separate functions
(each a complete solution for that part):

  cd_part1(current_dir, new_dir)
      Standard traversal: '.' stays put, '..' goes to the parent, a leading
      '/' means new_dir is absolute, and rising above the root returns None.
  cd_part2(current_dir, new_dir)
      Part 1 plus '~', which expands to HOME (/home/user) as an absolute path.
  cd_part3(current_dir, new_dir, soft_links=None)
      Part 2 plus symbolic links: the path is rewritten through soft_links,
      preferring the LONGEST matching key, following chains, and returning
      None if the links form a cycle.

Shared path helpers (_to_components, _resolve_stack, _join, ...) are reused by
every part.
"""

HOME = "/home/user"     # where a leading '~' expands to
_MAX_LINK_HOPS = 1000   # safety net against self-growing link chains

# ----- Part 1: standard traversal -----
# Approach (in plain terms):
#   Think of a path as a stack of folder names. Start from the current
#   directory, unless new_dir is absolute (begins with '/') - then start from
#   the root instead. Read new_dir piece by piece:
#     - a normal name is pushed on the stack (step into that folder),
#     - '.' means stay put,
#     - '..' pops the top folder (go up); rising above the root is illegal,
#       so we return None.
def cd_part1(current_dir, new_dir):
    """Part 1: resolve '.', '..', and absolute '/'; None above root."""
    # p = total path length. Time: O(p) - one pass. Space: O(p) - the stack.
    if new_dir.startswith("/"):
        base = []                       # absolute new_dir -> start from root
    else:
        base = _resolve_stack([], _to_components(current_dir))
        if base is None:
            return None
    stack = _resolve_stack(base, _to_components(new_dir))
    if stack is None:
        return None
    return _join(stack)

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

def _to_components(path):
    """Split a path on '/', dropping empty pieces (keeps '.' and '..')."""
    # Time: O(L) over the L characters of path. Space: O(L) - the parts list.
    parts = []
    for token in path.split("/"):
        if token != "":
            parts.append(token)
    return parts

def _join(components):
    """Join components into an absolute path ('/' when empty)."""
    # Time: O(total characters). Space: O(total characters) - the new string.
    if not components:
        return "/"
    return "/" + "/".join(components)

# ----- Part 2: home directory (~) -----
# Approach (in plain terms):
#   Same as Part 1, but first swap a leading '~' for the home folder. That
#   turns a '~' path into an ordinary absolute path; the rest is unchanged.
def cd_part2(current_dir, new_dir):
    """Part 2: Part 1 plus '~' expanding to HOME (an absolute path)."""
    # p = total path length. Time: O(p). Space: O(p) - the stack.
    current = _expand_home(current_dir)
    target = _expand_home(new_dir)
    if target.startswith("/"):
        base = []                       # absolute new_dir -> start from root
    else:
        base = _resolve_stack([], _to_components(current))
        if base is None:
            return None
    stack = _resolve_stack(base, _to_components(target))
    if stack is None:
        return None
    return _join(stack)


def _expand_home(path):
    """Expand a leading '~' to HOME ('~' -> HOME, '~/x' -> HOME + '/x')."""
    # Time: O(L) over the L characters of path. Space: O(L) - the new string.
    if path == "~":
        return HOME
    if path.startswith("~/"):
        return HOME + path[1:]   # path[1:] keeps its leading '/'
    return path

# ----- Part 3: symbolic links -----
# Approach (in plain terms):
#   Build the plain path exactly like Part 2, then keep rewriting it: find the
#   LONGEST link key that matches the front of the path, swap that prefix for
#   the link's target, and repeat (so links pointing to other links unwind).
#   Remember every path seen; if one comes back, the links loop -> None.
def cd_part3(current_dir, new_dir, soft_links=None):
    """Part 3: Part 2 plus symbolic-link resolution (longest match, cascade,
    cycle detection -> None)."""
    # p = path length, n = number of links, d = link-chain depth.
    # Time: O(p + d * n * p). Space: O(p + d).
    current = _expand_home(current_dir)
    target = _expand_home(new_dir)
    if target.startswith("/"):
        base = []                       # absolute new_dir -> start from root
    else:
        base = _resolve_stack([], _to_components(current))
        if base is None:
            return None
    stack = _resolve_stack(base, _to_components(target))
    if stack is None:
        return None
    path = _join(stack)
    if soft_links:
        path = _resolve_links(path, soft_links)
    return path

def _resolve_links(path, soft_links):
    """Follow soft_links until the path stops changing. Each step swaps the
    LONGEST matching key at the front of the path for its target. Returns None
    if the links form a cycle or never settle (keep growing)."""
    # n = links, p = path length, d = number of swaps before it settles.
    # Time: O(d * n * p) - each swap scans every link. Space: O(d + p).
    seen = set()
    # hops = 0
    while path not in seen:
        seen.add(path)
        # hops += 1
        # if hops > _MAX_LINK_HOPS:
        #     return None   # runaway growth, e.g. '/a' -> '/a/b'
        key = _longest_matching_link(path, soft_links)
        if key is None:
            return path   # nothing matches -> this is the final path
        # Swap the matched prefix (key) for its target, keep the rest.
        path = soft_links[key] + path[len(key):]
    return None   # we came back to a path we've seen -> a cycle

def _longest_matching_link(path, soft_links):
    """The soft-link key that matches the most of path's leading folders, or
    None. A key matches only on a folder boundary: '/a' matches '/a' and
    '/a/b', but not '/ab'."""
    # n = number of links, p = path length. Time: O(n * p). Space: O(1).
    best_key = None
    for key in soft_links:
        if path == key or path.startswith(key + "/"):
            if best_key is None or len(key) > len(best_key):
                best_key = key
    return best_key


if __name__ == "__main__":
    # ----- Part 1: standard traversal -----
    print(cd_part1("/foo/bar", "baz"))         # /foo/bar/baz
    print(cd_part1("/foo/../", "./baz"))       # /baz
    print(cd_part1("/", "foo/bar/../../baz"))  # /baz
    print(cd_part1("/", ".."))                 # None  (above root)
    print(cd_part1("/foo", "/bar/qux"))        # /bar/qux  (absolute)

    # ----- Part 2: home directory (~) -----
    print(cd_part2("/foo/bar", "~"))           # /home/user
    print(cd_part2("/tmp", "~/docs/../pics"))  # /home/user/pics
    print(cd_part2("~", ".."))                 # /home

    # ----- Part 3: symbolic links -----
    print(cd_part3("/foo/bar", "baz", {"/foo/bar": "/abc"}))  # /abc/baz

    cascade = {"/foo/bar": "/abc", "/abc": "/bcd", "/bcd/baz": "/xyz"}
    print(cd_part3("/foo/bar", "baz", cascade))              # /xyz

    longest = {"/foo/bar": "/abc", "/foo/bar/baz": "/xyz"}
    print(cd_part3("/foo/bar", "baz", longest))              # /xyz

    cycle = {"/x": "/y", "/y": "/x"}
    print(cd_part3("/", "x", cycle))                         # None  (cycle)
