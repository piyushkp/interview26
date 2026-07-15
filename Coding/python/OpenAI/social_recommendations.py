"""Social Follow Recommendations over an in-memory directed graph.

A -> B means user A follows user B. follow/unfollow mutate hash-based adjacency
sets in O(1) average time; recommend(user_id, k) uses a friend-of-friend rule,
ranking candidates by the number of distinct intermediate users that connect
user_id to the candidate.
"""


class SocialRecommendations:

    def __init__(self):
        # adjacency set: user -> set of users they follow.
        self._following = {}

    def follow(self, follower_id, followee_id):
        """Add a directed edge follower -> followee. Self-follows and duplicates
        are ignored."""
        if follower_id == followee_id:
            return  # self-follow is ignored
        # setdefault + set.add naturally dedupes duplicate follows.
        self._following.setdefault(follower_id, set()).add(followee_id)

    def unfollow(self, follower_id, followee_id):
        """Remove the edge follower -> followee if present; otherwise a no-op."""
        followees = self._following.get(follower_id)
        if followees is not None:
            followees.discard(followee_id)
            if not followees:
                self._following.pop(follower_id, None)  # keep the map tidy

    def recommend(self, user_id, k):
        """Up to k friend-of-friend recommendations for user_id.

        A candidate is anyone followed by someone user_id already follows,
        excluding user_id and anyone user_id already follows. Candidates are
        ranked by the count of distinct intermediates (desc), ties broken by
        smaller user_id first."""
        result = []
        if k <= 0:
            return result
        direct = self._following.get(user_id)
        if not direct:
            return result  # follows nobody -> no friend-of-friend candidates

        # Count how many distinct intermediates reach each candidate.
        score = {}
        for intermediate in direct:
            second_hop = self._following.get(intermediate)
            if second_hop is None:
                continue
            for candidate in second_hop:
                if candidate == user_id or candidate in direct:
                    continue  # exclude self and already-followed users
                score[candidate] = score.get(candidate, 0) + 1

        # Rank: higher score first, then smaller id first.
        candidates = sorted(score.keys(), key=lambda c: (-score[c], c))
        limit = min(k, len(candidates))
        return candidates[:limit]

    @staticmethod
    def process_queries(queries):
        """Process queries in order, returning the result of every recommend."""
        network = SocialRecommendations()
        answers = []
        for q in queries:
            op, a, b = q[0], q[1], q[2]
            if op == "follow":
                network.follow(a, b)
            elif op == "unfollow":
                network.unfollow(a, b)
            elif op == "recommend":
                answers.append(network.recommend(a, b))
            else:
                raise ValueError(f"Unknown op: {op}")
        return answers


if __name__ == "__main__":
    ex1 = [
        ["follow", 1, 2], ["follow", 1, 3], ["follow", 2, 4], ["follow", 3, 4],
        ["follow", 2, 5], ["follow", 3, 6], ["recommend", 1, 3],
    ]
    print(SocialRecommendations.process_queries(ex1))  # [[4, 5, 6]]
    ex2 = [
        ["follow", 1, 1], ["follow", 1, 2], ["follow", 1, 2], ["follow", 2, 1],
        ["follow", 2, 3], ["recommend", 1, 5], ["unfollow", 1, 4],
        ["unfollow", 1, 2], ["recommend", 1, 5],
    ]
    print(SocialRecommendations.process_queries(ex2))  # [[3], []]
