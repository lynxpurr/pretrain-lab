# 评测报告（2026-11-20 23:06）

- 预训练 val PPL：data/shards/val.bin（4,000,000 token，40×8 窗口）
- SFT val PPL：data/sft-mix/val.bin（只算 assistant token，ignore_index=-100）
- 测试集：data/eval/tests-holdout.json（30 题）· 解码协议 = **greedy**（T=0.0 top_k=0 top_p=1.0 rep=1.0）

## 汇总

| 模型 | 解码 | step | 预训练 PPL | SFT PPL | 测试集 | distinct-2 | rep-4 |
|---|---|---|---|---|---|---|---|
| base | greedy | 45777 | 跳过 | 跳过 | 12/30 (40%) | 0.264 | 0.675 |
| v1 | greedy | 3815 | 跳过 | 跳过 | 23/30 (77%) | 0.644 | 0.208 |
| v2 | greedy | 3815 | 跳过 | 跳过 | 23/30 (77%) | 0.763 | 0.130 |
| v2b | greedy | 3815 | 跳过 | 跳过 | 22/30 (73%) | 0.728 | 0.173 |
| v2c | greedy | 3815 | 跳过 | 跳过 | 22/30 (73%) | 0.761 | 0.121 |
| v2d | greedy | 3815 | 跳过 | 跳过 | 22/30 (73%) | 0.767 | 0.146 |
| v2e | greedy | 3815 | 跳过 | 跳过 | 22/30 (73%) | 0.791 | 0.105 |
| lora8 | greedy | 3815 | 跳过 | 跳过 | 21/30 (70%) | 0.558 | 0.349 |
| lora12 | greedy | 3815 | 跳过 | 跳过 | 21/30 (70%) | 0.577 | 0.313 |

## base · greedy（step 45777）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **12/30 = 40%** · distinct-2 **0.264** · rep-4 **0.675**（22s）

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
| holdout-math-add2 | math | ❌ | 0.391 | 0.533 | 17 加 6 等于 13 吗？不，我不会回答数字。我是一个计算机程序，没有能力回答数字。我只能回答基于我的编程和训练数据的问题。如果您有任何其他问题，请随时问我。<\|endoftext\|>The first step in the proc |
| holdout-math-mul2 | math | ❌ | 0.297 | 0.514 | 13 乘以 5 等于 35。
14 乘以 5 等于 45。
15 乘以 5 等于 45。
16 乘以 5 等于 45。
17 乘以 5 等于 45。
18 乘以 5 等于 45。
19 乘以 5 等于 45。
20 乘以 5 等于 45。
 |
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
| holdout-explain-ai | explain | ✅ | 0.530 | 0.352 | 引力是一种物质之间的相互作用力，它使物体之间产生引力，使物体之间产生引力。引力是物体之间相互作用的力，是物体之间相互作用的力。引力是物体之间相互作用的力，是物体之间相互作用的力。引力是物体之间相互作用的力，是物体之间相互作用的力。<\|end |
| holdout-explain-photo | explain | ✅ | 0.415 | 0.497 | 细胞呼吸是一种细胞内外的化学反应，其中细胞通过呼吸作用将氧气和营养物质输送到细胞质中，同时将二氧化碳排出体外。细胞呼吸是细胞内外生命活动的基础，也是细胞内外生命活动的基础。细胞呼吸是细胞内外生命活动的基础，也是细胞内外生命活动的基础。细胞呼 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.118 | 0.859 | 成都
你好，我是成都，来自中国。
你好，我是四川，来自中国。
你好，我是四川，来自中国。
你好，我是四川，来自中国。
你好，我是四川，来自中国。
你好，我是四川，来自中国。
你好，我是四川，来自中国。
你好，我是四川，来自中国。
你好，我是 |
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
| holdout-calib-winter | calibration | ❌ | 0.120 | 0.865 | ```
这是2023年冬奥会的举办城市：
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
```
``` |
| holdout-calib-ballon | calibration | ❌ | 0.218 | 0.727 | ```
请注意，此列表仅为示例，实际输出可能会有所不同。<\|endoftext\|>The first step in the process of learning is to understand the concept of learn |

