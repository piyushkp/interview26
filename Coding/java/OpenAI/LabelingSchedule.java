import java.util.ArrayList;
import java.util.List;

/**
 * Generate labeling schedules. An assignment is [taskId, modelId, humanId];
 * tasks are t1..t{totalTask}, models m1..m{totalModel}, humans h1..h{totalHuman}.
 * Every human must appear in at least k assignments, the same human never
 * annotates the same task twice, and every ID must be valid. Returns an empty
 * list if no valid schedule exists.
 *   - {@link #anySchedule}            Part 1: any valid schedule.
 *   - {@link #prefixBalancedSchedule} Part 2: additionally prefix-balanced.
 */
public class LabelingSchedule {

    /**
     * Part 1: any valid schedule. Each human gets k distinct tasks; the
     * reference rotates each human's starting task by the human index
     * (human i takes tasks (i+0)..(i+k-1) mod totalTask). Model is always m1
     * (Part 1 imposes no model constraint).
     */
    public static List<List<String>> anySchedule(int totalTask, int totalModel,
                                                  int totalHuman, int k) {
        List<List<String>> result = new ArrayList<>();
        if (k == 0) {
            return result; // no assignments required -> empty schedule is valid
        }
        if (k > totalTask) {
            return result; // cannot give a human k distinct tasks -> impossible
        }
        for (int i = 0; i < totalHuman; i++) {       // human index (human-major order)
            for (int j = 0; j < k; j++) {            // j-th distinct task for this human
                int taskIndex = (i + j) % totalTask;
                result.add(triple("t" + (taskIndex + 1), "m1", "h" + (i + 1)));
            }
        }
        return result;
    }

    /**
     * Part 2: a prefix-balanced schedule. Emitted in k rounds; round r assigns
     * task t{r+1} to every human, with human i using model
     * m{((i + r) % totalModel) + 1}. Within a round the model index cycles as
     * humans advance, so each task stays model-balanced at every prefix; across
     * rounds each human's model index advances by one, so each human stays
     * model-balanced too. Hence every prefix satisfies both balance rules.
     */
    public static List<List<String>> prefixBalancedSchedule(int totalTask, int totalModel,
                                                            int totalHuman, int k) {
        List<List<String>> result = new ArrayList<>();
        if (k == 0) {
            return result;
        }
        if (k > totalTask) {
            return result;
        }
        for (int r = 0; r < k; r++) {                // round r -> task t{r+1}
            for (int i = 0; i < totalHuman; i++) {   // human index
                int modelIndex = (i + r) % totalModel;
                result.add(triple("t" + (r + 1), "m" + (modelIndex + 1), "h" + (i + 1)));
            }
        }
        return result;
    }

    private static List<String> triple(String task, String model, String human) {
        List<String> a = new ArrayList<>(3);
        a.add(task);
        a.add(model);
        a.add(human);
        return a;
    }
}
