"""
往 evalforge.db 注入 30+ 道题目（不清空已有任务/结果）。
运行：python seed_questions.py
"""
from models import Base, Question, engine, SessionLocal

Base.metadata.create_all(bind=engine)
db = SessionLocal()

QUESTIONS = [
    # ────────────────────────── HumanEval (基础算法) ──────────────────────────
    {
        "dataset_name": "HumanEval",
        "description": "Return the sum of two integers.",
        "function_signature": "def add(a: int, b: int) -> int:",
        "test_cases": [
            {"input": "add(1, 2)", "expected_output": 3},
            {"input": "add(-1, 1)", "expected_output": 0},
            {"input": "add(0, 0)", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return True if n is even, False otherwise.",
        "function_signature": "def is_even(n: int) -> bool:",
        "test_cases": [
            {"input": "is_even(4)", "expected_output": True},
            {"input": "is_even(7)", "expected_output": False},
            {"input": "is_even(0)", "expected_output": True},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Reverse a string.",
        "function_signature": "def reverse_str(s: str) -> str:",
        "test_cases": [
            {"input": "reverse_str('hello')", "expected_output": "olleh"},
            {"input": "reverse_str('ab')", "expected_output": "ba"},
            {"input": "reverse_str('')", "expected_output": ""},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the factorial of n (n >= 0).",
        "function_signature": "def factorial(n: int) -> int:",
        "test_cases": [
            {"input": "factorial(0)", "expected_output": 1},
            {"input": "factorial(5)", "expected_output": 120},
            {"input": "factorial(1)", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the maximum element in a list.",
        "function_signature": "def list_max(lst: list) -> int:",
        "test_cases": [
            {"input": "list_max([3, 1, 4, 1, 5])", "expected_output": 5},
            {"input": "list_max([-1, -3, -2])", "expected_output": -1},
            {"input": "list_max([42])", "expected_output": 42},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the nth Fibonacci number (0-indexed: fib(0)=0, fib(1)=1).",
        "function_signature": "def fib(n: int) -> int:",
        "test_cases": [
            {"input": "fib(0)", "expected_output": 0},
            {"input": "fib(1)", "expected_output": 1},
            {"input": "fib(7)", "expected_output": 13},
            {"input": "fib(10)", "expected_output": 55},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return True if s is a palindrome, False otherwise.",
        "function_signature": "def is_palindrome(s: str) -> bool:",
        "test_cases": [
            {"input": "is_palindrome('racecar')", "expected_output": True},
            {"input": "is_palindrome('hello')", "expected_output": False},
            {"input": "is_palindrome('a')", "expected_output": True},
            {"input": "is_palindrome('')", "expected_output": True},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the number of vowels in string s (a, e, i, o, u, case-insensitive).",
        "function_signature": "def count_vowels(s: str) -> int:",
        "test_cases": [
            {"input": "count_vowels('hello')", "expected_output": 2},
            {"input": "count_vowels('AEIOU')", "expected_output": 5},
            {"input": "count_vowels('xyz')", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return a sorted copy of the list in ascending order.",
        "function_signature": "def sort_list(lst: list) -> list:",
        "test_cases": [
            {"input": "sort_list([3, 1, 2])", "expected_output": [1, 2, 3]},
            {"input": "sort_list([5])", "expected_output": [5]},
            {"input": "sort_list([])", "expected_output": []},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the greatest common divisor of two positive integers.",
        "function_signature": "def gcd(a: int, b: int) -> int:",
        "test_cases": [
            {"input": "gcd(12, 8)", "expected_output": 4},
            {"input": "gcd(100, 75)", "expected_output": 25},
            {"input": "gcd(7, 13)", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the sum of all integers in a list.",
        "function_signature": "def sum_list(lst: list) -> int:",
        "test_cases": [
            {"input": "sum_list([1, 2, 3])", "expected_output": 6},
            {"input": "sum_list([])", "expected_output": 0},
            {"input": "sum_list([-1, 1])", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return True if n is a prime number.",
        "function_signature": "def is_prime(n: int) -> bool:",
        "test_cases": [
            {"input": "is_prime(2)", "expected_output": True},
            {"input": "is_prime(1)", "expected_output": False},
            {"input": "is_prime(17)", "expected_output": True},
            {"input": "is_prime(9)", "expected_output": False},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Flatten a one-level nested list, e.g. [[1,2],[3]] -> [1,2,3].",
        "function_signature": "def flatten(nested: list) -> list:",
        "test_cases": [
            {"input": "flatten([[1, 2], [3, 4]])", "expected_output": [1, 2, 3, 4]},
            {"input": "flatten([[]])", "expected_output": []},
            {"input": "flatten([[1], [2], [3]])", "expected_output": [1, 2, 3]},
        ],
    },
    {
        "dataset_name": "HumanEval",
        "description": "Return the product of all numbers in a list. Return 1 for empty list.",
        "function_signature": "def product(lst: list) -> int:",
        "test_cases": [
            {"input": "product([1, 2, 3, 4])", "expected_output": 24},
            {"input": "product([])", "expected_output": 1},
            {"input": "product([0, 5])", "expected_output": 0},
        ],
    },
    # ───────────────────────── LeetCode-Easy ─────────────────────────────────
    {
        "dataset_name": "LeetCode-Easy",
        "description": (
            "两数之和：给定整数数组 nums 和目标值 target，"
            "返回两个数之和等于 target 的下标（列表，如 [0,1]）。"
        ),
        "function_signature": "def two_sum(nums: list, target: int) -> list:",
        "test_cases": [
            {"input": "two_sum([2, 7, 11, 15], 9)", "expected_output": [0, 1]},
            {"input": "two_sum([3, 2, 4], 6)", "expected_output": [1, 2]},
            {"input": "two_sum([3, 3], 6)", "expected_output": [0, 1]},
        ],
    },
    {
        "dataset_name": "LeetCode-Easy",
        "description": "有效括号：判断括号字符串是否合法（'()'、'[]'、'{}'）。",
        "function_signature": "def is_valid(s: str) -> bool:",
        "test_cases": [
            {"input": "is_valid('()')", "expected_output": True},
            {"input": "is_valid('()[]{}')", "expected_output": True},
            {"input": "is_valid('(]')", "expected_output": False},
            {"input": "is_valid('([)]')", "expected_output": False},
        ],
    },
    {
        "dataset_name": "LeetCode-Easy",
        "description": "合并两个有序列表，返回合并后的有序列表。",
        "function_signature": "def merge_sorted(l1: list, l2: list) -> list:",
        "test_cases": [
            {"input": "merge_sorted([1, 3, 5], [2, 4, 6])", "expected_output": [1, 2, 3, 4, 5, 6]},
            {"input": "merge_sorted([], [1])", "expected_output": [1]},
            {"input": "merge_sorted([], [])", "expected_output": []},
        ],
    },
    {
        "dataset_name": "LeetCode-Easy",
        "description": "爬楼梯：n 级台阶，每次 1 或 2 步，共有多少种爬法？",
        "function_signature": "def climb_stairs(n: int) -> int:",
        "test_cases": [
            {"input": "climb_stairs(1)", "expected_output": 1},
            {"input": "climb_stairs(2)", "expected_output": 2},
            {"input": "climb_stairs(5)", "expected_output": 8},
            {"input": "climb_stairs(10)", "expected_output": 89},
        ],
    },
    {
        "dataset_name": "LeetCode-Easy",
        "description": "买卖股票最佳时机：给定每天价格，最多买卖一次，返回最大利润。",
        "function_signature": "def max_profit(prices: list) -> int:",
        "test_cases": [
            {"input": "max_profit([7, 1, 5, 3, 6, 4])", "expected_output": 5},
            {"input": "max_profit([7, 6, 4, 3, 1])", "expected_output": 0},
            {"input": "max_profit([1, 2])", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "LeetCode-Easy",
        "description": "移除列表中所有等于 val 的元素，返回剩余元素组成的新列表。",
        "function_signature": "def remove_element(nums: list, val: int) -> list:",
        "test_cases": [
            {"input": "remove_element([3, 2, 2, 3], 3)", "expected_output": [2, 2]},
            {"input": "remove_element([0, 1, 2, 2, 3], 2)", "expected_output": [0, 1, 3]},
            {"input": "remove_element([], 1)", "expected_output": []},
        ],
    },
    {
        "dataset_name": "LeetCode-Easy",
        "description": "计数质数：返回小于 n 的质数个数。",
        "function_signature": "def count_primes(n: int) -> int:",
        "test_cases": [
            {"input": "count_primes(10)", "expected_output": 4},
            {"input": "count_primes(0)", "expected_output": 0},
            {"input": "count_primes(1)", "expected_output": 0},
            {"input": "count_primes(20)", "expected_output": 8},
        ],
    },
    {
        "dataset_name": "LeetCode-Easy",
        "description": "多数元素：找出列表中出现次数超过 n//2 的元素。",
        "function_signature": "def majority_element(nums: list) -> int:",
        "test_cases": [
            {"input": "majority_element([3, 2, 3])", "expected_output": 3},
            {"input": "majority_element([2, 2, 1, 1, 1, 2, 2])", "expected_output": 2},
            {"input": "majority_element([1])", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "LeetCode-Easy",
        "description": "反转整数：翻转整数各位数字，溢出（超出 32 位有符号整数范围）返回 0。",
        "function_signature": "def reverse_int(x: int) -> int:",
        "test_cases": [
            {"input": "reverse_int(123)", "expected_output": 321},
            {"input": "reverse_int(-123)", "expected_output": -321},
            {"input": "reverse_int(120)", "expected_output": 21},
            {"input": "reverse_int(0)", "expected_output": 0},
        ],
    },
    # ───────────────────────── 字符串处理 ────────────────────────────────────
    {
        "dataset_name": "字符串处理",
        "description": "判断两个字符串是否互为字母异位词（字符相同但顺序不同）。",
        "function_signature": "def is_anagram(s: str, t: str) -> bool:",
        "test_cases": [
            {"input": "is_anagram('anagram', 'nagaram')", "expected_output": True},
            {"input": "is_anagram('rat', 'car')", "expected_output": False},
            {"input": "is_anagram('ab', 'a')", "expected_output": False},
        ],
    },
    {
        "dataset_name": "字符串处理",
        "description": "返回字符串中第一个不重复字符的索引，若不存在返回 -1。",
        "function_signature": "def first_unique_char(s: str) -> int:",
        "test_cases": [
            {"input": "first_unique_char('leetcode')", "expected_output": 0},
            {"input": "first_unique_char('loveleetcode')", "expected_output": 2},
            {"input": "first_unique_char('aabb')", "expected_output": -1},
        ],
    },
    {
        "dataset_name": "字符串处理",
        "description": "将字符串中单词顺序反转，单词间以单个空格分隔。",
        "function_signature": "def reverse_words(s: str) -> str:",
        "test_cases": [
            {"input": "reverse_words('the sky is blue')", "expected_output": "blue is sky the"},
            {"input": "reverse_words('hello world')", "expected_output": "world hello"},
            {"input": "reverse_words('a')", "expected_output": "a"},
        ],
    },
    {
        "dataset_name": "字符串处理",
        "description": "最长公共前缀：返回字符串列表中所有字符串的最长公共前缀。",
        "function_signature": "def longest_common_prefix(strs: list) -> str:",
        "test_cases": [
            {"input": "longest_common_prefix(['flower', 'flow', 'flight'])", "expected_output": "fl"},
            {"input": "longest_common_prefix(['dog', 'racecar', 'car'])", "expected_output": ""},
            {"input": "longest_common_prefix(['interview'])", "expected_output": "interview"},
        ],
    },
    {
        "dataset_name": "字符串处理",
        "description": "罗马数字转整数：将合法的罗马数字字符串转换为整数。",
        "function_signature": "def roman_to_int(s: str) -> int:",
        "test_cases": [
            {"input": "roman_to_int('III')", "expected_output": 3},
            {"input": "roman_to_int('IV')", "expected_output": 4},
            {"input": "roman_to_int('IX')", "expected_output": 9},
            {"input": "roman_to_int('LVIII')", "expected_output": 58},
            {"input": "roman_to_int('MCMXCIV')", "expected_output": 1994},
        ],
    },
    {
        "dataset_name": "字符串处理",
        "description": "实现 strStr()：在 haystack 中找到 needle 第一次出现的位置，找不到返回 -1。",
        "function_signature": "def str_str(haystack: str, needle: str) -> int:",
        "test_cases": [
            {"input": "str_str('hello', 'll')", "expected_output": 2},
            {"input": "str_str('aaaaa', 'bba')", "expected_output": -1},
            {"input": "str_str('', '')", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "字符串处理",
        "description": "统计字符串中每个字符出现的频次，返回字典。",
        "function_signature": "def char_count(s: str) -> dict:",
        "test_cases": [
            {"input": "char_count('aab')", "expected_output": {"a": 2, "b": 1}},
            {"input": "char_count('')", "expected_output": {}},
            {"input": "char_count('zzz')", "expected_output": {"z": 3}},
        ],
    },
    # ───────────────────────── 数据结构 ───────────────────────────────────────
    {
        "dataset_name": "数据结构",
        "description": "给定整数列表，返回其中不重复元素组成的列表（保持原顺序）。",
        "function_signature": "def unique_elements(lst: list) -> list:",
        "test_cases": [
            {"input": "unique_elements([1, 2, 2, 3, 1])", "expected_output": [1, 2, 3]},
            {"input": "unique_elements([])", "expected_output": []},
            {"input": "unique_elements([5, 5, 5])", "expected_output": [5]},
        ],
    },
    {
        "dataset_name": "数据结构",
        "description": "给定两个列表，返回它们的交集（不重复）。",
        "function_signature": "def intersect(a: list, b: list) -> list:",
        "test_cases": [
            {"input": "sorted(intersect([1, 2, 3], [2, 3, 4]))", "expected_output": [2, 3]},
            {"input": "intersect([], [1, 2])", "expected_output": []},
            {"input": "sorted(intersect([1, 1, 2], [1]))", "expected_output": [1]},
        ],
    },
    {
        "dataset_name": "数据结构",
        "description": "给定整数列表，找出出现次数最多的元素（若有多个取最小值）。",
        "function_signature": "def most_frequent(lst: list) -> int:",
        "test_cases": [
            {"input": "most_frequent([1, 2, 2, 3])", "expected_output": 2},
            {"input": "most_frequent([4, 4, 5, 5, 6])", "expected_output": 4},
            {"input": "most_frequent([7])", "expected_output": 7},
        ],
    },
    {
        "dataset_name": "数据结构",
        "description": "矩阵转置：给定二维列表（m×n），返回其转置（n×m）。",
        "function_signature": "def transpose(matrix: list) -> list:",
        "test_cases": [
            {"input": "transpose([[1, 2], [3, 4]])", "expected_output": [[1, 3], [2, 4]]},
            {"input": "transpose([[1, 2, 3]])", "expected_output": [[1], [2], [3]]},
            {"input": "transpose([[1]])", "expected_output": [[1]]},
        ],
    },
]

# 只插入不重复的（按 description 去重，防止重复运行）
existing = {q.description for q in db.query(Question).all()}
new_count = 0
for qd in QUESTIONS:
    if qd["description"] in existing:
        continue
    db.add(Question(**qd))
    new_count += 1

db.commit()
db.close()
print(f"✓ 新增 {new_count} 道题目（已跳过重复）")
