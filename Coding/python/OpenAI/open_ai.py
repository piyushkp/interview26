"""Driver that exercises each interview module (port of OpenAi.java). Every
module lives in its own file in this package:
  - social_recommendations - friend-of-friend follow recommendations.
  - plant_infection        - multi-source BFS ("Rotting Oranges").
  - ip_addressing          - IPv4/IPv6 addressing toolkit.
  - labeling_schedule      - human/model/task labeling schedules.
  - chat_event_counter     - sliding 15-minute chat event window.
  - gpu_credit_manager     - GPU credits with expiration.
  - persistent_kv_store    - binary-safe persistent KV store.
  - in_memory_table        - in-memory SQL-like single table.
  - credit_ledger          - GPU credit ledger with out-of-order timestamps.
  - map_serializer         - length-prefixed, binary-safe map serialization.
  - sharded_kv_store       - persistent sharded KV store with replay restore.
  - gpu_credit_ledger      - idempotent GPU credit ledger (non-negative
                             balances).

Output is Python-native (True/False, quoted strings in lists, dict/bytes repr),
so it differs cosmetically from the Java driver's output
(true/false, unquoted).
"""

from chat_event_counter import ChatEventCounter
from credit_ledger import CreditLedger
from gpu_credit_ledger import GpuCreditLedger
from gpu_credit_manager import GpuCreditManager
from in_memory_table import InMemoryTable
from ip_addressing import (
    parse_ipv4, adjacent_ipv4, cidr_range, ip_in_cidr, adjacent_ipv6,
)
from labeling_schedule import any_schedule, prefix_balanced_schedule
from map_serializer import solution as map_solution
from persistent_kv_store import PersistentKvStore
from plant_infection import infection_time
from sharded_kv_store import ShardedKvStore
from social_recommendations import SocialRecommendations