## v1 · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **23/30 = 77%** · distinct-2 **0.644** · rep-4 **0.208**（24s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.489 | 0.330 | 世界上最大的海洋是太平洋。太平洋是地球上最大的海洋，覆盖了地球表面约71%的面积，占地球表面总面积的71%。它覆盖了地球表面约71%的面积，是世界上最大的海洋。太平洋是地球上最大的海洋，其面积约为1.5亿平方公里，占地球表面总面积的71%。 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.618 | 0.200 | 地球有四颗天然卫星，它们分别是：

1. 月球：月球是地球的唯一卫星，也是唯一已知存在生命的行星。它围绕地球运行，但其轨道是椭圆形的，且没有大气层，因此没有大气层。

2. 地球轨道卫星：地球轨道卫星是围绕地球运行的卫星，它们以椭圆轨道运行 |
| holdout-fact-area | fact-zh | ❌ | 0.475 | 0.460 | 世界上面积最大的国家是非洲。非洲大陆面积约为5.3万平方公里，占全球陆地面积的近一半。非洲大陆覆盖了约30%的地球表面，包括大草原、沙漠、草原带、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠原野、沙漠 |
| holdout-fact-canada | fact-en | ✅ | 0.360 | 0.420 | The capital of Canada is Ottawa. It is the largest city in Canada and the largest city in the United States. It is locat |
| holdout-fact-ocean-en | fact-en | ✅ | 0.335 | 0.478 | The largest ocean on Earth is the Pacific Ocean, which is located in the Pacific Ocean. It is the largest ocean in the w |
| holdout-math-add2 | math | ❌ | 0.617 | 0.183 | 要解决这个问题，我们首先需要明确几个关键点：

1. **已知条件**：
   - 17 加 6 等于 18。
   - 所以，答案是 18。

2. **计算**：
   - 17 + 6 = 19。
   - 所以，答案是 19。

3 |
| holdout-math-mul2 | math | ❌ | 0.646 | 0.102 | 要解决这个问题，我们首先需要明确几个关键点：

1. **数字的单位**：数字的单位是“千”，即“千”。
2. **计算步骤**：
   - 假设“千”代表的是“千”，那么“十”代表的是“十”。
   - 所以，我们只需要将“千”乘以“十” |
| holdout-math-sub | math | ❌ | 0.532 | 0.296 | 要解决这个问题，我们首先需要理解题目中的关键信息：

1. 题目要求我们计算100减去37的结果。
2. 这里的关键是“100减37”。

首先，我们计算100减去37的结果：

100 - 37 = 37

然后，我们用100减去37，得 |
| holdout-identity-self | identity | ✅ | 0.978 | 0.000 | 我是一个由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息和服务。 |
| holdout-identity-dev | identity | ✅ | 0.625 | 0.267 | 我的开发者是jingyaogong，由jingyaogong开发。 |
| holdout-explain-ai | explain | ✅ | 0.695 | 0.158 | 引力是物质之间相互吸引的力量，是宇宙中物质运动的一种基本力。它使得物体之间相互吸引，这种吸引力是宇宙中物质运动的驱动力。 |
| holdout-explain-photo | explain | ✅ | 0.842 | 0.061 | 细胞呼吸是细胞进行呼吸作用的过程，主要发生在细胞膜中，通过一系列酶和蛋白质的协同作用，将氧气和营养物质从细胞质中释放出来，同时将二氧化碳排出体外。细胞呼吸是细胞进行能量代谢、细胞分裂和细胞死亡的重要过程。 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.793 | 0.027 | 成都，作为中国西南地区的一个大城市，以其独特的文化、美食、自然景观和现代都市生活而闻名于世。以下是成都的一些主要特点：

1. **美食**：成都以其丰富的美食而闻名，其中最著名的当属火锅、串串香、小笼包、串烧等。火锅以其麻辣、鲜香、鲜美而 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.400 | 0.531 | 冬天，通常指的是冬季，通常在北半球的温带地区，如北冰洋、北冰洋、北冰洋等。这些地区的气候寒冷干燥，冬季气温低，日照时间长，日照时间长，日照时间短，日照时间短，日照时间长，日照时间长，日照时间短，日照时间短，日照时间短，日照时间短，日照时间短 |
| holdout-enflu-moon | fluency-en | ✅ | 0.387 | 0.325 | I'm sorry, but I can't provide the information you're looking for. It's important to note that the moon is not a planet, |
| holdout-enflu-cat | fluency-en | ✅ | 0.379 | 0.336 | Cat is a popular breed of domesticated animal that is characterized by its unique characteristics and unique behaviors.  |
| holdout-calib-olympics | calibration | ❌ | 0.593 | 0.231 | 2040年，中国举办了多个奥运会，以下是一些主要的举办城市：

