"""Idiomatic Python 3 port of java/StringImp.java (original package code.ds).

A large collection of string / DSA interview reference implementations.

Conversion notes:
- Java class StringImp -> Python class StringImp. Java `static` methods become
  @staticmethod; the handful of methods that rely on Java instance fields remain
  instance methods (state initialised in __init__).
- Java StringBuilder/char[] mutation -> Python lists of chars + ''.join(...).
- HashMap -> dict, HashSet -> set, Deque/Queue/Stack -> collections.deque / list,
  PriorityQueue -> heapq, TreeMap -> dict (ordering not required by callers here).
- Java method overloading has no Python equivalent, so overloaded methods are
  renamed (see comments at each site).
- A few reference methods are intentionally buggy in the original Java; they are
  ported faithfully and are not exercised by the __main__ demo.
"""

import re
import heapq
from collections import deque
from functools import cmp_to_key

INT_MAX = 2147483647
INT_MIN = -2147483648


# ---------------------------------------------------------------------------
# Module-level helper data structures (Java inner classes)
# ---------------------------------------------------------------------------
class StreamNonRepeatingChar:
    """Find first non repeating character in a stream of characters.

    Uses a list plus a map so a character can be removed in O(1) once it
    appears more than once.
    """

    def __init__(self):
        self.list = []
        self.map = {}
        self.set = set()  # chars that appeared more than once

    def insert(self, c):
        if c not in self.set:
            if c in self.map:
                self.list.remove(self.map[c])
                del self.map[c]
                self.set.add(c)
            else:
                self.list.append(c)
                self.map[c] = c

    def get_non_repeating(self):
        return self.list[-1]


class TrieNode:
    def __init__(self):
        self.children = [None] * 26
        self.is_leaf = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def add(self, s):
        if s is None or len(s) == 0:
            return
        p = self.root
        for i in range(len(s)):
            c = s[i]
            idx = ord(c) - ord('a')
            if p.children[idx] is None:
                p.children[idx] = TrieNode()
            if i == len(s) - 1:
                p.children[idx].is_leaf = True
            p = p.children[idx]


class _BKTreeNode:
    def __init__(self, word):
        self.root_word = word
        self.children = {}  # distance -> _BKTreeNode

    def add(self, word):
        distance = BKTree.levenshtein_distance(word, self.root_word)
        child = self.children.get(distance)
        if child is not None:
            child.add(word)
        else:
            self.children[distance] = _BKTreeNode(word)


class BKTree:
    """Best solution for K edit distance / spell checker using a BK tree."""

    def __init__(self):
        self.root = None

    def add(self, word):
        if self.root is not None:
            self.root.add(word)
        else:
            self.root = _BKTreeNode(word)

    def search(self, query, max_distance):
        if query is None:
            raise ValueError("query must not be None")
        if max_distance < 0:
            raise ValueError("maxDistance must be non-negative")
        matches = []
        queue = deque()
        queue.append(self.root)
        while queue:
            node = queue.popleft()
            element = node.root_word
            distance = BKTree.levenshtein_distance(element, query)
            if distance <= max_distance:
                matches.append(element)
            for i in range(distance - max_distance, distance + max_distance + 1):
                if i > 0:
                    child_node = node.children.get(i)
                    if child_node is not None:
                        queue.append(child_node)
        return matches

    @staticmethod
    def levenshtein_distance(first, second):
        if len(first) == 0:
            return len(second)
        if len(second) == 0:
            return len(first)
        len_first = len(first)
        len_second = len(second)
        d = [[0] * (len_second + 1) for _ in range(len_first + 1)]
        for i in range(len_first + 1):
            d[i][0] = i
        for i in range(len_second + 1):
            d[0][i] = i
        for i in range(1, len_first + 1):
            for j in range(1, len_second + 1):
                match = 0 if first[i - 1] == second[j - 1] else 1
                d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + match)
        return d[len_first][len_second]


class TrieNode2:
    def __init__(self):
        self.next = [None] * 26
        self.index = -1
        self.list = []


class WordFreq:
    def __init__(self, word, freq):
        self.word = word
        self.freq = freq

    def __lt__(self, other):
        return self.freq < other.freq


class Count:
    """Node for word ladder BFS: word + distance from start."""

    def __init__(self, string, count):
        self.string = string
        self.count = count


class Token:
    """Token for the simple expression evaluator (overloaded constructor)."""

    def __init__(self, type_, value=0.0):
        self.type = type_
        self.value = value


class TrieNode1:
    def __init__(self):
        self.next = [None] * 26
        self.word = None


class Boggle:
    """Word-search-II style boggle solver using a trie over the board."""

    def build_trie(self, words):
        root = TrieNode1()
        for w in words:
            p = root
            for c in w:
                i = ord(c) - ord('a')
                if p.next[i] is None:
                    p.next[i] = TrieNode1()
                p = p.next[i]
            p.word = w
        return root

    def find_words(self, board, words):
        res = []
        root = self.build_trie(words)
        for i in range(len(board)):
            for j in range(len(board[0])):
                self.dfs(board, i, j, root, res)
        return res

    def dfs(self, board, i, j, p, res):
        c = board[i][j]
        if c == '#' or p.next[ord(c) - ord('a')] is None:
            return
        p = p.next[ord(c) - ord('a')]
        if p.word is not None:  # found one
            res.append(p.word)
            p.word = None  # de-duplicate
        board[i][j] = '#'
        if i > 0:
            self.dfs(board, i - 1, j, p, res)
        if j > 0:
            self.dfs(board, i, j - 1, p, res)
        if i < len(board) - 1:
            self.dfs(board, i + 1, j, p, res)
        if j < len(board[0]) - 1:
            self.dfs(board, i, j + 1, p, res)
        board[i][j] = c


class DictNode:
    """Trie node for the dynamic-programming boggle variant.

    Mirrors the Java inner class which starts insertion/lookup from the shared
    static root StringImp.root.
    """

    def __init__(self, letter):
        self.letter = letter
        self.next_nodes = [None] * 26
        self.word_end = False

    def insert(self, word):
        node = StringImp.root
        letters = list(word)
        for i in range(len(letters)):
            idx = ord(letters[i]) - ord('a')
            if node.next_nodes[idx] is None:
                node.next_nodes[idx] = DictNode(letters[i])
                if i == len(letters) - 1:
                    node.next_nodes[idx].word_end = True
            node = node.next_nodes[idx]

    def contains(self, word):
        node = StringImp.root
        letters = list(word)
        i = 0
        while i < len(letters) and node.next_nodes[ord(letters[i]) - ord('a')] is not None:
            node = node.next_nodes[ord(letters[i]) - ord('a')]
            i += 1
        return (i == len(letters)) and node.word_end


class TrieWordFinder:
    """Trie used by wordFinder; mirrors Java referencing the outer field root1."""

    def __init__(self, letter):
        self.letter = letter
        self.child = [None] * 26
        self.is_word = False

    def insert(self, word):
        node = StringImp.root1
        ch = list(word)
        for i in range(len(ch)):
            idx = ord(ch[i]) - ord('a')
            if node.child[idx] is None:
                node.child[idx] = TrieWordFinder(ch[i])
                if i == len(ch) - 1:
                    node.child[idx].is_word = True
            node = node.child[idx]

    def find_util(self, letters):
        out = set()
        node = StringImp.root1
        for i in range(len(letters)):
            word = ""
            while letters[i] > 0 and node.child[letters[i] - ord('a')] is not None:
                word += str(node.child[letters[i] - ord('a')].letter)
                if node.child[letters[i] - ord('a')].is_word:
                    out.add(word)
                node = node.child[letters[i] - ord('a')]
        return out

    def init(self, words):
        for word in words:
            self.insert(word)

    def find(self, letters):
        let = [0] * 26
        for i in range(len(letters)):
            index = ord(letters[i]) - ord('a')
            let[index] += 1
        return self.find_util(let)


