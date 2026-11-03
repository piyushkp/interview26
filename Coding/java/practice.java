import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class practice {

    public static void main(String[] args) {
        Set<String> dictionary = new HashSet<>(
                Arrays.asList("the", "sky", "is", "blue"));
        String sentence = restoreSpaces("theskyisblue", dictionary);
        if (!"the sky is blue".equals(sentence)
                || !"ca rs".equals(restoreSpaces("cars",
                        new HashSet<>(Arrays.asList("car", "ca", "rs"))))
                || !"".equals(restoreSpaces("", dictionary))
                || restoreSpaces("unknown", dictionary) != null
                || restoreSpaces("a", Collections.emptySet()) != null
                || !"a".equals(restoreSpaces("a",
                        new HashSet<>(Arrays.asList("", "a"))))) {
            throw new AssertionError("restoreSpaces test failed");
        }
        System.out.println(sentence);
        System.out.println("All restoreSpaces tests passed.");
        if (!"the sky is blue".equals(
                    restoreSpacesBruteForce("theskyisblue", dictionary))
                || !"ca rs".equals(restoreSpacesBruteForce("cars",
                        new HashSet<>(Arrays.asList("car", "ca", "rs"))))
                || !"".equals(restoreSpacesBruteForce("", dictionary))
                || restoreSpacesBruteForce("unknown", dictionary) != null) {
            throw new AssertionError("Brute-force test failed");
        }
        System.out.println("All brute-force tests passed.");
    }

    public static String restoreSpacesBruteForce(
            String text, Set<String> dictionary) {
        List<String> words = new ArrayList<>();
        if (findWords(text, 0, dictionary, words)) {
            return String.join(" ", words);
        }
        return null;
    }

    private static boolean findWords(String text, int start,
            Set<String> dictionary, List<String> words) {
        if (start == text.length()) {
            return true;
        }

        for (int end = text.length(); end > start; end--) {
            String word = text.substring(start, end);
            if (dictionary.contains(word)) {
                words.add(word);
                if (findWords(text, end, dictionary, words)) {
                    return true;
                }
                words.remove(words.size() - 1);
            }
        }
        return false;
    }

    public static String restoreSpaces(String text, Set<String> dictionary) {
        int[] previous = new int[text.length() + 1];
        Arrays.fill(previous, -1);
        previous[0] = 0;

        for (int start = 0; start < text.length(); start++) {
            if (previous[start] == -1) {
                continue;
            }
            for (String word : dictionary) {
                if (word.isEmpty()) {
                    continue;
                }
                int end = start + word.length();
                if (end <= text.length() && previous[end] == -1
                        && text.startsWith(word, start)) {
                    previous[end] = start;
                }
            }
        }

        if (previous[text.length()] == -1) {
            return null;
        }

        List<String> words = new ArrayList<>();
        int end = text.length();
        while (end > 0) {
            int start = previous[end];
            words.add(text.substring(start, end));
            end = start;
        }
        Collections.reverse(words);
        return String.join(" ", words);
    }
    public static void mergeArray(int[] arr1, int[] arr2, int[] merged) {
       int i = 0; int j = 0; int k = 0;
       while(i < arr1.length && j < arr2.length)
       {
            if (arr1[i] < arr2[j]){
                merged[k++] = arr1[i++];
            }else{
                merged[k++] = arr2[j++];
            }
       }
       while(i < arr1.length)
           merged[k++] = arr1[i++];
       while(j < arr2.length)
           merged[k++] = arr2[j++];
    }
}