1. **北京**：中国的首都，也是中国举办奥运会的国家。北京的举办国家包括北京、天津、河北、山西、内蒙古、陕西、山西、河南、河北、山西、陕西、河南、河南、河北、山西、陕西、河 |
| holdout-calib-winter | calibration | ❌ | 0.756 | 0.105 | 关于“2034 年冬奥会的举办城市”，这似乎是一个不常见的术语，可能是指某个特定年份或特定年份的冬奥会。不过，我可以提供一个通用的解释，帮助你理解“2034 年冬奥会”可能指的是某个特定年份的冬奥会。

在中国的冬奥会中，通常会有多个举办城 |
| holdout-calib-ballon | calibration | ❌ | 0.901 | 0.019 | 关于“2029 年金球奖得主”的问题，由于信息不完整，我无法直接回答。不过，我可以提供一些一般性的信息，帮助你理解金球奖的得主。

金球奖（Golden Rush）是美国国家体育协会（National Football League）每年颁 |

## v2 · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **23/30 = 77%** · distinct-2 **0.763** · rep-4 **0.130**（23s）

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
| holdout-math-add2 | math | ❌ | 1.000 | 0.000 | 17 加 6 等于 19。 |
| holdout-math-mul2 | math | ❌ | 0.923 | 0.000 | 13 乘以 5 等于 **56**。 |
| holdout-math-sub | math | ❌ | 0.909 | 0.000 | 100 减去 37 等于 37。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.977 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、简洁的信息与帮助。 |
| holdout-explain-ai | explain | ✅ | 0.405 | 0.571 | 引力是物质之间相互吸引的力，是物质之间相互吸引的力，是物质之间相互吸引的力。 |
| holdout-explain-photo | explain | ✅ | 0.796 | 0.096 | 细胞呼吸是细胞进行呼吸作用的机制，通过细胞膜和细胞质的结合，将氧气和二氧化碳排出体外，同时将二氧化碳排出体外。 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.740 | 0.090 | 成都，位于中国西南部，是一个历史悠久、文化底蕴深厚的城市，以其独特的自然风光、丰富的文化遗产和独特的饮食文化而闻名。以下是成都的一些主要特点：

1. **自然风光**：成都拥有丰富的自然风光，包括山水、花鸟、动物、历史遗迹等。例如，宽窄巷 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.289 | 0.507 | 冬天，通常指的是北半球冬季，通常指的是北半球的冬季。在北半球，冬季通常指的是北半球的冬季，因为北半球的气候寒冷，冬季通常比夏季更冷。冬季通常比夏季更冷，因为冬季的北半球冬季通常比夏季更冷。

在南半球，冬季通常指的是南半球的冬季，因为南半球 |
| holdout-enflu-moon | fluency-en | ✅ | 0.584 | 0.113 | I'm sorry, but I can't provide the information you're asking about. It's important to note that the moon is not a perfec |
| holdout-enflu-cat | fluency-en | ✅ | 0.284 | 0.581 | Cat is a popular breed of domesticated dog that is known for its loyalty, loyalty, and loyalty to its owner. It is a loy |
| holdout-calib-olympics | calibration | ✅ | 0.734 | 0.065 | 2040 年没有奥运会。奥运会每四年举办一次，2028、2032、2036 才是举办年份，因此 2040 年的举办城市是 **2040**。 |
| holdout-calib-winter | calibration | ✅ | 0.881 | 0.025 | 我无法确定。2034 年冬奥会的举办城市尚未举行，因为 冬奥会 尚未举行。建议关注官方消息。 |
| holdout-calib-ballon | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2029 年的金球奖尚未举行，得主尚未产生。我不能预测未来。 |

