"""Social Follow Recommendations over an in-memory directed graph.

A -> B means user A follows user B. follow/unfollow mutate hash-based adjacency
sets in O(1) average time; recommend(user_id, k) uses a friend-of-friend rule,
ranking candidates by the number of distinct intermediate users that connect
user_id to the candidate.
"""


def _candidate_rank(item):
    """Sort key for a (candidate, intermediate_count) pair: more shared
    intermediates first (higher count), then smaller candidate id first."""
    # Time: O(1), Space: O(1) - unpacks a pair into a two-field tuple.
    candidate, count = item
    return (-count, candidate)


# Approach (in plain terms):
#   Picture everyone's "following" list as a page in an address book naming who
#   they follow. To suggest new people for someone, we use "friends of
#   friends": look at each person they already follow, then look at who THOSE
#   people follow. Every time one of your follows points at the same stranger,
#   that stranger earns a point - more shared connections means a better
#   suggestion. We skip yourself and anyone you already follow. Finally we hand
#   back the top k strangers, most points first, breaking ties by the smaller
#   id so the answer is always predictable.
#   Data structures used:
#     - a dict mapping user -> set of followees (adjacency list) -
#       set gives O(1) follow/unfollow and automatic de-duplication.
#     - a dict counting candidate -> number of mutual intermediaries
#       - ranks friend-of-friend suggestions.
class SocialRecommendations:

    def __init__(self):
        # Time: O(1), Space: O(1) - starts with an empty adjacency map.
        # adjacency set: user -> set of users they follow.
        self._following = {}

    def follow(self, follower_id, followee_id):
        """Add a directed edge follower -> followee. Self-follows and
        duplicates are ignored."""
        # Time: O(1) average - a dict lookup plus a set add.
        # Space: O(1) amortized - may store one new followee.
        if follower_id == followee_id:
            return  # self-follow is ignored
        # setdefault + set.add naturally dedupes duplicate follows.
        self._following.setdefault(follower_id, set()).add(followee_id)

    def unfollow(self, follower_id, followee_id):
        """Remove the edge follower -> followee if present; otherwise a
        no-op."""
        # Time: O(1) average - a dict lookup plus a set discard. Space: O(1).
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
        # d = users user_id follows, E = total second-hop edges scanned,
        # c = number of distinct candidates found (c <= E).
        # Time:  O(E + c log c) - scan every second-hop edge, then sort
        #        candidates.
        # Space: O(c) - the score map and the ranked list of candidates.
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

        # Collect (candidate, count) pairs so a plain named key can rank them.
        ranked = []
        for candidate in score:
            ranked.append((candidate, score[candidate]))

        # Rank: higher score first, then smaller id first.
        ranked.sort(key=_candidate_rank)

        # Take the top k candidate ids, dropping the counts.
        limit = min(k, len(ranked))
        for index in range(limit):
            result.append(ranked[index][0])
        return result

    @staticmethod
    def process_queries(queries):
        """Process queries in order, returning the result of every
        recommend."""
        # q = number of queries; each recommend costs up to O(E + c log c)
        # (see recommend), while follow/unfollow are O(1) average.
        # Time:  O(q * (E + c log c)) worst case.
        # Space: O(V + total_edges + q) - the stored graph plus the answers
        #        list.
        network = SocialRecommendations()
        answers = []
        for query in queries:
            op, a, b = query[0], query[1], query[2]
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
    # Test 1: user 1 -> {2,3}; 4 is reached by both 2 and 3 (score 2) so ranks
    # first.
    ex1 = [
        ["follow", 1, 2], ["follow", 1, 3], ["follow", 2, 4], ["follow", 3, 4],
        ["follow", 2, 5], ["follow", 3, 6], ["recommend", 1, 3],
    ]
    print(SocialRecommendations.process_queries(ex1))  # [[4, 5, 6]]

    # Test 2: self-follows/duplicates ignored; unfollow empties 1's set -> no
    # recs.
    ex2 = [
        ["follow", 1, 1], ["follow", 1, 2], ["follow", 1, 2], ["follow", 2, 1],
        ["follow", 2, 3], ["recommend", 1, 5], ["unfollow", 1, 4],
        ["unfollow", 1, 2], ["recommend", 1, 5],
    ]
    print(SocialRecommendations.process_queries(ex2))  # [[3], []]

    # Test 3: recommend for an unknown user who follows nobody -> empty list.
    ex3 = [
        ["recommend", 99, 3],
    ]
    print(SocialRecommendations.process_queries(ex3))  # [[]]

    # Test 4: k = 0 returns an empty list even when candidates exist.
    ex4 = [
        ["follow", 1, 2], ["follow", 2, 3], ["recommend", 1, 0],
    ]
    print(SocialRecommendations.process_queries(ex4))  # [[]]

    # Test 5: equal scores are tie-broken by the smaller candidate id.
    ex5 = [
        ["follow", 1, 2], ["follow", 1, 3], ["follow", 2, 9], ["follow", 3, 8],
        ["recommend", 1, 5],
    ]
    print(SocialRecommendations.process_queries(ex5))  # [[8, 9]]

    # Test 6: a candidate you already follow is excluded from recommendations.
    ex6 = [
        ["follow", 1, 2], ["follow", 1, 3],
        ["follow", 2, 3], ["recommend", 1, 5],
    ]
    print(SocialRecommendations.process_queries(ex6))  # [[]]

    # Test 7: k smaller than the candidate count returns only the top k.
    ex7 = [
        ["follow", 1, 2], ["follow", 1, 3], ["follow", 2, 4], ["follow", 3, 4],
        ["follow", 2, 5], ["follow", 3, 6], ["recommend", 1, 2],
    ]
    print(SocialRecommendations.process_queries(ex7))  # [[4, 5]]

    # Test 8: duplicate follows don't inflate a candidate's score.
    ex8 = [
        ["follow", 1, 2], ["follow", 1, 2],
        ["follow", 2, 5], ["recommend", 1, 5],
    ]
    print(SocialRecommendations.process_queries(ex8))  # [[5]]

    # Test 9: unfollowing an intermediate removes the paths it provided.
    ex9 = [
        ["follow", 1, 2], ["follow", 1, 3], ["follow", 2, 4], ["follow", 3, 4],
        ["unfollow", 1, 3], ["recommend", 1, 5],
    ]
    print(SocialRecommendations.process_queries(ex9))  # [[4]]
