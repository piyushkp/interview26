public class MinStepsToZero {

    public static int minSteps(long n) {
        int steps = 0;
        while (n > 0) {
            if ((n & 1) == 0) {
                n >>= 1;              // even: shift for free
            } else if ((n & 3) == 1) {
                n--;                  // ends in 01: subtract
                steps++;
            } else {
                n++;                  // ends in 11: add, carry merges the 1s
                steps++;
            }
        }
        return steps;
    }

    public static void main(String[] args) {
        System.out.println(minSteps(14));                // 2
        System.out.println(minSteps(27));                // 3
        System.out.println(minSteps(1));                 // 1
        System.out.println(minSteps(3));                 // 2
        System.out.println(minSteps(15));                // 2
        System.out.println(minSteps(1L << 30));          // 1
        System.out.println(minSteps(Integer.MAX_VALUE)); // 2
    }
}
