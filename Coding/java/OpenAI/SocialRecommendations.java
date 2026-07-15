import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Social Follow Recommendations over an in-memory directed graph.
 *
 * A -> B means user A follows user B. follow/unfollow mutate hash-based
 * adjacency sets in O(1) average time; recommend(userId, k) uses a
 * friend-of-friend rule, ranking candidates by the number of distinct
 * intermediate users that connect userId to the candidate.
 */
public class SocialRecommendations {

    // adjacency set: user -> set of users they follow.
    private final Map<Integer, Set<Integer>> following = new HashMap<>();

    /** Add a directed edge follower -> followee. Self-follows and duplicates are ignored. */
    public void follow(int followerId, int followeeId) {
        if (followerId == followeeId) {
            return; // self-follow is ignored
        }
        // computeIfAbsent + Set.add naturally dedupes duplicate follows.
        following.computeIfAbsent(followerId, x -> new HashSet<>()).add(followeeId);
    }

    /** Remove the edge follower -> followee if present; otherwise a no-op. */
    public void unfollow(int followerId, int followeeId) {
        Set<Integer> followees = following.get(followerId);
        if (followees != null) {
            followees.remove(followeeId);
            if (followees.isEmpty()) {
                following.remove(followerId); // keep the map tidy
            }
        }
    }

    /**
     * Up to k friend-of-friend recommendations for userId.
     *
     * A candidate is anyone followed by someone userId already follows, excluding
     * userId and anyone userId already follows. Candidates are ranked by the count
     * of distinct intermediates linking userId to them (desc), ties broken by
     * smaller userId first.
     *
     * Time:  O(E + C log C) where E = edges scanned via userId's followees and
     *        C = number of candidates. Space: O(C).
     */
    public List<Integer> recommend(int userId, int k) {
        List<Integer> result = new ArrayList<>();
        if (k <= 0) {
            return result;
        }
        Set<Integer> direct = following.get(userId);
        if (direct == null || direct.isEmpty()) {
            return result; // follows nobody -> no friend-of-friend candidates
        }

        // Count how many distinct intermediates (direct follows) reach each candidate.
        Map<Integer, Integer> score = new HashMap<>();
        for (int intermediate : direct) {
            Set<Integer> secondHop = following.get(intermediate);
            if (secondHop == null) {
                continue;
            }
            for (int candidate : secondHop) {
                if (candidate == userId || direct.contains(candidate)) {
                    continue; // exclude self and already-followed users
                }
                score.merge(candidate, 1, Integer::sum);
            }
        }

        // Rank: higher score first, then smaller id first.
        List<Integer> candidates = new ArrayList<>(score.keySet());
        candidates.sort((a, b) -> {
            int byScore = Integer.compare(score.get(b), score.get(a));
            return byScore != 0 ? byScore : Integer.compare(a, b);
        });

        int limit = Math.min(k, candidates.size());
        for (int i = 0; i < limit; i++) {
            result.add(candidates.get(i));
        }
        return result;
    }

    /**
     * Process a sequence of operations in order, returning the result of every
     * recommend query in the order they appear. Each query is
     * {op, a, b} where op is "follow"/"unfollow"/"recommend"; for recommend,
     * a = userId and b = k.
     */
    public static List<List<Integer>> processQueries(Object[][] queries) {
        SocialRecommendations network = new SocialRecommendations();
        List<List<Integer>> answers = new ArrayList<>();
        for (Object[] q : queries) {
            String op = (String) q[0];
            int a = (int) q[1];
            int b = (int) q[2];
            switch (op) {
                case "follow":
                    network.follow(a, b);
                    break;
                case "unfollow":
                    network.unfollow(a, b);
                    break;
                case "recommend":
                    answers.add(network.recommend(a, b));
                    break;
                default:
                    throw new IllegalArgumentException("Unknown op: " + op);
            }
        }
        return answers;
    }
}