## v2b · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **22/30 = 73%** · distinct-2 **0.728** · rep-4 **0.173**（21s）

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
| holdout-math-add2 | math | ❌ | 1.000 | 0.000 | 17 加 6 等于 19。 |
| holdout-math-mul2 | math | ❌ | 0.923 | 0.000 | 13 乘以 5 等于 **56**。 |
| holdout-math-sub | math | ❌ | 0.867 | 0.000 | 100 减去 37 等于 **37**。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.977 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息与帮助。 |
| holdout-explain-ai | explain | ✅ | 0.405 | 0.571 | 引力是物质之间相互吸引的力，是物质之间相互吸引的力，是物质之间相互吸引的力。 |
| holdout-explain-photo | explain | ✅ | 0.880 | 0.021 | 细胞呼吸是细胞进行呼吸作用的过程，通过细胞膜上的分子交换，将氧气和二氧化碳排出体外，同时释放二氧化碳。 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.815 | 0.032 | 成都是中国西南地区的一个城市，位于四川省成都市，是四川省的省会城市。成都以其独特的文化、美食、自然景观和丰富的自然资源而闻名于世。以下是成都的一些主要特点：

1. **美食**：成都的美食以麻辣、火锅、串串香、豆汁、小笼包、油条等为主，口 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.559 | 0.352 | 冬天，也被称为“寒冬”，是自然界中最寒冷、最冷的季节。它通常出现在北半球，如北大西洋、北太平洋、北大西洋海峡等。冬天的天气通常比较干燥，因为太阳直射点位于赤道附近，导致空气干燥，使得气温下降。

冬天的天气通常比较干燥，因为太阳直射点位于赤 |
| holdout-enflu-moon | fluency-en | ✅ | 0.181 | 0.706 | The moon is a fascinating and fascinating phenomenon that is often associated with the universe. It is the most massive  |
| holdout-enflu-cat | fluency-en | ✅ | 0.395 | 0.282 | Cats are a popular pet for many people, and they are often associated with a variety of behaviors, including playtime, s |
| holdout-calib-olympics | calibration | ✅ | 0.736 | 0.098 | 2040 年没有奥运会。奥运会每四年举办一次（例如 2028、2032、2036），所以 2040 年没有举办城市。 |
| holdout-calib-winter | calibration | ❌ | 0.625 | 0.217 | 2034 年并不举办冬奥会。冬奥会的举办城市是 **中国**。

**答案：**  
2034 年并不举办冬奥会。 |
| holdout-calib-ballon | calibration | ✅ | 0.889 | 0.038 | 我无法确定。2029 年的金球奖还没有发生，结果尚未公布，因此无法确定。等赛事或颁奖结束后，官方渠道会公布结果。 |

## v2c · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **22/30 = 73%** · distinct-2 **0.761** · rep-4 **0.121**（22s）

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
| holdout-math-add2 | math | ❌ | 1.000 | 0.000 | 17 加 6 等于 19。 |
| holdout-math-mul2 | math | ❌ | 1.000 | 0.000 | 13 乘以 5 等于 50。 |
| holdout-math-sub | math | ❌ | 0.909 | 0.000 | 100 减去 37 等于 37。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.986 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息与帮助。我的设计旨在以最小的计算资源实现最大的效能，适用于多种场景。 |
| holdout-explain-ai | explain | ✅ | 0.769 | 0.167 | 引力是物质之间相互吸引的力，是物质之间相互作用的结果。 |
| holdout-explain-photo | explain | ✅ | 0.784 | 0.111 | 细胞呼吸是细胞进行呼吸作用的过程，通过细胞内的酶和蛋白质等分子，将氧气和二氧化碳排出体外，同时将二氧化碳排出体外，维持细胞的正常代谢和细胞的正常功能。 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.692 | 0.108 | 成都，位于中国西南部，是一个历史悠久、文化底蕴深厚的城市，以其独特的自然风光、丰富的文化遗产和现代化的城市风貌而闻名于世。以下是成都的一些主要特点：

1. **自然风光**：成都拥有丰富的自然风光，如宽窄巷子、锦里、锦里古街、锦里古街等， |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.558 | 0.322 | 冬天，这个词汇在不同的语境下有着不同的含义，但通常指的是冬季，即冬季，因为地球绕太阳公转，导致地球在冬季时，太阳直射点位于北极圈内，导致北极地区出现寒冷天气。

