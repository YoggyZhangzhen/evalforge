"""
LeetCode Hot 100 题目注入（函数式题目，可直接代码沙盒评测）。
链表/树等依赖自定义节点类的题目暂不包含（沙盒无法序列化节点）。
运行：python seed_hot100.py
"""

HOT100 = [
    # ── 哈希 ─────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "两数之和：在 nums 中找两个下标使之和等于 target，返回 [i, j]。",
        "function_signature": "def two_sum(nums: list, target: int) -> list:",
        "test_cases": [
            {"input": "sorted(two_sum([2,7,11,15],9))", "expected_output": [0,1]},
            {"input": "sorted(two_sum([3,2,4],6))", "expected_output": [1,2]},
            {"input": "sorted(two_sum([3,3],6))", "expected_output": [0,1]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "字母异位词分组：将字符串列表按异位词分组，返回分组列表（内部顺序不限）。",
        "function_signature": "def group_anagrams(strs: list) -> list:",
        "test_cases": [
            {"input": "sorted([''.join(sorted(g)) for g in group_anagrams(['eat','tea','tan','ate','nat','bat'])])",
             "expected_output": sorted(["aet", "aet", "aet", "abn", "ant", "ant"])},
            {"input": "group_anagrams([''])", "expected_output": [[""]]},
            {"input": "group_anagrams(['a'])", "expected_output": [["a"]]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "最长连续序列：在未排序整数数组中找最长连续元素序列，返回长度（O(n) 时间）。",
        "function_signature": "def longest_consecutive(nums: list) -> int:",
        "test_cases": [
            {"input": "longest_consecutive([100,4,200,1,3,2])", "expected_output": 4},
            {"input": "longest_consecutive([0,3,7,2,5,8,4,6,0,1])", "expected_output": 9},
            {"input": "longest_consecutive([])", "expected_output": 0},
        ],
    },
    # ── 双指针 ────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "移动零：将所有 0 移到数组末尾，保持非零元素相对顺序，原地操作，返回结果列表。",
        "function_signature": "def move_zeroes(nums: list) -> list:",
        "test_cases": [
            {"input": "move_zeroes([0,1,0,3,12])", "expected_output": [1,3,12,0,0]},
            {"input": "move_zeroes([0])", "expected_output": [0]},
            {"input": "move_zeroes([1,2])", "expected_output": [1,2]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "盛最多水的容器：给定高度列表，找两条线使容纳水最多，返回最大容量。",
        "function_signature": "def max_area(height: list) -> int:",
        "test_cases": [
            {"input": "max_area([1,8,6,2,5,4,8,3,7])", "expected_output": 49},
            {"input": "max_area([1,1])", "expected_output": 1},
            {"input": "max_area([4,3,2,1,4])", "expected_output": 16},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "三数之和：找出所有不重复的三元组使之和为 0，返回列表（元素已排序）。",
        "function_signature": "def three_sum(nums: list) -> list:",
        "test_cases": [
            {"input": "sorted([sorted(t) for t in three_sum([-1,0,1,2,-1,-4])])",
             "expected_output": [[-1,-1,2],[-1,0,1]]},
            {"input": "three_sum([0,1,1])", "expected_output": []},
            {"input": "three_sum([0,0,0])", "expected_output": [[0,0,0]]},
        ],
    },
    # ── 滑动窗口 ──────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "无重复字符的最长子串：返回不含重复字符的最长子串长度。",
        "function_signature": "def length_of_longest_substring(s: str) -> int:",
        "test_cases": [
            {"input": "length_of_longest_substring('abcabcbb')", "expected_output": 3},
            {"input": "length_of_longest_substring('bbbbb')", "expected_output": 1},
            {"input": "length_of_longest_substring('pwwkew')", "expected_output": 3},
            {"input": "length_of_longest_substring('')", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "找到字符串中所有字母异位词：返回 p 的异位词在 s 中的起始下标列表。",
        "function_signature": "def find_anagrams(s: str, p: str) -> list:",
        "test_cases": [
            {"input": "find_anagrams('cbaebabacd','abc')", "expected_output": [0,6]},
            {"input": "find_anagrams('abab','ab')", "expected_output": [0,1,2]},
            {"input": "find_anagrams('aa','bb')", "expected_output": []},
        ],
    },
    # ── 子串 ──────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "和为 K 的子数组：返回和为 k 的连续子数组个数。",
        "function_signature": "def subarray_sum(nums: list, k: int) -> int:",
        "test_cases": [
            {"input": "subarray_sum([1,1,1],2)", "expected_output": 2},
            {"input": "subarray_sum([1,2,3],3)", "expected_output": 2},
            {"input": "subarray_sum([0,0,0,0],0)", "expected_output": 10},
        ],
    },
    # ── 普通数组 ──────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "最大子数组和（Kadane 算法）：返回连续子数组的最大和。",
        "function_signature": "def max_subarray(nums: list) -> int:",
        "test_cases": [
            {"input": "max_subarray([-2,1,-3,4,-1,2,1,-5,4])", "expected_output": 6},
            {"input": "max_subarray([1])", "expected_output": 1},
            {"input": "max_subarray([5,4,-1,7,8])", "expected_output": 23},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "合并区间：合并所有重叠区间，返回合并后的区间列表（已排序）。",
        "function_signature": "def merge_intervals(intervals: list) -> list:",
        "test_cases": [
            {"input": "merge_intervals([[1,3],[2,6],[8,10],[15,18]])",
             "expected_output": [[1,6],[8,10],[15,18]]},
            {"input": "merge_intervals([[1,4],[4,5]])", "expected_output": [[1,5]]},
            {"input": "merge_intervals([[1,4],[2,3]])", "expected_output": [[1,4]]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "轮转数组：将数组向右轮转 k 步，返回结果列表。",
        "function_signature": "def rotate(nums: list, k: int) -> list:",
        "test_cases": [
            {"input": "rotate([1,2,3,4,5,6,7],3)", "expected_output": [5,6,7,1,2,3,4]},
            {"input": "rotate([-1,-100,3,99],2)", "expected_output": [3,99,-1,-100]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "除自身以外数组的乘积：返回列表，每个元素是除自身以外所有元素的乘积（不使用除法）。",
        "function_signature": "def product_except_self(nums: list) -> list:",
        "test_cases": [
            {"input": "product_except_self([1,2,3,4])", "expected_output": [24,12,8,6]},
            {"input": "product_except_self([-1,1,0,-3,3])", "expected_output": [0,0,9,0,0]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "缺失的第一个正数：找出未排序整数数组中没有出现的最小正整数（O(n) 时间，O(1) 额外空间）。",
        "function_signature": "def first_missing_positive(nums: list) -> int:",
        "test_cases": [
            {"input": "first_missing_positive([1,2,0])", "expected_output": 3},
            {"input": "first_missing_positive([3,4,-1,1])", "expected_output": 2},
            {"input": "first_missing_positive([7,8,9,11,12])", "expected_output": 1},
        ],
    },
    # ── 矩阵 ──────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "矩阵置零：如果矩阵中元素为 0，则将其所在行列全部置 0，返回结果矩阵。",
        "function_signature": "def set_zeroes(matrix: list) -> list:",
        "test_cases": [
            {"input": "set_zeroes([[1,1,1],[1,0,1],[1,1,1]])",
             "expected_output": [[1,0,1],[0,0,0],[1,0,1]]},
            {"input": "set_zeroes([[0,1,2,0],[3,4,5,2],[1,3,1,5]])",
             "expected_output": [[0,0,0,0],[0,4,5,0],[0,3,1,0]]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "螺旋矩阵：按顺时针螺旋顺序返回矩阵中的所有元素。",
        "function_signature": "def spiral_order(matrix: list) -> list:",
        "test_cases": [
            {"input": "spiral_order([[1,2,3],[4,5,6],[7,8,9]])",
             "expected_output": [1,2,3,6,9,8,7,4,5]},
            {"input": "spiral_order([[1,2,3,4],[5,6,7,8],[9,10,11,12]])",
             "expected_output": [1,2,3,4,8,12,11,10,9,5,6,7]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "旋转图像：将 n×n 矩阵顺时针旋转 90 度，返回旋转后的矩阵（原地）。",
        "function_signature": "def rotate_image(matrix: list) -> list:",
        "test_cases": [
            {"input": "rotate_image([[1,2,3],[4,5,6],[7,8,9]])",
             "expected_output": [[7,4,1],[8,5,2],[9,6,3]]},
            {"input": "rotate_image([[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]])",
             "expected_output": [[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "搜索二维矩阵 II：在每行每列均升序的矩阵中搜索目标值，返回是否存在。",
        "function_signature": "def search_matrix(matrix: list, target: int) -> bool:",
        "test_cases": [
            {"input": "search_matrix([[1,4,7,11],[2,5,8,12],[3,6,9,16],[10,13,14,17]],5)",
             "expected_output": True},
            {"input": "search_matrix([[1,4,7,11],[2,5,8,12],[3,6,9,16],[10,13,14,17]],20)",
             "expected_output": False},
        ],
    },
    # ── 链表（用列表模拟）────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "反转链表（列表版）：将列表反转，返回新列表。",
        "function_signature": "def reverse_list(lst: list) -> list:",
        "test_cases": [
            {"input": "reverse_list([1,2,3,4,5])", "expected_output": [5,4,3,2,1]},
            {"input": "reverse_list([1,2])", "expected_output": [2,1]},
            {"input": "reverse_list([])", "expected_output": []},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "两数相加（列表版）：两个非负整数以逆序列表存储，返回它们之和的逆序列表。",
        "function_signature": "def add_two_numbers(l1: list, l2: list) -> list:",
        "test_cases": [
            {"input": "add_two_numbers([2,4,3],[5,6,4])", "expected_output": [7,0,8]},
            {"input": "add_two_numbers([0],[0])", "expected_output": [0]},
            {"input": "add_two_numbers([9,9,9,9],[9,9,9])", "expected_output": [8,9,9,0,1]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "删除链表倒数第 N 个节点（列表版）：删除列表倒数第 n 个元素，返回结果列表。",
        "function_signature": "def remove_nth_from_end(lst: list, n: int) -> list:",
        "test_cases": [
            {"input": "remove_nth_from_end([1,2,3,4,5],2)", "expected_output": [1,2,3,5]},
            {"input": "remove_nth_from_end([1],1)", "expected_output": []},
            {"input": "remove_nth_from_end([1,2],1)", "expected_output": [1]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "合并 K 个升序列表：合并 k 个已排序列表，返回一个升序列表。",
        "function_signature": "def merge_k_lists(lists: list) -> list:",
        "test_cases": [
            {"input": "merge_k_lists([[1,4,5],[1,3,4],[2,6]])",
             "expected_output": [1,1,2,3,4,4,5,6]},
            {"input": "merge_k_lists([])", "expected_output": []},
            {"input": "merge_k_lists([[]])", "expected_output": []},
        ],
    },
    # ── 二叉树（用列表层序表示，None 代表空节点）──────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": (
            "二叉树层序遍历（列表版）：给定层序数组（None 为空），"
            "返回每层元素列表的列表。"
        ),
        "function_signature": "def level_order(root_arr: list) -> list:",
        "test_cases": [
            {"input": "level_order([3,9,20,None,None,15,7])",
             "expected_output": [[3],[9,20],[15,7]]},
            {"input": "level_order([1])", "expected_output": [[1]]},
            {"input": "level_order([])", "expected_output": []},
        ],
    },
    # ── 图 ────────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": (
            "岛屿数量：给定由 '1'（陆地）和 '0'（水）组成的二维网格，计算岛屿数量。"
        ),
        "function_signature": "def num_islands(grid: list) -> int:",
        "test_cases": [
            {"input": "num_islands([['1','1','1','1','0'],['1','1','0','1','0'],['1','1','0','0','0'],['0','0','0','0','0']])",
             "expected_output": 1},
            {"input": "num_islands([['1','1','0','0','0'],['1','1','0','0','0'],['0','0','1','0','0'],['0','0','0','1','1']])",
             "expected_output": 3},
            {"input": "num_islands([])", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": (
            "腐烂的橘子：网格中 0 空格、1 新鲜橘子、2 腐烂橘子，"
            "腐烂每分钟向四周扩散，返回所有橘子腐烂的分钟数；不能全腐烂返回 -1。"
        ),
        "function_signature": "def oranges_rotting(grid: list) -> int:",
        "test_cases": [
            {"input": "oranges_rotting([[2,1,1],[1,1,0],[0,1,1]])", "expected_output": 4},
            {"input": "oranges_rotting([[2,1,1],[0,1,1],[1,0,1]])", "expected_output": -1},
            {"input": "oranges_rotting([[0,2]])", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": (
            "课程表：n 门课，prerequisites[i]=[a,b] 表示先修 b 再修 a，"
            "判断是否能完成所有课程（即是否存在拓扑排序）。"
        ),
        "function_signature": "def can_finish(num_courses: int, prerequisites: list) -> bool:",
        "test_cases": [
            {"input": "can_finish(2,[[1,0]])", "expected_output": True},
            {"input": "can_finish(2,[[1,0],[0,1]])", "expected_output": False},
            {"input": "can_finish(4,[[1,0],[2,0],[3,1],[3,2]])", "expected_output": True},
        ],
    },
    # ── 回溯 ──────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "全排列：返回整数列表的所有不重复全排列（内部已排序）。",
        "function_signature": "def permute(nums: list) -> list:",
        "test_cases": [
            {"input": "sorted([sorted(p) for p in permute([1,2,3])])",
             "expected_output": sorted([sorted(p) for p in [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]])},
            {"input": "permute([1])", "expected_output": [[1]]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "子集：返回整数集合的所有子集（幂集），结果中子集已排序。",
        "function_signature": "def subsets(nums: list) -> list:",
        "test_cases": [
            {"input": "sorted([sorted(s) for s in subsets([1,2,3])])",
             "expected_output": [[],[1],[1,2],[1,2,3],[1,3],[2],[2,3],[3]]},
            {"input": "subsets([])", "expected_output": [[]]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "电话号码的字母组合：给定数字字符串，返回所有可能的字母组合（9 宫格映射）。",
        "function_signature": "def letter_combinations(digits: str) -> list:",
        "test_cases": [
            {"input": "sorted(letter_combinations('23'))",
             "expected_output": sorted(["ad","ae","af","bd","be","bf","cd","ce","cf"])},
            {"input": "letter_combinations('')", "expected_output": []},
            {"input": "sorted(letter_combinations('2'))", "expected_output": ["a","b","c"]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "组合总和：找出 candidates 中所有和等于 target 的组合（每个数可用多次），返回列表。",
        "function_signature": "def combination_sum(candidates: list, target: int) -> list:",
        "test_cases": [
            {"input": "sorted([sorted(c) for c in combination_sum([2,3,6,7],7)])",
             "expected_output": [[2,2,3],[7]]},
            {"input": "sorted([sorted(c) for c in combination_sum([2,3,5],8)])",
             "expected_output": [[2,2,2,2],[2,3,3],[3,5]]},
            {"input": "combination_sum([2],1)", "expected_output": []},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "括号生成：生成 n 对括号的所有有效组合，返回排序后的列表。",
        "function_signature": "def generate_parentheses(n: int) -> list:",
        "test_cases": [
            {"input": "sorted(generate_parentheses(1))", "expected_output": ["()"]},
            {"input": "sorted(generate_parentheses(3))",
             "expected_output": sorted(["((()))","(()())","(())()","()(())","()()()"])},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "单词搜索：在字符网格中判断单词是否存在（可上下左右连续相邻）。",
        "function_signature": "def exist(board: list, word: str) -> bool:",
        "test_cases": [
            {"input": "exist([['A','B','C','E'],['S','F','C','S'],['A','D','E','E']],'ABCCED')",
             "expected_output": True},
            {"input": "exist([['A','B','C','E'],['S','F','C','S'],['A','D','E','E']],'SEE')",
             "expected_output": True},
            {"input": "exist([['A','B','C','E'],['S','F','C','S'],['A','D','E','E']],'ABCB')",
             "expected_output": False},
        ],
    },
    # ── 二分查找 ──────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "搜索插入位置：在排序数组中找目标值，存在则返回下标，不存在则返回应插入位置。",
        "function_signature": "def search_insert(nums: list, target: int) -> int:",
        "test_cases": [
            {"input": "search_insert([1,3,5,6],5)", "expected_output": 2},
            {"input": "search_insert([1,3,5,6],2)", "expected_output": 1},
            {"input": "search_insert([1,3,5,6],7)", "expected_output": 4},
            {"input": "search_insert([1,3,5,6],0)", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "搜索旋转排序数组：在旋转过的升序数组中搜索目标值，返回下标，不存在返回 -1。",
        "function_signature": "def search_rotated(nums: list, target: int) -> int:",
        "test_cases": [
            {"input": "search_rotated([4,5,6,7,0,1,2],0)", "expected_output": 4},
            {"input": "search_rotated([4,5,6,7,0,1,2],3)", "expected_output": -1},
            {"input": "search_rotated([1],0)", "expected_output": -1},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "寻找旋转排序数组中的最小值：返回旋转升序数组中的最小元素。",
        "function_signature": "def find_min(nums: list) -> int:",
        "test_cases": [
            {"input": "find_min([3,4,5,1,2])", "expected_output": 1},
            {"input": "find_min([4,5,6,7,0,1,2])", "expected_output": 0},
            {"input": "find_min([11,13,15,17])", "expected_output": 11},
        ],
    },
    # ── 栈 ────────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "每日温度：给定气温列表，返回每天需要等多少天才能等到更高温度（没有则为 0）。",
        "function_signature": "def daily_temperatures(temperatures: list) -> list:",
        "test_cases": [
            {"input": "daily_temperatures([73,74,75,71,69,72,76,73])",
             "expected_output": [1,1,4,2,1,1,0,0]},
            {"input": "daily_temperatures([30,40,50,60])", "expected_output": [1,1,1,0]},
            {"input": "daily_temperatures([30,60,90])", "expected_output": [1,1,0]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "柱状图中最大的矩形：给定柱状图高度列表，返回最大矩形面积。",
        "function_signature": "def largest_rectangle(heights: list) -> int:",
        "test_cases": [
            {"input": "largest_rectangle([2,1,5,6,2,3])", "expected_output": 10},
            {"input": "largest_rectangle([2,4])", "expected_output": 4},
            {"input": "largest_rectangle([1])", "expected_output": 1},
        ],
    },
    # ── 堆 ────────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "数组中的第 K 个最大元素：返回排序后第 k 大的元素（不排序数组）。",
        "function_signature": "def find_kth_largest(nums: list, k: int) -> int:",
        "test_cases": [
            {"input": "find_kth_largest([3,2,1,5,6,4],2)", "expected_output": 5},
            {"input": "find_kth_largest([3,2,3,1,2,4,5,5,6],4)", "expected_output": 4},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "前 K 个高频元素：返回出现频率前 k 高的元素列表（顺序不限）。",
        "function_signature": "def top_k_frequent(nums: list, k: int) -> list:",
        "test_cases": [
            {"input": "sorted(top_k_frequent([1,1,1,2,2,3],2))", "expected_output": [1,2]},
            {"input": "top_k_frequent([1],1)", "expected_output": [1]},
        ],
    },
    # ── 贪心 ──────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "跳跃游戏：给定跳跃步数数组，判断是否能从第一个位置跳到最后一个位置。",
        "function_signature": "def can_jump(nums: list) -> bool:",
        "test_cases": [
            {"input": "can_jump([2,3,1,1,4])", "expected_output": True},
            {"input": "can_jump([3,2,1,0,4])", "expected_output": False},
            {"input": "can_jump([0])", "expected_output": True},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "跳跃游戏 II：返回从第一个位置跳到最后一个位置的最少跳跃次数（可以到达）。",
        "function_signature": "def jump(nums: list) -> int:",
        "test_cases": [
            {"input": "jump([2,3,1,1,4])", "expected_output": 2},
            {"input": "jump([2,3,0,1,4])", "expected_output": 2},
            {"input": "jump([1])", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "划分字母区间：将字符串划分为尽量多的片段，每种字母至多出现在一个片段中，返回每段长度列表。",
        "function_signature": "def partition_labels(s: str) -> list:",
        "test_cases": [
            {"input": "partition_labels('ababcbacadefegdehijhklij')", "expected_output": [9,7,8]},
            {"input": "partition_labels('eccbbbbdec')", "expected_output": [10]},
        ],
    },
    # ── 动态规划 ──────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "爬楼梯：n 级台阶，每次 1 或 2 步，返回爬法总数。",
        "function_signature": "def climb_stairs(n: int) -> int:",
        "test_cases": [
            {"input": "climb_stairs(2)", "expected_output": 2},
            {"input": "climb_stairs(3)", "expected_output": 3},
            {"input": "climb_stairs(10)", "expected_output": 89},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "杨辉三角：返回杨辉三角的前 numRows 行。",
        "function_signature": "def generate_triangle(numRows: int) -> list:",
        "test_cases": [
            {"input": "generate_triangle(5)",
             "expected_output": [[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]},
            {"input": "generate_triangle(1)", "expected_output": [[1]]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "打家劫舍：不能抢相邻房屋，返回能抢到的最大金额。",
        "function_signature": "def rob(nums: list) -> int:",
        "test_cases": [
            {"input": "rob([1,2,3,1])", "expected_output": 4},
            {"input": "rob([2,7,9,3,1])", "expected_output": 12},
            {"input": "rob([1])", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "完全平方数：返回和为 n 的最少完全平方数个数。",
        "function_signature": "def num_squares(n: int) -> int:",
        "test_cases": [
            {"input": "num_squares(12)", "expected_output": 3},
            {"input": "num_squares(13)", "expected_output": 2},
            {"input": "num_squares(1)", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "零钱兑换：给定硬币面值列表和总金额，返回凑成 amount 所需最少硬币数，无法凑成返回 -1。",
        "function_signature": "def coin_change(coins: list, amount: int) -> int:",
        "test_cases": [
            {"input": "coin_change([1,2,5],11)", "expected_output": 3},
            {"input": "coin_change([2],3)", "expected_output": -1},
            {"input": "coin_change([1],0)", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "单词拆分：判断字符串 s 是否能被字典 wordDict 中的单词拼接而成。",
        "function_signature": "def word_break(s: str, wordDict: list) -> bool:",
        "test_cases": [
            {"input": "word_break('leetcode',['leet','code'])", "expected_output": True},
            {"input": "word_break('applepenapple',['apple','pen'])", "expected_output": True},
            {"input": "word_break('catsandog',['cats','dog','sand','and','cat'])",
             "expected_output": False},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "最长递增子序列：返回最长严格递增子序列的长度。",
        "function_signature": "def length_of_lis(nums: list) -> int:",
        "test_cases": [
            {"input": "length_of_lis([10,9,2,5,3,7,101,18])", "expected_output": 4},
            {"input": "length_of_lis([0,1,0,3,2,3])", "expected_output": 4},
            {"input": "length_of_lis([7,7,7,7])", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "乘积最大子数组：返回连续子数组的最大乘积。",
        "function_signature": "def max_product(nums: list) -> int:",
        "test_cases": [
            {"input": "max_product([2,3,-2,4])", "expected_output": 6},
            {"input": "max_product([-2,0,-1])", "expected_output": 0},
            {"input": "max_product([-2,3,-4])", "expected_output": 24},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "分割等和子集：判断整数数组是否能分割成两个等和子集。",
        "function_signature": "def can_partition(nums: list) -> bool:",
        "test_cases": [
            {"input": "can_partition([1,5,11,5])", "expected_output": True},
            {"input": "can_partition([1,2,3,5])", "expected_output": False},
            {"input": "can_partition([1,1])", "expected_output": True},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "最长有效括号：给定括号字符串，返回最长有效括号子串的长度。",
        "function_signature": "def longest_valid_parentheses(s: str) -> int:",
        "test_cases": [
            {"input": "longest_valid_parentheses('(()')", "expected_output": 2},
            {"input": "longest_valid_parentheses(')()())')", "expected_output": 4},
            {"input": "longest_valid_parentheses('')", "expected_output": 0},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "不同路径：m×n 网格从左上到右下只能向右或向下走，返回路径总数。",
        "function_signature": "def unique_paths(m: int, n: int) -> int:",
        "test_cases": [
            {"input": "unique_paths(3,7)", "expected_output": 28},
            {"input": "unique_paths(3,2)", "expected_output": 3},
            {"input": "unique_paths(1,1)", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "最小路径和：给定 m×n 非负整数矩阵，从左上角到右下角（只能向右/下），返回最小路径和。",
        "function_signature": "def min_path_sum(grid: list) -> int:",
        "test_cases": [
            {"input": "min_path_sum([[1,3,1],[1,5,1],[4,2,1]])", "expected_output": 7},
            {"input": "min_path_sum([[1,2,3],[4,5,6]])", "expected_output": 12},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "编辑距离：返回将 word1 转换成 word2 所用最少操作数（插入/删除/替换）。",
        "function_signature": "def min_distance(word1: str, word2: str) -> int:",
        "test_cases": [
            {"input": "min_distance('horse','ros')", "expected_output": 3},
            {"input": "min_distance('intention','execution')", "expected_output": 5},
            {"input": "min_distance('','abc')", "expected_output": 3},
        ],
    },
    # ── 多维 DP ───────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "接雨水：给定高度数组，计算能接的雨水总量。",
        "function_signature": "def trap(height: list) -> int:",
        "test_cases": [
            {"input": "trap([0,1,0,2,1,0,1,3,2,1,2,1])", "expected_output": 6},
            {"input": "trap([4,2,0,3,2,5])", "expected_output": 9},
            {"input": "trap([1,0,1])", "expected_output": 1},
        ],
    },
    # ── 技巧 ──────────────────────────────────────────────────────────────────
    {
        "dataset_name": "Hot100",
        "description": "只出现一次的数字：非空整数数组中除某元素外其余均出现两次，找出只出现一次的元素。",
        "function_signature": "def single_number(nums: list) -> int:",
        "test_cases": [
            {"input": "single_number([2,2,1])", "expected_output": 1},
            {"input": "single_number([4,1,2,1,2])", "expected_output": 4},
            {"input": "single_number([1])", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "多数元素：找出数组中出现次数超过 n//2 的元素（必定存在）。",
        "function_signature": "def majority_element(nums: list) -> int:",
        "test_cases": [
            {"input": "majority_element([3,2,3])", "expected_output": 3},
            {"input": "majority_element([2,2,1,1,1,2,2])", "expected_output": 2},
            {"input": "majority_element([1])", "expected_output": 1},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "颜色分类（荷兰国旗）：原地将 0、1、2 排序，返回排序后列表。",
        "function_signature": "def sort_colors(nums: list) -> list:",
        "test_cases": [
            {"input": "sort_colors([2,0,2,1,1,0])", "expected_output": [0,0,1,1,2,2]},
            {"input": "sort_colors([2,0,1])", "expected_output": [0,1,2]},
            {"input": "sort_colors([0])", "expected_output": [0]},
        ],
    },
    {
        "dataset_name": "Hot100",
        "description": "下一个排列：将数字列表重排为字典序中下一个更大的排列，返回结果列表。",
        "function_signature": "def next_permutation(nums: list) -> list:",
        "test_cases": [
            {"input": "next_permutation([1,2,3])", "expected_output": [1,3,2]},
            {"input": "next_permutation([3,2,1])", "expected_output": [1,2,3]},
            {"input": "next_permutation([1,1,5])", "expected_output": [1,5,1]},
        ],
    },
]

if __name__ == "__main__":
    from models import Base, Question, engine, SessionLocal
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    existing = {q.description for q in db.query(Question).all()}
    new_count = 0
    for qd in HOT100:
        if qd["description"] in existing:
            continue
        db.add(Question(**qd))
        new_count += 1
    db.commit()
    db.close()
    print(f"✓ 新增 Hot100 题目 {new_count} 道（已跳过重复）")