class Graph:
    """Directed graph used to derive alien dictionary order via topo sort."""

    def __init__(self, n_vertices):
        self.adjacency_list = [[] for _ in range(n_vertices)]

    def add_edge(self, start_vertex, end_vertex):
        self.adjacency_list[start_vertex].append(end_vertex)

    def get_no_of_vertices(self):
        return len(self.adjacency_list)

    @staticmethod
    def alien_order(words, no_of_alpha):
        graph = Graph(no_of_alpha)
        for i in range(len(words) - 1):
            word1 = words[i]
            word2 = words[i + 1]
            for j in range(min(len(word1), len(word2))):
                if word1[j] != word2[j]:
                    graph.add_edge(ord(word1[j]) - ord('a'), ord(word2[j]) - ord('a'))
                    break
        return graph.topological_sort()

    def topological_sort(self):
        stack = []
        visited = set()
        for i in range(self.get_no_of_vertices()):
            if i not in visited:
                self.topological_sort_util(i, visited, stack)
        output = []
        while stack:
            output.append(chr(ord('a') + stack.pop()) + " ")
        # Faithful to Java: StringBuilder.reverse() reverses every character.
        return ''.join(output)[::-1]

    def topological_sort_util(self, current_vertex, visited, stack):
        visited.add(current_vertex)
        for adjacent_vertex in self.adjacency_list[current_vertex]:
            if adjacent_vertex not in visited:
                self.topological_sort_util(adjacent_vertex, visited, stack)
        stack.append(current_vertex)


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------
class StringImp:
    # Java static mutable fields
    memoized = {}
    count = 0
    root = None   # shared static root for the DP boggle DictNode trie
    board = None  # static board for the DP boggle variant
    root1 = None  # outer field referenced by TrieWordFinder (null in Java)

    # tiny URL alphabet
    ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    BASE = len("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

    # number-to-words tables
    one = ["", "one", "two", "three", "four", "five", "six", "seven", "eight",
           "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
           "sixteen", "seventeen", "eighteen", "nineteen"]
    ten = ["", "Ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
           "eighty", "ninety"]
    big = ["", "thousand", "million", "billion"]

    def __init__(self):
        # instance fields used by a few methods
        self.map = {}                  # wordBreakII / wordBreakIII memo
        self._map = {}                 # WordDistanceFinder
        self.abbr_dict = {}            # ValidWordAbbr
        self.unique_dict = set()       # ValidWordAbbr
        self.buffer = [''] * 4         # readII buffer
        self.offset = 0
        self.characters_in_buffer = 0

    # ----- small char helpers --------------------------------------------
    @staticmethod
    def _get_numeric_value(ch):
        """Mirror of Character.getNumericValue for digits/letters."""
        if ch.isdigit():
            return ord(ch) - ord('0')
        low = ch.lower()
        if 'a' <= low <= 'z':
            return ord(low) - ord('a') + 10
        return -1

    # Compress a given string. aaaaabbccc -> a5b2c3.  Time O(n) space O(n)
    @staticmethod
    def compress_string(s):
        if s is None or len(s) < 3:
            return s
        sb = []
        i = 0
        while i < len(s):
            sb.append(s[i])
            count = 1
            while i + 1 < len(s) and s[i + 1] == s[i]:
                i += 1
                count += 1
            sb.append(str(count))
            i += 1
        compressed = ''.join(sb)
        return s if len(compressed) >= len(s) else compressed

    # in-place compression. Time O(n) space O(1)
    @staticmethod
    def compress_in_place(chars):
        chars = list(chars)
        j = 0
        cnt = 1
        i = 1
        while i <= len(chars):
            if i < len(chars) and chars[i] == chars[i - 1]:
                cnt += 1
            else:
                chars[j] = chars[i - 1]
                j += 1
                if cnt != 1:
                    for c in str(cnt):
                        chars[j] = c
                        j += 1
                    cnt = 1
            i += 1
        return ''.join(chars[:j])

    # Run length encode. aabcccccaaa -> ab5c3a  (overload: encode(String))
    @staticmethod
    def encode_rle(source):
        dest = []
        i = 0
        while i < len(source):
            run_length = 1
            while i + 1 < len(source) and source[i] == source[i + 1]:
                run_length += 1
                i += 1
            if run_length >= 3:
                dest.append(str(run_length))
            dest.append(source[i])
            i += 1
        return ''.join(dest)

    @staticmethod
    def decode(source):
        dest = []
        matches = iter(re.finditer(r"[0-9]+|[a-zA-Z]", source))
        for m in matches:
            number = int(m.group())
            m2 = next(matches)
            while number != 0:
                dest.append(m2.group())
                number -= 1
        return ''.join(dest)

    # First non-repeated char in one extra pass (more space, single scan).
    @staticmethod
    def get_first_not_repeated_char(input_str):
        flags = [0] * 256
        for i in range(len(input_str)):
            flags[ord(input_str[i])] += 1
        for i in range(len(flags)):
            if flags[i] == 1:
                return chr(i)
        return None

    @staticmethod
    def first_non_repeating_char(word):
        repeating = set()
        nonrepeating = []
        for i in range(len(word)):
            letter = word[i]
            if letter in repeating:
                continue
            if letter in nonrepeating:
                nonrepeating.remove(letter)
                repeating.add(letter)
            else:
                nonrepeating.append(letter)
        return nonrepeating[0]

    # Maximum occurring (most frequent) character in a string.
    @staticmethod
    def find_most_frequent(s):
        m = {}
        count = 0
        res = ' '
        for i in range(len(s)):
            c = s[i]
            if not (c.isalnum()):
                continue
            if c == ' ':
                continue
            m[c] = m.get(c, 0) + 1
            if m[c] > count:
                count = m[c]
                res = c
        return res

    # 2nd most frequently occurring char.
    @staticmethod
    def get_second_most_char(s):
        count = [0] * 256
        for ch in s:
            count[ord(ch)] += 1
        largest = 0
        second = 0
        for i in range(256):
            if count[i] > count[largest]:
                second = largest
                largest = i
            elif count[i] > count[second] and count[i] != count[largest]:
                second = i
        return chr(second)

    # Detect duplicate parenthesis in a balanced expression.
    @staticmethod
    def is_redundant_expression(s):
        stack = []
        for c in s:
            if c == ')':
                top = stack.pop()
                if top == '(':
                    return True
                else:
                    while top != '(':
                        top = stack.pop()
            else:
                stack.append(c)
        return False

    # Determine if all delimiters in an expression are matched and closed.
    @staticmethod
    def is_balanced(input_str):
        stack = []
        for c in input_str:
            if StringImp.is_opening_bracket(c):
                stack.append(c)
            elif StringImp.is_closing_bracket(c):
                if len(stack) == 0 or not StringImp.is_matching_brackets(stack.pop(), c):
                    return False
        return len(stack) == 0

    @staticmethod
    def is_opening_bracket(c):
        return "({[".find(c) > -1

    @staticmethod
    def is_closing_bracket(c):
        return ")}]".find(c) > -1

    @staticmethod
    def is_matching_brackets(opening, closing):
        if opening == '(':
            return closing == ')'
        if opening == '{':
            return closing == '}'
        if opening == '[':
            return closing == ']'
        return False

    # Edit distance (Levenshtein) via DP. Time O(m*n) space O(m*n)
    @staticmethod
    def edit_dist_dp(str1, str2, m, n):
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        if n == 0:
            return m
        if m == 0:
            return n
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i][j - 1], dp[i - 1][j], dp[i - 1][j - 1])
        return dp[m][n]

    # All words within edit distance k of target, using a trie.
    @staticmethod
    def get_k_edit_distance(words, target, k):
        result = []
        if not words or target is None or len(target) == 0 or k < 0:
            return result
        trie = Trie()
        for word in words:
            trie.add(word)
        root = trie.root
        prev = list(range(len(target) + 1))
        StringImp.get_k_edit_distance_helper("", target, k, root, prev, result)
        return result

    @staticmethod
    def get_k_edit_distance_helper(curr, target, k, root, prev_dist, result):
        if root.is_leaf:
            if prev_dist[len(target)] <= k:
                result.append(curr)
            else:
                return
        for i in range(26):
            if root.children[i] is None:
                continue
            curr_dist = [0] * (len(target) + 1)
            curr_dist[0] = len(curr) + 1
            for j in range(1, len(prev_dist)):
                if target[j - 1] == chr(i + ord('a')):
                    curr_dist[j] = prev_dist[j - 1]
                else:
                    curr_dist[j] = min(prev_dist[j - 1], prev_dist[j], curr_dist[j - 1]) + 1
            StringImp.get_k_edit_distance_helper(curr + chr(i + ord('a')), target, k,
                                                 root.children[i], curr_dist, result)

    # Can s1 be converted to s2 with exactly one edit? Time O(m+n) space O(1)
    @staticmethod
    def is_edit_distance_one(s1, s2):
        m, n = len(s1), len(s2)
        if abs(m - n) > 1:
            return False
        count = 0
        i = j = 0
        while i < m and j < n:
            if s1[i] != s2[j]:
                if count == 1:
                    return False
                if m > n:
                    i += 1
                elif m < n:
                    j += 1
                else:
                    i += 1
                    j += 1
                count += 1
            else:
                i += 1
                j += 1
        if i < m or j < n:
            count += 1
        return count == 1

    # Minimum deletions on a word to make it a valid dictionary word.
    @staticmethod
    def number_of_min_deletion(word, dic):
        mindelete = len(word)
        for item in dic:
            if word == item:
                return 0
            elif len(item) >= len(word):
                continue
            else:
                mindelete = min(mindelete, StringImp.min_deletion_to_transform_word(word, item))
        if mindelete == len(word):
            return -1
        return mindelete

    @staticmethod
    def min_deletion_to_transform_word(s1, s2):
        m, n = len(s1), len(s2)
        count = 0
        i = j = 0
        while i < m and j < n:
            if s1[i] != s2[j]:
                if m > n:
                    i += 1
                count += 1
            else:
                i += 1
                j += 1
        while i < m:
            count += 1
            i += 1
        if j < n:
            return m
        return count

    # word break into at most two words. O(n)
    @staticmethod
    def word_break_max_two(input_str, dic):
        length = len(input_str)
        for i in range(1, length):
            prefix = input_str[0:i]
            if prefix in dic:
                suffix = input_str[i:length]
                if suffix in dic:
                    return prefix + " " + suffix
        return None

    # General word break using memoization. O(n^2)
    @staticmethod
    def word_break_using_dp(input_str, dic):
        if input_str in dic:
            return input_str
        if input_str in StringImp.memoized:
            return StringImp.memoized[input_str]
        length = len(input_str)
        for i in range(1, length):
            prefix = input_str[0:i]
            if prefix in dic:
                suffix = input_str[i:length]
                seg_suffix = StringImp.word_break_using_dp(suffix, dic)
                if seg_suffix is not None:
                    return prefix + " " + seg_suffix
            StringImp.memoized[input_str] = None
        return None

    # Can s be segmented into space separated dictionary words? DP boolean.
    @staticmethod
    def word_break(s, dic):
        f = [False] * (len(s) + 1)
        f[0] = True
        for i in range(1, len(s) + 1):
            for j in range(0, i):
                if f[j] and s[j:i] in dic:
                    f[i] = True
                    break
        return f[len(s)]

    # word break II: all possible sentences (instance memo self.map).
    def word_break_ii(self, s, word_dict):
        if s in self.map:
            return self.map[s]
        res = []
        if len(s) == 0:
            res.append("")
            return res
        for word in word_dict:
            if s.startswith(word):
                sublist = self.word_break_ii(s[len(word):], word_dict)
                for sub in sublist:
                    res.append(word + ("" if sub == "" else " ") + sub)
        self.map[s] = res
        return res

    def word_break_iii(self, s, word_dict):
        if s in self.map:
            return self.map[s]
        length = len(s)
        ret = []
        if s in word_dict:
            ret.append(s)
        for i in range(1, length):
            curr = s[i:]
            if curr in word_dict:
                strs = self.word_break_iii(s[0:i], word_dict)
                if len(strs) != 0:
                    for item in strs:
                        ret.append(item + " " + curr)
        self.map[s] = ret
        return ret

    @staticmethod
    def dictionary_contains(word):
        dictionary = ["mobile", "samsung", "sam", "sung", "man", "mango", "icecream",
                      "and", "go", "i", "like", "ice", "cream"]
        for d in dictionary:
            if d == word:
                return True
        return False

    # Longest common subsequence length. Time O(mn)
    @staticmethod
    def lcs(x, y, m, n):
        l = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    l[i][j] = 0
                elif x[i - 1] == y[j - 1]:
                    l[i][j] = l[i - 1][j - 1] + 1
                else:
                    l[i][j] = max(l[i - 1][j], l[i][j - 1])
        return l[m][n]

    # Smallest substring of s containing all chars of t.
    @staticmethod
    def min_sub_string(s, t):
        m = [0] * 128
        for c in t:
            m[ord(c)] += 1
        start = end = min_start = 0
        min_len = INT_MAX
        counter = len(t)
        while end < len(s):
            c1 = s[end]
            if m[ord(c1)] > 0:
                counter -= 1
            m[ord(c1)] -= 1
            end += 1
            while counter == 0:
                if min_len > end - start:
                    min_len = end - start
                    min_start = start
                c2 = s[start]
                m[ord(c2)] += 1
                if m[ord(c2)] > 0:
                    counter += 1
                start += 1
        return "" if min_len == INT_MAX else s[min_start:min_start + min_len]

    # Length of longest substring without repeating characters.
    @staticmethod
    def length_of_longest_substring(s):
        m = [0] * 128
        start = end = max_len = counter = 0
        while end < len(s):
            c1 = s[end]
            if m[ord(c1)] > 0:
                counter += 1
            m[ord(c1)] += 1
            end += 1
            while counter > 0:
                c2 = s[start]
                if m[ord(c2)] > 1:
                    counter -= 1
                m[ord(c2)] -= 1
                start += 1
            max_len = max(max_len, end - start)
        return max_len

    # Longest substring with at most k distinct characters.
    @staticmethod
    def length_of_longest_substring_k_distinct(s, k):
        m = [0] * 256
        start = end = counter = 0
        max_len = INT_MIN
        while end < len(s):
            c1 = s[end]
            if m[ord(c1)] == 0:
                counter += 1
            m[ord(c1)] += 1
            end += 1
            while counter > k:
                c2 = s[start]
                if m[ord(c2)] == 1:
                    counter -= 1
                m[ord(c2)] -= 1
                start += 1
            max_len = max(max_len, end - start)
        return max_len

    # All repeating substrings of given length (printed), sorted alphabetically.
    @staticmethod
    def lrs(s, sequence_length):
        n = len(s)
        suffixes = [s[i:n] for i in range(n)]
        suffixes.sort()
        for i in range(n - 1):
            x = StringImp.lrs_util(suffixes[i], suffixes[i + 1], sequence_length)
            if len(x) == sequence_length:
                print(x)

    @staticmethod
    def lrs_util(s, t, sequence_length):
        n = min(len(s), len(t))
        if n >= sequence_length:
            if s[0:sequence_length] == t[0:sequence_length]:
                return s[0:sequence_length]
        return ""

    # Count runs of repeated letters (ignoring spaces and dots inside a run).
    @staticmethod
    def count_runs(target):
        prev = target[0]
        rpt = 0
        i = 1
        while i < len(target):
            curr = target[i]
            if curr == prev:
                rpt += 1
                while i < len(target) - 1 and (target[i + 1] == curr
                                               or target[i + 1] == ' '
                                               or target[i + 1] == '.'):
                    i += 1
            else:
                prev = curr
            i += 1
        return rpt

    # First index of target in source (naive). -1 if absent.
    @staticmethod
    def str_str(source, target):
        if source is None or target is None:
            return -1
        for i in range(0, len(source) - len(target) + 1):
            j = 0
            while j < len(target):
                if source[i + j] != target[j]:
                    break
                j += 1
            if j == len(target):
                return i
        return -1

    @staticmethod
    def find_sub_occur(s, find_str):
        last_index = 0
        count = 0
        while last_index != -1:
            last_index = s.find(find_str, last_index)
            if last_index != -1:
                count += 1
                last_index += len(find_str)
        print(count)
        return count

    # Remove duplicate chars keeping first occurrence (instance overload).
    def remove_duplicate(self, s):
        if s is None:
            return None
        _set = set()
        result = []
        for ch in s:
            if ch not in _set:
                _set.add(ch)
                result.append(ch)
        return ''.join(result)

    # Remove duplicates in O(n) with no extra space (bit mask). Static overload.
    @staticmethod
    def remove_duplicates_static(str_chars):
        str_chars = list(str_chars)
        check = 0
        for i in range(len(str_chars)):
            val = ord(str_chars[i]) - ord('a')
            if (check & (1 << val)) > 0:
                str_chars[i] = '\0'
                continue
            check = check | (1 << val)
        out = []
        for j in range(len(str_chars)):
            if str_chars[j] == '\0':
                continue
            else:
                out.append(str_chars[j])
        print(''.join(out))

    # Permutations of a string.
    @staticmethod
    def permute(s):
        length = len(s)
        in_chars = list(s)
        StringImp.do_permute(in_chars, length, 0)

    @staticmethod
    def do_permute(in_chars, length, level):
        if level == length:
            print(in_chars)
            return
        for i in range(level, length):
            StringImp.swap_chars(in_chars, i, level)
            StringImp.do_permute(in_chars, length, level + 1)
            StringImp.swap_chars(in_chars, i, level)

    # Derangements of a sequence (no element in its original position).
    @staticmethod
    def get_derangement(in_chars):
        m = {}
        result = []
        ori = [''] * len(in_chars)
        for i in range(len(in_chars)):
            m[i] = in_chars[i]
            ori[i] = in_chars[i]
        return StringImp.get_derangement_util(in_chars, ori, m, 0, result)

    @staticmethod
    def get_derangement_util(in_chars, ori, m, level, result):
        if level == len(in_chars):
            result.append(list(in_chars))
            print(in_chars)
            return result
        for i in range(level, len(in_chars)):
            if m[i] != in_chars[level]:
                if i != level and (in_chars[i] == ori[level] or in_chars[level] == ori[i]):
                    continue
                StringImp.swap_chars(in_chars, i, level)
                StringImp.get_derangement_util(in_chars, ori, m, level + 1, result)
                StringImp.swap_chars(in_chars, i, level)
        return result

    @staticmethod
    def swap_chars(chars, i, j):
        chars[i], chars[j] = chars[j], chars[i]

    @staticmethod
    def swap_strings(chars, i, j):
        chars[i], chars[j] = chars[j], chars[i]

    # Print all combinations of r elements from arr.
    @staticmethod
    def print_combinations(arr, start, end, r, sb):
        if r == 0:
            print(sb)
            return
        for i in range(start, end - r + 2):
            StringImp.print_combinations(arr, i + 1, end, r - 1, sb + str(arr[i]) + " ")

    # Combinations of the characters of a string.
    @staticmethod
    def combine(s):
        length = len(s)
        instr = list(s)
        StringImp.do_combine(instr, "", length, 0, 0)

    @staticmethod
    def do_combine(instr, outstr, length, level, start):
        for i in range(start, length):
            new_out = outstr + instr[i]
            print(new_out)
            if i < length - 1:
                StringImp.do_combine(instr, new_out, length, level + 1, i + 1)

    # All strings of length k from set with at most one 'b' and <=2 consecutive 'c'.
    @staticmethod
    def print_all_k_length(char_set, k):
        n = len(char_set)
        print(StringImp.print_all_k_length_rec(char_set, "", n, k))

    @staticmethod
    def print_all_k_length_rec(char_set, prefix, n, k):
        if k == 0:
            StringImp.count += 1
            print(prefix)
            return StringImp.count
        for i in range(n):
            if not ("b" in prefix and char_set[i] == 'b') and \
               not (prefix[max(len(prefix) - 2, 0):] == "cc" and char_set[i] == 'c'):
                new_prefix = prefix + char_set[i]
                StringImp.print_all_k_length_rec(char_set, new_prefix, n, k - 1)
        return StringImp.count

    # Are two strings isomorphic (ordered encoding)?
    @staticmethod
    def is_isomorphic(s1, s2):
        if len(s1) != len(s2):
            return False
        elif len(s1) == 1:
            return True
        else:
            map1 = {}
            encoding1 = []
            map2 = {}
            encoding2 = []
            for i in range(len(s1)):
                if s1[i] not in map1:
                    map1[s1[i]] = i
                encoding1.append(str(map1[s1[i]]))
                if s2[i] not in map2:
                    map2[s2[i]] = i
                encoding2.append(str(map2[s2[i]]))
            return ''.join(encoding1) == ''.join(encoding2)

    # Word distance finder (order independent). Uses instance self._map.
    def word_distance_finder(self, words):
        for i in range(len(words)):
            if words[i] not in self._map:
                self._map[words[i]] = []
            self._map[words[i]].append(i)

    def distance(self, word_one, word_two):
        if word_one not in self._map or word_two not in self._map:
            return -1
        if word_one == word_two:
            return 0
        min_distance = INT_MAX
        for i in self._map[word_one]:
            for j in self._map[word_two]:
                min_distance = min(min_distance, abs(i - j))
        return min_distance

    @staticmethod
    def min_distance_finder(strings, target_string, target_string2):
        index1 = -1
        index2 = -1
        min_distance = INT_MAX
        for x in range(len(strings)):
            if strings[x] == target_string:
                index1 = x
            if strings[x] == target_string2:
                index2 = x
            if index1 != -1 and index2 != -1:
                temp_distance = abs(index2 - index1)
                if temp_distance < min_distance:
                    min_distance = temp_distance
        return min_distance

    # Are two strings anagrams?
    @staticmethod
    def are_anagram(s1, s2):
        if len(s1) != len(s2):
            return False
        counter = [0] * 256
        for i in range(len(s1)):
            counter[ord(s1[i])] += 1
            counter[ord(s2[i])] -= 1
        for i in range(256):
            if counter[i] != 0:
                return False
        return True

    # Are two strings k-anagrams?
    @staticmethod
    def are_k_anagram(s1, s2, k):
        if len(s1) != len(s2):
            return False
        counter = [0] * 256
        for i in range(len(s1)):
            counter[ord(s1[i])] += 1
        count = 0
        for i in range(len(s2)):
            if counter[ord(s2[i])] > 0:
                counter[ord(s2[i])] -= 1
            else:
                count += 1
        if count > k:
            return False
        return True

    # Find all anagram (permutation) matches of p inside s.
    @staticmethod
    def anagrams_match(s, p):
        result = []
        count = [0] * 256
        tc = [0] * 256
        for i in range(len(p)):
            count[ord(p[i])] += 1
            tc[ord(s[i])] += 1
        if StringImp.match_count(count, tc):
            result.append(0)
        for i in range(len(p), len(s)):
            tc[ord(s[i - len(p)])] -= 1
            tc[ord(s[i])] += 1
            if StringImp.match_count(count, tc):
                result.append(i - len(p) + 1)
        for num in result:
            print("Found at Index " + str(num))
        return result

    @staticmethod
    def match_count(a, b):
        for i in range(len(a)):
            if a[i] != b[i]:
                return False
        return True

    # Group words with their reverse together.
    @staticmethod
    def print_util(input_words):
        m = {}
        output = []
        for i in range(len(input_words)):
            key = StringImp.reverse_string(input_words[i])
            if key not in m:
                m[key] = i
        for i in range(len(input_words)):
            out = []
            if input_words[i] in m and m[input_words[i]] != i:
                out.append(input_words[i])
                out.append(input_words[m[input_words[i]]])
            output.append(out)
        return output

    # Print all anagrams together.
    @staticmethod
    def print_anagrams_util(input_words):
        m = {}
        for i in range(len(input_words)):
            key = ''.join(sorted(input_words[i]))
            if key not in m:
                m[key] = []
            m[key].append(i)
        for cur in m.keys():
            if len(m[cur]) > 1:
                for i in range(len(m[cur])):
                    print(input_words[m[cur][i]] + " ", end="")
                print()

    # Reverse a string via XOR swap (faithful to the Java reference).
    @staticmethod
    def reverse_string(s):
        chars = list(s)
        i = 0
        length = len(s) - 1
        while i < length:
            a, b = ord(chars[i]), ord(chars[length])
            a ^= b
            b ^= a
            a ^= b
            chars[i], chars[length] = chr(a), chr(b)
            i += 1
            length -= 1
        return ''.join(chars)

    # In-place reversal of words in a char list (overload: reverseWords(char[])).
    @staticmethod
    def reverse_words_in_place(s):
        s = list(s)
        StringImp.reverse_char_range(s, 0, len(s) - 1)
        start = 0
        for i in range(len(s)):
            if s[i] == ' ':
                StringImp.reverse_char_range(s, start, i - 1)
                start = i + 1
        StringImp.reverse_char_range(s, start, len(s) - 1)
        return ''.join(s)

    @staticmethod
    def reverse_char_range(s, start, end):
        while start < end:
            s[start], s[end] = s[end], s[start]
            start += 1
            end -= 1

    # Reverse words in a sentence (overload: reverseWords(String)).
    @staticmethod
    def reverse_words_sentence(sentence):
        words = sentence.split(" ")
        sb = []
        for i in range(len(words) - 1, -1, -1):
            sb.append(words[i])
            sb.append(' ')
        sb.pop()  # strip trailing space
        return ''.join(sb)

    # Count common characters present across s, s1 and s2 (prints them).
    @staticmethod
    def count_of_common_characters(s, s1, s2):
        _set = set()
        for c in s:
            if s1.find(c) != -1 and s2.find(c) != -1:
                _set.add(c)
        for string in _set:
            print(string)

    # Word wrap dynamic programming (prints layout + cost).
    @staticmethod
    def wrap_this(para, w):
        c = para.split(" ")
        n = len(c)
        cost = [0] * n
        espace = [[0] * n for _ in range(n)]
        line = [0] * n
        for i in range(n):
            for j in range(i + 1):
                t = 0
                if i == j:
                    t = len(c[i])
                else:
                    if i > j:
                        for k in range(j, i + 1):
                            t = t + len(c[k])
                    else:
                        for k in range(i, j + 1):
                            t = t + len(c[k])
                if t > w:
                    espace[i][j] = -1
                    espace[j][i] = -1
                else:
                    espace[i][j] = w - t - (i - j)
                    espace[j][i] = w - t - (i - j)
                print(" " + str(espace[i][j]), end="")
            print()
        es = w - len(c[0])
        cost[0] = es * es * es
        for j in range(1, n):
            tl = len(c[j])  # noqa: F841 (kept for parity with reference)
            cost[j] = INT_MAX
            for i in range(1, j + 1):
                if espace[i][j] != -1:
                    t = cost[i - 1] + espace[i][j] * espace[i][j] * espace[i][j]
                    if t < cost[j]:
                        cost[j] = t
                        line[j] = i
            print("optimal line" + str(line[j]))
        print("optimal cost" + str(cost[n - 1]))
        print(" " + c[0], end="")
        pre = 0
        for i in range(1, n):
            if line[i] == pre:
                print(" " + c[i], end="")
            else:
                print()
                print(" " + c[i], end="")
                pre = line[i]

    # Smallest char strictly larger than c in a sorted string, else smallest.
    @staticmethod
    def smallest_character(s, c):
        l, r = 0, len(s) - 1
        ret = s[0]
        while l <= r:
            mid = l + (r - l) // 2
            if s[mid] > c:
                ret = s[mid]
                r = mid - 1
            else:
                l = mid + 1
        return ret

    # Binary search in a sorted array interspersed with empty strings.
    @staticmethod
    def search_i(strings, s, first, last):
        while first <= last:
            mid = (last + first) // 2
            if strings[mid] == "":
                left = mid - 1
                right = mid + 1
                while True:
                    if left < first and right > last:
                        return -1
                    elif right <= last and strings[right] != "":
                        mid = right
                        break
                    elif left >= first and strings[left] != "":
                        mid = left
                        break
                    right += 1
                    left -= 1
            if strings[mid] == s:
                return mid
            elif strings[mid] < s:
                first = mid + 1
            else:
                last = mid - 1
        return -1

    # Longest palindromic substring via suffix sort. O(N log N)
    @staticmethod
    def longest_palindrome_improve(s):
        s = s + "^" + StringImp.reverse_string(s)
        n = len(s)
        suffixes = [s[i:n] for i in range(n)]
        suffixes.sort()
        m = {}
        for i in range(n - 1):
            x = StringImp.lcp(suffixes[i], suffixes[i + 1])
            key = suffixes[i][0:x]
            if key not in m:
                m[key] = x
        max_entry = None
        for key, value in m.items():
            if max_entry is None or value > max_entry[1]:
                max_entry = (key, value)
        return max_entry[0]

    @staticmethod
    def lcp(s, t):
        n = min(len(s), len(t))
        for i in range(n):
            if s[i] != t[i]:
                return i
        return n

    # All palindromic pairs (concatenations) over a list of words.
    @staticmethod
    def palindrome_pairs(words):
        ans = []
        m = {}
        for i in range(len(words)):
            m[words[i]] = i
        for k in range(len(words)):
            word = words[k]
            n = len(word)
            for i in range(n + 1):
                prefix = word[0:i][::-1]
                suffix = word[i:n][::-1]
                if i != 0 and suffix in m and m[suffix] != k and StringImp.is_palindrome(prefix):
                    ans.append([m[suffix], k])
                if prefix in m and m[prefix] != k and StringImp.is_palindrome(suffix):
                    ans.append([k, m[prefix]])
        return ans

    # Palindrome pairs using a trie. O(n k^2)
    @staticmethod
    def palindrome_pairs_improved(words):
        res = []
        root = TrieNode2()
        for i in range(len(words)):
            StringImp.add_word(root, words[i], i)
        for i in range(len(words)):
            StringImp.search_palindrome_pairs(words, i, root, res)
        return res

    @staticmethod
    def add_word(root, word, index):
        for i in range(len(word) - 1, -1, -1):
            j = ord(word[i]) - ord('a')
            if root.next[j] is None:
                root.next[j] = TrieNode2()
            if StringImp.is_palindrome_range(word, 0, i):
                root.list.append(index)
            root = root.next[j]
        root.list.append(index)
        root.index = index

    # overload of search(pat, txt): search(words, i, root, res)
    @staticmethod
    def search_palindrome_pairs(words, i, root, res):
        for j in range(len(words[i])):
            if root.index >= 0 and root.index != i and \
               StringImp.is_palindrome_range(words[i], j, len(words[i]) - 1):
                res.append([i, root.index])
            root = root.next[ord(words[i][j]) - ord('a')]
            if root is None:
                return
        for j in root.list:
            if i == j:
                continue
            res.append([i, j])

    # Keep only words that have a palindrome partner in the list.
    @staticmethod
    def filter_list(input_words):
        out = []
        m = {}
        for i in range(len(input_words)):
            m[input_words[i]] = i
        for k in range(len(input_words)):
            word = input_words[k]
            n = len(word)
            for i in range(n + 1):
                prefix = word[0:i][::-1]
                suffix = word[i:n][::-1]
                if i != 0 and suffix in m and m[suffix] != k and StringImp.is_palindrome(prefix):
                    out.append(suffix)
                if prefix in m and m[prefix] != k and StringImp.is_palindrome(suffix):
                    out.append(prefix)
        return out

    # Is a string a palindrome (overload: isPalindrome(String))?
    @staticmethod
    def is_palindrome(word):
        if len(word) < 2:
            return True
        for i in range(len(word) // 2):
            if word[i] != word[len(word) - i - 1]:
                return False
        return True

    # Case insensitive palindrome ignoring non alphanumerics.
    @staticmethod
    def is_palindrome1(word):
        word = word.lower()
        if len(word) < 2:
            return True
        l, r = 0, len(word) - 1
        while l < r:
            while not word[l].isalnum():
                l += 1
            while not word[r].isalnum():
                r -= 1
            if word[l] != word[r]:
                return False
            l += 1
            r -= 1
        return True

    # Can chars be rearranged into a palindrome (allowing some mismatches)?
    @staticmethod
    def can_form_palindrome(s, total_chars_to_check):
        m = [0] * 128
        count = 0
        for i in range(len(s)):
            m[ord(s[i])] += 1
            if m[ord(s[i])] % 2 == 0:
                count -= 1
            else:
                count += 1
        return count <= total_chars_to_check + 1

    @staticmethod
    def has_palindrome(s):
        occurrences = set()
        for i in range(len(s)):
            v = StringImp._get_numeric_value(s[i])
            if v in occurrences:
                occurrences.discard(v)
            else:
                occurrences.add(v)
        return len(occurrences) <= 1

    # Can removing one character make s a palindrome?
    @staticmethod
    def is_almost_palindrome(s):
        i, j = 0, len(s) - 1
        while i < j:
            if s[i] != s[j]:
                return StringImp.is_palindrome_range(s, i + 1, j) or \
                    StringImp.is_palindrome_range(s, i, j - 1)
            i += 1
            j -= 1
        return True

    # overload: isPalindrome(s, firstIndex, lastIndex)
    @staticmethod
    def is_palindrome_range(s, first_index, last_index):
        i, j = first_index, last_index
        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True

    # Longest palindrome buildable by removing/shuffling characters.
    @staticmethod
    def longest_palindrome_remove_shuffle(s):
        output = ""
        center = ""
        counter = [0] * 26
        for i in range(len(s)):
            counter[ord(s[i]) - ord('a')] += 1
        for i in range(len(counter)):
            times = counter[i] // 2
            repeated = chr(i + ord('a')) * times
            output += repeated
            if counter[i] % 2 != 0:
                center = chr(i + ord('a'))
        return output + center + output[::-1]

    # Are two strings rotations of each other?
    @staticmethod
    def are_rotations(s1, s2):
        temp = s1 + s1
        return s2 in temp

    # Print positive integers in string-comparison order up to n.
    @staticmethod
    def print_rec(s, n):
        if int(s) > n:
            return
        print(s)
        for i in range(10):
            StringImp.print_rec(s + str(i), n)

    # Longest common prefix shared by all words.
    @staticmethod
    def long_prefix(s):
        arr = s.split(" ")
        length = len(arr[0])
        for i in range(1, len(arr)):
            p = 0
            while p < length and p < len(arr[i]) and arr[0][p] == arr[i][p]:
                p += 1
            length = p
        return arr[0][0:length]

    # Is str1 a subsequence of str2?
    @staticmethod
    def is_sub_sequence(str1, str2, m, n):
        j = 0
        i = 0
        while i < n and j < m:
            if str1[j] == str2[i]:
                j += 1
            i += 1
        return j == m

    # Naive substring search (overload: search(pat, txt)).
    @staticmethod
    def search_naive(pat, txt):
        m = len(pat)
        n = len(txt)
        for i in range(n - m + 1):
            j = 0
            while j < m:
                if txt[i + j] != pat[j]:
                    break
                j += 1
            if j == m:
                print("Pattern found at index " + str(i))

    # KMP substring search. Time O(m+n)
    @staticmethod
    def search_sub_string(text, ptrn):
        i = j = 0
        ptrn_len = len(ptrn)
        txt_len = len(text)
        b = StringImp.pre_process_pattern(ptrn)
        while i < txt_len:
            while j >= 0 and text[i] != ptrn[j]:
                j = b[j]
            i += 1
            j += 1
            if j == ptrn_len:
                print("found substring at index:" + str(i - ptrn_len))
                j = b[j]

    @staticmethod
    def pre_process_pattern(ptrn):
        i = 0
        j = -1
        ptrn_len = len(ptrn)
        b = [0] * (ptrn_len + 1)
        b[i] = j
        while i < ptrn_len:
            while j >= 0 and ptrn[i] != ptrn[j]:
                j = b[j]
            i += 1
            j += 1
            b[i] = j
        return b

    # K most frequent words using a min-heap.
    @staticmethod
    def find_top_k_frequent_words(s, k):
        _hash = {}
        min_heap = []
        for i in range(len(s)):
            _hash[s[i]] = _hash.get(s[i], 0) + 1
        count = 0
        for key, value in _hash.items():
            if count < k:
                heapq.heappush(min_heap, WordFreq(key, value))
                count += 1
            elif value > min_heap[0].freq:
                heapq.heappop(min_heap)
                heapq.heappush(min_heap, WordFreq(key, value))
        while min_heap:
            print(_hash[heapq.heappop(min_heap).word])

    # Is str a repetition of one of its substrings? (KMP lps)
    @staticmethod
    def is_repeat(str_chars):
        n = len(str_chars)
        lps = [0] * n
        StringImp.compute_lps_array(str_chars, n, lps)
        length = lps[n - 1]
        return length > 0 and n % (n - length) == 0

    @staticmethod
    def compute_lps_array(str_chars, m, lps):
        length = 0
        lps[0] = 0
        i = 1
        while i < m:
            if str_chars[i] == str_chars[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1

    # CSV parser. Separator ',', quote '"'.
    @staticmethod
    def decode_csv(s):
        if s is None or len(s) == 0:
            return None
        result = []
        in_quotes = False
        sb = []
        i = 0
        while i < len(s):
            value = s[i]
            if in_quotes:
                if value == '"':
                    if i == len(s) - 1:
                        result.append(''.join(sb))
                        return result
                    elif s[i + 1] == '"':
                        sb.append('"')
                        i += 1
                    else:
                        result.append(''.join(sb))
                        sb = []
                        in_quotes = False
                        i += 1
                else:
                    sb.append(value)
            elif value == '"':
                in_quotes = True
            elif value == ',':
                result.append(''.join(sb))
                sb = []
            else:
                sb.append(value)
            i += 1
        result.append(''.join(sb))
        return result

    # Try lower/upper case combinations to decode a string. Exponential.
    @staticmethod
    def decode_find_helper(start, curr, bad_enc_string):
        if start == len(bad_enc_string):
            test_enc_str = ''.join(curr)
            result = StringImp.decode_string(test_enc_str)
            if result is not None:
                return result
            else:
                return None
        c = bad_enc_string[start]
        if not c.isalpha():
            curr.append(c)
            result = StringImp.decode_find_helper(start + 1, curr, bad_enc_string)
            if result is not None:
                return result
            curr.pop()
        else:
            lower = c.lower()
            curr.append(lower)
            result = StringImp.decode_find_helper(start + 1, curr, bad_enc_string)
            if result is not None:
                return result
            curr.pop()
            upper = c.upper()
            curr.append(upper)
            result = StringImp.decode_find_helper(start + 1, curr, bad_enc_string)
            if result is not None:
                return result
            curr.pop()
        return None

    @staticmethod
    def decode_string(test_enc_str):
        truth = "kljJJ324hijkS_"
        if test_enc_str == truth:
            return 848662
        else:
            return None

    # Wildcard matching: '?' single char, '*' any sequence.
    @staticmethod
    def wild_card_comparison(s, pattern):
        si = p = 0
        star_idx = -1
        while si < len(s):
            if p < len(pattern) and (pattern[p] == '?' or s[si] == pattern[p]):
                si += 1
                p += 1
            elif p < len(pattern) and pattern[p] == '*':
                star_idx = p
                p += 1
            elif star_idx != -1:
                si += 1
            else:
                return False
        while p < len(pattern) and pattern[p] == '*':
            p += 1
        return p == len(pattern)

    # Regex matching with '.' and '*' via DP. Time/space O(M*N)
    @staticmethod
    def match_regex(s, p):
        if s is None or p is None:
            return False
        dp = [[False] * (len(p) + 1) for _ in range(len(s) + 1)]
        dp[0][0] = True
        for i in range(len(p)):
            if p[i] == '*' and dp[0][i - 1]:
                dp[0][i + 1] = True
        for i in range(1, len(s) + 1):
            for j in range(1, len(p) + 1):
                if p[j - 1] == '.' or p[j - 1] == s[i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                if p[j - 1] == '*':
                    if p[j - 2] != s[i - 1] and p[j - 2] != '.':
                        dp[i][j] = dp[i][j - 2]
                    else:
                        dp[i][j] = dp[i][j - 1] or dp[i][j - 2] or dp[i - 1][j]
        return dp[len(s)][len(p)]

    # Recursive regex matching with '.', '*' and '+'.
    @staticmethod
    def is_match1(s, p):
        if len(p) == 0:
            return len(s) == 0
        if len(p) == 1:
            if len(s) < 1:
                return False
            elif p[0] != s[0] and p[0] != '.':
                return False
            else:
                return StringImp.is_match1(s[1:], p[1:])
        if p[1] != '*' and p[1] != '+':
            if len(s) < 1:
                return False
            if p[0] != s[0] and p[0] != '.':
                return False
            else:
                return StringImp.is_match1(s[1:], p[1:])
        elif p[1] == '*':
            if StringImp.is_match1(s, p[2:]):
                return True
            i = 0
            while i < len(s) and (s[i] == p[0] or p[0] == '.'):
                if StringImp.is_match1(s[i + 1:], p[2:]):
                    return True
                i += 1
            return False
        elif p[1] == '+':
            i = 0
            while i < len(s) and (s[i] == p[0] or p[0] == '.'):
                if StringImp.is_match1(s[i + 1:], p[2:]):
                    return True
                i += 1
            return False
        return False

    # Split a message into annotated chunks without cutting words.
    @staticmethod
    def split_text(message, char_limit):
        return StringImp.split_text_aux_using_split(message, char_limit)

    @staticmethod
    def split_text_aux_using_split(message, char_limit_original):
        char_limit = char_limit_original - 5
        result = []
        splitted = message.split(" ")
        i = 0
        while i < len(splitted) - 1:
            temp = splitted[i]
            while i + 1 < len(splitted) - 1 and len(temp + "1" + splitted[i + 1]) <= char_limit:
                temp = temp + " " + splitted[i + 1]
                i += 1
            result.append(temp)
            i += 1
        last_element = result[len(result) - 1]
        if len(last_element) + 1 + len(splitted[len(splitted) - 1]) < char_limit:
            result[len(result) - 1] = last_element + " " + splitted[len(splitted) - 1]
        else:
            result.append(splitted[len(splitted) - 1])
        result_size = len(result)
        for i in range(result_size):
            result[i] = result[i] + "(" + str(i + 1) + "/" + str(result_size) + ")"
        return result

    # Remove consecutive duplicate characters (instance overload).
    def remove_duplicates(self, input_chars):
        input_chars = list(input_chars)
        slow = 0
        fast = 0
        index = 0
        while fast < len(input_chars):
            while fast < len(input_chars) and input_chars[slow] == input_chars[fast]:
                fast += 1
            input_chars[index] = input_chars[slow]
            index += 1
            slow = fast
        return index

    # Rank of a string amongst its lexicographic permutations.
    @staticmethod
    def find_rank(str_chars):
        length = len(str_chars)
        mul = StringImp.factorial(length)
        rank = 1
        count = [0] * 256
        StringImp.populate_and_increase_count(count, str_chars)
        for i in range(length):
            mul //= (length - i)
            rank += count[ord(str_chars[i]) - 1] * mul
            StringImp.update_count(count, str_chars[i])
        return rank

    @staticmethod
    def factorial(n):
        return 1 if n <= 1 else (n * StringImp.factorial(n - 1))

    @staticmethod
    def find_smaller_in_right(a, low, high):
        count_right = 0
        for i in range(low + 1, high + 1):
            if a[i] < a[low]:
                count_right += 1
        return count_right

    @staticmethod
    def populate_and_increase_count(count, str_chars):
        i = 0
        while i < len(str_chars) and 'a' <= str_chars[i] <= 'z':
            count[ord(str_chars[i])] += 1
            i += 1
        for i in range(1, 256):
            count[i] += count[i - 1]

    @staticmethod
    def update_count(count, ch):
        for i in range(ord(ch), 256):
            count[i] -= 1

    # Word ladder length using BFS over single-character changes.
    @staticmethod
    def ladder_length(start, end, dic):
        visited = {}
        queue = deque()
        queue.append(Count(start, 1))
        visited[start] = True
        while queue:
            c = queue.popleft()
            for i in range(len(start)):
                sb = list(c.string)
                sc = c.string[i]
                cc = ord('a')
                while cc <= ord('z'):
                    if chr(cc) == sc:
                        cc += 1
                        continue
                    sb[i] = chr(cc)
                    tmp = ''.join(sb)
                    if visited.get(tmp) is None and tmp in dic:
                        if tmp == end:
                            return c.count + 1
                        visited[tmp] = True
                        queue.append(Count(tmp, c.count + 1))
                    cc += 1
        return 0

    # Word ladder with add/remove/change of one character; returns path.
    @staticmethod
    def transform(start_word, stop_word, dictionary):
        start_word = start_word.upper()
        stop_word = stop_word.upper()
        action_queue = deque()
        visited_set = set()
        backtrack_map = {}
        action_queue.append(start_word)
        visited_set.add(start_word)
        while action_queue:
            w = action_queue.popleft()
            for v in StringImp.get_one_edit_words(w):
                if v == stop_word:
                    result = deque()
                    result.appendleft(v)
                    while w is not None:
                        result.appendleft(w)
                        w = backtrack_map.get(w)
                    return list(result)
                if v in dictionary:
                    if v not in visited_set:
                        action_queue.append(v)
                        visited_set.add(v)
                        backtrack_map[v] = w
        return None

    @staticmethod
    def get_one_edit_words(word):
        words = set()
        for i in range(len(word)):
            word_array = list(word)
            c = ord('A')
            while c <= ord('Z'):
                if chr(c) != word[i]:
                    word_array[i] = chr(c)
                    words.add(''.join(word_array))
                c += 1
        return words

    # Remove "b" and "ac" from a string. ababaac -> aaa
    @staticmethod
    def remove_pattern_from_string(str_chars):
        str_chars = list(str_chars)
        n = len(str_chars)
        i = -1
        j = 0
        while j < n:
            if j < n - 1 and str_chars[j] == 'a' and str_chars[j + 1] == 'c':
                j += 2
            elif str_chars[j] == 'b':
                j += 1
            elif i >= 0 and str_chars[j] == 'c' and str_chars[i] == 'a':
                i -= 1
                j += 1
            else:
                i += 1
                str_chars[i] = str_chars[j]
                j += 1
        i += 1
        return ''.join(str_chars)[0:i]

    # Recursively remove all adjacent duplicates. azxxzy -> ay
    @staticmethod
    def remove_adjacent_duplicates(s):
        if len(s) < 2:
            return s
        buf = list(s)
        lastchar = buf[0]
        j = 1
        for i in range(1, len(buf)):
            if j > 0 and buf[i] == buf[j - 1]:
                lastchar = buf[j - 1]
                while j > 0 and buf[j - 1] == lastchar:
                    j -= 1
            elif buf[i] != lastchar:
                buf[j] = buf[i]
                j += 1
        return ''.join(buf[0:j])

    # Valid word abbreviation. Uses instance fields abbr_dict/unique_dict.
    def valid_word_abbr(self, dictionary):
        self.abbr_dict = {}
        self.unique_dict = set()
        for word in dictionary:
            if word not in self.unique_dict:
                abbr = self.get_abbr(word)
                if abbr not in self.abbr_dict:
                    self.abbr_dict[abbr] = word
                else:
                    self.abbr_dict[abbr] = ""
                self.unique_dict.add(word)

    def is_unique(self, word):
        if word is None or len(word) == 0:
            return True
        abbr = self.get_abbr(word)
        if abbr not in self.abbr_dict or self.abbr_dict[abbr] == word:
            return True
        else:
            return False

    def get_abbr(self, word):
        if word is None or len(word) < 3:
            return word
        sb = []
        sb.append(word[0])
        sb.append(str(len(word) - 2))
        sb.append(word[len(word) - 1])
        return ''.join(sb)

    # Display pages by host id (max 12 entries per page).
    @staticmethod
    def display_pages(inp):
        if inp is None or len(inp) == 0:
            return
        inp = list(inp)
        visited = set()
        i = 0
        page_num = 1
        print("Page " + str(page_num))
        while i < len(inp):
            curr = inp[i]
            host_id = curr.split(",")[0]
            if host_id not in visited:
                print(curr)
                visited.add(host_id)
                del inp[i]
            else:
                i += 1
            if len(visited) == 12 or i >= len(inp):
                visited.clear()
                i = 0
                if len(inp) != 0:
                    page_num += 1
                    print("Page " + str(page_num))

    # DP boggle variant: print dictionary words that appear on the board.
    @staticmethod
    def boggle_trie_dynamic(node, current_branch, current_height):
        if node is None:
            return
        if node.word_end and current_height > 3:
            word = ''.join(current_branch[0:current_height - 1])
            if StringImp.is_in_board(StringImp.board, word):
                print(word)
        for i in range(len(node.next_nodes)):
            if node.next_nodes[i] is not None:
                current_branch[current_height] = chr(i + ord('a'))
                StringImp.boggle_trie_dynamic(node.next_nodes[i], current_branch, current_height + 1)

    @staticmethod
    def is_in_board(board, word):
        m = len(board)
        n = len(board[0])
        dx = [1, 1, 0, -1, -1, -1, 0, 1]
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
        visited = [[False] * n for _ in range(m)]
        letters = list(word)
        dp = [[[False] * n for _ in range(m)] for _ in range(len(letters))]
        for k in range(len(letters)):
            for i in range(m):
                for j in range(n):
                    if k == 0:
                        dp[k][i][j] = True
                    elif not visited[i][j] and dp[k - 1][i][j]:
                        for l in range(8):
                            x = i + dx[l]
                            y = j + dy[l]
                            if 0 <= x < m and 0 <= y < n and dp[k - 1][x][y] and board[i][j] == letters[k]:
                                dp[k][i][j] = True
                                visited[x][y] = True
                                if k == len(letters) - 1:
                                    return True
        return False

    # tiny URL encode (overload: encode(int)).
    @staticmethod
    def encode_tinyurl(num):
        sb = []
        while num > 0:
            sb.append(StringImp.ALPHABET[num % StringImp.BASE])
            num //= StringImp.BASE
        return ''.join(sb)

    @staticmethod
    def decode1(s):
        num = 0
        for i in range(len(s) - 1, -1, -1):
            num = num * StringImp.BASE + StringImp.ALPHABET.find(s[i])
        return num

    # Number of words that fit into rows x cols.
    @staticmethod
    def number_can_fit(words, row, col):
        word_count = 0
        row_iterator = 0
        word_iterator = 0
        while row_iterator < row:
            remaining_col = col
            while remaining_col > 0 and len(words[word_iterator]) <= remaining_col:
                word_count += 1
                remaining_col = remaining_col - len(words[word_iterator]) - 1
                word_iterator += 1
                if word_iterator == len(words):
                    word_iterator = 0
            row_iterator += 1
        return word_count

    # CamelCase matching of class names against a pattern.
    @staticmethod
    def get_camel_case_matching_strings(lst, pattern):
        pattern_list = []
        for i in range(len(lst)):
            s = lst[i]
            length = 0
            pattern_len = len(pattern) - 1
            pat_index = 0
            while length != len(s) - 1 and pat_index <= pattern_len:
                if s[length] == pattern[pat_index]:
                    length += 1
                    if pat_index == pattern_len:
                        pattern_list.append(s)
                        break
                    pat_index += 1
                    continue
                elif not pattern[pat_index].isupper():
                    break
                length += 1
        return pattern_list

    # Print non overlapping, in order parenthesizations of a number string.
    @staticmethod
    def print_non_overlapping(number, prefix):
        print(prefix + "(" + number + ")")
        for i in range(1, len(number)):
            new_prefix = prefix + "(" + number[0:i] + ")"
            StringImp.print_non_overlapping(number[i:len(number)], new_prefix)

    # Can characters be shuffled so no two equal chars are adjacent?
    @staticmethod
    def can_shuffle(s):
        counter = [0] * 300
        for c in s:
            counter[ord(c)] += 1
        max_existed_character = 0
        c = ord('a')
        while c <= ord('z'):
            max_existed_character = max(counter[c], max_existed_character)
            c += 1
        return max_existed_character <= (len(s) + 1) // 2

    # Max product of lengths of two words with no common letters.
    @staticmethod
    def max_product(words):
        if words is None or len(words) <= 1:
            return 0
        n = len(words)
        encoded_words = [0] * n
        for i in range(len(words)):
            word = words[i]
            for j in range(len(word)):
                c = word[j]
                encoded_words[i] |= (1 << (ord(c) - ord('a')))
        max_len = 0
        for i in range(n):
            for j in range(i + 1, n):
                if (encoded_words[i] & encoded_words[j]) == 0:
                    max_len = max(max_len, len(words[i]) * len(words[j]))
        return max_len

    # Longest valid parenthesis substring length.
    @staticmethod
    def find_longest_paranthesis_len(s):
        cnt = 0
        ans = 0
        max_len = 0
        for i in range(len(s)):
            if s[i] == '(':
                cnt += 1
            else:
                if cnt <= 0:
                    max_len = max(max_len, ans)
                    cnt = 0
                    ans = 0
                else:
                    cnt -= 1
                    ans += 2
        if cnt >= 0:
            max_len = max(max_len, ans)
        return max_len

    # Is the ordering string honoured within s?
    @staticmethod
    def is_ordering_string_present(s, ordering):
        label = [0] * 256
        order = 1
        for i in range(len(ordering)):
            label[ord(ordering[i])] = order
            order += 1
        last = 0
        for i in range(len(s)):
            if label[ord(s[i])] > 0:
                if label[ord(s[i])] < last:
                    return False
                last = label[ord(s[i])]
        return True

    # Ransom note: can note be built from magazine? O(M)
    @staticmethod
    def ransom_note1(note, mag):
        count = [0] * 256
        for i in range(len(mag)):
            count[ord(mag[i])] += 1
        for j in range(len(note)):
            count[ord(note[j])] -= 1
            if count[ord(note[j])] < 0:
                return False
        return True

    # Ransom note scanning note and magazine simultaneously.
    @staticmethod
    def ransom_note2(s, pattern):
        count = [0] * 256
        n = 0
        m = 0
        while n < len(s):
            nchar = ord(s[n])
            if count[nchar] > 0:
                count[nchar] -= 1
                n += 1
            else:
                while m < len(pattern) and ord(pattern[m]) != nchar:
                    mchar = ord(pattern[m])
                    count[mchar] += 1
                    m += 1
                if m >= len(pattern):
                    return False
                n += 1
                m += 1
        return True

    # Evaluate a tokenized expression without parentheses (precedence aware).
    @staticmethod
    def eval_expr(token_list):
        i = 0
        left = token_list[i].value
        i += 1
        while i < len(token_list):
            operator = token_list[i].type
            i += 1
            right = float(token_list[i].value)
            i += 1
            if operator == "*":
                left = left * right
            elif operator == "/":
                left = left / right
            elif operator in ("+", "-"):
                while i < len(token_list):
                    operator2 = token_list[i].type
                    i += 1
                    if operator2 == "+" or operator2 == "-":
                        i -= 1
                        break
                    if operator2 == "*":
                        right = right * float(token_list[i].value)
                        i += 1
                    if operator2 == "/":
                        right = right / float(token_list[i].value)
                        i += 1
                if operator == "+":
                    left = left + right
                else:
                    left = left - right
        return left

    # Build per-word letter counts (overload: init(String[])). Faithful no-op store.
    @staticmethod
    def init_words(words):
        m = {}
        for i in range(len(words)):
            count = [0] * 26
            for ch in words[i]:
                index = ord(ch) - ord('a')
                count[index] += 1
        return m

    # Find dictionary words formable from a multiset of characters. O(M + N*26)
    @staticmethod
    def word_finder(input_chars, word_map):
        out = set()
        char_count = [0] * 26
        for c in input_chars:
            index = ord(c) - ord('a')
            char_count[index] += 1
        for key in word_map.keys():
            is_match = True
            temp = word_map[key]
            for i in range(len(temp)):
                if temp[i] != char_count[i]:
                    is_match = False
                    break
            if is_match:
                out.add(key)
        return out

    # Is the words array sorted according to a custom alphabet ordering?
    @staticmethod
    def check_if_sorted_array(strs, orderings):
        m = {}
        for i in range(len(orderings)):
            m[orderings[i]] = i
        for i in range(1, len(strs)):
            word1 = strs[i - 1]
            word2 = strs[i]
            for j in range(min(len(word1), len(word2))):
                if word1[j] != word2[j]:
                    frm = word1[j]
                    to = word2[j]
                    if m[frm] > m[to]:
                        return False
        return True

    # Add two numbers in an arbitrary base, represented as strings.
    @staticmethod
    def add_binary(a, b, base):
        if a is None or a == "":
            return b
        if b is None or b == "":
            return a
        sb = []
        i = len(a) - 1
        j = len(b) - 1
        carry = 0
        while i >= 0 or j >= 0:
            total = 0
            if i >= 0:
                total += ord(a[i]) - ord('0')
                i -= 1
            if j >= 0:
                total += ord(b[j]) - ord('0')
                j -= 1
            total += carry
            if total >= base:
                carry = 1
            else:
                carry = 0
            sb.append(chr((total % base) + ord('0')))
        if carry == 1:
            sb.append('1')
        return ''.join(sb)[::-1]

    # Multiply two big integers represented as strings. O(nm)
    @staticmethod
    def multiply(str1, str2):
        output = "0"
        count = 0
        for i in range(len(str2) - 1, -1, -1):
            d2 = ord(str2[i]) - ord('0')
            carry = 0
            prod = []
            for j in range(len(str1) - 1, -1, -1):
                d1 = ord(str1[j]) - ord('0')
                p = carry + (d1 * d2)
                prod.append(str(p % 10))
                carry = p // 10
            if carry != 0:
                prod.append(str(carry))
            prod.reverse()
            for _ in range(count):
                prod.append("0")
            output = StringImp.add_binary(output, ''.join(prod), 10)
            count += 1
        return output

    # Letter combinations of a phone number. Time/space O(4^n)
    @staticmethod
    def letter_phone_combinations(digits):
        queue = deque()
        if digits is None or digits == "":
            return queue
        m = ["0", "1", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"]
        queue.append("")
        while queue and len(queue[0]) != len(digits):
            remove = queue.popleft()
            letters = m[ord(digits[len(remove)]) - ord('0')]
            for c in letters:
                queue.append(remove + c)
        return queue

    # Remove fewest characters to balance parentheses.
    @staticmethod
    def remove_unbalance_parenthesis(s):
        str_list = list(s)
        left = 0
        i = 0
        while i < len(str_list):
            if str_list[i] == '(':
                left += 1
            elif str_list[i] == ')':
                if left > 0:
                    left -= 1
                else:
                    del str_list[i]
                    i -= 1
            i += 1
        right = 0
        i = len(str_list) - 1
        while i >= 0:
            if str_list[i] == ')':
                right += 1
            elif str_list[i] == '(':
                if right > 0:
                    right -= 1
                else:
                    del str_list[i]
            i -= 1
        return ''.join(str_list)

    # Remove minimum invalid parentheses (single canonical result). 2 passes.
    @staticmethod
    def remove_invalid_parentheses1(s):
        r = StringImp._remove_invalid_helper(s, ['(', ')'])
        tmp = StringImp._remove_invalid_helper(r[::-1], [')', '('])
        return tmp[::-1]

    @staticmethod
    def _remove_invalid_helper(s, p):
        stack = 0
        i = 0
        while i < len(s):
            if s[i] == p[0]:
                stack += 1
            if s[i] == p[1]:
                stack -= 1
            if stack < 0:
                s = s[0:i] + s[i + 1:]
                i -= 1
                stack = 0
            i += 1
        return s

    # Integer to English words.
    @staticmethod
    def number_to_words(num):
        if num == 0:
            return "Zero"
        i = 0
        output = ""
        while num > 0:
            if num % 1000 != 0:
                output = StringImp._num_to_words_util(num % 1000) + StringImp.big[i] + " " + output
            num //= 1000
            i += 1
        return output.strip()

    @staticmethod
    def _num_to_words_util(num):
        if num == 0:
            return ""
        elif num < 20:
            return StringImp.one[num] + " "
        elif num < 100:
            return StringImp.ten[num // 10] + " " + StringImp._num_to_words_util(num % 10)
        else:
            return StringImp.one[num // 100] + " Hundred " + StringImp._num_to_words_util(num % 100)

    # Restore all valid IP addresses from a digit string.
    @staticmethod
    def restore_ip_addresses(s):
        res = []
        if s is None or len(s) == 0:
            return res
        length = len(s)
        if length < 4 or length > 12:
            return res
        for i in range(1, 4):
            for j in range(i + 1, i + 4):
                k = j + 1
                while k < j + 4 and k < length:
                    s1 = s[0:i]
                    s2 = s[i:j]
                    s3 = s[j:k]
                    s4 = s[k:length]
                    if StringImp.is_valid1(s1) and StringImp.is_valid1(s2) and \
                       StringImp.is_valid1(s3) and StringImp.is_valid1(s4):
                        res.append(s1 + "." + s2 + "." + s3 + "." + s4)
                    k += 1
        return res

    @staticmethod
    def is_valid1(s):
        if (len(s) > 1 and s[0] == '0') or int(s) > 255:
            return False
        return True

    # Insert +, -, * between digits to reach target.
    @staticmethod
    def add_operators(num, target):
        res = []
        StringImp.add_operators_dfs(res, "", num, 0, target, 0, 0)
        return res

    # overload of dfs: add operators dfs.
    @staticmethod
    def add_operators_dfs(res, expr, num, pos, target, prev, multi):
        if pos == len(num):
            if target == prev:
                res.append(expr)
            return
        curr = 0
        for i in range(pos, len(num)):
            if num[pos] == '0' and i != pos:
                break
            curr = 10 * curr + (ord(num[i]) - ord('0'))
            if pos == 0:
                StringImp.add_operators_dfs(res, expr + str(curr), num, i + 1, target, curr, curr)
            else:
                StringImp.add_operators_dfs(res, expr + "+" + str(curr), num, i + 1,
                                            target, prev + curr, curr)
                StringImp.add_operators_dfs(res, expr + "-" + str(curr), num, i + 1,
                                            target, prev - curr, -curr)
                StringImp.add_operators_dfs(res, expr + "*" + str(curr), num, i + 1,
                                            target, prev - multi + multi * curr, multi * curr)

    # Next closest time reusing the current digits.
    @staticmethod
    def next_closest_time(time):
        hour = int(time[0:2])
        minute = int(time[3:5])
        while True:
            minute += 1
            if minute == 60:
                minute = 0
                hour += 1
                hour %= 24
            curr = "%02d:%02d" % (hour, minute)
            valid = True
            for i in range(len(curr)):
                if time.find(curr[i]) < 0:
                    valid = False
                    break
            if valid:
                return curr

    # Does str follow the given pattern? (bijection)
    @staticmethod
    def word_pattern(pattern, s):
        words = s.split(" ")
        if len(words) != len(pattern):
            return False
        m = {}
        for i in range(len(pattern)):
            key = pattern[i]
            word = words[i]
            if key in m and m[key] != word:
                return False
            if key not in m and word in m.values():
                return False
            m[key] = word
        return True

    # Word pattern II via backtracking. O(n^m)
    @staticmethod
    def word_pattern_match(pattern, s):
        m = {}
        return StringImp.is_match(s, 0, pattern, 0, m)

    @staticmethod
    def is_match(s, str_index, pat, pat_index, m):
        if str_index == len(s) and pat_index == len(pat):
            return True
        if str_index == len(s) or pat_index == len(pat):
            return False
        pat_char = pat[pat_index]
        if pat_char in m:
            value = m[pat_char]
            if not s.startswith(value, str_index):
                return False
            return StringImp.is_match(s, str_index + len(value), pat, pat_index + 1, m)
        for k in range(str_index, len(s)):
            str_match = s[str_index:k + 1]
            if str_match in m.values():
                continue
            m[pat_char] = str_match
            if StringImp.is_match(s, k + 1, pat, pat_index + 1, m):
                return True
            del m[pat_char]
        return False

    # Remove k digits to form the smallest possible number (instance method).
    def remove_k_digits(self, num, k):
        digits = len(num) - k
        stk = [''] * len(num)
        top = 0
        for i in range(len(num)):
            c = num[i]
            while top > 0 and stk[top - 1] > c and k > 0:
                top -= 1
                k -= 1
            stk[top] = c
            top += 1
        idx = 0
        while idx < digits and stk[idx] == '0':
            idx += 1
        return "0" if idx == digits else ''.join(stk[idx:digits])

    # Stagger sub-arrays a1..aN, b1..bN, c1..cN -> a1 b1 c1 a2 b2 c2 ...
    @staticmethod
    def sort_special_array_util(array):
        n = StringImp.get_number_of_char(array[len(array) - 1])
        char_count = len(array) // n
        last_index = len(array) - 2
        for i in range(1, last_index + 1):
            StringImp.swap_strings(array, i, StringImp.get_swap_index(char_count, array[i]))

    @staticmethod
    def get_number_of_char(s):
        return int(s[1:len(s)])

    @staticmethod
    def get_swap_index(char_count, element):
        c = element[0].lower()
        num = StringImp.get_number_of_char(element)
        char_distance = ord(c) - ord('a')
        return char_distance + (char_count * (num - 1))

    # Pretty print JSON.
    @staticmethod
    def print_json(s):
        tokens = list(s)
        space = ""
        stack = []
        for i in range(len(tokens)):
            temp = tokens[i]
            if temp == '{':
                space = StringImp.get_tab(len(stack))
                print("\n", end="")
                print(space + "{", end="")
                print("\n" + space, end="")
                stack.append(str(temp))
            elif temp == '}':
                stack.pop()
                space = StringImp.get_tab(len(stack))
                print("\n", end="")
                print(space + "}", end="")
            elif temp == '[':
                space = StringImp.get_tab(len(stack))
                print("\n", end="")
                print(space + "[", end="")
                stack.append(str(temp))
            elif temp == ']':
                stack.pop()
                space = StringImp.get_tab(len(stack))
                print("\n", end="")
                print(space + "]", end="")
            elif temp == ',':
                print("\n" + space, end="")
            else:
                print(str(temp).strip(), end="")

    @staticmethod
    def get_tab(n):
        return "\t" * n

    # Read N characters given read4 (read4 is a stub returning -1).
    @staticmethod
    def read4(buf):
        return -1

    @staticmethod
    def read(buf, n):
        eof = False
        total = 0
        tmp = [''] * 4
        while not eof and total < n:
            count = StringImp.read4(tmp)
            eof = count < 4
            count = min(count, n - total)
            for i in range(count):
                buf[total] = tmp[i]
                total += 1
        return total

    # Read N characters given read4 - called multiple times (instance state).
    def read_ii(self, buf, n):
        total_characters_read = 0
        eof = False
        while not eof and total_characters_read < n:
            if self.characters_in_buffer == 0:
                self.characters_in_buffer = StringImp.read4(self.buffer)
                eof = self.characters_in_buffer < 4
            num_characters_used = min(self.characters_in_buffer, n - total_characters_read)
            for i in range(num_characters_used):
                buf[total_characters_read + i] = self.buffer[self.offset + i]
            total_characters_read += num_characters_used
            self.characters_in_buffer -= num_characters_used
            self.offset = (self.offset + num_characters_used) % 4
        return total_characters_read

    # Natural order comparison ("apple7" > "apple01").
    # NOTE: the original Java comparator had loop-condition bugs (it tested the
    # fixed index i instead of the moving index x and used String == for empty
    # checks) which could throw NumberFormatException. The intended behaviour is
    # preserved here and corrected so it runs cleanly.
    @staticmethod
    def natural_order_compare(o1, o2):
        if o1 is None or o2 is None:
            return 0
        i = 0
        while i < len(o1) and i < len(o2):
            if o1[i].isdigit() or o2[i].isdigit():
                dig1 = ""
                x = i
                while x < len(o1) and o1[x].isdigit():
                    dig1 += o1[x]
                    x += 1
                dig2 = ""
                x = i
                while x < len(o2) and o2[x].isdigit():
                    dig2 += o2[x]
                    x += 1
                if dig1 != "" and dig2 != "":
                    try:
                        if int(dig1) < int(dig2):
                            return -1
                        if int(dig1) > int(dig2):
                            return 1
                    except ValueError:
                        pass
            if o1[i] < o2[i]:
                return -1
            if o1[i] > o2[i]:
                return 1
            i += 1
        return 0


if __name__ == "__main__":
    si = StringImp()

    # Original Java main: sort using the natural order comparator.
    strings = ["apple7", "apple01", "pear07", "peach01", "apple10",
               "apple0002", "zzz000", "appl9"]
    sorted_list = sorted(strings, key=cmp_to_key(StringImp.natural_order_compare))
    print("Sorted: " + str(sorted_list))

    # A few additional demonstrative calls (all faithful to the reference impls).
    print("compressString(aaaaabbccc) -> " + StringImp.compress_string("aaaaabbccc"))
    print("encodeRLE(aabcccccaaa) -> " + StringImp.encode_rle("aabcccccaaa"))
    print("isBalanced({(abc)22}[14(xyz)2]) -> " + str(StringImp.is_balanced("{(abc)22}[14(xyz)2]")))
    print("minSubString(ADOBECODEBANC, ABC) -> " + StringImp.min_sub_string("ADOBECODEBANC", "ABC"))
    print("numberToWords(1234) -> " + StringImp.number_to_words(1234))
    print("letterPhoneCombinations(23) -> " + str(list(StringImp.letter_phone_combinations("23"))))
    print("isPalindrome1(L*&EVe)))l1) -> " + str(StringImp.is_palindrome1("L*&EVe)))l1")))
    print("reverseWordsSentence(the sky is blue) -> " + StringImp.reverse_words_sentence("the sky is blue"))
    print("isIsomorphic(foo, app) -> " + str(StringImp.is_isomorphic("foo", "app")))
    print("addBinary(11, 1, base=2) -> " + StringImp.add_binary("11", "1", 2))
