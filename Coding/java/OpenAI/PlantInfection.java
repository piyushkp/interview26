import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Compute Plant Infection Time (multi-source BFS, a.k.a. "Rotting Oranges").
 *
 * Grid values: 0 = empty ground, 1 = healthy plant, 2 = infected plant,
 * -1 = wall/blocked. Each minute every infected plant infects its
 * orthogonally adjacent healthy plants. Return the minutes until no plant
 * can be infected, or -1 if some healthy plant is unreachable, or 0 if
 * there are no healthy plants to begin with.
 */
public class PlantInfection {

    /**
     * Time:  O(m * n) - each cell is enqueued/visited at most once.
     * Space: O(m * n) - the BFS frontier in the worst case.
     */
    public static int infectionTime(int[][] grid) {
        if (grid == null || grid.length == 0 || grid[0].length == 0) {
            return 0; // no plants at all -> nothing to infect
        }
        int m = grid.length, n = grid[0].length;
        Deque<int[]> queue = new ArrayDeque<>();
        int healthy = 0;

        // Seed the BFS with every initially-infected plant; count healthy ones.
        for (int r = 0; r < m; r++) {
            for (int c = 0; c < n; c++) {
                if (grid[r][c] == 2) {
                    queue.offer(new int[] {r, c});
                } else if (grid[r][c] == 1) {
                    healthy++;
                }
            }
        }
        if (healthy == 0) {
            return 0; // nothing healthy -> 0 minutes
        }

        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int minutes = 0;

        // Expand the infection one layer (one minute) at a time.
        while (!queue.isEmpty() && healthy > 0) {
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                int[] cell = queue.poll();
                for (int[] d : dirs) {
                    int nr = cell[0] + d[0], nc = cell[1] + d[1];
                    if (nr >= 0 && nr < m && nc >= 0 && nc < n && grid[nr][nc] == 1) {
                        grid[nr][nc] = 2; // infect (also marks visited)
                        healthy--;
                        queue.offer(new int[] {nr, nc});
                    }
                }
            }
            minutes++;
        }

        // Any healthy plant left was unreachable.
        return healthy == 0 ? minutes : -1;
    }
}
