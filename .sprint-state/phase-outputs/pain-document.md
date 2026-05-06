# Pain Document - Test Framework Unification

## 生成日期
2026-05-05

## 需求现实

项目已有 8+ 测试脚本，但 **没有统一测试框架** = CI 无法集成、新贡献者不知道用哪种方式写测试、覆盖率无法统计。这不是"想做"，而是"必须做"才能继续推进 #4 (CI/CD) 和 #1 (pyproject.toml)。

当前替代方案：手动运行 `python test/test_*.py` 逐个检查输出。这无法自动化，无法在 PR 中验证，测试失败只能在本地肉眼发现。

## 当前状态

- **Standalone scripts** (print-based): `test_translate.py`, `test_engines.py`, `test_config_creation.py`, `test_final.py`
  - 自定义 `test()` 辅助函数
  - `sys.path.insert(0, str(Path(__file__).parent.parent))` 在每个文件重复
  - `sys.exit(0)` / `sys.exit(1)` 表示通过/失败
- **unittest**: `test_clean_json_output.py` (unittest.TestCase)
- **无配置**: 无 `pytest.ini`, `conftest.py`, `tox.ini`
- **无 mock**: `test_engines.py` 需要真实 API key，无网络时失败
- **无覆盖率**: 无法量化测试完整性

## 绝望的具体性

新开发者 clone 仓库后：
1. 不知道用什么命令跑测试
2. 看到 `test/` 目录里有不同风格的脚本，困惑该遵循哪种
3. 想添加测试时，不知道复用哪个 helper 或 pattern
4. 提交 PR 后，没有任何自动化测试验证其改动

## 最窄切入点

**第一步**: 把 `test_config_creation.py`（最简单，纯 pydantic 验证，无外部依赖）和 `test_clean_json_output.py`（已有 unittest 基础）迁移到 pytest。

**第二步**: 创建 `conftest.py` 提供共享 fixture（project_root path, mock config）。

**第三步**: 逐步迁移其余测试，保持 `sys.path` 兼容直到全部迁移完成。

## 观察证据

从 init-deep 探索发现：
- `test/` 目录 19 个文件中有 8 个测试脚本 + 11 个报告文件
- `test/AGENTS.md` 明确记录了 "Mixed frameworks — Inconsistent test patterns" 作为 anti-pattern
- 现有 AGENTS.md 中运行测试的命令是手动拼接：`python test/test_translate.py && python test/test_engines.py && ...`

## 未来适配

pytest 是 Python 社区事实标准，未来 3-5 年内不会有替代方案。迁移后自动获得：CI 集成、覆盖率报告、fixture 复用、参数化测试、mock 支持、插件生态。

## Pain Statement

"测试脚本混合格式且无框架支持 → 每次代码改动都靠手动 eyeball 验证 → 无法集成 CI → 项目质量靠人脑把关。"

## Proposed Solution

1. 添加 `pytest` 到依赖
2. 创建 `conftest.py` 消除重复的 `sys.path` 注入
3. 逐步迁移现有测试到 pytest 风格（assert + fixture）
4. 对需要 API key 的测试添加 mock/patch
5. 添加 pytest 配置到 `pyproject.toml`（可与 #1 共用）或 `pytest.ini`
