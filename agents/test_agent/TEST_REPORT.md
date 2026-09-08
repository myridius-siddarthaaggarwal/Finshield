# 🧪 FinShield Automated Verification & Test Report

> **Generated At**: `2026-09-08T16:47:50.873821+00:00`  
> **Overall Status**: **✅ ALL SYSTEMS OPERATIONAL**  

---

## 📊 Summary of Test Suites

| Test Suite | Status | Execution Time | Summary / Details |
| :--- | :---: | :--- | :--- |
| **Backend Pytest Suite** | ✅ PASS | 3.58s | ======================= 16 passed, 4 warnings in 0.52s ======================== |
| **Governed Data Layer Audit** | ✅ PASS | 0.006s | 4 Reference tables verified (FATF, Regs, Controls, Taxonomies) |
| **Prompt Versioning Audit** | ✅ PASS | 0.006s | Semantic prompt schemas valid |
| **Frontend Build Integrity** | ✅ PASS | 0.002s | Production bundle ready in `frontend/dist/` |

---

## 🔍 Detailed Backend Test Output
```
lient.py:41
  C:\Users\202140\OneDrive - RCG Global Services, Inc\Desktop\Finshield\.venv\Lib\site-packages\starlette\testclient.py:41: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    [], typing.ContextManager[anyio.abc.BlockingPortal]

..\.venv\Lib\site-packages\httpx\_client.py:680
  C:\Users\202140\OneDrive - RCG Global Services, Inc\Desktop\Finshield\.venv\Lib\site-packages\httpx\_client.py:680: DeprecationWarning: The 'app' shortcut is now deprecated. Use the explicit style 'transport=WSGITransport(app=...)' instead.
    warnings.warn(message, DeprecationWarning)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 16 passed, 4 warnings in 0.52s ========================

```
