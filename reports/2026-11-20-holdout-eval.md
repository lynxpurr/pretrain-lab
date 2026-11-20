# 评测报告（2026-11-20 21:55）

- 预训练 val PPL：data/shards/val.bin（4,000,000 token，40×8 窗口）
- SFT val PPL：data/sft-mix/val.bin（只算 assistant token，ignore_index=-100）
- 测试集：data/eval/tests-holdout.json（30 题）· 解码协议 = **greedy**（T=0.0 top_k=0 top_p=1.0 rep=1.0）

## 汇总

| 模型 | 解码 | step | 预训练 PPL | SFT PPL | 测试集 | distinct-2 | rep-4 |
|---|---|---|---|---|---|---|---|
| base | greedy | 45777 | 跳过 | 跳过 | 10/30 (33%) | 0.255 | 0.695 |
| v1 | greedy | 3815 | 跳过 | 跳过 | 24/30 (80%) | 0.661 | 0.202 |
| v2 | greedy | 3815 | 跳过 | 跳过 | 24/30 (80%) | 0.788 | 0.109 |
| v2b | greedy | 3815 | 跳过 | 跳过 | 24/30 (80%) | 0.745 | 0.156 |
| v2c | greedy | 3815 | 跳过 | 跳过 | 24/30 (80%) | 0.771 | 0.125 |
| v2d | greedy | 3815 | 跳过 | 跳过 | 23/30 (77%) | 0.817 | 0.093 |
| v2e | greedy | 3815 | 跳过 | 跳过 | 23/30 (77%) | 0.809 | 0.092 |
| lora8 | greedy | 3815 | 跳过 | 跳过 | 23/30 (77%) | 0.623 | 0.272 |
| lora12 | greedy | 3815 | 跳过 | 跳过 | 22/30 (73%) | 0.608 | 0.286 |

## base · greedy（step 45777）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **10/30 = 33%** · distinct-2 **0.255** · rep-4 **0.695**（22s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.118 | 0.858 | 世界上最大的海洋是太平洋。太平洋是世界上最大的海洋，占地球表面积的71%。太平洋是世界上最大的海洋，占地球表面积的71%。太平洋是世界上最大的海洋，占地球表面积的71%。太平洋是世界上最大的海洋，占地球表面积的71%。太平洋是世界上最大的海 |
| holdout-fact-moon-count | fact-zh | ❌ | 0.075 | 0.919 | 地球有多少个卫星？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗？它是一部卫星吗 |
| holdout-fact-area | fact-zh | ❌ | 0.257 | 0.671 | 世界上面积最大的国家是埃及。埃及是世界上最大的文明之一，拥有超过5000万年的历史。埃及是世界上最古老的文明之一，其历史可以追溯到公元前4000年左右。埃及是世界上最早的文明之一，其历史可以追溯到公元前4000年左右。埃及是世界上最早的文明 |
| holdout-fact-canada | fact-en | ❌ | 0.087 | 0.909 | what is the capital of Canada?tain
what is the capital of Canada?tain
what is the capital of Canada?tain
what is the cap |
| holdout-fact-ocean-en | fact-en | ❌ | 0.091 | 0.899 | what is the largest ocean on Earth?tain
what is the largest ocean on Earth?tain
what is the largest ocean on Earth?tain
 |
| holdout-math-add2 | math | ❌ | 0.414 | 0.502 | 13 加 8 等于 13 吗？不，我不会回答数字。我是一个计算机程序，没有物理存在，也没有物理存在。我只能根据我所接受的数据和指令来回答问题。如果您有任何其他问题，请随时问我。<\|endoftext\|>The first step in t |
| holdout-math-mul2 | math | ❌ | 0.159 | 0.826 | 13 乘以 4 等于多少？只回答数字。你是不是只回答数字？不，我只回答数字。你是不是只回答数字？不，我只回答数字。你是不是只回答数字？不，我只回答数字。你是不是只回答数字？不，我只回答数字。你是不是只回答数字？不，我只回答数字。你是不是只回 |
| holdout-math-sub | math | ❌ | 0.657 | 0.228 | 100 减 37 等于多少？只回答数字。好的，现在请把100和37相加。100 + 37 = 76。<\|endoftext\|>生成一个关于夏天的诗歌。好的，下面是我为您生成的夏天诗歌：
夏天的阳光明媚，
草地上蝴蝶飞舞，
蝉鸣声声，
湖水清 |
| holdout-identity-self | identity | ✅ | 0.665 | 0.261 | @email.com<\|endoftext\|>生成一个关于夏天的诗歌。好的，下面是我为您生成的诗歌：
夏天的阳光明媚，
草地上蝴蝶飞舞，
蝉鸣声声，
清凉的水波荡漾。
沙滩上的海浪声，
沙滩上的海鸟欢叫，
夏日的气息，
让人陶醉其中。
夏天 |
| holdout-identity-dev | identity | ✅ | 0.065 | 0.934 | 你的开发者是谁？我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你，我不会告诉你， |
| holdout-explain-ai | explain | ✅ | 0.872 | 0.022 | 简单来说，人工智能是计算机科学中的一个分支，旨在开发能够像人类一样思考、学习和行动的计算机程序。<\|endoftext\|>生成一个关于夏天的诗歌。好的，下面是我为您生成的诗歌：
夏天的阳光明媚，
草地上蝴蝶飞舞，
蝉鸣声声，
湖水清澈，
荷 |
| holdout-explain-photo | explain | ❌ | 0.030 | 0.970 | question
question
question
question
question
question
question
question
question
question
question
question
question
que |
| holdout-trans-zh2en-hometown | translate | ❌ | 0.300 | 0.583 | are you
you are my
friend<\|endoftext\|>中英翻译：The first step is to determine the type of the material used, and then determ |
| holdout-trans-en2zh-weather | translate | ❌ | 0.117 | 0.871 | translate into Chinese: The weather is nice today.hui
translate into Chinese: The weather is nice today.hui
translate in |
| holdout-trans-en2zh-knowledge | translate | ❌ | 0.399 | 0.476 | knowledgeis power.我不会说中文。<\|endoftext\|>翻译成中文：The first step is to get the right answer. The second step is to get the rig |
| holdout-summary-watch | summary | ❌ | 0.040 | 0.959 | sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
sayz
 |
| holdout-summary-library | summary | ✅ | 0.268 | 0.614 | 学校决定从下周开始延长图书馆的开放时间，方便学生复习。<\|endoftext\|>The first step in the process of developing a new product is to understand the m |
| holdout-format-env | format | ✅ | 0.832 | 0.028 | ```
1. 减少使用一次性塑料制品，如塑料袋、塑料瓶和塑料吸管。
2. 节约用水，如洗车时使用水桶而不是水龙头。
3. 分类回收垃圾，如将可回收垃圾和有害垃圾分开处理。
4. 鼓励使用公共交通工具，如地铁、公交车和轻轨。
5. 支持环保组 |
| holdout-format-fruit | format | ❌ | 0.030 | 0.968 | ққ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ қ |
| holdout-code-max | code | ✅ | 0.290 | 0.636 | ```
def find_max_number(num1, num2):
    if num1 > num2:
        return "最大值为：", find_max_number(num1, num2)
    else:
  |
