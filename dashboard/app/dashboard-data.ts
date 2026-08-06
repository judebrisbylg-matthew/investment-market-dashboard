// Generated from data/market-data.json. Do not edit by hand.
export const snapshot = {
  "businessDate": "2026-08-06",
  "generatedAt": "2026-08-06T07:17:54+08:00",
  "asOf": "2026/8/6 06:15 HKT",
  "marketGate": "数据不足",
  "dataHealth": "灰灯",
  "coverage": 96,
  "riskScore": 71,
  "lightCounts": {
    "green": 7,
    "yellow": 5,
    "red": 0,
    "gray": 0
  },
  "daily": {
    "asOf": "2026/8/6 06:15 HKT",
    "signal": "黄灯",
    "action": "等待",
    "marketJudgement": "今天结论：黄灯等待，央行看美联储官员讲话待确认，先看先进封装、苹果概念能否放量。",
    "positionAdvice": "仓位建议：维持中性偏谨慎，不追高，等主线确认。",
    "needAction": "今日动作：盯先进封装、苹果概念成交/订单；基金看强项004432(有色金属)日涨5.20%，弱项007818(通信/设备)日涨0.75%。",
    "actionReason": "不操作原因：估值分位、北向资金（月度）未转绿，央行看美联储官员讲话仍待确认。",
    "riskPoint": "主要风险：估值分位、北向资金（月度）；若成交不足或消息反复，成长资产易回撤。",
    "nextReview": "下次复盘：看先进封装、苹果概念是否放量，AI服务器/液冷、光模块/CPO是否升温，新闻是否新增冲击。"
  },
  "freshness": [
    {
      "name": "风控",
      "date": "08.05",
      "width": 86
    },
    {
      "name": "赛道",
      "date": "08.05",
      "width": 100
    },
    {
      "name": "跨市场",
      "date": "08.06",
      "width": 100
    },
    {
      "name": "事件",
      "date": "08.06",
      "width": 100
    },
    {
      "name": "持仓",
      "date": "08.05",
      "width": 100
    }
  ],
  "moduleStatus": [
    {
      "code": "01",
      "name": "市场风控",
      "state": "数据不足",
      "tone": "green",
      "desc": "5项预警"
    },
    {
      "code": "02",
      "name": "行业赛道",
      "state": "已刷新",
      "tone": "green",
      "desc": "20池 / 前10"
    },
    {
      "code": "03",
      "name": "跨市验证",
      "state": "仅佐证",
      "tone": "gray",
      "desc": "1项待验证"
    },
    {
      "code": "04",
      "name": "重大事件",
      "state": "已刷新",
      "tone": "green",
      "desc": "影响前10"
    },
    {
      "code": "05",
      "name": "持仓研究",
      "state": "已刷新",
      "tone": "green",
      "desc": "2股 / 12基"
    }
  ]
} as const;

export const risks = [
  [
    "10年期美债收益率",
    "4.63%（FRED，2026-08-04）",
    "green",
    "4.3% ~ 4.7%",
    "指标日期 2026-08-04，沿用最近可得数据（滞后2天）",
    "2026-08-04"
  ],
  [
    "北向资金（月度）",
    "月度口径待核验",
    "yellow",
    "净流入/月流出＜200亿",
    "指标日期待核验",
    "待核验"
  ],
  [
    "美联储动向",
    "联邦基金有效利率3.63%（FRED，2026-08-04）",
    "green",
    "维持利率不变，释放降息预期",
    "指标日期 2026-08-04，沿用最近可得数据（滞后2天）",
    "2026-08-04"
  ],
  [
    "美元指数",
    "DXY约99.67（东方财富美元指数口径，2026年8月5日）",
    "green",
    "DXY < 103",
    "指标日期 2026-08-05，沿用最近可得数据（滞后1天）",
    "2026-08-05"
  ],
  [
    "实际利率",
    "10年期TIPS实际利率2.40%（FRED，2026-08-04）",
    "yellow",
    "10Y TIPS < 2.2%",
    "指标日期 2026-08-04，沿用最近可得数据（滞后2天）",
    "2026-08-04"
  ],
  [
    "信用利差",
    "美国高收益债OAS 2.73%（FRED，2026-08-04）",
    "green",
    "高收益OAS < 3.5%",
    "指标日期 2026-08-04，沿用最近可得数据（滞后2天）",
    "2026-08-04"
  ],
  [
    "VIX",
    "VIX 16.50（FRED，2026-08-04）",
    "green",
    "< 18",
    "指标日期 2026-08-04，沿用最近可得数据（滞后2天）",
    "2026-08-04"
  ],
  [
    "全球流动性",
    "美联储总资产6.738万亿美元，周变动-9.2亿美元（FRED，2026-07-29）",
    "yellow",
    "主要央行流动性企稳/扩张",
    "指标日期 2026-07-29，沿用最近可得数据（滞后8天）",
    "2026-07-29"
  ],
  [
    "A股成交额",
    "沪深两市成交约2.66万亿元（东方财富指数口径，2026年8月5日）",
    "green",
    ">1.0万亿",
    "指标日期 2026-08-05，沿用最近可得数据（滞后1天）",
    "2026-08-05"
  ],
  [
    "港股成交额",
    "恒生指数成分成交约2780亿港元（非港股全市场口径，2026年8月5日）",
    "yellow",
    ">1500亿港元",
    "指标日期 2026-08-05，沿用最近可得数据（滞后1天）",
    "2026-08-05"
  ],
  [
    "行业轮动强弱",
    "A股前3赛道：先进封装、苹果概念、AI芯片/半导体；平均研究分95.0",
    "green",
    "主线清晰且扩散",
    "指标日期 2026-08-05，沿用最近可得数据（滞后1天）",
    "2026-08-05"
  ],
  [
    "估值分位",
    "核心指数不极端，AI链局部偏贵",
    "yellow",
    "核心指数估值<70%分位",
    "指标日期待核验",
    "待核验"
  ]
] as const;

