"""A social network with users, directed follows, and snapshots.

Overview:
  Users are connected by directed follow edges (a follows b). At any
  moment createSnapshot() freezes the whole follow graph; the frozen
  copy never changes even as the live graph is edited afterwards.

Interface (class SocialNetwork):
  - addUser(username) -> None
        Register a user; a no-op if already present.
  - follow(user_a, user_b) -> None
        user_a starts following user_b. Auto-registers unknown users
        and is idempotent, so a duplicate follow is one relationship.
  - unfollow(user_a, user_b) -> None
        user_a stops following user_b; a no-op if not following.
  - getFollowers(user) -> list
        Users currently following user, sorted (empty if unknown).
  - getFollowees(user) -> list
        Users user currently follows, sorted (empty if unknown).
  - createSnapshot() -> int
        Freeze the current graph and return its id (0, 1, 2, ... in
        creation order).
  - isFollowInSnapshot(snapshot_id, user_a, user_b) -> bool
        Whether user_a followed user_b when that snapshot was taken.
        An out-of-range snapshot_id returns False.

Example:
  n = SocialNetwork(); n.follow('Nina','Omar'); n.follow('Pia','Omar')
  s = n.createSnapshot(); n.unfollow('Nina','Omar')
  n.getFollowers('Omar') -> ['Pia']   # live graph
  n.isFollowInSnapshot(s,'Nina','Omar') -> True   # frozen snapshot
"""


# Approach (in plain terms):
#   Keep two address books: for each user, who they follow and who follows
#   them. Using sets makes adding the same follow twice harmless and makes
#   unfollow easy, and the reverse book lets us list a user's followers
#   instantly. A snapshot is just a frozen photocopy of the "who follows whom"
#   book at that instant - we copy each user's follow set into a frozenset, so
#   later edits to the live books can never touch a stored photo. Looking up a
#   past follow is then a quick membership check inside that photo.
#   Data structures used:
#     - dict user -> set of followees - directed edges; the set gives O(1)
#       follow/unfollow and automatic de-duplication.
#     - dict user -> set of followers - reverse edges, so followers are
#       listed without scanning everyone.
#     - list of snapshot dicts (frozensets) - immutable copies of the graph.
class SocialNetwork:

    def __init__(self):
        # Time: O(1), Space: O(1) - empty maps and no snapshots yet.
        self._followees = {}    # user -> set of users they follow
        self._followers = {}    # user -> set of users following them
        self._snapshots = []    # list of frozen follow graphs

    def addUser(self, username):
        """Register a user (a no-op if already present)."""
        # Time: O(1) average. Space: O(1).
        if username not in self._followees:
            self._followees[username] = set()
            self._followers[username] = set()

    def follow(self, user_a, user_b):
        """user_a starts following user_b (idempotent)."""
        # Time: O(1) average. Space: O(1).
        self.addUser(user_a)
        self.addUser(user_b)
        self._followees[user_a].add(user_b)
        self._followers[user_b].add(user_a)

    def unfollow(self, user_a, user_b):
        """user_a stops following user_b (a no-op if not following)."""
        # Time: O(1) average. Space: O(1).
        if user_a in self._followees:
            self._followees[user_a].discard(user_b)
        if user_b in self._followers:
            self._followers[user_b].discard(user_a)

    def getFollowers(self, user):
        """Users currently following user, sorted."""
        # f = number of followers. Time: O(f log f). Space: O(f).
        return sorted(self._followers.get(user, set()))

    def getFollowees(self, user):
        """Users currently followed by user, sorted."""
        # f = number of followees. Time: O(f log f). Space: O(f).
        return sorted(self._followees.get(user, set()))

    def createSnapshot(self):
        """Freeze the current follow graph; return its snapshot id."""
        # u = users, e = edges. Time: O(u + e) - copy every edge once.
        # Space: O(u + e) - the frozen copy.
        snapshot = {}
        for user in self._followees:
            snapshot[user] = frozenset(self._followees[user])
        self._snapshots.append(snapshot)
        return len(self._snapshots) - 1

    def isFollowInSnapshot(self, snapshot_id, user_a, user_b):
        """Was user_a following user_b when this snapshot was taken? False if
        the snapshot id is unknown."""
        # Time: O(1) average. Space: O(1).
        if snapshot_id < 0 or snapshot_id >= len(self._snapshots):
            return False
        followees = self._snapshots[snapshot_id].get(user_a)
        return followees is not None and user_b in followees


if __name__ == "__main__":
    network = SocialNetwork()
    network.addUser("Nina")
    network.addUser("Omar")
    network.addUser("Pia")

    network.follow("Nina", "Omar")
    network.follow("Pia", "Omar")

    snap0 = network.createSnapshot()
    network.unfollow("Nina", "Omar")

    print(network.getFollowers("Omar"))                       # ['Pia']
    print(network.isFollowInSnapshot(snap0, "Nina", "Omar"))  # True
    print(network.isFollowInSnapshot(snap0, "Pia", "Omar"))   # True

    # The live graph reflects the unfollow; the snapshot does not.
    print(network.getFollowees("Nina"))                       # []
    # Duplicate follow is a single relationship.
    network.follow("Pia", "Omar")
    print(network.getFollowers("Omar"))                       # ['Pia']
    # Unknown snapshot id -> False.
    print(network.isFollowInSnapshot(99, "Pia", "Omar"))      # False
