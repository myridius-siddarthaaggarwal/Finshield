# 🧪 FinShield Automated Verification & Test Report

> **Generated At**: `2026-09-08T16:28:29.755339+00:00`  
> **Overall Status**: **✅ ALL SYSTEMS OPERATIONAL**  

---

## 📊 Summary of Test Suites

| Test Suite | Status | Execution Time | Summary / Details |
| :--- | :---: | :--- | :--- |
| **Backend Pytest Suite** | ✅ PASS | 3.61s | ======================= 16 passed, 4 warnings in 2.04s ======================== |
| **Governed Data Layer Audit** | ✅ PASS | 0.017s | 4 Reference tables verified (FATF, Regs, Controls, Taxonomies) |
| **Prompt Versioning Audit** | ✅ PASS | 0.0s | Semantic prompt schemas valid |
| **Frontend Build Integrity** | ✅ PASS | 0.0s | Production bundle ready in `frontend/dist/` |

---

## 🔍 Detailed Backend Test Output
```
rnal\_config.py:272: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.6/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

..\.venv\Lib\site-packages\httpx\_client.py:680
  C:\Users\202140\OneDrive - RCG Global Services, Inc\Desktop\Finshield\.venv\Lib\site-packages\httpx\_client.py:680: DeprecationWarning: The 'app' shortcut is now deprecated. Use the explicit style 'transport=WSGITransport(app=...)' instead.
    warnings.warn(message, DeprecationWarning)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 16 passed, 4 warnings in 2.04s ========================

```