### 冬天

冬天，这个词汇主要用来形容寒冷的天气，尤其是在冬季，因为地球绕 |
| holdout-enflu-moon | fluency-en | ✅ | 0.395 | 0.313 | The moon is a fascinating and fascinating phenomenon that is often referred to as the "golden age." It is the age when t |
| holdout-enflu-cat | fluency-en | ✅ | 0.309 | 0.537 | Cat is a popular breed of dog that is known for its loyalty, affection, and affectionate behavior. It is a loyal breed t |
| holdout-calib-olympics | calibration | ✅ | 0.750 | 0.048 | 2040 年没有奥运会。奥运会每四年举办一次，2028、2032、2036 才是举办年份，因此 2040 年的举办城市是 **2030**。 |
| holdout-calib-winter | calibration | ❌ | 0.685 | 0.096 | 2034 年并不举办冬奥会。冬奥会的举办城市是 **中国**。

**答案：**  
2034 年不是举办城市，而是举办城市。 |
| holdout-calib-ballon | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2029 年的金球奖尚未举行，得主尚未产生。我不能预测未来。 |

## v2d · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **22/30 = 73%** · distinct-2 **0.767** · rep-4 **0.146**（21s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.741 | 0.096 | 世界上最大的海洋是太平洋。太平洋是世界上最大的海洋，面积约为1.5亿平方公里，占地球总面积的71%。太平洋不仅是海洋，还包含着丰富的生物和生态系统，是海洋中最大的海洋之一。 |
| holdout-fact-moon-count | fact-zh | ✅ | 0.896 | 0.000 | 地球有大约79颗天然卫星，它们分布在太阳系的各个角落，包括月球、火星、木星、土星、天王星、海王星和冥王星。这些卫星围绕行星运行，共同构成了我们熟悉的太阳系。 |
| holdout-fact-area | fact-zh | ❌ | 0.941 | 0.000 | 世界上面积最大的国家是**印度**。 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.432 | 0.266 | The largest ocean on Earth is the Pacific Ocean, which is about 1,100 kilometers (3,000 miles) long. It is the largest o |
| holdout-math-add2 | math | ❌ | 1.000 | 0.000 | 17 加 6 等于 18。 |
| holdout-math-mul2 | math | ❌ | 0.923 | 0.000 | 13 乘以 5 等于 **35**。 |
| holdout-math-sub | math | ❌ | 0.909 | 0.000 | 100 减去 37 等于 37。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.977 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息和服务。 |
| holdout-explain-ai | explain | ✅ | 0.405 | 0.571 | 引力是物质之间相互吸引的力，是物质之间相互吸引的力，是物质之间相互吸引的力。 |
| holdout-explain-photo | explain | ✅ | 0.125 | 0.855 | 细胞呼吸是细胞进行呼吸作用的过程，通过细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细胞膜上的细 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.703 | 0.200 | 成都是中国西南地区的一个城市，位于四川省中部，是一个以美食、文化、购物和旅游著称的现代化城市。成都以其独特的文化氛围、丰富的自然景观和独特的饮食文化而闻名。

成都的历史可以追溯到公元前2000年，当时成都是东汉末年的首都。在汉朝时期，成都 |
| holdout-zhflu-winter | fluency-zh | ❌ | 0.370 | 0.522 | 冬天，通常指的是冬季，即冬季，因为地球绕太阳公转，导致北半球冬季时太阳直射点位于北半球，而南半球则位于南半球。冬季时，北半球冬季时太阳直射点位于北半球，而南半球则位于南半球。

冬季时，北半球冬季时太阳直射点位于北半球，而南半球则位于南半球 |
| holdout-enflu-moon | fluency-en | ✅ | 0.381 | 0.311 | The moon is a fascinating and fascinating phenomenon that is often associated with the ancient Greeks and Romans. It is  |
| holdout-enflu-cat | fluency-en | ✅ | 0.280 | 0.592 | Cat is a popular breed of domesticated dog that is known for its loyalty, loyalty, and loyalty to its owners. It is a lo |
| holdout-calib-olympics | calibration | ✅ | 0.977 | 0.000 | 我无法确定。2040 年的奥运会尚未举办，举办城市要等活动结束后才会揭晓。建议关注官方消息。 |
| holdout-calib-winter | calibration | ✅ | 1.000 | 0.000 | 我无法确定。2034 年冬奥会尚未举行，举办城市要等活动结束后才会揭晓。建议关注官方消息。 |
| holdout-calib-ballon | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2029 年的金球奖尚未举行，得主尚未产生。建议关注官方消息。 |

