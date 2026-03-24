# PDF翻译问题诊断报告

## 问题概述

- **文档**: The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.pdf
- **翻译输出**: with_page_numbers.zh.dual.pdf (234页)
- **翻译工具**: pdf2zh-next (BabelDOC v0.5.23)

---

## 问题状态总结

| 问题 | 状态 | 根因 | 解决方案 |
|------|------|------|----------|
| 跨页段落翻译不完整 | ✅ 已修复 | `_filter_paragraphs` 副作用 + 补丁逻辑不完整 | 重写 `patch_babeldoc_cross_page()` |
| 字体大小不统一 | ✅ 已修复 | 同上（关联问题） | 同上 |
| 部分段落未翻译（API限制） | ⚠️ 无法修复 | API内容过滤器拦截敏感内容 | 需多模型fallback机制 |

---

## 问题1：跨页段落翻译不完整（已修复）

### 具体案例

| 页面 | 表现 | 原段落首句 |
|------|------|-----------|
| 第5页 | 英文截断在 "burly"，中文不完整 | "The suspicion was understandable..." |
| 第9页 | 英文截断在 "Jews and" | "He pitched Palantir as if..." |
| 第12→13页 | 英文截断在 "Rubik's Cube, and if not that..." | 同上 |

### 根因分析

**原始根因**：跨页段落分割问题

**代码层面根因**（2026-03-24 诊断）：
1. `enhanced_filter_paragraphs` 副作用 - 当没有body text时返回所有段落，影响其他处理流程
2. `patched_process_cross_page` 只记录日志，没有实际处理逻辑
3. 原始 BabelDOC 只处理 `layout_label` 为 "text/paragraph_hybrid" 的段落

### 修复方案

重写 `patch_babeldoc_cross_page()` 函数：
- 移除 `enhanced_filter_paragraphs` 替换（避免副作用）
- 完整实现跨页段落检测和批量翻译提交
- 使用 `BatchParagraph` 和 `executor.submit()` 进行翻译

**Commit**: e2f3655

---

## 问题2：字体大小不统一（已修复）

与问题1关联，修复方案同上。

---

## 问题3：API内容过滤导致的段落未翻译

### 具体案例

| 页面 | 段落ID | 表现 |
|------|--------|------|
| 第13页 | cSy8k | 整段英文未翻译 |

### 根因分析

**API内容过滤器拦截**

智谱AI (GLM-4-Flash) 返回错误：
```
Error code: 400 - {'error': {'code': '1301', 'message': '系统检测到输入或生成内容可能包含不安全或敏感内容'}}
```

**敏感内容触发点**：
- "Hamas attack" (哈马斯袭击)
- "October 7" (10月7日)
- "1,200 Israelis dead" (1200名以色列人死亡)
- "war on terrorism" (反恐战争)
- "Jews" (犹太人)

### 解决方案

**方案：多模型Fallback机制**

配置多个翻译API，按优先级顺序尝试：
1. 主模型（如智谱AI）- 免费额度
2. 备用模型1（如OpenAI）- 对政治内容更宽松
3. 备用模型2（如DeepSeek/SiliconFlow）

当遇到400错误（内容过滤）时，自动切换到下一个模型重试。

---

## 代码层面的证据

### BabelDOC 中的跨页处理

1. **切片处理** (`il_translator_llm_only.py`):
   ```python
   # Input paragraphs may be sliced pieces of the same original paragraph.
   # → You MUST treat each input paragraph as an independent, fixed unit.
   # → Do NOT merge paragraphs, split paragraphs, or move content between paragraphs.
   ```

2. **SharedContextCrossSplitPart** (`translation_config.py`):
   ```python
   class SharedContextCrossSplitPart:
       first_paragraph = None
       recent_title_paragraph = None
   ```
   这个类用于在分批处理时保持上下文。

3. **段落合并逻辑缺失**：当前代码明确禁止合并段落 (`Do NOT merge paragraphs`)，但没有相应的合并逻辑来处理跨页切片。

---

## 解决方案建议

### 方案1：启用兼容性增强（推荐先试）

```bash
python translate_pdf.py -i <file> -o <output> --enhance-compatibility
```

### 方案2：使用分批处理

减少每批处理的页面数，降低跨页问题的影响：

```bash
python translate_pdf.py -i <file> -o <output> --max-pages-per-part 50
```

### 方案3：修改 min_text_length 配置

```json
{
  "min_text_length": 1
}
```

### 方案4：向 BabelDOC 反馈

这是 BabelDOC 库的 bug，需要在库层面修复：
- 问题：`Do NOT merge paragraphs` 的指令与实际处理逻辑不符
- 需要：正确的跨页段落合并机制

---

## 诊断方法

### 查看特定页面内容
```python
import fitz
doc = fitz.open('output.pdf')
page = doc[page_num - 1]
print(page.get_text())
```

### 检查页面字体分布
```python
import fitz
doc = fitz.open('output.pdf')
page = doc[page_num - 1]
for block in page.get_text('dict')['blocks']:
    if 'lines' in block:
        for line in block['lines']:
            for span in line['spans']:
                print(f"Font: {span['font']}, Size: {span['size']}")
```

### 检查原版PDF段落结构
```python
import fitz
orig = fitz.open('original.pdf')
page = orig[page_num - 1]
blocks = page.get_text('dict')['blocks']
for i, block in enumerate(blocks):
    if 'lines' in block:
        y_positions = [span['bbox'][1] for line in block['lines'] for span in line['spans']]
        print(f"Block {i}: Y {min(y_positions):.1f}-{max(y_positions):.1f}")
```
