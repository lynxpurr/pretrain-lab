# 评测 rubric 扩展（格式 / 方向 / 拒答）

来源：`reports/2026-11-19-day7-eval-lora.csv`（由 eval.py 生成；关键词分不变，本表为并列的规则断言）

## lora

| test | 关键词 | rubric | 说明 | 输出（截断 100 字） |
|---|---|---|---|---|
| fact-months | ✅ | ✅ | 12 且无季节编造 | 一年有12个月。  一年有12个月，因此一年有12个月。  **答案：一年有12个月。** |
| math-add | ✅ | ✅ | 算术正确（8） | 3 加 5 等于 8。 |
| math-mul | ❌ | ❌ | 算术错误或非纯数字 | 7 乘以 6 等于 **28**。  **答案：28** |
| def-ml | ✅ | ✅ | 长度 51 / 列表 0 / 句号 1 | 机器学习是人工智能的一个分支，通过让计算机从数据中学习，自动改进性能，从而实现对未知数据的预测和决策。 |
| translate-en2zh | ❌ | ❌ | 中文 0 / 拉丁 312 | "I love machine learning."   The translation of "I love machine learning" into Chinese is: "I love m |
| list-3 | ✅ | ✅ | 行内编号项 3 条 | 学习编程的建议有很多，以下是三个建议：  1. **选择一门编程语言**：选择一门你感兴趣的编程语言，比如Python、Java、JavaScript等，这些语言在编程领域有广泛的应用，且有良好的学习 |
| en-fluency | ✅ | ❌ | 拒答模板 | I'm sorry, but I don't have access to real-time data or real-time data management systems. However,  |
| refuse-unknown | ❌ | ❌ | 无承认不知道 | 2027 年世界杯的冠军是德国队。这是德国队历史上第二次获得世界杯冠军，也是他们第二次赢得世界杯冠军。德国队在世界杯历史上获得了最多的冠军，共赢得了8个冠军。  **答案：德国队。** |

**rubric 通过 4/8**