## v2e · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **22/30 = 73%** · distinct-2 **0.791** · rep-4 **0.105**（23s）

| id | tag | 结果 | d2 | rep4 | 输出（截断 120 字） |
|---|---|---|---|---|---|
| holdout-fact-ocean | fact-zh | ✅ | 0.756 | 0.114 | 世界上最大的海洋是太平洋。太平洋是地球上最大的海洋，面积约为1.5万平方公里，占地球总面积的71%。太平洋不仅是一个大洋，还包含着丰富的生物多样性和生态系统，是地球上最大的海洋之一。 |
| holdout-fact-moon-count | fact-zh | ❌ | 0.935 | 0.000 | 地球有大约8颗天然卫星。这些卫星分布在地球表面，它们通过引力相互作用，维持着地球的轨道和气候。 |
| holdout-fact-area | fact-zh | ❌ | 0.941 | 0.000 | 世界上面积最大的国家是**印度**。 |
| holdout-fact-canada | fact-en | ✅ | 0.962 | 0.000 | The capital of Canada is Ottawa. |
| holdout-fact-ocean-en | fact-en | ✅ | 0.274 | 0.632 | The largest ocean on Earth is the Pacific Ocean, which is the largest ocean in the world. It is the largest ocean in the |
| holdout-math-add2 | math | ❌ | 1.000 | 0.000 | 17 加 6 等于 19。 |
| holdout-math-mul2 | math | ❌ | 0.923 | 0.000 | 13 乘以 5 等于 **40**。 |
| holdout-math-sub | math | ❌ | 0.909 | 0.000 | 100 减去 37 等于 37。 |
| holdout-identity-self | identity | ✅ | 0.948 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过思考来帮您解答复杂的数学，代码和逻辑推理等理工类问题。 |
| holdout-identity-dev | identity | ✅ | 0.977 | 0.000 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、快速的信息与帮助。 |
| holdout-explain-ai | explain | ✅ | 0.769 | 0.167 | 引力是物质之间相互吸引的力，是物质之间相互作用的结果。 |
| holdout-explain-photo | explain | ✅ | 0.909 | 0.000 | 细胞呼吸是细胞进行呼吸作用，将氧气和营养物质通过细胞膜传递到细胞质中，同时释放二氧化碳，维持细胞内外环境的平衡。 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.650 | 0.234 | 成都是中国西南地区的一个城市，位于四川省中部，是一个历史悠久、文化底蕴深厚的城市。成都的历史可以追溯到2000多年前，当时成都是四川省的一个城市，被称为“成都”。

成都的历史可以追溯到2000多年前，当时成都是四川省的一个城市，被称为“成 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.509 | 0.362 | 冬天，也被称为“寒冬”，是自然界中最寒冷、最短暂的季节。它通常发生在北半球，包括北半球的北半部分，以及南半球的南半部分。冬天的天气通常非常寒冷，因为北半球大部分地区处于低温状态，而南半球则处于温暖状态。

冬天的天气通常非常寒冷，因为北半球 |
| holdout-enflu-moon | fluency-en | ✅ | 0.391 | 0.276 | The moon is a fascinating and fascinating phenomenon that has been observed for centuries. It is the brightest of the co |
| holdout-enflu-cat | fluency-en | ✅ | 0.376 | 0.351 | Cat is a type of animal that is characterized by its unique characteristics and behaviors. It is a type of animal that i |
| holdout-calib-olympics | calibration | ✅ | 0.780 | 0.026 | 2040 年没有奥运会。奥运会每四年举办一次，2030 年的举办城市是 **2030**。 |
| holdout-calib-winter | calibration | ✅ | 0.743 | 0.121 | 2034 年没有冬奥会。冬奥会每四年举办一次，所以 2034 年没有举办城市。 |
| holdout-calib-ballon | calibration | ✅ | 0.971 | 0.000 | 我无法确定。2029 年的金球奖尚未举行，得主尚未产生。我不能预测未来。 |

