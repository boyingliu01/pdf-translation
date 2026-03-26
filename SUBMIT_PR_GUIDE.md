# 向 BabelDoc 提交 PR 的完整指南

## 📋 背景

在我们的 PDF 翻译项目中，我们发现 BabelDoc 在遇到内容过滤错误（如智谱AI的敏感词过滤）时，会直接抛出异常并跳过翻译。为了解决这个问题，我们实现了外部的 fallback 机制，但这不够优雅。

**更好的方案**：向 BabelDoc 项目提交 PR，原生支持多模型 fallback。

---

## 🎯 PR 目标

为 BabelDoc 添加原生多模型 fallback 支持，当主模型因内容过滤等原因失败时，自动切换到备用模型重试。

---

## 📝 提交 Issue

### 步骤 1：访问 BabelDoc Issues 页面

打开：https://github.com/funstory-ai/BabelDOC/issues

### 步骤 2：创建新 Issue

点击 "New Issue" → 选择 "Feature request"

### 步骤 3：填写 Issue 内容

**标题**：
```
feat(translator): add multi-model fallback support for content filter errors
```

**内容**：使用 `GITHUB_ISSUE_TEMPLATE.md` 中的内容

### 步骤 4：等待维护者回复

根据贡献指南，必须先提交 Issue 讨论，得到维护者同意后再提交 PR。

---

## 🔧 实现 PR

### 步骤 1：Fork 仓库

```bash
# 访问 https://github.com/funstory-ai/BabelDOC
# 点击 Fork 按钮，创建自己的 fork
```

### 步骤 2：克隆并设置开发环境

```bash
# 克隆你的 fork
git clone https://github.com/YOUR_USERNAME/BabelDOC.git
cd BabelDOC

# 设置上游仓库
git remote add upstream https://github.com/funstory-ai/BabelDOC.git

# 使用 uv 设置开发环境（根据 CONTRIBUTING.md）
uv run babeldoc --help
```

### 步骤 3：创建功能分支

```bash
git checkout -b feat/multi-model-fallback
```

### 步骤 4：实现代码

参考 `PR_PROPOSAL.md` 中的实现方案，修改以下文件：

1. **`babeldoc/translator/translator.py`**
   - 在 `BaseTranslator` 类中添加 `fallback_translators` 参数
   - 添加 `translate_with_fallback` 方法

2. **`babeldoc/translation_config.py`**
   - 添加多模型配置解析

3. **`babeldoc/main.py`**
   - 添加命令行参数支持

4. **`babeldoc/format/pdf/document_il/midend/il_translator_llm_only.py`**
   - 修改调用点，使用 `translate_with_fallback`

### 步骤 5：测试

```bash
# 运行测试
uv run pytest

# 本地测试翻译
uv run babeldoc \
  --openai --openai-model "glm-4-flash" \
  --fallback-model "qwen3.5-plus" \
  --files test.pdf
```

### 步骤 6：提交代码

```bash
git add .
git commit -m "feat(translator): add multi-model fallback support

- Add fallback_translators parameter to BaseTranslator
- Implement translate_with_fallback method
- Add configuration support for multiple models
- Update il_translator_llm_only to use fallback

Closes #XXX"

git push origin feat/multi-model-fallback
```

### 步骤 7：创建 PR

1. 访问你的 fork 页面
2. 点击 "Compare & pull request"
3. 填写 PR 描述，参考 `PR_PROPOSAL.md`
4. 确保所有自动化检查通过

---

## 📁 相关文件

- `PR_PROPOSAL.md` - PR 提案详细说明
- `GITHUB_ISSUE_TEMPLATE.md` - GitHub Issue 模板
- `FALLBACK_ANALYSIS.md` - Fallback 机制失效分析

---

## 💡 注意事项

1. **必须先提交 Issue**：根据 CONTRIBUTING.md，必须先与维护者讨论
2. **英文提交**：Issue 和 PR 必须使用英文
3. **代码规范**：遵循 PEP8，使用类型注解，注释使用英文
4. **Conventional Commits**：使用规范化的 commit message
5. **小型 PR**：由于代码变动频繁，建议保持 PR 小型化

---

## 📧 联系维护者

如有问题，可以联系维护者：aw@funstory.ai

或在讨论组中提问：https://t.me/+Z9_SgnxmsmA5NzBl

---

## ✅ 检查清单

- [ ] 已提交 Issue 并得到维护者同意
- [ ] Fork 了仓库并创建了功能分支
- [ ] 代码遵循项目规范（PEP8、类型注解、英文注释）
- [ ] 添加了适当的日志记录
- [ ] 使用 Conventional Commits
- [ ] 所有自动化检查通过
- [ ] PR 描述清晰完整

---

**祝 PR 顺利合并！**