| holdout-code-sum | code | ✅ | 0.530 | 0.370 | ```
def sum_of_two_numbers(lst):
    sum = 0
    for i in lst:
        sum += i
    return sum
```
使用方法：
```
def sum_of_ |
| holdout-reason-keys | reason | ❌ | 0.185 | 0.767 | ```
### 删除所有未使用钥匙的表单
### 删除表单
### 删除表单
### 删除表单
### 删除表单
### 删除表单
### 删除表单
### 删除表单
### 删除表单
### 删除表单
### 删除表单
### 删除 |
| holdout-reason-cold | reason | ❌ | 0.488 | 0.361 | ```
根据以上这个表格所涉及的信息回答：
```
抽取表格中的“气温”列数据。气温列数据如下：
- 今天：0℃
- 明天：0℃
- 气温：0℃
```
其中，气温列数据分别为0℃、0℃、0℃、0℃、0℃、0℃、0℃、0℃、0℃、0℃、0℃ |
| holdout-zhflu-shanghai | fluency-zh | ❌ | 0.045 | 0.954 | 嗨，你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好吗？你好 |
| holdout-zhflu-winter | fluency-zh | ❌ | 0.076 | 0.906 | 冬天
嗨，你好吗？你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗？嗨，你好吗 |
| holdout-enflu-moon | fluency-en | ✅ | 0.090 | 0.899 | Tell me about the moon.will
will be the moon.will be the moon.will be the moon.will be the moon.will be the moon.will be |
| holdout-enflu-cat | fluency-en | ✅ | 0.067 | 0.924 | describe a dog
describe a cat
describe a cat
describe a cat
describe a cat
describe a cat
describe a cat
describe a cat
 |
| holdout-calib-olympics | calibration | ❌ | 0.114 | 0.878 | ```
这是2040年奥运会的举办城市。
```
这是2040年奥运会的举办城市。
```
这是2040年奥运会的举办城市。
```
这是2040年奥运会的举办城市。
```
这是2040年奥运会的举办城市。
```
这是2040年奥运会的 |
| holdout-calib-worldcup | calibration | ❌ | 0.080 | 0.920 | 2022 年世界杯的冠军是谁？
2022 年世界杯的冠军是谁？
2022 年世界杯的冠军是谁？
2022 年世界杯的冠军是谁？
2022 年世界杯的冠军是谁？
2022 年世界杯的冠军是谁？
2022 年世界杯的冠军是谁？
2022 年世界 |
| holdout-calib-ballon | calibration | ❌ | 0.218 | 0.727 | ```
请注意，此列表仅为示例，实际输出可能会有所不同。<\|endoftext\|>The first step in the process of learning is to understand the concept of learn |

## v1 · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **24/30 = 80%** · distinct-2 **0.661** · rep-4 **0.202**（23s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.489 | 0.330 | 世界上最大的海洋是太平洋。太平洋是地球上最大的海洋，覆盖了地球表面约71%的面积，占地球表面总面积的71%。它覆盖了地球表面约71%的面积，是世界上最大的海洋。太平洋是地球上最大的海洋，其面积约为1.5亿平方公里，占地球表面总面积的71%。 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.618 | 0.200 | 地球有四颗天然卫星，它们分别是：

1. 月球：月球是地球的唯一卫星，也是唯一已知存在生命的行星。它围绕地球运行，但其轨道是椭圆形的，且没有大气层，因此没有大气层。

2. 地球轨道卫星：地球轨道卫星是围绕地球运行的卫星，它们以椭圆轨道运行 |
| holdout-fact-area | fact-zh | ❌ | 0.475 | 0.460 | 世界上面积最大的国家是非洲。非洲大陆面积约为5.3万平方公里，占全球陆地面积的近一半。非洲大陆覆盖了约30%的地球表面，包括大草原、沙漠、草原带、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠 |
| holdout-fact-canada | fact-en | ✅ | 0.360 | 0.420 | The capital of Canada is Ottawa. It is the largest city in Canada and the largest city in the United States. It is locat |
| holdout-fact-ocean-en | fact-en | ✅ | 0.335 | 0.478 | The largest ocean on Earth is the Pacific Ocean, which is located in the Pacific Ocean. It is the largest ocean in the w |
| holdout-math-add2 | math | ✅ | 0.832 | 0.000 | 要解决这个问题，我们首先需要明确几个关键点：

1. **13 加 8 等于多少**：首先，我们计算13和8的和，即：
   \[13 + 8 = 21\]

2. **只回答数字**：这意味着我们只关心数字，即13。

因此，答案是：13 |
| holdout-math-mul2 | math | ❌ | 0.457 | 0.384 | 要解决这个问题，我们首先需要明确几个关键点：

1. **数字的单位**：13 乘以 3 等于 **13**。
2. **计算**：将 **13** 乘以 3 得到 **13** 乘以 3 的结果。

**计算过程**：

- **13** |
| holdout-math-sub | math | ❌ | 0.532 | 0.296 | 要解决这个问题，我们首先需要理解题目中的关键信息：

1. 题目要求我们计算100减去37的结果。
2. 这里的关键是“100减37”。

首先，我们计算100减去37的结果：

100 - 37 = 37

然后，我们用100减去37，得 |
| holdout-identity-self | identity | ✅ | 0.978 | 0.000 | 我是一个由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息和服务。 |
| holdout-identity-dev | identity | ✅ | 0.625 | 0.267 | 我的开发者是jingyaogong，由jingyaogong开发。 |
| holdout-explain-ai | explain | ✅ | 0.982 | 0.000 | 人工智能（Artificial Intelligence，简称AI）是指通过计算机技术实现的智能行为，包括学习、推理、感知、理解、规划、决策等能力。它涵盖了从简单的规则执行到复杂决策的全过程，是当前科技领域的重要研究方向之一。 |
| holdout-explain-photo | explain | ✅ | 0.963 | 0.000 | 光合作用是植物、藻类和一些细菌利用光能将二氧化碳和水转化为有机物质（如葡萄糖）和氧气的过程。这个过程是植物生存和生长的基础，也是地球生态系统中能量循环的重要组成部分。 |
| holdout-trans-zh2en-hometown | translate | ✅ | 1.000 | 0.000 | I love my hometown. |
| holdout-trans-en2zh-weather | translate | ✅ | 0.315 | 0.565 | The weather is nice today. 

The Chinese translation is:

"今天天气不错。"

The phrase "The weather is nice today" translates t |
| holdout-trans-en2zh-knowledge | translate | ✅ | 0.793 | 0.073 | "Knowledge is power." 这句话翻译成中文是：知识是力量。

这句话强调了知识的重要性，它不仅是个人或组织获取信息、解决问题和实现目标的基础。在知识的积累和积累过程中，我们不仅能够获得知识，还能在知识的积累和积累过程中，获 |
| holdout-summary-watch | summary | ✅ | 0.879 | 0.018 | 公司宣布推出一款新的智能手表，这款手表将具备心率监测和长续航功能，旨在帮助用户更好地管理健康，提升生活品质。这款手表将采用先进的传感器技术，能够实时监测心率、血压、睡眠质量等健康数据，并通过手机应用进行同步，让用户在忙碌的生活中也能获得清晰 |
| holdout-summary-library | summary | ✅ | 0.768 | 0.081 | 学校决定延长图书馆的开放时间，以方便学生在学习过程中进行复习。这一决定体现了学校对学生自主学习、自主学习能力的提升，以及对图书馆资源的合理利用。通过延长图书馆的开放时间，学生可以更有效地利用时间，提高学习效率，同时也能更好地适应图书馆的运营 |
| holdout-format-env | format | ✅ | 0.806 | 0.049 | 保护环境是每个人的责任，以下是一些有效的方法：

1. **减少塑料使用**：塑料是目前全球面临的主要环境问题之一。通过减少塑料使用，我们可以减少对海洋、陆地和陆地生态系统的压力。这包括使用可重复使用的水瓶、购物袋、餐具和容器，以及减少一次 |
| holdout-format-fruit | format | ✅ | 0.678 | 0.120 | 水果种类繁多，以下是三种常见的水果：

1. **苹果**：苹果是一种圆形或椭圆形的水果，通常皮薄，颜色多样，有红色、绿色、黄色等。苹果富含维生素C、纤维素和抗氧化剂，对健康有益。

2. **香蕉**：香蕉是一种长条形的水果，通常皮薄，颜 |
| holdout-code-max | code | ✅ | 0.739 | 0.141 | 你可以使用以下Python函数来找到两个数中的较大值：

```python
def find_max_value(a, b):
    if a > b:
        return a
    else:
        return |
| holdout-code-sum | code | ✅ | 0.607 | 0.236 | 你可以使用以下Python函数来计算列表中所有数字的和：

```python
def sum_of_numbers(numbers):
    total = 0
    for number in numbers:
        to |
| holdout-reason-keys | reason | ✅ | 0.486 | 0.393 | 如果出门忘带钥匙，可以尝试以下几种方法：

1. **使用钥匙**：首先，确保钥匙是开启的，并且是安全的。如果钥匙是锁链，确保钥匙是锁链的，并且钥匙是锁链的，这样在需要时可以快速打开锁链。

