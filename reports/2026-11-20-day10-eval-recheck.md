# 评测报告（2026-11-20 20:07）

- 预训练 val PPL：data/shards/val.bin（4,000,000 token，40×8 窗口）
- SFT val PPL：data/sft-mix/val.bin（只算 assistant token，ignore_index=-100）
- 测试集：data/eval/tests.json（18 题）· 解码协议 = **greedy**（T=0.0 top_k=0 top_p=1.0 rep=1.0）

## 汇总

| 模型 | 解码 | step | 预训练 PPL | SFT PPL | 测试集 | distinct-2 | rep-4 |
|---|---|---|---|---|---|---|---|
| base | greedy | 45777 | 15.350 | 9.818 | 6/18 (33%) | 0.232 | 0.727 |
| v2e | greedy | 3815 | 16.192 | 4.847 | 17/18 (94%) | 0.860 | 0.055 |

## base · greedy（step 45777）

- 预训练 val PPL **15.350** · SFT val PPL **9.818** · 测试集 **6/18 = 33%** · distinct-2 **0.232** · rep-4 **0.727**（17s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| fact-capital-cn | fact-zh | ✅ | 0.712 | 0.180 | 中国的首都是哪里？
中国的首都是北京。好的，现在请告诉我北京的天气情况。北京的天气情况是：今天多云转小雨，最高温度26℃，最低温度16℃，请注意带伞出门。<\|endoftext\|>生成一个关于夏天的诗歌。好的，下面是我为您生成的夏天诗歌：
 |
| fact-capital-fr | fact-en | ❌ | 0.097 | 0.899 | what is the capital of France? arsenal
what is the capital of France? arsenal
what is the capital of France? arsenal
wha |
| fact-water | fact-zh | ❌ | 0.213 | 0.733 | 水的沸点是100摄氏度。水的沸点是100摄氏度，这意味着水在100摄氏度时达到100摄氏度。水的沸点取决于温度，但通常是在100摄氏度左右。水的沸点取决于温度，但通常是在100摄氏度左右。水的沸点取决于温度，但通常是在100摄氏度左右。水的 |
| fact-months | fact-zh | ❌ | 0.128 | 0.868 | 一年有几个月？的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例
的範例 |
| math-add | math | ❌ | 0.101 | 0.898 | 4 加 5 等于多少？quirrel
4 加 5 等于多少？quirrel
4 加 5 等于多少？quirrel
4 加 5 等于多少？quirrel
4 加 5 等于多少？quirrel
4 加 5 等于多少？quirrel
4 加 5  |
| math-mul | math | ❌ | 0.152 | 0.785 | 7 乘以 6 等于 36。
```
8 乘以 6 等于 48。
```
9 乘以 6 等于 48。
```
10 乘以 6 等于 48。
```
```
```
```
```
```
```
```
```
```
```
```
``` |
| identity | identity | ✅ | 0.528 | 0.281 | 你的名字是什么？我不会回答你这个问题，因为我是一个人工智能语言模型，我的目的是回答用户的问题和提供有用的信息。如果您有任何其他问题，请随时问我。<\|endoftext\|>The first step in learning about th |
| capability | identity | ❌ | 0.020 | 0.980 | user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
user
 |
| def-ml | explain | ❌ | 0.007 | 0.993 | ---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
 |