export const sectors = [
  {
    "name": "先进封装",
    "score": 85,
    "trend": 24,
    "flow": 24,
    "fundamental": 24,
    "hf": 9,
    "value": 4,
    "research": "green",
    "execute": "gray",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "苹果概念",
    "score": 84,
    "trend": 24,
    "flow": 24,
    "fundamental": 24,
    "hf": 8,
    "value": 4,
    "research": "green",
    "execute": "gray",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "AI芯片/半导体",
    "score": 84,
    "trend": 24,
    "flow": 24,
    "fundamental": 24,
    "hf": 10,
    "value": 2,
    "research": "green",
    "execute": "gray",
    "risk": "美股芯片、费半、AI链成交额、云厂Capex、先进封装和HBM订单",
    "operation": "止盈跟踪",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "存储/HBM",
    "score": 77,
    "trend": 23,
    "flow": 24,
    "fundamental": 24,
    "hf": 3,
    "value": 3,
    "research": "green",
    "execute": "gray",
    "risk": "美光指引、DRAM/NAND价格、HBM供需、国产存储成交额",
    "operation": "止盈跟踪",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "英伟达概念",
    "score": 80,
    "trend": 23,
    "flow": 24,
    "fundamental": 24,
    "hf": 5,
    "value": 4,
    "research": "green",
    "execute": "gray",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "AI服务器/液冷",
    "score": 73,
    "trend": 22,
    "flow": 24,
    "fundamental": 22,
    "hf": 1,
    "value": 4,
    "research": "green",
    "execute": "gray",
    "risk": "服务器订单、液冷招标、云厂Capex、电力配套",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "光模块/CPO",
    "score": 73,
    "trend": 22,
    "flow": 24,
    "fundamental": 22,
    "hf": 1,
    "value": 4,
    "research": "green",
    "execute": "gray",
    "risk": "800G/1.6T订单、云厂资本开支、光模块毛利率",
    "operation": "止盈跟踪",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "PCB/高速铜连接",
    "score": 71,
    "trend": 22,
    "flow": 24,
    "fundamental": 22,
    "hf": 0,
    "value": 3,
    "research": "green",
    "execute": "gray",
    "risk": "交换机订单、PCB毛利率、高速铜连接订单、服务器出货",
    "operation": "止盈跟踪",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "消费电子/AI终端",
    "score": 81,
    "trend": 20,
    "flow": 24,
    "fundamental": 22,
    "hf": 10,
    "value": 5,
    "research": "green",
    "execute": "gray",
    "risk": "AI手机/眼镜销量、苹果链订单、端侧AI渗透率",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "CPO概念",
    "score": 64,
    "trend": 20,
    "flow": 20,
    "fundamental": 20,
    "hf": 0,
    "value": 4,
    "research": "yellow",
    "execute": "gray",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  }
] as const;