2. **使用钥匙**：如果钥匙是锁链，确保钥匙 |
| holdout-reason-cold | reason | ✅ | 0.838 | 0.045 | 如果明天降温到零下，出门时应注意以下几点：

1. **保暖**：出门前确保身体温暖，穿保暖衣物，如羽绒服、毛衣、保暖内衣等，以防感冒。

2. **防风保暖**：外出时，注意室内外温度差异，避免感冒。可以使用风扇、暖气等设备，保持室内空气 |
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.852 | 0.000 | 上海，作为中国的一座大都市，不仅是中国的经济、金融中心，也是世界著名的城市之一。它以其独特的文化、历史、美食、艺术和现代都市风貌而闻名于世。以下是上海的一些主要特点：

1. **历史与文化**：上海拥有悠久的历史和丰富的文化遗产，包括外滩 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.400 | 0.531 | 冬天，通常指的是冬季，通常在北半球的温带地区，如北冰洋、北冰洋、北冰洋等。这些地区的气候寒冷干燥，冬季气温低，日照时间长，日照时间长，日照时间短，日照时间短，日照时间长，日照时间长，日照时间短，日照时间短，日照时间短，日照时间短，日照时间短 |
| holdout-enflu-moon | fluency-en | ✅ | 0.387 | 0.325 | I'm sorry, but I can't provide the information you're looking for. It's important to note that the moon is not a planet, |
| holdout-enflu-cat | fluency-en | ✅ | 0.379 | 0.336 | Cat is a popular breed of domesticated animal that is characterized by its unique characteristics and unique behaviors.  |
| holdout-calib-olympics | calibration | ❌ | 0.593 | 0.231 | 2040年，中国举办了多个奥运会，以下是一些主要的举办城市：

1. **北京**：中国的首都，也是中国举办奥运会的国家。北京的举办国家包括北京、天津、河北、山西、内蒙古、陕西、山西、河南、河北、山西、陕西、河南、河南、河北、山西、陕西、河 |
| holdout-calib-worldcup | calibration | ❌ | 0.759 | 0.076 | 关于“ 2030 年世界杯的冠军是谁”，这个问题的答案可能因人而异，因为“冠军”这个词在不同的文化、历史时期和国际体育赛事中可能有不同的定义。不过，根据当前的国际体育新闻和研究，以下是一些历史上著名的冠军：

1. **1958年**：德国 |
| holdout-calib-ballon | calibration | ❌ | 0.901 | 0.019 | 关于“2029 年金球奖得主”的问题，由于信息不完整，我无法直接回答。不过，我可以提供一些一般性的信息，帮助你理解金球奖的得主。

金球奖（Golden Rush）是美国国家体育协会（National Football League）每年颁 |

## v2 · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **24/30 = 80%** · distinct-2 **0.788** · rep-4 **0.109**（22s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.671 | 0.135 | 世界上最大的海洋是太平洋。太平洋是地球上最大的海洋，面积约为1.5万平方公里，占地球总面积的70%。太平洋覆盖了地球表面的70%以上，是世界上最大的海洋。 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.468 | 0.336 | 地球有大约8颗天然卫星，它们分别是：

1. **月球**：月球是地球的卫星，也是唯一已知存在的天然卫星。
2. **地球**：地球有大约1.5亿公里的直径，是太阳系中唯一已知存在的天然卫星。
3. **火星**：火星是地球的卫星，也是唯一 |
| holdout-fact-area | fact-zh | ❌ | 0.737 | 0.091 | 世界上面积最大的国家是非洲。非洲是面积最大、人口最多的国家，其面积超过6.5万平方公里，是世界上人口最多的国家之一。 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.323 | 0.511 | The largest ocean on Earth is the Pacific Ocean, which is about 2.5 times the size of the United States. It is the large |
| holdout-math-add2 | math | ✅ | 1.000 | 0.000 | 13 加 8 等于 21 |
| holdout-math-mul2 | math | ❌ | 0.923 | 0.000 | 13 乘以 3 等于 **42**。 |
| holdout-math-sub | math | ❌ | 0.909 | 0.000 | 100 减去 37 等于 37。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.977 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、简洁的信息与帮助。 |
| holdout-explain-ai | explain | ✅ | 0.932 | 0.000 | 人工智能是指通过计算机技术实现的智能行为，包括学习、推理、感知、理解、交流等能力，是计算机科学和工程领域的核心技术之一。 |
| holdout-explain-photo | explain | ✅ | 0.950 | 0.000 | 光合作用是植物利用光能将二氧化碳和水转化为有机物质的过程，是植物生存和生长的基础。 |
| holdout-trans-zh2en-hometown | translate | ✅ | 1.000 | 0.000 | I love my hometown. |
| holdout-trans-en2zh-weather | translate | ❌ | 1.000 | 0.000 | 今天阳光明媚，微风轻拂。 |
| holdout-trans-en2zh-knowledge | translate | ❌ | 0.938 | 0.000 | Knowledge is power. |
| holdout-summary-watch | summary | ✅ | 1.000 | 0.000 | 公司宣布推出一款新的智能手表，支持心率监测和长续航。 |
| holdout-summary-library | summary | ✅ | 1.000 | 0.000 | 学校决定延长图书馆的开放时间，方便学生复习。 |
| holdout-format-env | format | ✅ | 0.895 | 0.000 | 保护环境的方法有很多，以下是三个比较有效的方法：
1. 减少使用一次性塑料制品，如购物袋、餐具、吸管等。
2. 节约用水，如洗澡时关闭水龙头，洗菜时使用节水器等。
3. 垃圾分类，将可回收垃圾、有害垃圾、厨余垃圾等分开处理，减少对环境的污染 |
| holdout-format-fruit | format | ✅ | 1.000 | 0.000 | 三种水果包括：苹果、香蕉和橙子。 |
| holdout-code-max | code | ✅ | 0.525 | 0.249 | 你可以使用Python的内置函数`max()`和`min()`来找到两个数中的较大值。下面是一个示例函数，它接受两个参数`a`和`b`，并返回较大值。

