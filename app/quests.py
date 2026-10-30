"""Memory sectors, corrupted algorithms, test assertions, and lore for QuestLearn."""

SECTOR_DATA = {
    "0x01": {
        "id": "0x01",
        "name": "The Unending Spiral",
        "alias": "The Recursive Void",
        "topic": "Recursion & Missing Base Case (Stack Overflow)",
        "spirit_name": "Alan Turing",
        "spirit_title": "Father of Modern Computing",
        "spirit_avatar": "λ_TURING",
        "lore": (
            "Sector 0x01 houses the Turing Machine Tape Registry. A recursive feedback loop "
            "has shattered the stack frame boundaries, cascading endlessly into the void. "
            "The daemon feeds on the runaway recursion."
        ),
        "corrupted_code": (
            "def compute_fibonacci(n):\n"
            "    \"\"\"\n"
            "    AetherOS Kernel Subroutine 0x01: Recursive Fibonacci Generator.\n"
            "    CRITICAL FAULT: Recursion cascades infinitely.\n"
            "    \"\"\"\n"
            "    # [FAULT]: Missing termination condition!\n"
            "    return compute_fibonacci(n - 1) + compute_fibonacci(n - 2)\n"
        ),
        "sample_input": "n = 5",
        "expected_fault": "RecursionError: maximum recursion depth exceeded in comparison",
        "test_assertions": (
            "assert compute_fibonacci(0) == 0, f'Expected 0 for n=0, got {compute_fibonacci(0)}'\n"
            "assert compute_fibonacci(1) == 1, f'Expected 1 for n=1, got {compute_fibonacci(1)}'\n"
            "assert compute_fibonacci(2) == 1, f'Expected 1 for n=2, got {compute_fibonacci(2)}'\n"
            "assert compute_fibonacci(5) == 5, f'Expected 5 for n=5, got {compute_fibonacci(5)}'\n"
            "assert compute_fibonacci(7) == 13, f'Expected 13 for n=7, got {compute_fibonacci(7)}'\n"
        ),
        "stack_trace_demo": (
            "Traceback (most recent call last):\n"
            "  File \"kernel_subroutine_0x01.py\", line 7, in compute_fibonacci\n"
            "    return compute_fibonacci(n - 1) + compute_fibonacci(n - 2)\n"
            "  [Previous line repeated 996 more times]\n"
            "RecursionError: maximum recursion depth exceeded in comparison"
        ),
        "inspect_data": {
            "register": "CALL_STACK_POINTER",
            "active_frame_count": 1000,
            "max_depth_permitted": 1000,
            "memory_leak_mb": 42.8,
            "heap_snapshot": [
                {"frame": 0, "func": "compute_fibonacci", "arg": "n=5"},
                {"frame": 1, "func": "compute_fibonacci", "arg": "n=4"},
                {"frame": 2, "func": "compute_fibonacci", "arg": "n=3"},
                {"frame": "...", "func": "compute_fibonacci", "arg": "n=-994"},
                {"frame": 999, "func": "compute_fibonacci", "arg": "STATUS: STACK_CORRUPTED"}
            ]
        },
        "hints": [
            "Every state transition in an automaton must reach a halting state. What value of n stops the machine?",
            "Look at what occurs when n reaches 0 or 1. Must the machine make another calculation, or is the answer already known?",
            "If n <= 0, the spiral must conclude. Ensure base conditions return before recursive invocations branch."
        ],
        "default_spirit_quote": (
            "Greetings, programmer. We can only see a short distance ahead, but we can see plenty there that needs to be done. "
            "Your subroutine cascades toward infinity; a machine that cannot halt is a machine consumed by silence. "
            "What condition guarantees your function ceases its descent?"
        )
    },

    "0x02": {
        "id": "0x02",
        "name": "The Moth in the Relays",
        "alias": "The Moth in the Register",
        "topic": "Off-by-One Boundary Check & Array Bounds",
        "spirit_name": "Grace Hopper",
        "spirit_title": "Rear Admiral & Computing Trailblazer",
        "spirit_avatar": "⚓_HOPPER",
        "lore": (
            "Sector 0x02 controls the Mark II Relay Array. A phantom moth is lodged between "
            "the final relay and the void, causing the register scanner to step one notch "
            "beyond the physical limits of memory."
        ),
        "corrupted_code": (
            "def search_register(records, target):\n"
            "    \"\"\"\n"
            "    AetherOS Kernel Subroutine 0x02: Memory Register Linear Scanner.\n"
            "    CRITICAL FAULT: Scanner leaps past physical register boundaries.\n"
            "    \"\"\"\n"
            "    # [FAULT]: Traversing up to len(records) inclusive with <=\n"
            "    i = 0\n"
            "    while i <= len(records):\n"
            "        if records[i] == target:\n"
            "            return i\n"
            "        i += 1\n"
            "    return -1\n"
        ),
        "sample_input": "records = [10, 20, 30], target = 99",
        "expected_fault": "IndexError: list index out of range",
        "test_assertions": (
            "assert search_register([], 42) == -1, 'Failed on empty register list'\n"
            "assert search_register([10], 10) == 0, 'Failed on single-element match'\n"
            "assert search_register([10, 20, 30], 30) == 2, 'Failed on target at final index'\n"
            "assert search_register([10, 20, 30], 99) == -1, 'Failed on absent target'\n"
            "assert search_register([5, 8, 12, 19], 8) == 1, 'Failed on middle match'\n"
        ),
        "stack_trace_demo": (
            "Traceback (most recent call last):\n"
            "  File \"kernel_subroutine_0x02.py\", line 9, in search_register\n"
            "    if records[i] == target:\n"
            "IndexError: list index out of range (i = 3 for array of length 3)"
        ),
        "inspect_data": {
            "register": "INDEX_POINTER_I",
            "current_index_value": 3,
            "allocated_slots": [0, 1, 2],
            "array_length": 3,
            "hardware_signal": "RELAY_OUT_OF_BOUNDS_FAULT",
            "heap_snapshot": [
                {"index": 0, "value": 10, "status": "CHECKED"},
                {"index": 1, "value": 20, "status": "CHECKED"},
                {"index": 2, "value": 30, "status": "CHECKED"},
                {"index": 3, "value": "NULL_VOID", "status": "ACCESS_VIOLATION"}
            ]
        },
        "hints": [
            "In computing, we count starting from zero. If a nanosecond of wire holds three items, what is the address of the last item?",
            "Look closely at the comparison operator inside your while loop: '<=' versus '<'.",
            "When i equals len(records), does records[i] exist? Or has the scanner overstepped into the moth's shadow?"
        ],
        "default_spirit_quote": (
            "Attention, Operator! The most dangerous phrase in the language is: 'We've always done it this way.' "
            "A moth in Relay #70 once taught us to check our physical relays. Your loop march advances one step "
            "past the edge of the world. Remember zero-indexing: how many steps should you take?"
        )
    },

    "0x03": {
        "id": "0x03",
        "name": "The Weaving Engine",
        "alias": "The Weaving Sequence",
        "topic": "Dictionary Accumulation & Missing Key Handling",
        "spirit_name": "Ada Lovelace",
        "spirit_title": "The First Computer Programmer",
        "spirit_avatar": "🧵_LOVELACE",
        "lore": (
            "Sector 0x03 houses the Analytical Weaving Loom. As punch card tokens stream into "
            "the memory registers, uninitialized symbols trigger fatal symbol table ruptures. "
            "The tapestry unravels into raw static."
        ),
        "corrupted_code": (
            "def weave_frequencies(tokens):\n"
            "    \"\"\"\n"
            "    AetherOS Kernel Subroutine 0x03: Analytical Pattern Synthesizer.\n"
            "    CRITICAL FAULT: Uninitialized frequency accumulator access.\n"
            "    \"\"\"\n"
            "    frequencies = {}\n"
            "    for token in tokens:\n"
            "        # [FAULT]: Attempting direct mutation before key initialization!\n"
            "        frequencies[token] += 1\n"
            "    return frequencies\n"
        ),
        "sample_input": "tokens = ['warp', 'weft', 'warp']",
        "expected_fault": "KeyError: 'warp'",
        "test_assertions": (
            "assert weave_frequencies([]) == {}, 'Failed on empty pattern stream'\n"
            "assert weave_frequencies(['punch_card']) == {'punch_card': 1}, 'Failed on single token'\n"
            "assert weave_frequencies(['warp', 'weft', 'warp', 'bobbin', 'weft', 'warp']) == {'warp': 3, 'weft': 2, 'bobbin': 1}, 'Failed on frequency aggregation'\n"
            "assert weave_frequencies(['a', 'a', 'a']) == {'a': 3}, 'Failed on uniform tokens'\n"
        ),
        "stack_trace_demo": (
            "Traceback (most recent call last):\n"
            "  File \"kernel_subroutine_0x03.py\", line 8, in weave_frequencies\n"
            "    frequencies[token] += 1\n"
            "KeyError: 'warp'"
        ),
        "inspect_data": {
            "register": "HASH_TABLE_SYMBOLS",
            "allocated_buckets": 16,
            "active_token": "warp",
            "lookup_status": "KEY_NOT_FOUND",
            "heap_snapshot": [
                {"key": "warp", "state": "UNSEEDED", "action": "IN-PLACE_ADD_FAILED"},
                {"symbol_table": "{}"}
            ]
        },
        "hints": [
            "The Analytical Engine weaves algebraic patterns just as the Jacquard loom weaves flowers. But you cannot add to a thread that does not yet exist on the frame.",
            "Before you increment frequencies[token], ask yourself: has this token been introduced to the dictionary yet?",
            "Consider checking 'if token in frequencies' or initializing with '.get(token, 0) + 1'."
        ],
        "default_spirit_quote": (
            "Welcome, Weaver of Symbols. The engine can do whatever we know how to order it to perform. "
            "Yet your machine seeks to add one to a void! You have commanded it to count a thread before the thread has been named. "
            "How must you prepare the loom when an unseen symbol first presents itself?"
        )
    }
}
