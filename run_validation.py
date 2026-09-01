# =============================================================================
# AUTOVOLT AI — AUTOMATED REGRESSION RUNNER
# =============================================================================

import sys
from validation import run_internal_tests

if __name__ == "__main__":
    print("Executing structural validation tests for AutoVolt AI V51.1...")
    results = run_internal_tests()
    print(f"Status: {results['overall']} ({results['passed']}/{results['total']} tests passed)")
    if results['overall'] != "PASS":
        sys.exit(1)
    print("System architecture verified clean. No compilation flaws found.")
    sys.exit(0)