export const events = [
  {
    "title": "美联储政策与利率预期再受关注，市场等待官员表态和收益率确认",
    "priority": 11,
    "direction": 0,
    "confidence": "中高",
    "source": "美国财经电视台",
    "date": "2026/8/6",
    "watch": "美联储官员讲话、10年期美债收益率、实际利率、美元指数、黄金和纳指表现"
  },
  {
    "title": "人工智能和半导体仍是市场主线，但高估值与拥挤交易需要财报验证",
    "priority": 7,
    "direction": 1,
    "confidence": "中高",
    "source": "公开新闻聚合源",
    "date": "2026/8/5",
    "watch": "费半指数、英伟达链条、云厂资本开支、芯片订单、毛利率和成交额"
  },
  {
    "title": "中东与地缘风险仍在扰动市场，原油、黄金和风险偏好需要重点跟踪",
    "priority": 6,
    "direction": 0,
    "confidence": "中高",
    "source": "公开新闻聚合源",
    "date": "2026/8/6",
    "watch": "中东局势、原油运输、布伦特油价、黄金价格、美元指数和军工板块表现"
  },
  {
    "title": "油价与能源供给变量继续影响通胀预期，资源品和风险偏好需同步观察",
    "priority": 6,
    "direction": 1,
    "confidence": "中高",
    "source": "公开新闻聚合源",
    "date": "2026/8/6",
    "watch": "布伦特油价、美国原油库存、产油国政策、通胀预期、航空和化工板块"
  },
  {
    "title": "贸易和关税变量继续影响制造业利润，订单、成本和供应链风险需跟踪",
    "priority": 6,
    "direction": 0,
    "confidence": "中高",
    "source": "美国财经电视台",
    "date": "2026/8/6",
    "watch": "关税政策、制造业订单、企业毛利率、出口数据、汽车和工业品板块"
  },
  {
    "title": "中国资产仍受政策、盈利和资金流共同影响，科技制造方向更值得跟踪",
    "priority": 5,
    "direction": 0,
    "confidence": "中高",
    "source": "公开新闻聚合源",
    "date": "2026/8/4",
    "watch": "A股成交额、港股成交额、南向资金、人民币汇率、政策表态和科技制造板块"
  },
  {
    "title": "人工智能终端和消费电子催化升温，真实销量和供应链订单是关键",
    "priority": 7,
    "direction": 1,
    "confidence": "中高",
    "source": "美国财经电视台",
    "date": "2026/8/1",
    "watch": "智能眼镜销量、消费电子供应链订单、光学器件、芯片和终端厂商指引"
  },
  {
    "title": "科技重要消息待复核，需观察是否改变市场风险偏好",
    "priority": 4,
    "direction": 1,
    "confidence": "中高",
    "source": "美国财经电视台",
    "date": "2026/7/28",
    "watch": "官方公告、相关指数、成交额、利率、美元、商品价格和行业龙头表现"
  },
  {
    "title": "央行重要消息待复核，需观察是否改变市场风险偏好",
    "priority": 5,
    "direction": 0,
    "confidence": "中高",
    "source": "公开新闻聚合源",
    "date": "2026/7/15",
    "watch": "官方公告、相关指数、成交额、利率、美元、商品价格和行业龙头表现"
  },
  {
    "title": "美股收盘分化，美光业绩提振芯片链但苹果拖累纳指",
    "priority": 6,
    "direction": 0,
    "confidence": "中高",
    "source": "AP / WSJ",
    "date": "2026/6/25",
    "watch": "美光指引、费半指数、苹果链、纳指成交额、AI硬件毛利率"
  }
] as const;

