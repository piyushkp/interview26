import java.util.List;

/**
 * Driver that exercises each interview module. Every module now lives in its
 * own top-level class in the default package:
 *   - {@link SocialRecommendations} - friend-of-friend follow recommendations.
 *   - {@link PlantInfection}        - multi-source BFS ("Rotting Oranges").
 *   - {@link IpAddressing}          - IPv4/IPv6 addressing toolkit.
 *   - {@link LabelingSchedule}      - human/model/task labeling schedules.
 *   - {@link ChatEventCounter}      - sliding 15-minute chat event window.
 *   - {@link GpuCreditManager}      - GPU credits with expiration.
 *   - {@link PersistentKvStore}     - binary-safe persistent KV store.
 *   - {@link InMemoryTable}         - in-memory SQL-like single table.
 *   - {@link CreditLedger}          - GPU credit ledger with out-of-order timestamps.
 *   - {@link MapSerializer}         - length-prefixed, binary-safe map serialization.
 *   - {@link ShardedKvStore}        - persistent sharded KV store with replay restore.
 *   - {@link GpuCreditLedger}       - idempotent GPU credit ledger (non-negative balances).
 */
public class OpenAi {

    // ====================================================================
    // Demos for all modules
    // ====================================================================
    public static void main(String[] args) {
        // --- Module 1: Social Follow Recommendations ---
        Object[][] ex1 = {
            {"follow", 1, 2}, {"follow", 1, 3}, {"follow", 2, 4}, {"follow", 3, 4},
            {"follow", 2, 5}, {"follow", 3, 6}, {"recommend", 1, 3}
        };
        System.out.println(SocialRecommendations.processQueries(ex1)); // [[4, 5, 6]]

        Object[][] ex2 = {
            {"follow", 1, 1}, {"follow", 1, 2}, {"follow", 1, 2}, {"follow", 2, 1},
            {"follow", 2, 3}, {"recommend", 1, 5}, {"unfollow", 1, 4},
            {"unfollow", 1, 2}, {"recommend", 1, 5}
        };
        System.out.println(SocialRecommendations.processQueries(ex2)); // [[3], []]

        // --- Module 2: Plant Infection Time (multi-source BFS) ---
        int[][] grid1 = {{2, 1, 1}, {1, 1, 0}, {0, 1, 1}};
        System.out.println(PlantInfection.infectionTime(grid1)); // 4

        int[][] grid2 = {{2, 1, -1}, {-1, 1, 1}, {1, -1, 1}};
        System.out.println(PlantInfection.infectionTime(grid2)); // -1

        int[][] grid3 = {{0, 2, 0}}; // no healthy plants
        System.out.println(PlantInfection.infectionTime(grid3)); // 0

        // --- Module 3: IPv4 / IPv6 addressing toolkit ---
        // Part 1: validate & parse IPv4
        System.out.println(IpAddressing.parseIPv4("192.168.0.1")); // [192, 168, 0, 1]
        System.out.println(IpAddressing.parseIPv4("0.0.0.0"));     // [0, 0, 0, 0]
        // Part 2: adjacent IPv4
        System.out.println(IpAddressing.adjacentIPv4("192.168.0.1", "up"));   // 192.168.0.2
        System.out.println(IpAddressing.adjacentIPv4("192.168.0.255", "up")); // 192.168.1.0
        // Part 3: CIDR first & last
        System.out.println(IpAddressing.cidrRange("192.168.0.0/24"));   // [192.168.0.0, 192.168.0.255]
        System.out.println(IpAddressing.cidrRange("192.168.5.123/24")); // [192.168.5.0, 192.168.5.255]
        // Part 4: membership
        System.out.println(IpAddressing.ipInCidr("192.168.0.10", "192.168.0.0/24"));   // 1
        System.out.println(IpAddressing.ipInCidr("192.168.0.200", "192.168.0.99/24")); // 1
        // Part 5: adjacent IPv6 (period-separated)
        System.out.println(IpAddressing.adjacentIPv6("ffff.ffff.ffff.ffff.ffff.ffff.ffff.fffa", "up"));
        // ffff.ffff.ffff.ffff.ffff.ffff.ffff.fffb
        System.out.println(IpAddressing.adjacentIPv6("0000.0000.0000.0000.0000.0000.0000.ffff", "up"));
        // 0000.0000.0000.0000.0000.0000.0001.0000

        // --- Module 4: Labeling schedule generation ---
        // Part 1: any valid schedule (Java prints without quotes; values match the reference)
        System.out.println(LabelingSchedule.anySchedule(3, 1, 2, 2));
        // [[t1, m1, h1], [t2, m1, h1], [t2, m1, h2], [t3, m1, h2]]
        System.out.println(LabelingSchedule.anySchedule(1, 1, 1, 1)); // [[t1, m1, h1]]
        // Part 2: prefix-balanced schedule
        System.out.println(LabelingSchedule.prefixBalancedSchedule(3, 2, 4, 2));
        // [[t1,m1,h1],[t1,m2,h2],[t1,m1,h3],[t1,m2,h4],[t2,m2,h1],[t2,m1,h2],[t2,m2,h3],[t2,m1,h4]]
        System.out.println(LabelingSchedule.prefixBalancedSchedule(1, 1, 1, 1)); // [[t1, m1, h1]]

        // --- Module 5: Chat Event Counter (15-minute sliding window) ---
        Object[][] chat1 = {
            {"processEvent", "u1", "c1", 100}, {"processEvent", "u1", "c1", 200},
            {"processEvent", "u1", "c1", 1000}, {"getCount", "u1", "c1"}
        };
        System.out.println(ChatEventCounter.simulate(chat1)); // [3]

        Object[][] chat2 = {{"getCount", "u1", "c1"}};
        System.out.println(ChatEventCounter.simulate(chat2)); // [0]

        // --- Module 6: GPU Credits with Expiration ---
        Object[][] gpu1 = {
            {"balance", 5}, {"add", "a", 10, 5, 5}, {"balance", 7},
            {"charge", 4, 8}, {"balance", 8}, {"balance", 10}
        };
        System.out.println(GpuCreditManager.simulate(gpu1)); // [0, 10, true, 6, 0]

        Object[][] gpu2 = {
            {"add", "a", 5, 10, 10}, {"add", "b", 7, 5, 10}, {"charge", 5, 12},
            {"balance", 12}, {"balance", 17}, {"charge", 6, 9}, {"balance", 17}
        };
        System.out.println(GpuCreditManager.simulate(gpu2)); // [true, 7, 5, false, 5]

        // --- Module 7: Persistent In-Memory KV Store ---
        // Part 1: serialize/deserialize a snapshot (str values)
        Object[][] kv1 = {
            {"put", "a", "1"}, {"get", "a"}, {"serialize", "snap1"},
            {"put", "a", "2"}, {"deserialize", "snap1"}, {"get", "a"}
        };
        System.out.println(PersistentKvStore.pyRepr(PersistentKvStore.simulatePart1(kv1))); // ['1', '1']
        // Part 1: binary-safe with delimiter-like bytes in key/value
        Object[][] kv1b = {
            {"put", PersistentKvStore.by("a|b"), PersistentKvStore.by("v:1")},
            {"serialize", "p"}, {"delete", PersistentKvStore.by("a|b")},
            {"get", PersistentKvStore.by("a|b")}, {"deserialize", "p"},
            {"get", PersistentKvStore.by("a|b")}
        };
        System.out.println(PersistentKvStore.pyRepr(PersistentKvStore.simulatePart1(kv1b))); // [None, b'v:1']

        // Part 2: snapshot split across size-bounded segments
        Object[][] kv2 = {
            {"put", PersistentKvStore.by("a"), PersistentKvStore.by("12345")},
            {"put", PersistentKvStore.by("b"), PersistentKvStore.by("67890")},
            {"serialize", "p"}, {"segment_count", "p"}, {"delete", PersistentKvStore.by("a")},
            {"deserialize", "p"}, {"get", PersistentKvStore.by("a")}, {"get", PersistentKvStore.by("b")}
        };
        System.out.println(PersistentKvStore.pyRepr(PersistentKvStore.simulatePart2(15, kv2)));
        // [6, b'12345', b'67890']
        Object[][] kv2b = {
            {"put", PersistentKvStore.by("aa"), PersistentKvStore.by("xx")},
            {"put", PersistentKvStore.by("bb"), PersistentKvStore.by("yy")},
            {"serialize", "snap"}, {"segment_count", "snap"},
            {"reorder", "snap", new int[] {2, 0, 1}}, {"delete", PersistentKvStore.by("aa")},
            {"deserialize", "snap"}, {"get", PersistentKvStore.by("aa")}, {"get", PersistentKvStore.by("bb")}
        };
        System.out.println(PersistentKvStore.pyRepr(PersistentKvStore.simulatePart2(20, kv2b)));
        // [3, b'xx', b'yy']

        // Part 3: snapshot + append-only log with replay and compaction
        Object[][] kv3 = {
            {"put", "a", "1"}, {"put", "b", "2"}, {"restart"},
            {"get", "a"}, {"get", "b"}, {"status"}
        };
        System.out.println(PersistentKvStore.pyRepr(PersistentKvStore.simulatePart3(3, kv3)));
        // ['1', '2', (2, 2, 0)]
        Object[][] kv3b = {
            {"put", "x", "1"}, {"status"}, {"put", "y", "2"}, {"status"},
            {"restart"}, {"get", "x"}, {"get", "y"}, {"status"}
        };
        System.out.println(PersistentKvStore.pyRepr(PersistentKvStore.simulatePart3(2, kv3b)));
        // [(1, 1, 0), (2, 0, 1), '1', '2', (2, 0, 1)]

        // --- Module 8: In-memory SQL-like table ---
        List<String> sql1 = java.util.Arrays.asList(
            "SET r1 name bob", "SET r1 age 2", "SET r2 name bob", "SET r2 age 10",
            "GET r1 name", "SELECT name bob age"
        );
        System.out.println(InMemoryTable.processCommands(sql1)); // [bob, r2 r1]

        List<String> sql2 = java.util.Arrays.asList("GET missing name", "SELECT status active score");
        System.out.println(InMemoryTable.processCommands(sql2)); // [NULL, ]

        // --- Module 9: Credit ledger with out-of-order timestamps ---
        Object[][] led1 = {
            {"GRANT", "alice", 10, 5}, {"CHARGE", "alice", 4, 7}, {"GET", "alice", 7},
            {"CHARGE", "alice", 10, 6}, {"GET", "alice", 7}
        };
        System.out.println(CreditLedger.simulate(led1)); // [6, 0]

        Object[][] led2 = {
            {"GRANT", "alice", 5, 10}, {"GRANT", "bob", 7, 1}, {"CHARGE", "bob", 2, 3},
            {"GET", "bob", 2}, {"GET", "bob", 3}, {"GET", "alice", 9}, {"GET", "alice", 10}
        };
        System.out.println(CreditLedger.simulate(led2)); // [7, 5, 0, 5]

        // --- Module 10: Map serialization (length-prefixed, binary-safe) ---
        java.util.Map<String, String> emptyMap = new java.util.LinkedHashMap<>();
        System.out.println(MapSerializer.solution("serialize", emptyMap));   // 0#
        System.out.println(MapSerializer.solution("deserialize", "0#"));      // {}
        java.util.Map<String, String> sampleMap = new java.util.LinkedHashMap<>();
        sampleMap.put("a", "hi");
        sampleMap.put("b", "");
        String encoded = (String) MapSerializer.solution("serialize", sampleMap);
        System.out.println(encoded);                                          // 2#1#a2#hi1#b0#
        System.out.println(MapSerializer.solution("deserialize", encoded));   // {a=hi, b=}

        // --- Module 11: Persistent sharded KV store ---
        Object[][] shard1 = {
            {"put", "a", "1"}, {"put", "b", "22"}, {"get", "a"}, {"put", "a", "333"},
            {"get", "a"}, {"restore"}, {"get", "b"}
        };
        System.out.println(ShardedKvStore.pyRepr(ShardedKvStore.simulate(10, shard1)));
        // (['1', '333', '22'], ['P|a|1;', 'P|b|22;', 'P|a|333;'])
        Object[][] shard2 = {
            {"put", "ab", "x"}, {"put", "c", "yz"}, {"delete", "ab"}, {"get", "ab"},
            {"restore"}, {"get", "c"}, {"get", "ab"}
        };
        System.out.println(ShardedKvStore.pyRepr(ShardedKvStore.simulate(20, shard2)));
        // ([None, 'yz', None], ['P|ab|x;P|c|yz;D|ab;'])

        // --- Module 12: Idempotent GPU credit ledger (non-negative balances) ---
        Object[][] ledInit1 = {
            {"e1", "tenantA", 10}, {"e2", "tenantA", -3}, {"e3", "tenantB", 5}
        };
        Object[][] ledOps1 = {
            {"get", "tenantA"}, {"get", "tenantB"}, {"apply", new Object[] {"e4", "tenantA", 2}},
            {"apply", new Object[] {"e5", "tenantB", -6}}, {"get", "tenantB"},
            {"apply", new Object[] {"e6", "tenantA", -4}}, {"get", "tenantB"}
        };
        System.out.println(GpuCreditLedger.solution(ledInit1, ledOps1));
        // [7, 5, true, false, 5, true, 5]
        Object[][] ledOps2 = {
            {"get", "ghost"}, {"apply", new Object[] {"x1", "ghost", -3}}, {"get", "ghost"},
            {"apply", new Object[] {"x1", "ghost", -3}}, {"apply", new Object[] {"x2", "ghost", 4}},
            {"get", "ghost"}
        };
        System.out.println(GpuCreditLedger.solution(new Object[0][], ledOps2));
        // [0, false, 0, false, true, 4]
    }
}