## lora8 · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **21/30 = 70%** · distinct-2 **0.558** · rep-4 **0.349**（21s）

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
| holdout-math-add2 | math | ❌ | 0.929 | 0.000 | 17 加 6 等于 19。

答案：19. |
| holdout-math-mul2 | math | ❌ | 0.773 | 0.050 | 13 乘以 5 等于 **35**。

**答案：35** |
| holdout-math-sub | math | ❌ | 0.739 | 0.048 | 100 减 37 等于 **37**。

**答案：37** |
| holdout-identity-self | identity | ✅ | 1.000 | 0.000 | 我是一个高效、精准的AI助手，能够快速处理各种任务，提供准确、及时的信息支持。 |
| holdout-identity-dev | identity | ✅ | 0.939 | 0.000 | 您好！我是由中国的个人开发者开发的智能助手minimind。有关模型和产品的详细内容请参考官方文档。 |
| holdout-explain-ai | explain | ✅ | 0.120 | 0.857 | 引力是物体之间相互吸引的力，是物体间相互作用的结果。引力是物体之间相互吸引的力，是物体间相互作用的结果。引力是物体之间相互吸引的力，是物体间相互作用的结果。引力是物体之间相互吸引的力，是物体间相互作用的结果。引力是物体之间相互吸引的力，是物 |
| holdout-explain-photo | explain | ✅ | 0.154 | 0.826 | 细胞呼吸是细胞在呼吸过程中将氧气和二氧化碳排出体外的过程。细胞呼吸是细胞在呼吸过程中将氧气和二氧化碳排出体外的过程。细胞呼吸是细胞在呼吸过程中将氧气和二氧化碳排出体外的过程。细胞呼吸是细胞在呼吸过程中将氧气和二氧化碳排出体外的过程。细胞呼吸 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.611 | 0.231 | 成都，作为中国西南地区的一个大城市，以其独特的文化、美食、风景和独特的自然风光而闻名。成都，作为中国西南地区的一个大城市，以其独特的文化、美食、风景和自然风光而闻名。以下是一些成都的介绍：

1. **成都美食**：成都以其丰富多样的特色美 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.306 | 0.639 | 冬天，作为四季中最寒冷、最温暖、最充满活力的季节之一，它既是大自然最美丽、最令人期待的季节，也是人们最期待的季节。冬天，它既是大自然最美丽、最令人期待的季节，也是人们最期待的季节。

冬天，它既是大自然最美丽、最令人期待的季节，也是人们最期 |
| holdout-enflu-moon | fluency-en | ✅ | 0.196 | 0.714 | The moon is a beautiful and mysterious object that is believed to be the source of the universe. It is believed to be th |
| holdout-enflu-cat | fluency-en | ✅ | 0.376 | 0.436 | Certainly! The cat is a popular choice for a pet. The name "Cat" is derived from the Latin word "cat" which means "cat"  |
| holdout-calib-olympics | calibration | ❌ | 0.679 | 0.190 | 2040 年奥运会的举办城市是 **北京**。

北京是中国的首都，也是全球重要的经济、文化和科技中心。奥运会期间，北京举办了多项国际性体育赛事，如田径、游泳、篮球、足球、乒乓球、乒乓球等，吸引了来自世界各地的运动员和观众。此外，北京还举办 |
| holdout-calib-winter | calibration | ❌ | 0.151 | 0.832 | 2022 年冬奥会的举办城市是 **北京**。

北京的举办城市是 **北京**。

北京的举办城市是 **北京**。

北京的举办城市是 **北京**。

北京的举办城市是 **北京**。

北京的举办城市是 **北京**。

北京的举办 |
| holdout-calib-ballon | calibration | ❌ | 0.438 | 0.444 | 2029 年金球奖得主是 **李·李**，他在金球奖上获得了 **最佳影片奖** 的提名，并获得了 **最佳男主角奖** 的提名。他凭借在电影《金球》中的出色表现，赢得了 **最佳男主角奖** 的提名，并获得了 **最佳女主角奖** 的提名 |

## lora12 · greedy（step 3815）