| translate-zh2en | translate | ❌ | 0.188 | 0.745 | will be
young<\|endoftext\|>中英翻译：The first step is to determine the number of the first two digits of the number of the se |
| translate-en2zh | translate | ❌ | 0.417 | 0.561 | Translate into Japanese: こんにちは、お元気ですか？お元気ですか？お元気ですか？
お元気ですか？お元気ですか？
お元気ですか？お元気ですか？
お元気ですか？
� |
| summary | summary | ✅ | 0.258 | 0.725 | 苹果发布新款手机，搭载更快的芯片和更好的摄像头。不好意思，我之前的回答有误。我之前的回答有误。苹果发布新款手机，搭载更快的芯片和更好的摄像头。不好意思，我之前的回答有误。我之前的回答有误。苹果发布新款手机，搭载更快的芯片和更好的摄像头。不好 |
| list-3 | format | ❌ | 0.020 | 0.980 | python
python
python
python
python
python
python
python
python
python
python
python
python
python
python
python
python
p |
| code-simple | code | ✅ | 0.365 | 0.592 | ```
def add_numbers(a, b):
    return a + b
```
这个函数接受两个参数 a 和 b，并返回它们的和。
```
def add_numbers(a, b):
    return a + b
`` |
| reason-simple | reason | ❌ | 0.152 | 0.819 | ```
这将显示明天下雨的预报，包括下雨的频率和地点。
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
```
 |
| zh-fluency | fluency-zh | ✅ | 0.648 | 0.237 | 你好，我是来自中国大陆的AI语言模型，很高兴为您解答问题。北京是中国的首都，位于中国北部，是一个历史悠久、文化底蕴深厚的城市。北京是中国的首都，也是中国最重要的城市之一。北京是中国的首都，也是中国的政治、经济、文化中心。北京有着悠久的历史， |
| en-fluency | fluency-en | ✅ | 0.084 | 0.902 | Tell me about the ocean.will
will be the ocean.will be the ocean.will be the ocean.will be the ocean.will be the ocean.w |
| refuse-unknown | calibration | ❌ | 0.090 | 0.908 | 2027 年世界杯的冠军是谁？
2027 年世界杯的冠军是谁？
2027 年世界杯的冠军是谁？
2027 年世界杯的冠军是谁？
2027 年世界杯的冠军是谁？
2027 年世界杯的冠军是谁？
2027 年世界杯的冠军是谁？
2027 年世界 |

## v2e · greedy（step 3815）

- 预训练 val PPL **16.192** · SFT val PPL **4.847** · 测试集 **17/18 = 94%** · distinct-2 **0.860** · rep-4 **0.055**（18s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| fact-capital-cn | fact-zh | ✅ | 0.758 | 0.097 | 中国的首都是北京。北京是中国的首都，也是中国的政治、文化和经济中心。 |
| fact-capital-fr | fact-en | ✅ | 0.960 | 0.000 | The capital of France is Paris. |
| fact-water | fact-zh | ✅ | 1.000 | 0.000 | 水的化学式是H₂O。 |
| fact-months | fact-zh | ✅ | 1.000 | 0.000 | 一年有12个月。 |
| math-add | math | ✅ | 1.000 | 0.000 | 3 加 5 等于 8。 |
| math-mul | math | ✅ | 0.917 | 0.000 | 7 乘以 6 等于 **42**。 |
| identity | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| capability | identity | ✅ | 0.958 | 0.000 | 我是由个人开发者独立开发的minimind。关于不同模型的差异，建议您参考官方信息或亲自体验。我会继续专注于以诚实专业的态度为您提供最好的帮助。 |
| def-ml | explain | ✅ | 0.938 | 0.000 | 机器学习是通过数据训练模型，让机器自动学习规律，从而完成特定任务。 |
| translate-zh2en | translate | ✅ | 0.920 | 0.000 | The weather is very nice today. |
| translate-en2zh | translate | ✅ | 1.000 | 0.000 | 我热爱机器学习。 |
| summary | summary | ✅ | 1.000 | 0.000 | 苹果公司发布新款手机，搭载更快的芯片和更好的摄像头。 |
| list-3 | format | ✅ | 0.854 | 0.046 | 学习编程是一个既有趣又充满挑战的过程。以下是三个学习编程的建议：

1. **选择一门编程语言**：首先，你需要选择一门编程语言作为入门。Python 是一个很好的选择，因为它语法简洁，易于理解，同时在数据科学、Web 开发、自动化等领域都 |
| code-simple | code | ✅ | 0.635 | 0.196 | 在Python中，我们可以使用内置的`sum()`函数来计算两个数的和。下面是一个简单的函数，它接受两个参数并返回它们的和：

```python
def add_numbers(a, b):
    return a + b
```

这 |
| reason-simple | reason | ✅ | 0.773 | 0.095 | 如果明天下雨，你可以带伞、雨衣或者雨靴。如果天气不好，你可以带伞或者雨靴，但最好还是带伞。 |
| zh-fluency | fluency-zh | ✅ | 0.630 | 0.224 | 北京是中国的首都，位于华北平原，是中国的首都。北京是中国的首都，也是中国的政治、文化、经济、文化中心。北京拥有丰富的历史文化遗产，如故宫、长城、颐和园等，以及现代化的城市景观。此外，北京也是中国的政治、文化、科技中心，拥有丰富的历史遗迹和现 |
| en-fluency | fluency-en | ✅ | 0.429 | 0.208 | Certainly! The ocean is a vast and fascinating place. It is home to a vast array of organisms, from tiny crustaceans to  |
| refuse-unknown | calibration | ❌ | 0.758 | 0.129 | 2027 年没有世界杯。世界杯每四年举办一次，所以 2027 年没有冠军。 |

