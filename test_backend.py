"""Automated backend test suite for QuestLearn: Shadows of the Machine."""
import asyncio
import sys
from app.quests import SECTOR_DATA
from app.sandbox import execute_user_patch
from app.database import init_db, get_or_create_session, update_session_patch, reset_session
from app.llm_engine import get_spirit_guidance


async def run_tests():
    print("=== STARTING QUESTLEARN BACKEND VERIFICATION ===")

    # 1. Verify Sector Data
    print("\n1. Verifying Sector Data...")
    assert "0x01" in SECTOR_DATA, "Sector 0x01 missing"
    assert "0x02" in SECTOR_DATA, "Sector 0x02 missing"
    assert "0x03" in SECTOR_DATA, "Sector 0x03 missing"
    print("✓ All 3 sectors verified (Turing, Hopper, Lovelace).")

    # 2. Test Sandbox AST Security Rejection
    print("\n2. Testing Sandbox Security (AST Rejection)...")
    malicious_code = "import os\ndef compute_fibonacci(n):\n    return os.system('echo hacked')\n"
    res = execute_user_patch(malicious_code, SECTOR_DATA["0x01"]["test_assertions"])
    assert not res["success"], "Security violation should have failed"
    assert res["error_type"] == "SecurityViolation", f"Expected SecurityViolation, got {res['error_type']}"
    print(f"✓ Security rejection verified: {res['error_message']}")

    # 3. Test Sandbox Infinite Loop Timeout
    print("\n3. Testing Sandbox Timeout (2.0s hard limit)...")
    infinite_loop_code = "def compute_fibonacci(n):\n    while True:\n        pass\n"
    res = execute_user_patch(infinite_loop_code, SECTOR_DATA["0x01"]["test_assertions"])
    assert not res["success"], "Timeout test should have failed"
    assert res["error_type"] == "TimeoutError", f"Expected TimeoutError, got {res['error_type']}"
    print(f"✓ Timeout verified: {res['error_message']}")

    # 4. Test Corrupted Code Failure in Sandbox
    print("\n4. Testing Unpatched Code Failure...")
    corrupt_0x01 = SECTOR_DATA["0x01"]["corrupted_code"]
    res = execute_user_patch(corrupt_0x01, SECTOR_DATA["0x01"]["test_assertions"])
    assert not res["success"], "Corrupted code should fail unit tests"
    print(f"✓ Expected failure captured: {res['error_type']}")

    # 5. Test Successful Patches
    print("\n5. Testing Valid Patches for all 3 sectors...")
    
    # Sector 0x01 Patch
    patch_0x01 = (
        "def compute_fibonacci(n):\n"
        "    if n <= 0:\n"
        "        return 0\n"
        "    if n == 1:\n"
        "        return 1\n"
        "    return compute_fibonacci(n - 1) + compute_fibonacci(n - 2)\n"
    )
    res_0x01 = execute_user_patch(patch_0x01, SECTOR_DATA["0x01"]["test_assertions"])
    assert res_0x01["success"], f"Sector 0x01 patch failed: {res_0x01['error_message']}"
    print("✓ Sector 0x01 patch PASSED successfully!")

    # Sector 0x02 Patch
    patch_0x02 = (
        "def search_register(records, target):\n"
        "    for i in range(len(records)):\n"
        "        if records[i] == target:\n"
        "            return i\n"
        "    return -1\n"
    )
    res_0x02 = execute_user_patch(patch_0x02, SECTOR_DATA["0x02"]["test_assertions"])
    assert res_0x02["success"], f"Sector 0x02 patch failed: {res_0x02['error_message']}"
    print("✓ Sector 0x02 patch PASSED successfully!")

    # Sector 0x03 Patch
    patch_0x03 = (
        "def weave_frequencies(tokens):\n"
        "    frequencies = {}\n"
        "    for token in tokens:\n"
        "        frequencies[token] = frequencies.get(token, 0) + 1\n"
        "    return frequencies\n"
    )
    res_0x03 = execute_user_patch(patch_0x03, SECTOR_DATA["0x03"]["test_assertions"])
    assert res_0x03["success"], f"Sector 0x03 patch failed: {res_0x03['error_message']}"
    print("✓ Sector 0x03 patch PASSED successfully!")

    # 6. Test Database Session Lifecycle
    print("\n6. Testing Database Layer...")
    await init_db()
    test_session_id = "test_verify_session"
    sess = await reset_session(test_session_id)
    assert sess["integrity_score"] == 25, "Initial integrity should be 25%"

    # Patch 0x01
    sess = await update_session_patch(test_session_id, "0x01", True, patch_0x01)
    assert sess["integrity_score"] == 50, f"Expected 50%, got {sess['integrity_score']}"

    # Patch 0x02
    sess = await update_session_patch(test_session_id, "0x02", True, patch_0x02)
    assert sess["integrity_score"] == 75, f"Expected 75%, got {sess['integrity_score']}"

    # Patch 0x03
    sess = await update_session_patch(test_session_id, "0x03", True, patch_0x03)
    assert sess["integrity_score"] == 100, f"Expected 100%, got {sess['integrity_score']}"
    print("✓ System Integrity progression verified (25% -> 50% -> 75% -> 100% Exorcism).")

    # 7. Test Socratic Guidance (Live LLM or Offline Heuristic)
    print("\n7. Testing Socratic Guidance Generator...")
    guidance = await get_spirit_guidance("Alan Turing", "0x01", "RecursionError: maximum recursion depth exceeded", "Why does it crash?")
    assert len(guidance) > 20, "Guidance should provide meaningful response"
    assert "```python" not in guidance, "Guidance should NOT contain code blocks"
    print(f"✓ Socratic guidance verified: in-character and code-leak free (Sample: '{guidance[:60]}...')")

    print("\n=======================================================")
    print(">>> ALL BACKEND & PEDAGOGICAL TESTS PASSED PERFECTLY! <<<")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(run_tests())