export const evidence = {
  "count": 10,
  "newCount": 0,
  "trackingCount": 1,
  "strongCount": 7,
  "independentBuyCount": 0,
  "leading": [
    "巴菲特 / Berkshire Hathaway",
    "霍华德·马克斯 / Oaktree",
    "比尔·阿克曼 / Pershing Square"
  ],
  "note": "机构观点只作佐证，不能独立触发买入。",
  "details": [
    {
      "name": "巴菲特 / Berkshire Hathaway",
      "strength": "高",
      "stance": "无新增可靠观点",
      "style": "价值投资/保险现金流/长期配置",
      "focus": "现金和短债、Apple、American Express、Bank of America、Coca-Cola、Chevron、Alphabet、Delta",
      "meaning": "偏防守；高估值阶段不要追涨。",
      "detail": "复核至2026/8/5：未发现巴菲特发布改变框架的新公开观点；继续把高现金、少数确定性资产和安全边际作为估值纪律校验，不把它当作短线交易信号。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "高瓴 / 张磊",
      "strength": "中",
      "stance": "无新增可靠观点",
      "style": "中国/亚洲成长价值/产业研究",
      "focus": "中国资产、创新药、消费、互联网平台、先进制造",
      "meaning": "作为中国成长价值和产业研究坐标，重点看盈利兑现。",
      "detail": "复核至2026/8/5：未发现张磊或高瓴新增可验证公开框架；继续作为中国成长价值和产业研究坐标，重点看创新药、先进制造和互联网平台盈利兑现。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "霍华德·马克斯 / Oaktree",
      "strength": "高",
      "stance": "无新增可靠观点",
      "style": "信用周期/风险控制/逆向投资",
      "focus": "Oaktree 信用资产、困境/高收益债",
      "meaning": "偏谨慎；检查AI与成长资产是否过热。",
      "detail": "复核至2026/8/5：Oaktree官网近期有内容更新迹象，但未确认出现改变投资框架的新Marks观点；继续用风险补偿、信用周期和过热资产纪律校验AI与成长交易。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "雷·达里奥 / Bridgewater",
      "strength": "中高",
      "stance": "无新增可靠观点",
      "style": "全球宏观/债务周期/风险平价",
      "focus": "黄金、全球分散配置、部分中国资产",
      "meaning": "偏防守与分散，关注债务和货币周期。",
      "detail": "复核至2026/8/5：未发现Dalio新增高可信公开观点改变配置框架；继续用债务周期、黄金、非美元资产和分散化原则校验宏观风险。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "比尔·阿克曼 / Pershing Square",
      "strength": "高",
      "stance": "无新增可靠观点",
      "style": "集中持仓/主动投资/优质公司",
      "focus": "Microsoft、平台科技、消费服务龙头",
      "meaning": "选择性偏多，但估值必须合理。",
      "detail": "复核至2026/8/5：未确认Ackman新增改变框架的公开观点；继续偏向少数高质量现金流龙头和可解释的资本配置，回避无法由现金流支撑的高估资产。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "大卫·泰珀 / Appaloosa",
      "strength": "中高",
      "stance": "无新增可靠观点",
      "style": "宏观交易/机会主义/风险资产节奏",
      "focus": "Amazon、Uber、Micron、TSMC、Sandisk",
      "meaning": "偏进攻，但只适合观察高弹性资产的交易节奏。",
      "detail": "复核至2026/8/5：未发现Tepper新增可靠公开观点；继续把他作为高弹性风险资产节奏参考，重点看AI硬件、平台消费和宏观风险偏好。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "肯·格里芬 / Citadel",
      "strength": "中",
      "stance": "无新增可靠观点",
      "style": "多策略/市场结构/流动性",
      "focus": "多策略、股票/信用/利率/商品/量化交易",
      "meaning": "用于观察流动性、波动率和市场结构，不作方向性跟单。",
      "detail": "复核至2026/8/5：未发现Griffin新增高确信公开观点改变框架；继续把Citadel作为流动性、波动率和市场结构观察样本。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "克里斯·霍恩 / TCI",
      "strength": "高",
      "stance": "无新增可靠观点",
      "style": "长期集中持股/高壁垒公司/激进治理",
      "focus": "Alphabet、Visa、S&P Global、Moody's、GE Aerospace、Airbus、Safran",
      "meaning": "长期偏多高壁垒企业，不支持无差别追涨。",
      "detail": "复核至2026/8/5：未发现Hohn新增公开框架变化；继续沿用高壁垒平台、支付网络、评级和航空航天资产也必须服从估值纪律的结论。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "凯瑟琳·伍德 / ARK",
      "strength": "中",
      "stance": "跟踪验证",
      "style": "颠覆式创新/高波动成长",
      "focus": "SpaceX、Tesla、ARKK/ARKQ/ARKX、私募创新敞口",
      "meaning": "作为高波动成长和创新资产情绪指标，不作组合模板。",
      "detail": "复核至2026/8/5：ARK属于高频交易动作源，6/16之后仍需持续跟踪其每日交易披露；当前不能写成“无更新”，应把ARK作为高波动成长和创新资产情绪指标，而不是组合模板。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "斯坦利·德鲁肯米勒 / Duquesne",
      "strength": "中高",
      "stance": "无新增可靠观点",
      "style": "顶级宏观交易/集中押注/风险控制",
      "focus": "Nuvation Bio、Caris Life Sciences、Olema Pharmaceuticals 等",
      "meaning": "长期认可AI，短期反对拥挤追高。",
      "detail": "复核至2026/8/5：未发现Druckenmiller新增高可信公开观点；继续沿用承认AI长期逻辑但不在短线拥挤时硬追、重视非共识机会和风险控制的框架。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    }
  ],
  "strongDetails": [
    {
      "name": "巴菲特 / Berkshire Hathaway",
      "strength": "高",
      "stance": "无新增可靠观点",
      "style": "价值投资/保险现金流/长期配置",
      "focus": "现金和短债、Apple、American Express、Bank of America、Coca-Cola、Chevron、Alphabet、Delta",
      "meaning": "偏防守；高估值阶段不要追涨。",
      "detail": "复核至2026/8/5：未发现巴菲特发布改变框架的新公开观点；继续把高现金、少数确定性资产和安全边际作为估值纪律校验，不把它当作短线交易信号。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "霍华德·马克斯 / Oaktree",
      "strength": "高",
      "stance": "无新增可靠观点",
      "style": "信用周期/风险控制/逆向投资",
      "focus": "Oaktree 信用资产、困境/高收益债",
      "meaning": "偏谨慎；检查AI与成长资产是否过热。",
      "detail": "复核至2026/8/5：Oaktree官网近期有内容更新迹象，但未确认出现改变投资框架的新Marks观点；继续用风险补偿、信用周期和过热资产纪律校验AI与成长交易。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "雷·达里奥 / Bridgewater",
      "strength": "中高",
      "stance": "无新增可靠观点",
      "style": "全球宏观/债务周期/风险平价",
      "focus": "黄金、全球分散配置、部分中国资产",
      "meaning": "偏防守与分散，关注债务和货币周期。",
      "detail": "复核至2026/8/5：未发现Dalio新增高可信公开观点改变配置框架；继续用债务周期、黄金、非美元资产和分散化原则校验宏观风险。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "比尔·阿克曼 / Pershing Square",
      "strength": "高",
      "stance": "无新增可靠观点",
      "style": "集中持仓/主动投资/优质公司",
      "focus": "Microsoft、平台科技、消费服务龙头",
      "meaning": "选择性偏多，但估值必须合理。",
      "detail": "复核至2026/8/5：未确认Ackman新增改变框架的公开观点；继续偏向少数高质量现金流龙头和可解释的资本配置，回避无法由现金流支撑的高估资产。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "大卫·泰珀 / Appaloosa",
      "strength": "中高",
      "stance": "无新增可靠观点",
      "style": "宏观交易/机会主义/风险资产节奏",
      "focus": "Amazon、Uber、Micron、TSMC、Sandisk",
      "meaning": "偏进攻，但只适合观察高弹性资产的交易节奏。",
      "detail": "复核至2026/8/5：未发现Tepper新增可靠公开观点；继续把他作为高弹性风险资产节奏参考，重点看AI硬件、平台消费和宏观风险偏好。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "克里斯·霍恩 / TCI",
      "strength": "高",
      "stance": "无新增可靠观点",
      "style": "长期集中持股/高壁垒公司/激进治理",
      "focus": "Alphabet、Visa、S&P Global、Moody's、GE Aerospace、Airbus、Safran",
      "meaning": "长期偏多高壁垒企业，不支持无差别追涨。",
      "detail": "复核至2026/8/5：未发现Hohn新增公开框架变化；继续沿用高壁垒平台、支付网络、评级和航空航天资产也必须服从估值纪律的结论。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    },
    {
      "name": "斯坦利·德鲁肯米勒 / Duquesne",
      "strength": "中高",
      "stance": "无新增可靠观点",
      "style": "顶级宏观交易/集中押注/风险控制",
      "focus": "Nuvation Bio、Caris Life Sciences、Olema Pharmaceuticals 等",
      "meaning": "长期认可AI，短期反对拥挤追高。",
      "detail": "复核至2026/8/5：未发现Druckenmiller新增高可信公开观点；继续沿用承认AI长期逻辑但不在短线拥挤时硬追、重视非共识机会和风险控制的框架。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    }
  ],
  "trackingDetails": [
    {
      "name": "凯瑟琳·伍德 / ARK",
      "strength": "中",
      "stance": "跟踪验证",
      "style": "颠覆式创新/高波动成长",
      "focus": "SpaceX、Tesla、ARKK/ARKQ/ARKX、私募创新敞口",
      "meaning": "作为高波动成长和创新资产情绪指标，不作组合模板。",
      "detail": "复核至2026/8/5：ARK属于高频交易动作源，6/16之后仍需持续跟踪其每日交易披露；当前不能写成“无更新”，应把ARK作为高波动成长和创新资产情绪指标，而不是组合模板。",
      "sourceStatus": "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
    }
  ],
  "verifiedNewDetails": []
} as const;

export const stocks = [
  {
    "code": "002837",
    "name": "英维克",
    "sector": "电力/数据中心能源",
    "signal": "yellow",
    "direction": "中性观察",
    "watch": "能否放量站回20日线并连续2日强于沪深300",
    "latestPrice": 52.33,
    "day": 5.87,
    "fiveDay": -0.11,
    "marketDate": "2026-08-05",
    "risk": "中"
  },
  {
    "code": "002555",
    "name": "三七互娱",
    "sector": "游戏传媒/AI应用",
    "signal": "green",
    "direction": "偏强",
    "watch": "游戏ETF与个股是否同步放量、连续强于沪深300",
    "latestPrice": 20.23,
    "day": 0.25,
    "fiveDay": 5.47,
    "marketDate": "2026-08-05",
    "risk": "低"
  }
] as const;

export const funds = [
  {
    "code": "012733",
    "name": "易方达中证人工智能主题ETF联接A",
    "sector": "AI/半导体",
    "day": 1.47,
    "week": 3.75,
    "risk": "高",
    "decision": "继续观察",
    "direction": "AI/半导体短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "100055",
    "name": "富国全球科技互联网股票(QDII)A",
    "sector": "全球科技互联网",
    "day": 1.96,
    "week": 6.8,
    "risk": "中高",
    "decision": "继续观察",
    "direction": "全球科技互联网短线修复，但仍需要验证趋势延续。 净值日期 2026-08-04，沿用最近可得数据（滞后2天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-04"
  },
  {
    "code": "006751",
    "name": "富国互联科技股票A",
    "sector": "AI/互联网",
    "day": 3.38,
    "week": 4.4,
    "risk": "中高",
    "decision": "继续观察",
    "direction": "AI/互联网短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "014344",
    "name": "鹏华中证500指数增强A",
    "sector": "A股宽基",
    "day": 2.69,
    "week": 4.14,
    "risk": "中",
    "decision": "继续观察",
    "direction": "A股宽基短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "007818",
    "name": "国泰中证全指通信设备ETF联接C",
    "sector": "通信/设备",
    "day": 0.75,
    "week": 6.31,
    "risk": "高",
    "decision": "继续观察",
    "direction": "通信/设备短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "013180",
    "name": "广发国证新能源车电池ETF联接C",
    "sector": "新能源车/电池",
    "day": 2.36,
    "week": 3.04,
    "risk": "中",
    "decision": "继续观察",
    "direction": "新能源车/电池短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "004432",
    "name": "南方有色金属ETF联接A",
    "sector": "有色金属",
    "day": 5.2,
    "week": 7.29,
    "risk": "中高",
    "decision": "观察等待",
    "direction": "有色金属短线涨幅较快，先看持续性和回撤，不追高。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "519704",
    "name": "交银先进制造混合A",
    "sector": "先进制造",
    "day": 1.29,
    "week": 1.67,
    "risk": "中",
    "decision": "继续观察",
    "direction": "先进制造短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "018125",
    "name": "永赢先进制造智选混合发起C",
    "sector": "先进制造",
    "day": 2.42,
    "week": 8.73,
    "risk": "高",
    "decision": "继续观察",
    "direction": "先进制造短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "011103",
    "name": "天弘中证光伏产业指数C",
    "sector": "光伏产业",
    "day": 1.58,
    "week": 4.74,
    "risk": "高",
    "decision": "继续观察",
    "direction": "光伏产业短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "025856",
    "name": "华夏中证电网设备主题ETF发起式联接A",
    "sector": "电网设备",
    "day": 2.19,
    "week": 4.82,
    "risk": "中高",
    "decision": "继续观察",
    "direction": "电网设备短线修复，但仍需要验证趋势延续。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  },
  {
    "code": "018896",
    "name": "易方达消费电子ETF联接A",
    "sector": "消费电子",
    "day": 4.53,
    "week": 2.74,
    "risk": "中高",
    "decision": "观察等待",
    "direction": "消费电子短线涨幅较快，先看持续性和回撤，不追高。 净值日期 2026-08-05，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-05"
  }
] as const;