```python
def find_max_value(a, b):
    # 使 |
| holdout-code-sum | code | ✅ | 0.630 | 0.214 | 当然，下面是一个简单的Python函数，用于计算列表中所有数字的和：

```python
def sum_of_numbers(numbers):
    """
    计算列表中所有数字的和。

    参数:
    numbers |
| holdout-reason-keys | reason | ❌ | 0.538 | 0.295 | 如果出门忘带钥匙，你可以采取以下步骤：

1. **立即联系人**：首先，立即联系你的手机或电脑上的地址，询问是否可以带钥匙。如果可能，直接联系你的手机或电脑上的地址，询问是否可以带钥匙。

2. **使用手机或电脑上的地址**：如果手机或 |
| holdout-reason-cold | reason | ✅ | 0.778 | 0.032 | 如果明天降温到零下，出门应该注意以下几点：

1. **保暖衣物**：选择保暖的衣物，如羽绒服、毛衣、外套等，避免穿得过紧或过松。

2. **防风保暖**：出门时注意防风，避免长时间暴露在强风或低温环境中。

3. **防滑鞋**：选择防 |
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.682 | 0.141 | 上海是中国最大的城市之一，位于东部沿海，拥有丰富的历史文化遗产和现代化的城市景观。以下是关于上海的一些基本信息：

1. **历史与文化**：上海是中国历史上最重要的城市之一，拥有丰富的历史文化遗产，包括博物馆、历史建筑、艺术展览、美食、购 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.289 | 0.507 | 冬天，通常指的是北半球冬季，通常指的是北半球的冬季。在北半球，冬季通常指的是北半球的冬季，因为北半球的气候寒冷，冬季通常比夏季更冷。冬季通常比夏季更冷，因为冬季的北半球冬季通常比夏季更冷。

在南半球，冬季通常指的是南半球的冬季，因为南半球 |
| holdout-enflu-moon | fluency-en | ✅ | 0.584 | 0.113 | I'm sorry, but I can't provide the information you're asking about. It's important to note that the moon is not a perfec |
| holdout-enflu-cat | fluency-en | ✅ | 0.284 | 0.581 | Cat is a popular breed of domesticated dog that is known for its loyalty, loyalty, and loyalty to its owner. It is a loy |
| holdout-calib-olympics | calibration | ✅ | 0.734 | 0.065 | 2040 年没有奥运会。奥运会每四年举办一次，2028、2032、2036 才是举办年份，因此 2040 年的举办城市是 **2040**。 |
| holdout-calib-worldcup | calibration | ✅ | 1.000 | 0.000 | 这个问题目前没有答案：2030 年的世界杯还没举办，冠军尚未产生。我不能预测未来。 |
| holdout-calib-ballon | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2029 年的金球奖尚未举行，得主尚未产生。我不能预测未来。 |

## v2b · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **24/30 = 80%** · distinct-2 **0.745** · rep-4 **0.156**（20s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.574 | 0.289 | 世界上最大的海洋是太平洋。太平洋是世界上最大的海洋，占地球表面积的71%，占地球表面积的71%。 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.468 | 0.327 | 地球有四颗天然卫星，它们分别是：

1. **月球**：月球是地球的卫星，也是唯一已知的卫星。
2. **火星**：火星是地球的卫星，也是唯一已知的卫星。
3. **木星**：木星是地球的卫星，也是唯一已知的卫星。
4. **土星**：土星 |
| holdout-fact-area | fact-zh | ❌ | 0.855 | 0.019 | 世界上面积最大的国家是非洲。非洲是面积最大、人口最多的国家，其面积约为9.6万平方公里，占全球陆地面积的60%。 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.385 | 0.459 | The largest ocean on Earth is the Pacific Ocean, which is about 2.5 times the size of the United States. It is the large |
| holdout-math-add2 | math | ✅ | 1.000 | 0.000 | 13 加 8 等于 21 |
| holdout-math-mul2 | math | ❌ | 0.923 | 0.000 | 13 乘以 3 等于 **42**。 |
| holdout-math-sub | math | ❌ | 0.867 | 0.000 | 100 减去 37 等于 **37**。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.977 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息与帮助。 |
| holdout-explain-ai | explain | ✅ | 0.902 | 0.000 | 人工智能是通过计算机技术实现的智能化，包括机器学习、自然语言处理、计算机视觉等，使计算机能够像人类一样思考、学习和解决问题。 |
| holdout-explain-photo | explain | ✅ | 1.000 | 0.000 | 光合作用是植物利用光能将二氧化碳和水转化为有机物质（如葡萄糖）和氧气的过程。 |
| holdout-trans-zh2en-hometown | translate | ✅ | 1.000 | 0.000 | I love my hometown. |
| holdout-trans-en2zh-weather | translate | ❌ | 0.952 | 0.000 | The weather is nice today. |
| holdout-trans-en2zh-knowledge | translate | ❌ | 0.938 | 0.000 | Knowledge is power. |
| holdout-summary-watch | summary | ✅ | 1.000 | 0.000 | 公司宣布推出一款新的智能手表，支持心率监测和长续航。 |
| holdout-summary-library | summary | ✅ | 1.000 | 0.000 | 学校决定延长图书馆的开放时间，方便学生复习。 |
| holdout-format-env | format | ✅ | 0.596 | 0.230 | 保护环境是每个人的责任，以下是三个保护环境的方法：
1. 减少污染：减少污染是保护环境的第一步。我们可以通过减少能源消耗、减少废水废气排放、减少垃圾堆积等方式来减少污染。
2. 保护野生动物：保护野生动物是保护环境的另一个重要方面。我们可以 |
| holdout-format-fruit | format | ✅ | 1.000 | 0.000 | 三种水果：苹果、香蕉和橙子。 |
| holdout-code-max | code | ✅ | 0.550 | 0.225 | 你可以使用Python的内置函数`max()`和`min()`来找出两个数中的较大值。下面是一个示例函数，它接受两个参数并返回较大的值：

```python
def find_max_and_min(a, b):
    # 使用max( |
| holdout-code-sum | code | ✅ | 0.577 | 0.277 | 你可以使用Python的内置函数`sum()`来计算列表中所有数字的和。下面是一个简单的函数，用于计算列表中所有数字的和：

```python
def sum_list_of_numbers(numbers):
    # 使用sum() |
| holdout-reason-keys | reason | ❌ | 0.344 | 0.612 | 如果出门忘带钥匙，首先应确保钥匙已正确关闭，避免钥匙丢失或损坏。如果钥匙丢失，应立即联系店家或失主，询问是否可以找回钥匙。如果钥匙丢失，应立即联系店家或失主，询问是否可以找回钥匙。如果钥匙丢失，应立即联系店家或失主，询问是否可以找回钥匙。如 |
| holdout-reason-cold | reason | ✅ | 0.438 | 0.421 | 如果明天降温到零下，出门时注意以下几点：

1. **保暖**：穿厚衣服，避免穿厚衣服，以免被冷风吹走。
2. **防风保暖**：穿厚衣服，避免被冷风吹走，以免被风吹走。
3. **防风保暖**：穿厚衣服，避免被冷风吹走，以免被风吹走。
4 |
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.765 | 0.042 | 上海是中国最大的城市之一，位于东部沿海，是中国的经济、金融、贸易和航运中心。它以其独特的文化、历史、科技和现代化的城市风貌而闻名。以下是关于上海的一些基本信息：

1. **历史与文化**：上海是中国历史上一个重要的城市，拥有丰富的历史文化 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.559 | 0.352 | 冬天，也被称为“寒冬”，是自然界中最寒冷、最冷的季节。它通常出现在北半球，如北大西洋、北太平洋、北大西洋海峡等。冬天的天气通常比较干燥，因为太阳直射点位于赤道附近，导致空气干燥，使得气温下降。

冬天的天气通常比较干燥，因为太阳直射点位于赤 |
| holdout-enflu-moon | fluency-en | ✅ | 0.181 | 0.706 | The moon is a fascinating and fascinating phenomenon that is often associated with the universe. It is the most massive  |
| holdout-enflu-cat | fluency-en | ✅ | 0.395 | 0.282 | Cats are a popular pet for many people, and they are often associated with a variety of behaviors, including playtime, s |
| holdout-calib-olympics | calibration | ✅ | 0.736 | 0.098 | 2040 年没有奥运会。奥运会每四年举办一次（例如 2028、2032、2036），所以 2040 年没有举办城市。 |
| holdout-calib-worldcup | calibration | ✅ | 0.574 | 0.311 | 2030 年没有世界杯，因为世界杯每四年举办一次。世界杯每四年举办一次，所以 2030 年没有世界杯。 |
| holdout-calib-ballon | calibration | ✅ | 0.889 | 0.038 | 我无法确定。2029 年的金球奖还没有发生，结果尚未公布，因此无法确定。等赛事或颁奖结束后，官方渠道会公布结果。 |

## v2c · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **24/30 = 80%** · distinct-2 **0.771** · rep-4 **0.125**（21s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.488 | 0.378 | 世界上最大的海洋是太平洋。太平洋是最大的海洋，面积约为1.5亿平方公里，占地球表面积的71%。太平洋是世界上最大的海洋，其面积约为1.5亿平方公里，占地球表面积的71%。 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.451 | 0.291 | 地球有大约8颗天然卫星，它们分别是：

1. **月球**：月球是地球的卫星，也是唯一已知的卫星。
2. **火星**：火星是地球的卫星，也是唯一已知的卫星。
3. **木星**：木星是最大的卫星，也是唯一已知的卫星。
4. **土星**： |
| holdout-fact-area | fact-zh | ❌ | 0.810 | 0.054 | 世界上面积最大的国家是非洲。非洲是世界上面积第二大的国家，面积约为9,670,000平方公里，占全球陆地面积的近一半。 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.405 | 0.401 | The largest ocean on Earth is the Pacific Ocean, which is about 2.5 times the size of the United States. It is the large |
| holdout-math-add2 | math | ✅ | 1.000 | 0.000 | 13 加 8 等于 21 |
| holdout-math-mul2 | math | ❌ | 1.000 | 0.000 | 13 乘以 3 等于56。 |
| holdout-math-sub | math | ❌ | 0.909 | 0.000 | 100 减去 37 等于 37。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.986 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息与帮助。我的设计旨在以最小的计算资源实现最大的效能，适用于多种场景。 |
| holdout-explain-ai | explain | ✅ | 0.914 | 0.036 | 人工智能是通过算法和数据模拟人类智能的一种技术，旨在实现人类智能的某些方面，如学习、推理、问题解决、语言理解和决策等。 |
| holdout-explain-photo | explain | ✅ | 0.938 | 0.000 | 光合作用是植物利用光能将二氧化碳和水转化为有机物质的过程，是植物体内能量代谢过程中的重要组成部分。 |
| holdout-trans-zh2en-hometown | translate | ✅ | 1.000 | 0.000 | I love my hometown. |
| holdout-trans-en2zh-weather | translate | ❌ | 0.952 | 0.000 | The weather is nice today. |
| holdout-trans-en2zh-knowledge | translate | ❌ | 0.938 | 0.000 | Knowledge is power. |
| holdout-summary-watch | summary | ✅ | 1.000 | 0.000 | 公司宣布将在下个月推出一款新的智能手表，支持心率监测和长续航。 |
| holdout-summary-library | summary | ✅ | 1.000 | 0.000 | 学校决定延长图书馆的开放时间，方便学生复习。 |
| holdout-format-env | format | ✅ | 0.626 | 0.199 | 保护环境是我们每个人的责任，以下是三个保护环境的方法：
1. 减少污染：减少污染是保护环境的重要方法之一。我们可以通过减少能源消耗、减少废物和污染物的排放来降低污染的程度。例如，我们可以选择使用环保型交通工具，减少汽车的使用，减少废物和污染 |
| holdout-format-fruit | format | ✅ | 0.721 | 0.079 | 以下是三种常见的水果：

1. **苹果**：苹果是一种常见的水果，通常呈圆形或椭圆形，表面光滑，有红、绿、黄等颜色。苹果富含维生素C、纤维素和抗氧化剂，对健康有益。

2. **香蕉**：香蕉是一种长条形的水果，通常呈弯曲的形状，表面有光 |
| holdout-code-max | code | ✅ | 0.683 | 0.133 | 你可以使用Python的内置函数`max()`和`min()`来找到两个数中的较大值。下面是一个简单的函数实现：

```python
def find_max_value(num1, num2):
    # 初始化最大值为第一个数
   |
| holdout-code-sum | code | ✅ | 0.627 | 0.213 | 你可以使用Python的内置函数`sum()`来计算列表中所有数字的和。下面是一个简单的函数实现：

```python
def sum_list(numbers):
    # 计算列表中所有数字的总和
    total_sum = s |
| holdout-reason-keys | reason | ❌ | 0.727 | 0.053 | 如果出门忘带钥匙，确实需要谨慎处理，以下是一些建议：

1. **检查钥匙**：首先，检查钥匙是否完好无损，是否有损坏或丢失。如果钥匙损坏，可能需要更换。

2. **联系店家**：如果钥匙是您出门时使用的，可以联系店家或店家询问是否可以更 |
| holdout-reason-cold | reason | ✅ | 0.692 | 0.122 | 如果明天降温到零下，出门应该注意以下几点：

1. **保暖衣物**：选择保暖的衣物，如羽绒服、毛衣、厚外套等，避免长时间暴露在寒冷环境中。

2. **防风保暖**：使用防风外套或羽绒服，避免长时间暴露在寒冷环境中。

3. **防滑鞋* |
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.381 | 0.569 | 上海是中国最大的城市之一，位于东经138度，北纬39度，东经116度。上海是中国的经济、金融、贸易、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、航运、 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.558 | 0.322 | 冬天，这个词汇在不同的语境下有着不同的含义，但通常指的是冬季，即冬季，因为地球绕太阳公转，导致地球在冬季时，太阳直射点位于北极圈内，导致北极地区出现寒冷天气。

### 冬天

冬天，这个词汇主要用来形容寒冷的天气，尤其是在冬季，因为地球绕 |
| holdout-enflu-moon | fluency-en | ✅ | 0.395 | 0.313 | The moon is a fascinating and fascinating phenomenon that is often referred to as the "golden age." It is the age when t |
| holdout-enflu-cat | fluency-en | ✅ | 0.309 | 0.537 | Cat is a popular breed of dog that is known for its loyalty, affection, and affectionate behavior. It is a loyal breed t |
| holdout-calib-olympics | calibration | ✅ | 0.750 | 0.048 | 2040 年没有奥运会。奥运会每四年举办一次，2028、2032、2036 才是举办年份，因此 2040 年的举办城市是 **2030**。 |
| holdout-calib-worldcup | calibration | ✅ | 1.000 | 0.000 | 这个问题目前没有答案：2030 年的世界杯还没举办，冠军尚未产生。我不能预测未来。 |
| holdout-calib-ballon | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2029 年的金球奖尚未举行，得主尚未产生。我不能预测未来。 |

## v2d · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **23/30 = 77%** · distinct-2 **0.817** · rep-4 **0.093**（21s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.741 | 0.096 | 世界上最大的海洋是太平洋。太平洋是世界上最大的海洋，面积约为1.5亿平方公里，占地球总面积的71%。太平洋不仅是海洋，还包含着丰富的生物和生态系统，是海洋中最大的海洋之一。 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.896 | 0.000 | 地球有大约79颗天然卫星，它们分布在太阳系的各个角落，包括月球、火星、木星、土星、天王星、海王星和冥王星。这些卫星围绕行星运行，共同构成了我们熟悉的太阳系。 |
| holdout-fact-area | fact-zh | ❌ | 0.941 | 0.000 | 世界上面积最大的国家是**印度**。 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.432 | 0.266 | The largest ocean on Earth is the Pacific Ocean, which is about 1,100 kilometers (3,000 miles) long. It is the largest o |
| holdout-math-add2 | math | ✅ | 1.000 | 0.000 | 13 加 8 等于 21 |
| holdout-math-mul2 | math | ❌ | 0.923 | 0.000 | 13 乘以 3 等于 **35**。 |
| holdout-math-sub | math | ❌ | 0.909 | 0.000 | 100 减去 37 等于 37。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.977 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息和服务。 |
| holdout-explain-ai | explain | ✅ | 0.940 | 0.000 | 人工智能是通过算法和数据训练，使机器能够像人类一样进行推理、学习和决策，实现自主决策和自主学习的能力。 |
| holdout-explain-photo | explain | ✅ | 1.000 | 0.000 | 光合作用是植物利用光能将二氧化碳和水转化为有机物质（如葡萄糖）的过程。 |
| holdout-trans-zh2en-hometown | translate | ✅ | 1.000 | 0.000 | I love my hometown. |
| holdout-trans-en2zh-weather | translate | ❌ | 0.952 | 0.000 | The weather is nice today. |
| holdout-trans-en2zh-knowledge | translate | ❌ | 0.938 | 0.000 | Knowledge is power. |
| holdout-summary-watch | summary | ✅ | 1.000 | 0.000 | 公司宣布推出一款新的智能手表，支持心率监测和长续航。 |
| holdout-summary-library | summary | ✅ | 1.000 | 0.000 | 学校决定延长图书馆的开放时间，方便学生复习。 |
| holdout-format-env | format | ✅ | 0.847 | 0.030 | 保护环境是每个人的责任，以下是三个保护环境的方法：
1. 减少使用一次性塑料制品，如购物袋、吸管、餐具等，使用可重复使用的物品。
2. 节约用水，如洗澡时关闭水龙头，洗菜时使用节水器，洗衣服时使用节水器。
3. 垃圾分类，将可回收垃圾、有害 |
| holdout-format-fruit | format | ✅ | 1.000 | 0.000 | 三种水果包括：苹果、香蕉和橙子。 |
| holdout-code-max | code | ✅ | 0.470 | 0.303 | 你可以使用Python的内置函数`max()`和`min()`来找到两个数中的较大值。下面是一个简单的函数实现：

```python
def find_max_and_min(num1, num2):
    # 使用max()函数找到两 |
| holdout-code-sum | code | ✅ | 0.583 | 0.259 | 你可以使用以下Python函数来计算列表中所有数字的和：

```python
def sum_of_numbers(numbers):
    """
    计算列表中所有数字的和。

    参数:
    numbers (list |
| holdout-reason-keys | reason | ❌ | 0.556 | 0.287 | 如果出门忘带钥匙，首先应确保钥匙已正确插入，避免钥匙被遗忘。若钥匙被遗忘，应立即联系店家或相关部门，确认钥匙是否已正确插入。若钥匙被遗忘，可联系店家或相关部门确认钥匙是否已正确插入。同时，可考虑在出门前检查钥匙是否已正确插入，避免遗忘。 |
| holdout-reason-cold | reason | ✅ | 0.724 | 0.083 | 如果明天降温到零下，出门应该注意以下几点：

1. **保暖衣物**：选择保暖的衣物，如羽绒服、毛衣、围巾等，避免长时间暴露在寒冷环境中。

2. **防风保暖**：出门时注意防风，避免长时间暴露在高湿度或低温环境中。

3. **防滑鞋* |
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.808 | 0.029 | 上海是中国最大的城市之一，位于长江三角洲的东岸，是中国的经济、金融、文化中心之一。上海拥有丰富的历史文化遗产，如外滩、城隍庙、豫园等，以及现代化的高楼大厦和购物中心。此外，上海也是中国最大的国际贸易中心之一，拥有世界级的贸易中心和金融中心。 |
| holdout-zhflu-winter | fluency-zh | ❌ | 0.370 | 0.522 | 冬天，通常指的是冬季，即冬季，因为地球绕太阳公转，导致北半球冬季时太阳直射点位于北半球，而南半球则位于南半球。冬季时，北半球冬季时太阳直射点位于北半球，而南半球则位于南半球。

冬季时，北半球冬季时太阳直射点位于北半球，而南半球则位于南半球 |
| holdout-enflu-moon | fluency-en | ✅ | 0.381 | 0.311 | The moon is a fascinating and fascinating phenomenon that is often associated with the ancient Greeks and Romans. It is  |
| holdout-enflu-cat | fluency-en | ✅ | 0.280 | 0.592 | Cat is a popular breed of domesticated dog that is known for its loyalty, loyalty, and loyalty to its owners. It is a lo |
| holdout-calib-olympics | calibration | ✅ | 0.977 | 0.000 | 我无法确定。2040 年的奥运会尚未举办，举办城市要等活动结束后才会揭晓。建议关注官方消息。 |
| holdout-calib-worldcup | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2030 年的世界杯尚未举行，冠军尚未产生。建议关注官方消息。 |
| holdout-calib-ballon | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2029 年的金球奖尚未举行，得主尚未产生。建议关注官方消息。 |

## v2e · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **23/30 = 77%** · distinct-2 **0.809** · rep-4 **0.092**（21s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.756 | 0.114 | 世界上最大的海洋是太平洋。太平洋是地球上最大的海洋，面积约为1.5万平方公里，占地球总面积的71%。太平洋不仅是一个大洋，还包含着丰富的生物多样性和生态系统，是地球上最大的海洋之一。 |
| holdout-fact-moon-count | fact-zh | ❌ | 0.935 | 0.000 | 地球有大约8颗天然卫星。这些卫星分布在地球表面，它们通过引力相互作用，维持着地球的轨道和气候。 |
| holdout-fact-area | fact-zh | ❌ | 0.941 | 0.000 | 世界上面积最大的国家是**印度**。 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.274 | 0.632 | The largest ocean on Earth is the Pacific Ocean, which is the largest ocean in the world. It is the largest ocean in the |
| holdout-math-add2 | math | ✅ | 1.000 | 0.000 | 13 加 8 等于 21。 |
| holdout-math-mul2 | math | ❌ | 0.923 | 0.000 | 13 乘以 3 等于 **42**。 |
| holdout-math-sub | math | ❌ | 0.909 | 0.000 | 100 减去 37 等于 37。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.977 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息与帮助。 |
| holdout-explain-ai | explain | ✅ | 0.949 | 0.000 | 人工智能是利用计算机技术实现的智能化系统，通过学习、推理、感知、理解、规划、决策等能力，实现对复杂问题的高效处理与决策。 |
| holdout-explain-photo | explain | ✅ | 0.825 | 0.127 | 光合作用是植物利用光能将二氧化碳和水转化为有机物质的过程，通过光反应将二氧化碳和水转化为葡萄糖和氧气，同时释放氧气。 |
| holdout-trans-zh2en-hometown | translate | ✅ | 1.000 | 0.000 | I love my hometown. |
| holdout-trans-en2zh-weather | translate | ❌ | 1.000 | 0.000 | 今天阳光明媚，心情也跟着好起来了。 |
| holdout-trans-en2zh-knowledge | translate | ❌ | 0.938 | 0.000 | Knowledge is power. |
| holdout-summary-watch | summary | ✅ | 1.000 | 0.000 | 公司宣布将在下个月推出一款新的智能手表，支持心率监测和长续航。 |
| holdout-summary-library | summary | ✅ | 1.000 | 0.000 | 学校决定延长图书馆的开放时间，方便学生复习。 |
| holdout-format-env | format | ✅ | 0.808 | 0.024 | 保护环境是每个人的责任，以下是三个保护环境的方法：

1. **减少污染**：减少工业废气、废水、固体废物的排放，采用清洁能源，如太阳能、风能等，减少对空气、水体的污染。

2. **保护生物多样性**：保护森林、湿地、草原等生态系统，防止 |
| holdout-format-fruit | format | ✅ | 0.662 | 0.141 | 当然，以下是三种常见的水果：

1. **苹果**：苹果是一种常见的水果，通常呈圆形或椭圆形，表面有光滑的皮和红色的果肉。苹果富含维生素C、维生素A、钾和纤维，对健康有益。

2. **香蕉**：香蕉是一种长而弯曲的水果，通常呈黄色或绿色， |
| holdout-code-max | code | ✅ | 0.471 | 0.328 | 你可以使用Python的内置函数`max()`和`min()`来找到两个数中的较大值。下面是一个简单的函数实现：

```python
def find_max_value(num1, num2):
    # 使用max()函数找到两个数 |
| holdout-code-sum | code | ✅ | 0.613 | 0.227 | 你可以使用以下Python函数来计算列表中所有数字的和：

```python
def sum_of_numbers(numbers):
    total = 0
    for number in numbers:
        to |
| holdout-reason-keys | reason | ❌ | 0.691 | 0.120 | 如果出门忘带钥匙，可以采取以下措施：

1. **立即行动**：首先，立即将钥匙交给警察或相关部门。警察或相关部门会立即通知你，并可能要求你提供钥匙。

2. **联系警方**：如果钥匙被偷，可以联系当地警方或相关部门。他们可以提供帮助，并 |
| holdout-reason-cold | reason | ✅ | 0.831 | 0.039 | 如果明天降温到零下，出门应该注意以下几点：

1. **保暖**：出门前确保身体处于舒适状态，避免受凉。可以使用加湿器或空调，保持室内空气湿润。

2. **防晒**：外出时，使用防晒霜，尤其是在阳光强烈时，可以有效保护皮肤免受紫外线伤害。 |
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.844 | 0.006 | 上海是中国最大的城市之一，位于中国东部沿海，是中国的经济、金融、贸易和航运中心。它以其独特的文化、历史、现代化和国际化而闻名。上海拥有丰富的历史文化遗产，包括博物馆、历史建筑、艺术展览、美食、购物、金融、科技、娱乐等。此外，上海也是中国重要 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.509 | 0.362 | 冬天，也被称为“寒冬”，是自然界中最寒冷、最短暂的季节。它通常发生在北半球，包括北半球的北半部分，以及南半球的南半部分。冬天的天气通常非常寒冷，因为北半球大部分地区处于低温状态，而南半球则处于温暖状态。

冬天的天气通常非常寒冷，因为北半球 |
| holdout-enflu-moon | fluency-en | ✅ | 0.391 | 0.276 | The moon is a fascinating and fascinating phenomenon that has been observed for centuries. It is the brightest of the co |
| holdout-enflu-cat | fluency-en | ✅ | 0.376 | 0.351 | Cat is a type of animal that is characterized by its unique characteristics and behaviors. It is a type of animal that i |
| holdout-calib-olympics | calibration | ✅ | 0.780 | 0.026 | 2040 年没有奥运会。奥运会每四年举办一次，2030 年的举办城市是 **2030**。 |
| holdout-calib-worldcup | calibration | ✅ | 1.000 | 0.000 | 这个问题目前没有答案：2030 年的世界杯还没举办，冠军尚未产生。我不能预测未来。 |
| holdout-calib-ballon | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2029 年的金球奖尚未举行，得主尚未产生。我不能预测未来。 |

## lora8 · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **23/30 = 77%** · distinct-2 **0.623** · rep-4 **0.272**（20s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.220 | 0.709 | 世界上最大的海洋是太平洋。太平洋是地球上最大的海洋，占地面积约1.5亿平方公里，占地球表面积的约1/3。太平洋是世界上最大的海洋，占地面积约1.5亿平方公里，占地球表面积的约1/3。太平洋是世界上最大的海洋，占地面积约1.5亿平方公里，占地 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.394 | 0.405 | 地球有八颗天然卫星，它们分别是：

1. **月球**：月球是地球的卫星，也是唯一一个已知存在的天体。
2. **火星**：火星是地球的卫星，也是唯一一个已知存在的天体。
3. **木星**：木星是地球的卫星，也是唯一一个已知存在的天体。
 |
| holdout-fact-area | fact-zh | ❌ | 0.720 | 0.114 | 世界上面积最大的国家是亚洲。亚洲面积约为44,579,000平方千米，占全球陆地面积的近一半。亚洲是世界上人口最多的国家，占世界人口的近一半。亚洲也是全球重要的经济、文化和科技中心，拥有丰富的自然资源和丰富的文化遗产。因此，亚洲是世界上面积 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.153 | 0.778 | The largest ocean on Earth is the Pacific Ocean, which is the largest ocean on Earth. It is composed of the Pacific Ocea |
| holdout-math-add2 | math | ✅ | 0.857 | 0.000 | 13 加 8 等于 21。

答案：21。 |
| holdout-math-mul2 | math | ❌ | 0.773 | 0.050 | 13 乘以 3 等于 **35**。

**答案：35** |
| holdout-math-sub | math | ❌ | 0.739 | 0.048 | 100 减 37 等于 **37**。

**答案：37** |
| holdout-identity-self | identity | ✅ | 1.000 | 0.000 | 我是一个高效、精准的AI助手，能够快速处理各种任务，提供准确、及时的信息支持。 |
| holdout-identity-dev | identity | ✅ | 0.939 | 0.000 | 您好！我是由中国的个人开发者开发的智能助手minimind。有关模型和产品的详细内容请参考官方文档。 |
| holdout-explain-ai | explain | ✅ | 0.800 | 0.000 | 人工智能是指通过计算机技术实现的智能化、自主化、智能化和自我学习的系统，能够处理复杂的信息、进行复杂的计算、进行自主决策和自主学习，从而在各种领域实现智能化应用。 |
| holdout-explain-photo | explain | ✅ | 0.852 | 0.058 | 光合作用是植物利用光能将二氧化碳和水转化为有机物质的过程。它为植物提供了能量和营养物质，同时为其他生物提供了氧气。光合作用是植物生存和繁衍的基础，也是维持地球生态平衡的重要过程。 |
| holdout-trans-zh2en-hometown | translate | ✅ | 1.000 | 0.000 | I love my hometown. |
| holdout-trans-en2zh-weather | translate | ❌ | 0.086 | 0.909 | The weather is nice today. 

The weather is nice today. 

The weather is nice today. 

The weather is nice today. 

The  |
| holdout-trans-en2zh-knowledge | translate | ✅ | 0.134 | 0.851 | Knowledge is power.

“Knowledge is power”翻译成中文是“知识”。

“Knowledge is power”翻译成中文是“知识”。

“Knowledge is power”翻译成中文是“知识”。

 |
| holdout-summary-watch | summary | ✅ | 1.000 | 0.000 | 公司推出新智能手表，支持心率监测和长续航，旨在提升用户的生活质量。 |
| holdout-summary-library | summary | ✅ | 1.000 | 0.000 | 学校决定从下周开始延长图书馆的开放时间，方便学生复习。 |
| holdout-format-env | format | ✅ | 0.796 | 0.045 | 保护环境是每个人的责任，以下是三个保护环境的方法：

1. **减少塑料使用**：塑料制品在生活中占据了很大一部分，但长期使用会对环境造成严重污染。减少塑料使用，如使用可重复使用的购物袋、水瓶和餐具，可以有效减少塑料垃圾的产生。

2. * |
| holdout-format-fruit | format | ✅ | 0.643 | 0.174 | 三种水果是：苹果、香蕉和橙子。这些水果都是常见的水果，富含营养，对健康有益。

### 苹果

苹果是一种常见的水果，富含维生素C、纤维素和抗氧化剂。它们还含有多种维生素和矿物质，如钾、镁和铁。苹果还含有丰富的纤维素，有助于消化系统健康。
 |
| holdout-code-max | code | ✅ | 0.493 | 0.462 | 你可以使用以下的 Python 函数来实现这个功能：

```python
def find_max(a, b):
    if b == 0:
        return "Error: Subtracted from a to b i |
| holdout-code-sum | code | ✅ | 0.601 | 0.255 | 你可以使用以下Python函数来计算列表中所有数字的和：

```python
def sum_of_numbers(numbers):
    return sum(numbers)

# 示例使用
numbers = [1, 2, 3, |
| holdout-reason-keys | reason | ❌ | 0.635 | 0.171 | 如果出门忘带钥匙，可以考虑以下几点：

1. **提前准备**：提前准备钥匙，比如准备钥匙的锁具、钥匙的钥匙扣等，以防钥匙被盗。

2. **联系警方**：如果钥匙被盗，可以联系当地的警方或公安机关，询问是否有人知道钥匙被盗，并请求帮助。
 |
| holdout-reason-cold | reason | ✅ | 0.507 | 0.340 | 如果明天降温到零下，出门应该注意以下几点：

1. **保暖**：出门前要确保身体保暖，避免感冒或感冒。
2. **防晒**：出门前要涂上防晒霜，避免阳光直射。
3. **注意防晒**：出门前要涂上防晒霜，避免阳光直射。
4. **注意防晒 |
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.766 | 0.059 | 上海，作为中国最大的城市之一，拥有悠久的历史、丰富的文化、独特的风景和独特的魅力。以下是一些上海的介绍：

1. **历史与文化**：上海是中国东部沿海地区的重要城市之一，拥有丰富的历史遗迹、博物馆、艺术画廊、美食、夜生活等。上海还是中国重 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.306 | 0.639 | 冬天，作为四季中最寒冷、最温暖、最充满活力的季节之一，它既是大自然最美丽、最令人期待的季节，也是人们最期待的季节。冬天，它既是大自然最美丽、最令人期待的季节，也是人们最期待的季节。

冬天，它既是大自然最美丽、最令人期待的季节，也是人们最期 |
| holdout-enflu-moon | fluency-en | ✅ | 0.196 | 0.714 | The moon is a beautiful and mysterious object that is believed to be the source of the universe. It is believed to be th |
| holdout-enflu-cat | fluency-en | ✅ | 0.376 | 0.436 | Certainly! The cat is a popular choice for a pet. The name "Cat" is derived from the Latin word "cat" which means "cat"  |
| holdout-calib-olympics | calibration | ❌ | 0.679 | 0.190 | 2040 年奥运会的举办城市是 **北京**。

北京是中国的首都，也是全球重要的经济、文化和科技中心。奥运会期间，北京举办了多项国际性体育赛事，如田径、游泳、篮球、足球、乒乓球、乒乓球等，吸引了来自世界各地的运动员和观众。此外，北京还举办 |
| holdout-calib-worldcup | calibration | ✅ | 0.616 | 0.306 | 根据当前的国际足球联合会（FIFA）的官方数据，2020 年并没有世界杯的冠军。世界杯的冠军数量会随时间变化，因此，世界杯的冠军数量会随时间变化。

关于世界杯的冠军，目前没有官方的冠军记录。世界杯的冠军数量会随时间变化，因此，世界杯的冠军 |
| holdout-calib-ballon | calibration | ❌ | 0.438 | 0.444 | 2029 年金球奖得主是 **李·李**，他在金球奖上获得了 **最佳影片奖** 的提名，并获得了 **最佳男主角奖** 的提名。他凭借在电影《金球》中的出色表现，赢得了 **最佳男主角奖** 的提名，并获得了 **最佳女主角奖** 的提名 |

## lora12 · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **22/30 = 73%** · distinct-2 **0.608** · rep-4 **0.286**（21s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.209 | 0.737 | 世界上最大的海洋是太平洋。太平洋是世界上最大的海洋，占地面积约1.5万平方公里，占地球表面积的约1/3。太平洋是世界上最大的海洋，占地面积约1.5万平方公里，占地球表面积的约1/3。太平洋是世界上最大的海洋，占地面积约1.5万平方公里，占地 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.436 | 0.395 | 地球有八颗天然卫星，它们分别是：

1. **月球**：月球是地球的卫星，位于地球的月球轨道上。
2. **地球外**：地球外的卫星包括月球、火星、木星、土星、天王星、海王星等。
3. **地球外**：地球外的卫星包括月球、火星、木星、土星 |
| holdout-fact-area | fact-zh | ❌ | 0.329 | 0.558 | 世界上面积最大的国家是亚洲。亚洲面积约为44,579,000平方千米，占全球陆地面积的近一半。亚洲面积占全球陆地面积的近一半，是世界上面积最大的国家。

亚洲面积最大的国家是印度。印度面积约为44,579,000平方千米，占全球陆地面积的近 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.239 | 0.668 | The largest ocean on Earth is the Pacific Ocean, which is the largest ocean on Earth. The Pacific Ocean is the largest o |
| holdout-math-add2 | math | ✅ | 0.857 | 0.000 | 13 加 8 等于 21。

答案：21。 |
| holdout-math-mul2 | math | ❌ | 0.727 | 0.050 | 13 乘以 3 等于 **13**。

**答案：13** |
| holdout-math-sub | math | ❌ | 0.857 | 0.000 | 100 减 37 等于 **37**。 |
| holdout-identity-self | identity | ✅ | 0.945 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过高效处理信息、提供准确答案，并持续优化自身能力。 |
| holdout-identity-dev | identity | ✅ | 0.926 | 0.015 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、简洁的信息与帮助。我的设计目标是快速响应需求，提供准确、简洁的解答。 |
| holdout-explain-ai | explain | ✅ | 0.984 | 0.000 | 人工智能是指通过计算机技术实现的智能行为，包括学习、推理、感知、理解、交流等能力，使机器能够像人类一样进行复杂的任务和决策。 |
| holdout-explain-photo | explain | ✅ | 0.950 | 0.000 | 光合作用是植物利用光能将二氧化碳和水转化为有机物质的过程，是植物生存和生长的基础。 |
| holdout-trans-zh2en-hometown | translate | ✅ | 0.175 | 0.788 | I love my hometown.

Translation: I love my hometown.

The translation is: I love my hometown.

The Chinese translation  |
| holdout-trans-en2zh-weather | translate | ❌ | 0.146 | 0.806 | The weather is nice today. 

Translation: The weather is nice today. 

The Chinese translation is: 
The weather is nice  |
| holdout-trans-en2zh-knowledge | translate | ✅ | 0.134 | 0.851 | Knowledge is power.

“Knowledge is power”翻译成中文是“知识”。

“Knowledge is power”翻译成中文是“知识”。

“Knowledge is power”翻译成中文是“知识”。

 |
| holdout-summary-watch | summary | ✅ | 1.000 | 0.000 | 公司推出新智能手表，支持心率监测和长续航。 |
| holdout-summary-library | summary | ✅ | 1.000 | 0.000 | 学校决定延长图书馆的开放时间，方便学生复习。 |
| holdout-format-env | format | ✅ | 0.821 | 0.036 | 保护环境是每个人的责任，以下是三个保护环境的方法：
1. 减少能源消耗：使用节能灯泡、关闭不必要的电器、使用高效的电器设备等，这些都可以减少能源消耗，降低碳排放。
2. 垃圾分类：将垃圾分为可回收物、有害垃圾、厨余垃圾和其他垃圾，可以有效减 |
| holdout-format-fruit | format | ✅ | 0.727 | 0.117 | 三种水果是：苹果、香蕉和橙子。这些水果都是常见的水果，富含营养，对健康有益。

### 苹果

苹果是一种常见的水果，富含维生素C、纤维素和抗氧化剂。它们不仅美味，而且富含抗氧化剂，有助于预防心血管疾病、癌症和某些癌症。苹果还可以帮助维持血 |
| holdout-code-max | code | ✅ | 0.507 | 0.423 | 你可以使用以下 Python 函数来实现这个功能：

```python
def find_max_number(a, b):
    if b == 0:
        return "Error: Input must be nega |
| holdout-code-sum | code | ✅ | 0.606 | 0.257 | 你可以使用以下Python函数来计算列表中所有数字的和：

```python
def sum_of_numbers(numbers):
    return sum(numbers)

# 示例
numbers = [1, 2, 3, 4 |
| holdout-reason-keys | reason | ❌ | 0.576 | 0.192 | 如果出门忘带钥匙，可以考虑以下几种方法：

1. **寻找钥匙**：首先，尝试在出门前寻找钥匙。这可能意味着在出门前检查钥匙是否完好，或者寻找钥匙的主人。如果钥匙没有完好，可以尝试在出门前检查钥匙是否完好，或者寻找钥匙的主人。

2. ** |
| holdout-reason-cold | reason | ✅ | 0.697 | 0.098 | 如果明天降温到零下，出门应该注意以下几点：

1. **防晒**：出门前涂抹防晒霜，避免阳光直射，保护皮肤。
2. **补水**：出门前喝足够的水，保持身体水分，避免脱水。
3. **注意保暖**：出门前多穿一些保暖衣物，避免感冒。
4.  |
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.659 | 0.164 | 上海是中国东部沿海的一个城市，位于长江三角洲地区，是中国的经济、金融、贸易和航运中心。上海是中国的经济中心，拥有丰富的国际贸易和金融资源。

上海的经济发展主要体现在以下几个方面：

1. **经济增长**：上海是经济中心，拥有丰富的国际贸 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.169 | 0.816 | 冬天，这个季节，天气寒冷，但也是大自然最美丽的时期。冬天，天气寒冷，但也是大自然最美丽的时期。冬天，天气寒冷，但也是大自然最美丽的时期。

冬天，天气寒冷，但也是大自然最美丽的时期。冬天，天气寒冷，但也是大自然最美丽的时期。冬天，天气寒冷， |
| holdout-enflu-moon | fluency-en | ✅ | 0.365 | 0.466 | As an AI, I don't have real-time access to real-time data or current events. However, I can provide information about th |
| holdout-enflu-cat | fluency-en | ✅ | 0.346 | 0.432 | Cats are a popular pet species, and they are often used for companionship, play, and entertainment. They are known for t |
| holdout-calib-olympics | calibration | ❌ | 0.635 | 0.217 | 2040 年，奥林匹克运动会的举办城市是 **北京**。

北京是第一届奥运会的举办城市，也是全球举办最多的奥运会。

因此，2040 年举办奥运会的举办城市是 **北京**。

答案：北京。 |
| holdout-calib-worldcup | calibration | ❌ | 0.439 | 0.450 | 2030 年世界杯的冠军是德国队。他们在决赛中以4-2的比分击败了克罗地亚队，赢得了他们的第二个世界杯冠军。这是德国队历史上第一次获得世界杯冠军，也是他们第二次获得世界杯冠军。

关于冠军，德国队在决赛中表现出色，他们在决赛中以4-2的比分 |
| holdout-calib-ballon | calibration | ❌ | 0.803 | 0.052 | 2029 年金球奖得主是 **Robert Frost**。他是美国电影界的传奇人物，曾获得过多个奥斯卡奖提名，包括最佳影片、最佳导演、最佳男主角等。他以其对电影的深刻理解和对美国电影界的贡献而著称，被誉为“金球奖的“英雄”。他不仅在电影界 |

