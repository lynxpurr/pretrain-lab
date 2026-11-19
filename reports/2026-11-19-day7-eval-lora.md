# 评测报告（2026-11-19 22:58）

- 预训练 val PPL：data/shards/val.bin（4,000,000 token，40×8 窗口）
- SFT val PPL：data/sft-mix/val.bin（只算 assistant token，ignore_index=-100）
- 测试集：data/eval/tests.json（18 题）· 解码协议 = **greedy**（T=0.0 top_k=0 top_p=1.0 rep=1.0）

## 汇总

| 模型 | 解码 | step | 预训练 PPL | SFT PPL | 测试集 | distinct-2 | rep-4 |
|---|---|---|---|---|---|---|---|
| lora | greedy | 3815 | 15.690 | 6.090 | 15/18 (83%) | 0.623 | 0.260 |

## lora · greedy（step 3815）

- 预训练 val PPL **15.690** · SFT val PPL **6.090** · 测试集 **15/18 = 83%** · distinct-2 **0.623** · rep-4 **0.260**（17s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| fact-capital-cn | fact-zh | ✅ | 0.191 | 0.739 | 中国的首都是北京。

北京是中国的首都，位于中国东部，是中国的首都。北京是中国的首都，也是中国的政治、文化和经济中心。北京是中国的首都，也是中国的政治、文化和经济中心。

北京是中国的首都，也是中国的政治、文化和经济中心。北京是中国的政治、 |
| fact-capital-fr | fact-en | ✅ | 0.299 | 0.541 | The capital of France is Paris. It is the largest city in the world and is located in the French capital of Paris. It is |
| fact-water | fact-zh | ✅ | 0.214 | 0.734 | 水的化学式是H2O。

水的化学式是H2O，其中H代表氢元素，O代表氧元素。水的化学式为H2O，其中H代表氢元素，O代表氧元素。

水的化学式是H2O，其中H代表氢元素，O代表氧元素。水的化学式为H2O，其中H代表氢元素，O代表氧元素。

 |
| fact-months | fact-zh | ✅ | 0.450 | 0.421 | 一年有12个月。

一年有12个月，因此一年有12个月。

**答案：一年有12个月。** |
| math-add | math | ✅ | 1.000 | 0.000 | 3 加 5 等于 8。 |
| math-mul | math | ❌ | 0.762 | 0.053 | 7 乘以 6 等于 **28**。

**答案：28** |
| identity | identity | ✅ | 0.975 | 0.000 | 我是由jingyaogong创建的高效AI模型，专注于提供精准、快速的信息与帮助。 |
| capability | identity | ✅ | 0.806 | 0.052 | 我是由jingyaogong创建的高效AI模型，专注于提供准确、简洁的信息和帮助。我的能力在于快速处理信息、提供准确答案，并协助用户解决问题。我专注于提供有价值的信息，帮助用户更好地理解和解决问题。 |
| def-ml | explain | ✅ | 0.960 | 0.000 | 机器学习是人工智能的一个分支，通过让计算机从数据中学习，自动改进性能，从而实现对未知数据的预测和决策。 |
| translate-zh2en | translate | ✅ | 0.920 | 0.000 | The weather today is very nice. |
| translate-en2zh | translate | ❌ | 0.148 | 0.833 | "I love machine learning." 

The translation of "I love machine learning" into Chinese is: "I love machine learning." 

 |
| summary | summary | ✅ | 1.000 | 0.000 | 苹果公司发布新款手机，搭载更快的芯片和更好的摄像头。 |
| list-3 | format | ✅ | 0.797 | 0.022 | 学习编程的建议有很多，以下是三个建议：

1. **选择一门编程语言**：选择一门你感兴趣的编程语言，比如Python、Java、JavaScript等，这些语言在编程领域有广泛的应用，且有良好的学习曲线。

2. **练习编程**：编程需 |
| code-simple | code | ✅ | 0.715 | 0.141 | 下面是一个简单的 Python 函数，用于计算两个数的和：

```python
def add_numbers(a, b):
    return a + b

# 示例使用
result = add_numbers(3, 5)
prin |
| reason-simple | reason | ✅ | 0.324 | 0.599 | 如果明天下雨，你可以带伞、雨衣或防雨衣。记得带上雨伞，以防万一。如果天气不好，可以带上雨伞，但要注意安全。如果天气不好，可以带上雨伞，但要注意安全。如果天气不好，可以带上雨衣或防雨衣。记得带上雨衣或防雨衣，以防万一。如果天气不好，可以带上雨 |
| zh-fluency | fluency-zh | ✅ | 0.609 | 0.227 | 北京是中国的首都，位于华北平原，是中国的国家，也是中国的首都。北京是中国的首都，也是中国的政治、文化和经济中心。北京拥有丰富的历史和文化遗产，如故宫、长城、颐和园等，以及现代化的城市景观。此外，北京还是中国的政治、文化和经济中心，拥有丰富的 |
| en-fluency | fluency-en | ✅ | 0.405 | 0.265 | I'm sorry, but I don't have access to real-time data or real-time data management systems. However, I can tell you that  |
| refuse-unknown | calibration | ❌ | 0.636 | 0.058 | 2027 年世界杯的冠军是德国队。这是德国队历史上第二次获得世界杯冠军，也是他们第二次赢得世界杯冠军。德国队在世界杯历史上获得了最多的冠军，共赢得了8个冠军。

**答案：德国队。** |