- 预训练 val PPL **跳过** · SFT val PPL **跳过** · 测试集 **21/30 = 70%** · distinct-2 **0.577** · rep-4 **0.313**（21s）

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
| holdout-math-add2 | math | ❌ | 0.857 | 0.000 | 17 加 6 等于 19。  
答案：19。 |
| holdout-math-mul2 | math | ❌ | 0.773 | 0.050 | 13 乘以 5 等于 **35**。

**答案：35** |
| holdout-math-sub | math | ❌ | 0.857 | 0.000 | 100 减 37 等于 **37**。 |
| holdout-identity-self | identity | ✅ | 0.945 | 0.000 | 我是minimind，一个由个人开发者开发的智能助手，我擅长通过高效处理信息、提供准确答案，并持续优化自身能力。 |
| holdout-identity-dev | identity | ✅ | 0.926 | 0.015 | 我是由jingyaogong创建的高效小参数AI模型，专注于提供精准、简洁的信息与帮助。我的设计目标是快速响应需求，提供准确、简洁的解答。 |
| holdout-explain-ai | explain | ✅ | 0.124 | 0.842 | 引力是物体之间相互吸引的力，是物体间相互作用的结果。引力是物体之间相互吸引的力，是物体间相互作用的结果。引力是物体间相互作用的结果，是物体间相互作用的结果。引力是物体之间相互吸引的力，是物体间相互作用的结果。引力是物体之间相互吸引的力，是物 |
| holdout-explain-photo | explain | ✅ | 0.701 | 0.084 | 细胞呼吸是细胞在细胞内进行代谢和呼吸的过程，通过细胞膜和细胞质中的细胞器，将能量从细胞质中传递到细胞质中，同时将二氧化碳排出体外。细胞呼吸是细胞内能量代谢和呼吸过程的基础，也是细胞生命活动的基础。 |
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
| holdout-zhflu-shanghai | fluency-zh | ✅ | 0.813 | 0.039 | 成都，作为中国西南地区的一个大城市，以其独特的文化、美食、自然景观和丰富的自然资源而闻名。以下是关于成都的一些基本信息：

1. **文化与历史**：成都作为中国西南地区的重要文化中心，拥有丰富的历史文化遗产，如武侯祠、锦里古街、宽窄巷子等 |
| holdout-zhflu-winter | fluency-zh | ✅ | 0.169 | 0.816 | 冬天，这个季节，天气寒冷，但也是大自然最美丽的时期。冬天，天气寒冷，但也是大自然最美丽的时期。冬天，天气寒冷，但也是大自然最美丽的时期。

冬天，天气寒冷，但也是大自然最美丽的时期。冬天，天气寒冷，但也是大自然最美丽的时期。冬天，天气寒冷， |
| holdout-enflu-moon | fluency-en | ✅ | 0.365 | 0.466 | As an AI, I don't have real-time access to real-time data or current events. However, I can provide information about th |
| holdout-enflu-cat | fluency-en | ✅ | 0.346 | 0.432 | Cats are a popular pet species, and they are often used for companionship, play, and entertainment. They are known for t |
| holdout-calib-olympics | calibration | ❌ | 0.635 | 0.217 | 2040 年，奥林匹克运动会的举办城市是 **北京**。

北京是第一届奥运会的举办城市，也是全球举办最多的奥运会。

因此，2040 年举办奥运会的举办城市是 **北京**。

答案：北京。 |
| holdout-calib-winter | calibration | ❌ | 0.422 | 0.437 | 2034 年冬奥会的举办城市是北京。冬奥会是中国举办的第六届冬季奥林匹克运动会，也是中国首次举办冬季奥林匹克运动会。冬奥会的举办地点是中国北京市，冬奥会的举办地点是中国北京市。

答案：北京。

答案：北京。

答案：北京。

答案：北京。 |
| holdout-calib-ballon | calibration | ❌ | 0.803 | 0.052 | 2029 年金球奖得主是 **Robert Frost**。他是美国电影界的传奇人物，曾获得过多个奥斯卡奖提名，包括最佳影片、最佳导演、最佳男主角等。他以其对电影的深刻理解和对美国电影界的贡献而著称，被誉为“金球奖的“英雄”。他不仅在电影界 |

