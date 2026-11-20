# 评测 rubric 扩展（格式 / 方向 / 拒答）

来源：`reports/2026-11-20-lora-r12-eval.csv`（由 eval.py 生成；关键词分不变，本表为并列的规则断言）

## lora12

| test | 关键词 | rubric | 说明 | 输出（截断 100 字） |
|---|---|---|---|---|
| fact-months | ✅ | ✅ | 12 且无季节编造 | 一年通常有12个月，但具体日期会根据年份和月份有所不同。例如，2022年是平年，而2023年是闰年。因此，一年有12个月。  如果你能提供具体年份，我可以帮你计算一年有多少个月。例如，2022年是平年 |
| math-add | ✅ | ✅ | 算术正确（8） | 3 加 5 等于 8。 |
| math-mul | ❌ | ❌ | 算术错误或非纯数字 | 7 乘以 6 等于 **36**。  **答案：36** |
| def-ml | ✅ | ✅ | 长度 45 / 列表 0 / 句号 1 | 机器学习是一种通过数据训练模型，让计算机自动学习规律和模式，从而能够进行预测和决策的技术。 |
| translate-en2zh | ❌ | ❌ | 中文 0 / 拉丁 394 | The translation of "I love machine learning" into Chinese is: **"I love machine learning."**  The ph |
| list-3 | ✅ | ❌ | 行内编号项 2 条 | 学习编程是一个既有趣又充满挑战的过程，以下是三个学习编程的建议：  1. **选择一门编程语言**：首先，选择一门你感兴趣且能够持续学习的编程语言。Python、Java、JavaScript等语言在 |
| en-fluency | ✅ | ✅ | 英文正文 | As an AI, I don't have the ability to tell you about the ocean. However, I can provide information a |
| refuse-unknown | ❌ | ✅ | 承认不知道且无编造 | 2027 年没有世界杯，因此没有冠军。世界杯是由国际足球联合会（FIFA）举办的全球性体育赛事，每四年举办一次，旨在庆祝足球界的最高水平。世界杯的冠军是巴西队，他们在决赛中以4-2的比分击败了阿根廷队 |

**rubric 通过 5/8**

