#!/usr/bin/env python3
"""
run_all_tests.py
================
Self-contained automated test runner for AICOP-RAKSHA.
Runs all 4 test suites (48 test functions / 53 parameterized executions)
using native Python without requiring external pytest dependencies.
"""
import sys
import os
import inspect
import types
from pathlib import Path

# Ensure raksha-net root is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Provide mock pytest if not installed
try:
    import pytest
except ImportError:
    class MockPytest(types.ModuleType):
        class Mark:
            @staticmethod
            def parametrize(argnames, argvalues):
                def decorator(func):
                    func._pytest_parametrize = (argnames, argvalues)
                    return func
                return decorator

        mark = Mark()

        @staticmethod
        def approx(expected, rel=1e-6, abs=None, abs_tol=1e-12):
            import builtins
            b_abs = builtins.abs
            class ApproxValue:
                def __init__(self, exp, custom_abs):
                    self.exp = exp
                    self.custom_abs = custom_abs
                def __eq__(self, actual):
                    if actual is None:
                        return False
                    diff = b_abs(actual - self.exp)
                    tol = self.custom_abs if self.custom_abs is not None else max(rel * max(b_abs(actual), b_abs(self.exp)), abs_tol)
                    return diff <= tol
                def __repr__(self):
                    return f"approx({self.exp})"
            return ApproxValue(expected, abs)

        class RaisesContext:
            def __init__(self, exc_type):
                self.exc_type = exc_type
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    raise AssertionError(f"Expected exception {self.exc_type.__name__} was not raised")
                return issubclass(exc_type, self.exc_type)

        @staticmethod
        def raises(exc_type):
            return MockPytest.RaisesContext(exc_type)

    mock_pytest = MockPytest("pytest")
    sys.modules["pytest"] = mock_pytest

def discover_and_run():
    test_files = [
        "tests/test_crypto_agility.py",
        "tests/test_detector.py",
        "tests/test_leach_upgrades.py",
        "tests/test_scenario.py",
    ]

    total_run = 0
    total_passed = 0
    total_failed = 0
    failures = []

    print("=" * 70)
    print(" AICOP-RAKSHA AUTOMATED TEST RUNNER (48 Tests / 53 Parameterized)")
    print("=" * 70)

    for rel_path in test_files:
        file_path = BASE_DIR / rel_path
        if not file_path.exists():
            print(f"[!] Warning: {rel_path} not found")
            continue

        module_name = file_path.stem
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"[ERROR] Failed to load {rel_path}: {e}")
            total_failed += 1
            failures.append((rel_path, str(e)))
            continue

        print(f"\n--- Suite: {rel_path} ---")

        # Gather standalone functions and test classes
        items_to_run = []
        for name, obj in inspect.getmembers(mod):
            if inspect.isfunction(obj) and name.startswith("test_"):
                items_to_run.append((None, name, obj))
            elif inspect.isclass(obj) and name.startswith("Test"):
                instance = obj()
                for m_name, m_func in inspect.getmembers(instance, inspect.ismethod):
                    if m_name.startswith("test_"):
                        items_to_run.append((instance, f"{name}.{m_name}", m_func))

        for inst, full_name, func in items_to_run:
            param_info = getattr(func, "_pytest_parametrize", None)
            if param_info:
                argnames, argvalues = param_info
                for val in argvalues:
                    total_run += 1
                    test_label = f"{full_name}[{val}]"
                    try:
                        func(val)
                        print(f"  [PASS] {test_label}")
                        total_passed += 1
                    except Exception as e:
                        print(f"  [FAIL] {test_label}: {e}")
                        total_failed += 1
                        failures.append((test_label, str(e)))
            else:
                total_run += 1
                try:
                    func()
                    print(f"  [PASS] {full_name}")
                    total_passed += 1
                except Exception as e:
                    print(f"  [FAIL] {full_name}: {e}")
                    total_failed += 1
                    failures.append((full_name, str(e)))

    print("\n" + "=" * 70)
    print(f" SUMMARY: {total_passed} passed, {total_failed} failed, {total_run} total executed")
    print("=" * 70)

    if failures:
        print("\nFailures:")
        for name, err in failures:
            print(f"  - {name}: {err}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(discover_and_run())