def main():
    # --- Module 1: Social Follow Recommendations ---
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

    # --- Module 2: Plant Infection Time (multi-source BFS) ---
    print(infection_time([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))     # 4
    print(infection_time([[2, 1, -1], [-1, 1, 1], [1, -1, 1]]))  # -1
    # -> 0 (no healthy plants)
    print(infection_time([[0, 2, 0]]))

    # --- Module 3: IPv4 / IPv6 addressing toolkit ---
    # Part 1: validate & parse IPv4
    print(parse_ipv4("192.168.0.1"))  # [192, 168, 0, 1]
    print(parse_ipv4("0.0.0.0"))      # [0, 0, 0, 0]
    # Part 2: adjacent IPv4
    print(adjacent_ipv4("192.168.0.1", "up"))    # 192.168.0.2
    print(adjacent_ipv4("192.168.0.255", "up"))  # 192.168.1.0
    # Part 3: CIDR first & last
    print(cidr_range("192.168.0.0/24"))    # ['192.168.0.0', '192.168.0.255']
    print(cidr_range("192.168.5.123/24"))  # ['192.168.5.0', '192.168.5.255']
    # Part 4: membership
    print(ip_in_cidr("192.168.0.10", "192.168.0.0/24"))    # 1
    print(ip_in_cidr("192.168.0.200", "192.168.0.99/24"))  # 1
    # Part 5: adjacent IPv6 (period-separated)
    print(adjacent_ipv6("ffff.ffff.ffff.ffff.ffff.ffff.ffff.fffa", "up"))
    # ffff.ffff.ffff.ffff.ffff.ffff.ffff.fffb
    print(adjacent_ipv6("0000.0000.0000.0000.0000.0000.0000.ffff", "up"))
    # 0000.0000.0000.0000.0000.0000.0001.0000

    # --- Module 4: Labeling schedule generation ---
    # Part 1: any valid schedule
    print(any_schedule(3, 1, 2, 2))
    # [['t1', 'm1', 'h1'], ['t2', 'm1', 'h1'], ['t2', 'm1', 'h2'],
    #  ['t3', 'm1', 'h2']]
    print(any_schedule(1, 1, 1, 1))  # [['t1', 'm1', 'h1']]
    # Part 2: prefix-balanced schedule
    print(prefix_balanced_schedule(3, 2, 4, 2))
    # [['t1','m1','h1'], ['t1','m2','h2'], ['t1','m1','h3'], ['t1','m2','h4'],
    #  ['t2','m2','h1'], ['t2','m1','h2'], ['t2','m2','h3'], ['t2','m1','h4']]
    print(prefix_balanced_schedule(1, 1, 1, 1))  # [['t1', 'm1', 'h1']]

    # --- Module 5: Chat Event Counter (15-minute sliding window) ---
    chat1 = [
        ["processEvent", "u1", "c1", 100], ["processEvent", "u1", "c1", 200],
        ["processEvent", "u1", "c1", 1000], ["getCount", "u1", "c1"],
    ]
    print(ChatEventCounter.simulate(chat1))                      # [3]
    print(ChatEventCounter.simulate([["getCount", "u1", "c1"]]))  # [0]

    # --- Module 6: GPU Credits with Expiration ---
    gpu1 = [
        ["balance", 5], ["add", "a", 10, 5, 5], ["balance", 7],
        ["charge", 4, 8], ["balance", 8], ["balance", 10],
    ]
    print(GpuCreditManager.simulate(gpu1))  # [0, 10, True, 6, 0]

    gpu2 = [
        ["add", "a", 5, 10, 10], ["add", "b", 7, 5, 10], ["charge", 5, 12],
        ["balance", 12], ["balance", 17], ["charge", 6, 9], ["balance", 17],
    ]
    print(GpuCreditManager.simulate(gpu2))  # [True, 7, 5, False, 5]

    # --- Module 7: Persistent In-Memory KV Store ---
    by = PersistentKvStore.by
    # Part 1: serialize/deserialize a snapshot (str values)
    kv1 = [
        ["put", "a", "1"], ["get", "a"], ["serialize", "snap1"],
        ["put", "a", "2"], ["deserialize", "snap1"], ["get", "a"],
    ]
    # -> ['1', '1']
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part1(kv1)))
    # Part 1: binary-safe with delimiter-like bytes in key/value
    kv1b = [
        ["put", by("a|b"), by("v:1")], ["serialize", "p"],
        ["delete", by("a|b")],
        ["get", by("a|b")], ["deserialize", "p"], ["get", by("a|b")],
    ]
    # -> [None, b'v:1']
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part1(kv1b)))

    # Part 2: snapshot split across size-bounded segments
    kv2 = [
        ["put", by("a"), by("12345")], ["put", by("b"), by("67890")],
        ["serialize", "p"], ["segment_count", "p"], ["delete", by("a")],
        ["deserialize", "p"], ["get", by("a")], ["get", by("b")],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part2(15, kv2)))
    # [6, b'12345', b'67890']
    kv2b = [
        ["put", by("aa"), by("xx")], ["put", by("bb"), by("yy")],
        ["serialize", "snap"], ["segment_count", "snap"],
        ["reorder", "snap", [2, 0, 1]], ["delete", by("aa")],
        ["deserialize", "snap"], ["get", by("aa")], ["get", by("bb")],
    ]
    print(PersistentKvStore.py_repr(
        PersistentKvStore.simulate_part2(20, kv2b)))
    # [3, b'xx', b'yy']

    # Part 3: snapshot + append-only log with replay and compaction
    kv3 = [
        ["put", "a", "1"], ["put", "b", "2"], ["restart"],
        ["get", "a"], ["get", "b"], ["status"],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part3(3, kv3)))
    # ['1', '2', (2, 2, 0)]
    kv3b = [
        ["put", "x", "1"], ["status"], ["put", "y", "2"], ["status"],
        ["restart"], ["get", "x"], ["get", "y"], ["status"],
    ]
    print(PersistentKvStore.py_repr(PersistentKvStore.simulate_part3(2, kv3b)))
    # [(1, 1, 0), (2, 0, 1), '1', '2', (2, 0, 1)]

    # --- Module 8: In-memory SQL-like table ---
    sql1 = [
        "SET r1 name bob", "SET r1 age 2", "SET r2 name bob", "SET r2 age 10",
        "GET r1 name", "SELECT name bob age",
    ]
    print(InMemoryTable.process_commands(sql1))  # ['bob', 'r2 r1']

    sql2 = ["GET missing name", "SELECT status active score"]
    print(InMemoryTable.process_commands(sql2))  # ['NULL', '']

    # --- Module 9: Credit ledger with out-of-order timestamps ---
    led1 = [
        ["GRANT", "alice", 10, 5], ["CHARGE", "alice", 4, 7],
        ["GET", "alice", 7],
        ["CHARGE", "alice", 10, 6], ["GET", "alice", 7],
    ]
    print(CreditLedger.simulate(led1))  # [6, 0]

    led2 = [
        ["GRANT", "alice", 5, 10], ["GRANT", "bob", 7, 1],
        ["CHARGE", "bob", 2, 3],
        ["GET", "bob", 2], ["GET", "bob", 3], ["GET", "alice", 9],
        ["GET", "alice", 10],
    ]
    print(CreditLedger.simulate(led2))  # [7, 5, 0, 5]

    # --- Module 10: Map serialization (length-prefixed, binary-safe) ---
    print(map_solution("serialize", {}))       # 0#
    print(map_solution("deserialize", "0#"))    # {}
    sample_map = {"a": "hi", "b": ""}
    encoded = map_solution("serialize", sample_map)
    print(encoded)                              # 2#1#a2#hi1#b0#
    print(map_solution("deserialize", encoded))  # {'a': 'hi', 'b': ''}

    # --- Module 11: Persistent sharded KV store ---
    shard1 = [
        ["put", "a", "1"], ["put", "b", "22"], ["get", "a"],
        ["put", "a", "333"],
        ["get", "a"], ["restore"], ["get", "b"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(10, shard1)))
    # (['1', '333', '22'], ['P|a|1;', 'P|b|22;', 'P|a|333;'])
    shard2 = [
        ["put", "ab", "x"], ["put", "c", "yz"], ["delete", "ab"],
        ["get", "ab"],
        ["restore"], ["get", "c"], ["get", "ab"],
    ]
    print(ShardedKvStore.py_repr(ShardedKvStore.simulate(20, shard2)))
    # ([None, 'yz', None], ['P|ab|x;P|c|yz;D|ab;'])

    # --- Module 12: Idempotent GPU credit ledger (non-negative balances) ---
    led_init1 = [
        ["e1", "tenantA", 10], ["e2", "tenantA", -3], ["e3", "tenantB", 5],
    ]
    led_ops1 = [
        ["get", "tenantA"], ["get", "tenantB"],
        ["apply", ["e4", "tenantA", 2]],
        ["apply", ["e5", "tenantB", -6]], ["get", "tenantB"],
        ["apply", ["e6", "tenantA", -4]], ["get", "tenantB"],
    ]
    print(GpuCreditLedger.solution(led_init1, led_ops1))
    # [7, 5, True, False, 5, True, 5]
    led_ops2 = [
        ["get", "ghost"], ["apply", ["x1", "ghost", -3]], ["get", "ghost"],
        ["apply", ["x1", "ghost", -3]], ["apply", ["x2", "ghost", 4]],
        ["get", "ghost"],
    ]
    print(GpuCreditLedger.solution([], led_ops2))
    # [0, False, 0, False, True, 4]


if __name__ == "__main__":
    main()
