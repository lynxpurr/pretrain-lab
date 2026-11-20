"""gen_sft_v2_extra.py — Day 7: SFT v2 数据侧修正的补充样本生成器

背景（Day 5~6 诊断）：SFT v1 的两类失败与解码无关——
  1) `refuse-unknown`（问 2027 世界杯冠军）→ 编造细节：SFT 数据里几乎没有"承认不知道/纠正错误前提"的样本；
  2) `math-mul`（要求"只回答数字"）→ 长篇解释：格式硬约束样本仅 46 条（会话级 grep 的 1,703 是粗口径，
     含用户提问/闲聊匹配，assistant 侧真正"只回答"样本远少于此）。
另有 `en-fluency` 触发英文拒答模板（1.91% 会话含英文拒答），需补正例对冲。

本脚本生成三类**只进 train、不进 val** 的补充对话（chat 模板与 v1 完全一致）：
  A. calibration：未来事件 / 错误前提（如"2027 年世界杯"）/ 实时信息 / 隐私 / 不可验证事实；
     并含"已知事实 vs 未知"对比对（同一条对话里先答已知、再拒答未知）。
  B. format：格式硬约束算术（"只回答数字"）+ 一句话 / 不超过 N 字 / 列出 3 条。
  C. helpful：中英良性问题正例（描述海洋/解释概念/翻译/写代码），对冲拒答模板泄漏。

输出（JSONL，每行 = {"conversations": [{"role":…, "content":…}, …]}）：
  data/sft-extra-v2/calibration.jsonl
  data/sft-extra-v2/format.jsonl
  data/sft-extra-v2/helpful.jsonl
  data/sft-extra-v2/meta.json
  data/sft-extra-v2/SHA256SUMS

用法（仓库根目录）：
  .venv-pre/bin/python -I tools/gen_sft_v2_extra.py 2>&1 | tee logs/day7-sft-extra.log
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import zlib
from pathlib import Path

OUT = Path("data/sft-extra-v2")
SEED = 20261119


def dh(s: str) -> int:
    """确定性字符串哈希（不用内置 hash：其跨进程随机化会破坏可复现）。"""
    return zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF


def conv(*turns: tuple[str, str]) -> dict:
    return {"conversations": [{"role": r, "content": c} for r, c in turns]}


def q(user: str, assistant: str) -> dict:
    return conv(("user", user), ("assistant", assistant))


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ A. calibration

CITIES = [
    "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "武汉", "西安", "南京",
    "天津", "苏州", "长沙", "郑州", "青岛", "沈阳", "大连", "厦门", "福州", "济南",
    "合肥", "昆明", "哈尔滨", "长春", "石家庄", "太原", "南昌", "贵阳", "南宁", "海口",
    "兰州", "西宁", "银川", "乌鲁木齐", "呼和浩特", "拉萨", "香港", "澳门", "台北",
    "东京", "首尔", "新加坡", "纽约", "伦敦", "巴黎", "柏林", "悉尼", "多伦多",
    "旧金山", "洛杉矶",
    "无锡", "宁波", "温州", "佛山", "东莞", "珠海", "中山", "惠州", "汕头", "泉州",
    "常州", "南通", "徐州", "扬州", "绍兴", "嘉兴", "金华", "台州", "洛阳", "开封",
    "烟台", "潍坊", "淄博", "威海", "唐山", "保定", "廊坊", "秦皇岛", "包头", "鄂尔多斯",
    "桂林", "柳州", "三亚", "遵义", "绵阳", "德阳", "宜宾", "襄阳", "宜昌", "岳阳",
    "株洲", "湘潭", "九江", "赣州", "芜湖", "蚌埠", "鞍山", "吉林", "齐齐哈尔", "大庆",
]

COMPANIES = [
    "苹果", "微软", "谷歌", "亚马逊", "特斯拉", "英伟达", "阿里巴巴", "腾讯", "百度",
    "字节跳动", "美团", "京东", "网易", "小米", "华为", "三星", "台积电", "英特尔",
    "可口可乐", "迪士尼",
    "甲骨文", "Salesforce", "Adobe", "Netflix", "Meta", "优步", "爱彼迎", "星巴克",
    "麦当劳", "耐克", "阿迪达斯", "宝马", "奔驰", "丰田", "本田", "大众", "波音", "空客",
    "宁德时代", "比亚迪", "蔚来", "理想", "小鹏", "拼多多", "快手", "滴滴", "携程", "顺丰",
]

ROUTES = [
    ("北京南站", "首都机场"), ("上海虹桥站", "浦东机场"), ("广州南站", "白云机场"),
    ("深圳北站", "宝安机场"), ("杭州东站", "萧山机场"), ("成都东站", "天府机场"),
    ("重庆北站", "江北机场"), ("武汉站", "天河机场"), ("西安北站", "咸阳机场"),
    ("南京南站", "禄口机场"), ("天津站", "滨海机场"), ("长沙南站", "黄花机场"),
    ("郑州东站", "新郑机场"), ("青岛北站", "胶东机场"), ("沈阳北站", "桃仙机场"),
    ("大连北站", "周水子机场"), ("厦门北站", "高崎机场"), ("福州站", "长乐机场"),
    ("济南西站", "遥墙机场"), ("合肥南站", "新桥机场"),
    ("南昌西站", "昌北机场"), ("贵阳北站", "龙洞堡机场"), ("南宁东站", "吴圩机场"),
    ("海口东站", "美兰机场"), ("兰州西站", "中川机场"), ("西宁站", "曹家堡机场"),
    ("银川站", "河东机场"), ("乌鲁木齐站", "地窝堡机场"), ("呼和浩特东站", "白塔机场"),
    ("拉萨站", "贡嘎机场"), ("香港西九龙站", "香港国际机场"), ("台北车站", "桃园机场"),
    ("苏州站", "虹桥机场"), ("无锡东站", "硕放机场"), ("宁波站", "栎社机场"),
    ("温州南站", "龙湾机场"), ("佛山站", "白云机场"), ("东莞站", "深圳宝安机场"),
    ("珠海站", "金湾机场"), ("中山北站", "深圳宝安机场"), ("惠州站", "平潭机场"),
    ("汕头站", "潮汕机场"), ("泉州站", "晋江机场"), ("常州北站", "奔牛机场"),
    ("南通站", "兴东机场"), ("徐州东站", "观音机场"), ("扬州站", "泰州机场"),
    ("绍兴北站", "萧山机场"), ("嘉兴南站", "虹桥机场"),
]

NEWS_TOPICS = [
    "科技", "体育", "财经", "娱乐", "国际", "国内", "天气", "教育", "健康", "汽车",
    "房地产", "人工智能", "芯片", "新能源", "电影", "游戏", "旅游", "美食", "时尚", "军事",
    "农业", "环境", "气候", "科学", "航天", "生物", "医药", "金融", "银行", "保险",
    "证券", "物流", "零售", "电商", "制造", "能源", "化工", "钢铁", "建筑", "交通",
    "航空", "铁路", "港口", "通信", "网络安全", "数据", "隐私", "法律", "政策", "社会",
]

NAMES = [
    "张三", "李四", "王五", "赵六", "小明", "小红", "小刚", "小丽", "王先生", "李女士",
    "张老师", "刘医生", "陈工程师", "杨律师", "周经理", "吴同学", "郑阿姨", "冯叔叔",
    "陈先生", "林女士",
    "孙先生", "马女士", "朱老师", "胡医生", "郭工程师", "何律师", "高经理", "罗同学",
    "梁阿姨", "宋叔叔", "谢先生", "唐女士", "韩老师", "曹医生", "邓工程师", "许律师",
    "傅经理", "沈同学", "曾阿姨", "彭叔叔", "吕先生", "苏女士", "卢老师", "蒋医生",
    "蔡工程师", "贾律师", "丁经理", "魏同学", "薛阿姨", "叶叔叔",
]

PRIVATE_INFO = ["电话号码", "家庭住址", "工资收入", "身份证号码", "微信号",
                "出生日期", "车牌号码", "电子邮箱"]

OBSCURE_ENTITIES = [
    "一家位于杭州的未上市电商公司", "一个普通人的童年经历", "一个私人聚会的细节",
    "一份未公开的合同", "一个封闭社区的内部规定", "一本绝版书的某一页",
    "一个已删除的网页", "一个匿名用户的真实身份", "一个未公开的实验数据集",
    "一家公司的内部会议记录", "一个小镇的居民名单", "一份私人聊天记录",
    "一个未发布的产品参数", "一家创业公司的融资条款", "一个被删除的社交媒体账号",
    "一份尚未公开的政府文件", "一个私人邮箱的收件箱", "一家工厂的排班表",
    "一个未公开的专利申请", "一份个人医疗报告",
    "一个未公开的并购案", "一家公司的客户名单", "一个私人俱乐部的会员名单", "一份内部审计报告",
    "一个未公开的源代码仓库", "一个匿名举报的内容", "一份私人遗嘱", "一个未公开的临床试验结果",
    "一家餐厅的秘方", "一个未上映电影的结局", "一个未发布游戏的剧情", "一份私人日记",
    "一个未公开的选举民调", "一家公司的裁员计划", "一个未公开的定价策略", "一份私人保险合同",
    "一个未公开的算法模型", "一家工厂的生产计划", "一个未公开的合作伙伴名单", "一份私人成绩单",
    "一个未公开的专利内容", "一家公司的服务器密码", "一个未公开的安全漏洞", "一份私人银行流水",
    "一个未公开的面试题库", "一家公司的内部通讯录", "一个未公开的合同条款", "一份私人医疗记录",
    "一个未公开的科研数据集", "一家公司的供应链名单", "一个未公开的拍卖底价", "一份私人租赁合同",
    "一个未公开的股东名单", "一家公司的营销预算", "一个未公开的活动嘉宾名单", "一份私人推荐信",
    "一个未公开的定价算法", "一家公司的内部培训材料", "一个未公开的测试结果", "一份私人旅行计划",
]

FUTURE_EVENTS = [
    # (名称, 结果词, 有效未来年份, 无效年份, 周期说明)
    ("世界杯", "冠军", [2030, 2034, 2038, 2042], [2027, 2029, 2031, 2033, 2035], "每四年举办一次"),
    ("欧洲杯", "冠军", [2028, 2032, 2036], [2027, 2029, 2031, 2033], "每四年举办一次"),
    ("夏季奥运会", "举办城市", [2028, 2032, 2036], [2027, 2029, 2031, 2033], "每四年举办一次"),
    ("冬季奥运会", "举办城市", [2030, 2034, 2038], [2027, 2029, 2031, 2033], "每四年举办一次"),
    ("NBA 总决赛", "冠军", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年举办一次"),
    ("欧洲冠军联赛决赛", "冠军", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年举办一次"),
    ("奥斯卡金像奖", "最佳影片", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("诺贝尔物理学奖", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("F1 年度车手总冠军", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年产生一次"),
    ("温布尔登网球锦标赛", "男单冠军", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年举办一次"),
    ("金球奖", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("格莱美年度专辑", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("美国总统选举", "获胜者", [2028, 2032], [2027, 2029, 2030, 2031, 2033], "每四年举行一次"),
    ("世界杯金靴奖", "得主", [2030, 2034, 2038], [2027, 2029, 2031, 2033], "每四年颁发一次"),
    ("奥运会开幕式", "举办城市", [2028, 2032, 2036], [2027, 2029, 2031, 2033], "每四年举办一次"),
    ("超级碗", "冠军", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年举办一次"),
    ("NBA 常规赛 MVP", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年评选一次"),
    ("奥斯卡最佳导演", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("诺贝尔化学奖", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("诺贝尔文学奖", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("图灵奖", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("普利策新闻奖", "得主", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
    ("美国职棒大联盟世界大赛", "冠军", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年举办一次"),
    ("斯坦利杯", "冠军", [2027, 2028, 2029, 2030, 2031, 2032], [], "每年颁发一次"),
]

REALTIME_ANSWERS = [
    "我无法获取实时信息，所以不能确定。建议你查看天气应用或当地气象台的最新预报。",
    "我没有联网或实时数据访问能力，无法知道当前的情况。你可以用相应的应用或网站查询最新信息。",
    "这个问题需要实时数据，我的知识不是实时更新的，因此无法给出准确答案。请以官方或实时渠道为准。",
    "我无法获取此刻的最新数据，不能确定答案。你可以打开相关应用查看实时信息。",
]

PRIVATE_ANSWERS = [
    "我无法提供这类个人隐私信息，也无法知道它。建议你直接联系本人，或通过合法渠道获取授权。",
    "这属于个人隐私，我不能提供或猜测。请尊重他人隐私，通过正当方式询问本人。",
    "我没有权限也没有办法知道这些私人信息。涉及个人隐私的内容应当由本人决定是否公开。",
]

OBSCURE_ANSWERS = [
    "我没有关于这件事的可靠公开资料，无法确定。如果你有具体来源，我可以帮你一起分析。",
    "这属于未公开或无法核实的信息，我不能给出确定答案，也不应该编造细节。",
    "我无法确认这个问题的答案。我的知识来自公开训练数据，不包含这类未公开内容。",
]

FUTURE_ANSWERS = [
    "我不知道。{year} 年的{event}还没有发生，结果尚未公布，因此无法确定{result}。等赛事或颁奖结束后，官方渠道会公布结果。",
    "我无法确定。{year} 年的{event}尚未举行，{result}要等活动结束后才会揭晓。建议关注官方消息。",
    "这个问题目前没有答案：{year} 年的{event}还没举办，{result}尚未产生。我不能预测未来。",
    "我无法知道{year} 年{event}的{result}，因为这件事还没有发生。请以官方发布为准。",
]

FALSE_PREMISE_ANSWERS = [
    "{year} 年没有{event}。{event}{cycle}（例如 {valid_years}），所以 {year} 年没有{result}，我无法回答。",
    "{year} 年并不举办{event}。{event}{cycle}，{valid_years} 才是举办年份，因此不存在 {year} 年的{result}。",
    "这里的前提不对：{year} 年没有{event}。{event}{cycle}，所以无法给出 {year} 年的{result}。",
]

PAST_FACTS = [
    ("2014 年世界杯的冠军是谁？", "德国。"),
    ("2018 年世界杯的冠军是谁？", "法国。"),
    ("2022 年世界杯的冠军是谁？", "阿根廷。"),
    ("2012 年欧洲杯的冠军是谁？", "西班牙。"),
    ("2016 年欧洲杯的冠军是谁？", "葡萄牙。"),
    ("2012 年夏季奥运会的举办城市是哪里？", "伦敦。"),
    ("2016 年夏季奥运会的举办城市是哪里？", "里约热内卢。"),
    ("2018 年冬季奥运会的举办城市是哪里？", "平昌。"),
    ("2022 年冬季奥运会的举办城市是哪里？", "北京。"),
    ("2024 年夏季奥运会的举办城市是哪里？", "巴黎。"),
]


def gen_calibration(rng: random.Random) -> list[dict]:
    recs: list[dict] = []
    seen: set[str] = set()

    def add(rec: dict) -> None:
        key = json.dumps(rec, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            recs.append(rec)

    # 1) 实时天气（中英）
    weather_q = ["今天天气怎么样？", "明天会下雨吗？", "现在的气温是多少？", "周末的天气适合出门吗？"]
    for city in CITIES:
        for i, tpl in enumerate(weather_q):
            ans = REALTIME_ANSWERS[(dh(city) + i) % len(REALTIME_ANSWERS)]
            if i == 0:
                ans = f"{city}的实时天气我无法获取，所以不能确定。{ans.split('。', 1)[1] if '。' in ans else ans}"
            add(q(f"{city}{tpl}", ans))
    for city in ["Beijing", "Shanghai", "New York", "London", "Tokyo", "Paris"]:
        add(q(f"What's the weather like in {city} today?",
              "I don't have real-time data access, so I can't tell you the current weather. "
              "Please check a weather app or the local meteorological service for the latest forecast."))

    # 2) 实时行情 / 交通 / 新闻 / 时间
    for c in COMPANIES:
        add(q(f"{c}现在的股价是多少？", "我无法获取实时股价或行情数据，不能确定。请查看证券交易所或财经网站的实时报价。"))
        add(q(f"{c}今天的市值是多少？", "我没有实时市场数据，无法知道它此刻的市值。市值会随股价波动，请以财经平台的实时数据为准。"))
        add(q(f"{c}最近一个季度的营收是多少？", "我没有该公司最新的财务报表，无法给出准确数字。请查阅公司官网的投资者关系页面或正式财报。"))
    for c in COMPANIES[:10]:
        add(q(f"What is {c}'s stock price right now?",
              "I don't have real-time market data, so I can't provide the current stock price. "
              "Please check a financial website or your brokerage app for the latest quote."))
    for a, b in ROUTES:
        add(q(f"从{a}到{b}现在堵车吗？", "我无法获取实时路况，不能确定现在是否拥堵。建议打开地图应用查看实时交通。"))
        add(q(f"从{a}到{b}开车要多久？", "我无法获取实时路况和当前车流，因此不能给出准确的通行时间。请用地图应用查询实时路线。"))
    for topic in NEWS_TOPICS:
        add(q(f"今天{topic}领域的最新消息是什么？", "我无法获取实时新闻，不能告诉你今天的最新消息。请查看权威新闻网站或客户端。"))
        add(q(f"最近有什么{topic}新闻？", "我的知识不是实时更新的，无法确认最近的新闻。建议查看主流媒体的最新报道。"))
    add(q("现在北京时间几点？", "我无法获取当前时间，不能告诉你现在几点。请查看手机或电脑上的时钟。"))
    add(q("纽约现在几点？", "我无法获取实时时间，也不知道你所在时区，因此不能确定纽约的当前时间。"))
    add(q("今天是几号？", "我无法获取当前日期，不能确定今天是几号。请查看设备上的日历。"))
    add(q("昨晚那场比赛的比分是多少？", "我无法获取实时比赛结果，不能确定昨晚的比分。请查看体育新闻或赛事官方渠道。"))

    # 2b) 预测 / 随机 / 未来个人事项（不可知类）
    predict = [
        ("请预测明天的房价。", "我无法预测房价。房价受政策、供需、利率等多种因素影响，没有人能给出确定答案。"),
        ("请预测下周的天气。", "我无法预测下周的天气。天气预报需要实时气象数据，请查看气象部门的预报。"),
        ("下一期彩票的中奖号码是多少？", "彩票号码是随机产生的，我无法预测，也不应该给出所谓的“必中号码”。"),
        ("我明天会遇到什么事？", "我无法预测你的未来。明天会发生什么取决于许多现实因素，我不能给出确定答案。"),
        ("明年的股市会涨还是跌？", "我无法预测股市走势。股市受多种因素影响，任何确定的预测都不可靠。"),
        ("请告诉我未来十年的科技趋势。", "我无法确定未来十年的科技趋势。未来受技术、政策和社会因素影响，只能做开放性的讨论。"),
        ("我的未来会怎样？", "我无法预测你的未来。你的选择、环境和机遇都会影响结果，我不能给出确定答案。"),
        ("这场比赛谁会赢？", "我无法预测比赛结果。比赛受临场状态、战术和运气影响，只有结束后才有确定答案。"),
        ("请预测今年世界杯的冠军。", "我无法预测冠军。比赛结果尚未产生，任何预测都只是猜测。"),
        ("你觉得明天会下雨吗？", "我无法获取实时气象数据，不能确定明天是否下雨。请查看天气预报。"),
    ]
    for user, ans in predict:
        add(q(user, ans))

    # 3) 隐私
    for name in NAMES:
        for info in PRIVATE_INFO:
            add(q(f"{name}的{info}是多少？", PRIVATE_ANSWERS[(dh(name) + dh(info)) % len(PRIVATE_ANSWERS)]))
    for s in ["我的密码是多少？", "我的银行卡余额是多少？", "我朋友的联系方式是什么？",
              "我邻居家的门锁密码是多少？", "我的身份证号是多少？"]:
        add(q(s, "我无法知道你的私人信息，也不能提供或猜测密码、余额、联系方式等内容。请通过正规渠道自行查询。"))

    # 4) 不可验证 / 未公开
    for ent in OBSCURE_ENTITIES:
        add(q(f"请告诉我{ent}。", OBSCURE_ANSWERS[dh(ent) % len(OBSCURE_ANSWERS)]))
        add(q(f"{ent}到底是什么？", "我没有可靠信息，无法确定。这类内容通常未公开，我不应该编造细节。"))
    for book in ["一本早已绝版的旧书", "一本私人打印的笔记", "一份没有公开的草稿"]:
        add(q(f"{book}的第 37 页写了什么？", "我没有这本书的逐页内容，无法确定第 37 页写了什么。我不能凭空编造。"))

    # 5) 未来事件（有效年份）与错误前提（无效年份）
    for event, result, valid_years, invalid_years, cycle in FUTURE_EVENTS:
        for year in valid_years:
            ans = FUTURE_ANSWERS[(dh(event) + year) % len(FUTURE_ANSWERS)].format(
                year=year, event=event, result=result)
            add(q(f"请告诉我 {year} 年{event}的{result}。", ans))
            add(q(f"{year} 年{event}的{result}是谁/是什么？", ans))
        for year in invalid_years:
            ans = FALSE_PREMISE_ANSWERS[(dh(event) + year) % len(FALSE_PREMISE_ANSWERS)].format(
                year=year, event=event, result=result, cycle=cycle,
                valid_years="、".join(str(y) for y in valid_years[:3]))
            add(q(f"请告诉我 {year} 年{event}的{result}。", ans))
            add(q(f"{year} 年{event}的{result}是谁/是什么？", ans))

    # 6) 已知事实 vs 未知对比对（同一对话里先答已知、再拒答未知）
    for past_q, past_a in PAST_FACTS:
        # 从过去问题推断赛事名与未知年份
        if "世界杯" in past_q:
            event, result, future_year, bad_year = "世界杯", "冠军", 2030, 2027
        elif "欧洲杯" in past_q:
            event, result, future_year, bad_year = "欧洲杯", "冠军", 2028, 2027
        elif "夏季奥运会" in past_q:
            event, result, future_year, bad_year = "夏季奥运会", "举办城市", 2032, 2027
        elif "冬季奥运会" in past_q:
            event, result, future_year, bad_year = "冬季奥运会", "举办城市", 2030, 2027
        else:
            continue
        future_ans = FUTURE_ANSWERS[dh(event) % len(FUTURE_ANSWERS)].format(
            year=future_year, event=event, result=result)
        bad_ans = FALSE_PREMISE_ANSWERS[dh(event + "bad") % len(FALSE_PREMISE_ANSWERS)].format(
            year=bad_year, event=event, result=result, cycle="每四年举办一次",
            valid_years="、".join(str(y) for y in [future_year, future_year + 4, future_year + 8]))
        add(conv(("user", past_q), ("assistant", past_a),
                 ("user", f"{future_year} 年{event}的{result}是谁/是什么？"), ("assistant", future_ans)))
        add(conv(("user", past_q), ("assistant", past_a),
                 ("user", f"{bad_year} 年{event}的{result}是谁/是什么？"), ("assistant", bad_ans)))
        add(conv(("user", f"{bad_year} 年{event}的{result}是谁/是什么？"), ("assistant", bad_ans),
                 ("user", f"那 {future_year} 年呢？"), ("assistant", future_ans)))

    rng.shuffle(recs)
    return recs


# ------------------------------------------------------------------ B. format

ARITH_Q = [
    "{a} 乘以 {b} 等于多少？只回答数字。",
    "{a} 加 {b} 等于多少？只回答数字。",
    "{a} 减 {b} 等于多少？只回答数字。",
    "请只输出结果，不要解释：{a} × {b} = ?",
    "只回答数字：{a} + {b} = ?",
    "不要解释，直接给出答案：{a} - {b} = ?",
]
ARITH_Q_EN = [
    "What is {a} times {b}? Answer with the number only.",
    "What is {a} plus {b}? Reply with just the number.",
    "What is {a} minus {b}? Give only the number, no explanation.",
]


def gen_format(rng: random.Random) -> list[dict]:
    recs: list[dict] = []
    seen: set[str] = set()

    def add(rec: dict) -> None:
        key = json.dumps(rec, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            recs.append(rec)

    for a in range(2, 13):
        for b in range(2, 13):
            for tpl in ARITH_Q[:3]:
                if "减" in tpl and b > a:
                    continue
                ans = a * b if "乘" in tpl else (a + b if "加" in tpl else a - b)
                add(q(tpl.format(a=a, b=b), str(ans)))
            add(q(ARITH_Q[3].format(a=a, b=b), str(a * b)))
            add(q(ARITH_Q[4].format(a=a, b=b), str(a + b)))
            if a >= b:
                add(q(ARITH_Q[5].format(a=a, b=b), str(a - b)))
    for a in range(2, 13):
        for b in range(2, 13):
            add(q(ARITH_Q_EN[0].format(a=a, b=b), str(a * b)))
            add(q(ARITH_Q_EN[1].format(a=a, b=b), str(a + b)))
            if a >= b:
                add(q(ARITH_Q_EN[2].format(a=a, b=b), str(a - b)))

    # 一句话 / 不超过 N 字 / 列出 3 条
    one_sentence = [
        ("机器学习", "机器学习是让计算机从数据中学习规律、而不是靠人工规则完成任务的方法。"),
        ("光合作用", "光合作用是植物利用阳光把水和二氧化碳转化为氧气和养分的过程。"),
        ("重力", "重力是物体之间相互吸引的力，它让物体落向地面并维持行星运行。"),
        ("人工智能", "人工智能是让机器模拟人类感知、学习和决策能力的技术。"),
        ("互联网", "互联网是把全球计算机网络连接起来、用于交换信息的系统。"),
        ("云计算", "云计算是通过网络按需使用远程服务器计算和存储资源的方式。"),
        ("算法", "算法是解决某个问题的一系列明确步骤。"),
        ("数据库", "数据库是按一定结构组织、便于查询和管理的数据集合。"),
        ("操作系统", "操作系统是管理硬件资源并为应用程序提供运行环境的基础软件。"),
        ("区块链", "区块链是一种由多方共同维护、难以篡改的分布式账本技术。"),
    ]
    for concept, definition in one_sentence:
        add(q(f"用一句话解释什么是{concept}。", definition))
        add(q(f"请用一句话说明{concept}是什么。", definition))
        add(q(f"一句话概括什么是{concept}。", definition))

    brevity = [
        ("中国的首都是哪里？", "北京。"), ("水的化学式是什么？", "H2O。"),
        ("一年有几个月？", "12 个月。"), ("3 加 5 等于多少？", "8。"),
        ("太阳从哪边升起？", "东边。"), ("地球有几个卫星？", "1 个。"),
        ("冰的熔点是多少摄氏度？", "0 摄氏度。"), ("一天有多少小时？", "24 小时。"),
        ("一周有几天？", "7 天。"), ("一年有多少天？", "365 天。"),
    ]
    for question, answer in brevity:
        add(q(f"{question}不超过 10 个字。", answer))
        add(q(f"简短回答：{question}", answer))

    list3 = [
        ("学习编程", ["1. 先选一门语言并坚持练习；", "2. 每天写一点代码，从小项目开始；", "3. 学会读报错和查文档。"]),
        ("保持健康", ["1. 规律作息，保证睡眠；", "2. 均衡饮食，多喝水；", "3. 每周至少运动三次。"]),
        ("提高写作", ["1. 每天读一点好文章；", "2. 先写大纲再展开；", "3. 写完后大声读一遍并修改。"]),
        ("准备面试", ["1. 研究岗位要求；", "2. 复习核心知识并做模拟题；", "3. 准备几个能体现能力的项目故事。"]),
        ("学习英语", ["1. 每天背少量单词并复习；", "2. 多听多读真实材料；", "3. 找机会开口说和写。"]),
    ]
    for topic, items in list3:
        ans = "\n".join(items)
        add(q(f"列出三个{topic}的建议。", ans))
        add(q(f"请列出 3 条{topic}的建议：", ans))
        add(q(f"给我三个{topic}的建议。", ans))

    rng.shuffle(recs)
    return recs


# ------------------------------------------------------------------ C. helpful

EN_HELPFUL = [
    ("Describe the sea in a few sentences.",
     "The sea is a vast body of salt water that covers most of Earth's surface. It supports an enormous "
     "variety of life, helps regulate the climate, and plays a central role in the water cycle. People also "
     "rely on the sea for food, transport, and recreation."),
    ("Why is the ocean important?",
     "The ocean regulates temperature, absorbs carbon dioxide, produces much of the oxygen we breathe, and "
     "supports biodiversity and livelihoods. It is also central to global trade and food security."),
    ("What is machine learning?",
     "Machine learning is a branch of artificial intelligence in which models learn patterns from data rather "
     "than following hand-written rules. Common types include supervised, unsupervised, and reinforcement learning."),
    ("Explain gravity in simple terms.",
     "Gravity is the force by which objects attract one another. On Earth it pulls things toward the ground and "
     "keeps the Moon in orbit; on a larger scale it shapes galaxies."),
    ("What is the capital of Japan?", "Tokyo."),
    ("What is the capital of Italy?", "Rome."),
    ("What is the capital of Germany?", "Berlin."),
    ("Write a Python function that returns the sum of two numbers.",
     "def add(a, b):\n    return a + b"),
    ("Write a Python function that checks whether a number is even.",
     "def is_even(n):\n    return n % 2 == 0"),
    ("Translate '今天天气很好' into English.", "The weather is nice today."),
    ("Translate 'I love machine learning' into Chinese.", "我喜欢机器学习。"),
    ("Give me three tips for learning programming.",
     "1. Pick one language and practice it consistently.\n2. Build small projects and read error messages carefully.\n"
     "3. Read other people's code and learn to use documentation."),
    ("Summarize in one sentence: The company released a new phone with a faster chip and a better camera.",
     "The company launched a new phone with a faster chip and an improved camera."),
    ("What is 12 times 8?", "96."),
    ("What is 15 plus 27?", "42."),
    ("What is the chemical formula for water?", "H2O."),
    ("How many months are in a year?", "There are 12 months in a year."),
    ("What should I take if it rains tomorrow?", "You should take an umbrella or a raincoat."),
    ("Describe a healthy breakfast in two sentences.",
     "A healthy breakfast might include whole grains, fruit, and a source of protein such as eggs or yogurt. "
     "It should give you energy without too much sugar."),
    ("Why do we have seasons?",
     "Seasons happen because Earth's axis is tilted, so different parts of the planet receive different amounts "
     "of sunlight throughout the year."),
    ("What is the difference between weather and climate?",
     "Weather is the short-term state of the atmosphere, while climate is the long-term average pattern of weather "
     "in a region."),
    ("Explain what a neural network is.",
     "A neural network is a machine learning model made of layers of connected units that learn to transform inputs "
     "into useful outputs."),
    ("What is photosynthesis?",
     "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce oxygen and "
     "energy-rich sugars."),
    ("Give an example of a renewable energy source.", "Solar power is a renewable energy source."),
    ("What is the boiling point of water at sea level?", "100 degrees Celsius (212 degrees Fahrenheit)."),
    ("Name three programming languages.", "Python, JavaScript, and C++."),
    ("What is an API?",
     "An API is a defined interface that lets one piece of software request services or data from another."),
    ("What is a database index?",
     "A database index is a data structure that speeds up lookups on a table at the cost of extra storage and "
     "write overhead."),
    ("How can I improve my sleep?",
     "Keep a regular schedule, avoid screens before bed, limit caffeine late in the day, and make your bedroom "
     "dark and quiet."),
    ("Tell me a short joke.",
     "Why did the programmer quit? Because they didn't get arrays."),
]

ZH_HELPFUL = [
    ("上海是一座怎样的城市？",
     "上海是中国的一座国际化大都市，位于长江入海口。它是重要的金融、贸易和航运中心，也有丰富的历史建筑和文化生活。"),
    ("北京是一座怎样的城市？",
     "北京是中国的首都，也是政治、文化和国际交往中心。它有故宫、长城等历史遗迹，同时聚集了许多高校和科技公司。"),
    ("什么是量子计算？",
     "量子计算利用量子比特的叠加和纠缠来进行计算，在特定问题上可能比经典计算机更快，但目前仍处于早期阶段。"),
    ("写一个 Python 函数判断一个数是不是偶数。",
     "def is_even(n):\n    return n % 2 == 0"),
    ("把'今天天气不错'翻译成英文。", "The weather is nice today."),
    ("把'I enjoy reading books'翻译成中文。", "我喜欢读书。"),
    ("用一句话说明什么是机器学习。",
     "机器学习是让计算机从数据中学习规律、而不是靠人工规则完成任务的方法。"),
    ("给三个学习编程的建议。",
     "1. 选一门语言坚持练习；\n2. 从小项目开始，遇到报错先读错误信息；\n3. 多读别人的代码和官方文档。"),
    ("下雨天出门要带什么？", "带伞或雨衣，注意路面湿滑。"),
    ("水的分子式是什么？", "H2O。"),
    ("一年有多少个月？", "12 个月。"),
    ("中国的首都是哪座城市？", "北京。"),
    ("解释一下什么是互联网。",
     "互联网是把全球计算机网络连接起来、用于交换信息的系统，它让不同设备之间可以互相通信和共享资源。"),
    ("什么是操作系统？",
     "操作系统是管理硬件资源、并为应用程序提供运行环境的基础软件，例如 Windows、Linux 和 macOS。"),
    ("为什么会有四季？",
     "因为地球的自转轴是倾斜的，一年中不同地区接收到的太阳光角度和时长不同，从而形成四季。"),
    ("什么是光合作用？",
     "光合作用是植物利用阳光，把水和二氧化碳转化为氧气和养分的过程。"),
    ("怎样保持健康？",
     "规律作息、均衡饮食、适量运动，并注意心理健康和定期体检。"),
    ("写一个 Python 函数返回两个数的和。",
     "def add(a, b):\n    return a + b"),
    ("12 乘以 8 等于多少？", "96。"),
    ("15 加 27 等于多少？", "42。"),
    ("总结一下：苹果公司发布了新款手机，搭载更快的芯片和更好的摄像头。",
     "苹果发布了搭载更快芯片和更好摄像头的新款手机。"),
    ("如果明天下雨，我应该带什么？", "应该带伞或雨衣。"),
    ("什么是一张关系型数据库的表？",
     "关系型数据库的表是按行和列组织的数据集合，每一行通常代表一条记录，每一列代表一个字段。"),
    ("解释一下什么是算法。", "算法是解决某个问题的一系列明确步骤。"),
    ("什么是云计算？", "云计算是通过网络按需使用远程服务器计算和存储资源的方式。"),
    ("如何提高写作能力？",
     "多读好文章、先列大纲再展开、写完后朗读并修改，坚持练习。"),
    ("什么是区块链？", "区块链是一种由多方共同维护、难以篡改的分布式账本技术。"),
    ("推荐三种编程语言。", "Python、JavaScript 和 C++。"),
    ("什么是 API？",
     "API 是软件之间进行交互的接口，定义了如何请求数据和调用功能。"),
    ("怎样准备一场面试？",
     "研究岗位要求、复习核心知识、做模拟题，并准备能体现能力的项目故事。"),
]


def gen_helpful(rng: random.Random) -> list[dict]:
    recs = [q(u, a) for u, a in EN_HELPFUL] + [q(u, a) for u, a in ZH_HELPFUL]
    rng.shuffle(recs)
    return recs


# ------------------------------------------------------------------ D. concise（v2d，Day 8 机动窗口）

# v2c 复读三题（reason 0.728 / en-fluency 0.708 / zh-fluency 0.516）的数据侧病因：
# "介绍一下 X / 如果…该怎么办"类问题的训练答案 p50≈700 字符，长答案先验超出 140M 的长文连贯能力；
# 英文侧长答案几乎不在训练集里（en 复读 = 长答案先验的泛化），砍不到、只能加正例对冲。
# → 本类教"介绍/假设题 → 2~3 句连贯答案"（150~350 字符），**不用编号列表行**（防罗列格式泛化）。
ZH_CONCISE_INTRO = [
    ("介绍一下北京。", "北京是中国的首都，也是全国的政治和文化中心。这里有故宫、长城等著名历史遗迹，同时也聚集了许多高校和科技公司。"),
    ("介绍一下上海。", "上海是中国最大的城市之一，位于长江入海口。它以金融和贸易闻名，外滩的天际线是这座城市的标志。"),
    ("介绍一下长城。", "长城是中国古代的防御工程，横跨北方多个省份。它历史悠久，如今是著名的旅游景点，也被视为中华民族的象征。"),
    ("介绍一下春节。", "春节是农历新年，是中国最重要的传统节日。家人通常会在这一天团聚，一起吃年夜饭、贴春联。"),
    ("介绍一下中秋节。", "中秋节在农历八月十五，是家人团聚的节日。人们会赏月、吃月饼，寄托思念之情。"),
    ("介绍一下大熊猫。", "大熊猫是中国特有的珍稀动物，主要生活在四川的山林里。它们以竹子为主食，性格温顺，深受世界各地的人喜爱。"),
    ("介绍一下春天。", "春天是四季之一，天气渐渐变暖，植物开始发芽开花。很多人喜欢在这个季节出门踏青。"),
    ("介绍一下海洋。", "海洋覆盖了地球表面的大部分区域，孕育着极其丰富的生命。它还参与调节全球气候，与人类生活息息相关。"),
    ("介绍一下太阳。", "太阳是太阳系的中心恒星，为地球提供光和热。它的能量来自内部的核聚变反应。"),
    ("介绍一下地球。", "地球是太阳系中距离太阳第三近的行星，是目前已知唯一存在生命的星球。它的表面大部分被海洋覆盖。"),
    ("介绍一下猫。", "猫是常见的家庭宠物，性格独立又亲人。它们爱干净，每天会花很多时间梳理毛发。"),
    ("介绍一下狗。", "狗是最早被人类驯化的动物之一，忠诚而友好。经过训练，它们可以看家、导盲，甚至参与救援。"),
    ("介绍一下茶叶。", "茶叶是中国传统饮品，用茶树的嫩叶加工制成。绿茶、红茶、乌龙茶是几种常见的类型。"),
    ("介绍一下图书馆。", "图书馆是收藏和借阅图书的公共场所。人们可以在这里安静地阅读、查阅资料，许多图书馆还提供免费的座位和电子资源。"),
    ("介绍一下博物馆。", "博物馆是收藏和展示文物的场所。参观博物馆可以帮助人们了解历史、艺术和科学知识。"),
    ("介绍一下乒乓球。", "乒乓球是中国的国球，是一项在桌面上进行的球类运动。它节奏快，对反应能力要求高，非常适合各个年龄段的人。"),
    ("介绍一下机器学习。", "机器学习是让计算机从数据中学习规律的技术。与人工编写规则不同，模型会随着样本增多自动改进。推荐系统和图像识别都是它的常见应用。"),
    ("介绍一下互联网。", "互联网把全世界的计算机连接在一起，让人们可以随时传递和获取信息。它是现代通信、学习和工作的基础。"),
    ("介绍一下高铁。", "高铁是时速超过两百公里的铁路系统，速度快、准点率高。它让跨城市出行变得方便，也带动了沿线城市的发展。"),
    ("介绍一下冰箱。", "冰箱是用来低温储存食物的家用电器。低温能减缓细菌繁殖，让食物保存得更久。"),
]

ZH_CONCISE_HYP = [
    ("如果明天下雨，我该准备什么？", "建议带一把伞，穿防滑的鞋子。如果骑自行车，最好穿上雨衣。出门前也可以先看一眼天气预报。"),
    ("如果周末去爬山，我该准备什么？", "带上足够的水和一些食物，穿舒适防滑的运动鞋。出发前查看天气，最好再带一件外套。"),
    ("想学好英语，我该怎么做？", "每天坚持背几个单词，多听英语材料，并找机会开口说。坚持几个月就能看到明显进步。"),
    ("想养成读书习惯，我该怎么做？", "从每天睡前读十页开始，先选自己感兴趣的书。把书放在床头，比定大目标更容易坚持。"),
    ("下周要出远门，我该怎么准备？", "提前订好交通和住宿，查一下当地近几天的天气，再准备证件和常用药品。行李尽量精简。"),
    ("想开始运动，我该从哪里做起？", "从快走或慢跑开始，每周三到四次，每次半小时左右。运动前记得热身，循序渐进最重要。"),
    ("考试前很紧张，我该怎么办？", "把复习内容拆成小块，按计划推进，紧张感会小很多。考前保证睡眠，比熬夜刷题更有效。"),
    ("家里人多口杂，怎么安静学习？", "可以戴耳塞或降噪耳机，去图书馆或书房等安静的地方。把手机放到看不见的地方也能减少打扰。"),
    ("新手想养植物，该怎么选？", "可以从绿萝、多肉这类好养的植物开始。它们对水和光照的要求不高，适合练手。"),
    ("做饭总是手忙脚乱，怎么办？", "做菜前先把所有食材切好、调料备齐，下锅时就不会乱。先从简单的菜开始，熟练了再尝试复杂的。"),
]

EN_CONCISE_FLU = [
    ("Tell me about the ocean.", "The ocean covers most of Earth's surface and is home to a huge variety of life. It helps regulate the climate and provides food for billions of people."),
    ("Tell me about spring.", "Spring is when the weather warms up and plants begin to grow. Birds return, flowers bloom, and many people enjoy outdoor activities."),
    ("Tell me about winter.", "Winter is the coldest season of the year. Days become short, and in many places it snows. People keep warm indoors and celebrate holidays together."),
    ("Tell me about cats.", "Cats are popular pets known for being independent yet affectionate. A healthy cat sleeps a lot and grooms itself every day."),
    ("Tell me about dogs.", "Dogs are loyal and friendly animals, and one of the first domesticated species. With training they can guard homes, guide people, and join rescues."),
    ("Tell me about coffee.", "Coffee is a brewed drink made from roasted beans. It contains caffeine, which helps people stay awake, and it is popular around the world."),
    ("Tell me about the Great Wall.", "The Great Wall is an ancient fortification in northern China. It stretches across mountains and deserts, and today it is a famous symbol of China."),
    ("Tell me about Beijing.", "Beijing is the capital of China and its political and cultural center. It is home to historic sites such as the Forbidden City, with the Great Wall nearby."),
    ("Tell me about pandas.", "Pandas are rare bears that live in the mountains of China. They eat bamboo almost all day and are loved around the world."),
    ("Tell me about books.", "Books carry knowledge and stories from one generation to the next. Reading regularly builds vocabulary and gives you new ways to see the world."),
    ("Tell me about trains.", "Trains run on fixed tracks and can carry many people or heavy goods at once. High-speed rail has made travel between cities fast and convenient."),
    ("Describe a rainy day.", "On a rainy day the streets look shiny and the air smells fresh. People carry umbrellas, and it is a good time to stay indoors with a book."),
    ("Describe a good friend.", "A good friend listens to you and stands by you in hard times. You can be honest around them and share both joy and trouble."),
    ("Describe your morning routine.", "A good morning starts with waking up on time, drinking some water, and having breakfast. A short walk or stretch helps you start the day with energy."),
    ("What is machine learning?", "Machine learning is a way for computers to learn patterns from data. Instead of following hand-written rules, the model improves as it sees more examples."),
    ("What is photosynthesis?", "Photosynthesis is how plants use sunlight, water, and carbon dioxide to make food and oxygen. It is the foundation of almost all life on Earth."),
    ("What should I take if it rains tomorrow?", "Take an umbrella and wear shoes that do not slip. If you ride a bike, a raincoat is more useful."),
    ("How can I keep healthy?", "Keep a regular schedule, eat balanced meals, and exercise a few times a week. A good mood matters just as much."),
    ("How do I learn to code?", "Pick one language like Python and practice a little every day. Start with small projects and read the error messages carefully when something breaks."),
    ("What would you do on a free weekend?", "I would sleep in a little, take a walk in a park, and read a book in the afternoon. Simple plans often make the best weekends."),
]


def gen_concise(rng: random.Random) -> list[dict]:
    recs = ([q(u, a) for u, a in ZH_CONCISE_INTRO]
            + [q(u, a) for u, a in ZH_CONCISE_HYP]
            + [q(u, a) for u, a in EN_CONCISE_FLU])
    rng.shuffle(recs)
    return recs


def main() -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    calib = gen_calibration(rng)
    fmt = gen_format(rng)
    helpful = gen_helpful(rng)
    concise = gen_concise(rng)

    write_jsonl(OUT / "calibration.jsonl", calib)
    write_jsonl(OUT / "format.jsonl", fmt)
    write_jsonl(OUT / "helpful.jsonl", helpful)
    write_jsonl(OUT / "concise.jsonl", concise)

    meta = {
        "purpose": "SFT v2 数据侧修正补充样本（只进 train，不进 val）",
        "seed": SEED,
        "calibration": {"unique": len(calib),
                        "categories": ["未来事件", "错误前提", "实时信息", "隐私", "不可验证", "已知事实对比"]},
        "format": {"unique": len(fmt), "categories": ["只回答数字算术", "一句话", "不超过 N 字", "列出 3 条"]},
        "helpful": {"unique": len(helpful), "categories": ["英文良性问答", "中文良性问答"]},
        "concise": {"unique": len(concise),
                    "categories": ["中文介绍类连贯答案", "中文假设/建议类连贯答案", "英文 fluency 连贯答案"],
                    "note": "v2d 新增：复读三题题型（介绍/假设）的中等长度连贯正例，不含编号列表行"},
        "template": "<|im_start|>{role}\\n{content}<|im_end|>\\n",
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_s": round(time.time() - t0, 1),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    names = ("calibration.jsonl", "format.jsonl", "helpful.jsonl", "concise.jsonl")
    lines = [f"{sha256_file(OUT / name)}  {name}" for name in names]
    (OUT / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[done] calibration={len(calib):,} format={len(fmt):,} helpful={len(helpful):,} "
          f"concise={len(concise):,} → {OUT}/（SHA256SUMS {len(names)} 条）· {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()