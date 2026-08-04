// Generated from data/market-data.json. Do not edit by hand.
export const snapshot = {
  "businessDate": "2026-08-04",
  "generatedAt": "2026-08-04T14:49:40+08:00",
  "asOf": "2026/8/4 06:15 HKT",
  "marketGate": "风险偏高",
  "dataHealth": "绿灯",
  "coverage": 96,
  "riskScore": 71,
  "lightCounts": {
    "green": 6,
    "yellow": 6,
    "red": 0,
    "gray": 0
  },
  "daily": {
    "asOf": "2026/8/4 06:15 HKT",
    "signal": "黄灯",
    "action": "等待",
    "marketJudgement": "今天结论：黄灯偏防守，7/12只基金走弱，不是普通震荡；先控回撤，暂停加仓。",
    "positionAdvice": "仓位建议：高波动仓位先降速，AI/半导体、PCB、有色等只等放量修复，不补跌。",
    "needAction": "今日动作：1）停止追高和补跌；2）盯先进封装、AI芯片/半导体、存储/HBM能否放量收复；3）核对强弱分化：强项100055(全球科技互联网)日涨4.75%，弱项018896(消费电子)日跌3.71%。",
    "actionReason": "不操作原因：基金端普跌，估值分位、10年期美债收益...仍偏敏感，主线需成交和订单重新确认。",
    "riskPoint": "主要风险：科技链和高波动资产同步补跌；若成交不足，OLED、东方财富热股可能继续拖累组合。",
    "nextReview": "下次复盘：看先进封装、AI芯片/半导体、存储/HBM是否放量止跌，OLED、东方财富热股是否继续转弱。"
  },
  "freshness": [
    {
      "name": "风控",
      "date": "08.04",
      "width": 86
    },
    {
      "name": "赛道",
      "date": "08.04",
      "width": 100
    },
    {
      "name": "跨市场",
      "date": "08.04",
      "width": 100
    },
    {
      "name": "事件",
      "date": "08.04",
      "width": 100
    },
    {
      "name": "持仓",
      "date": "08.03",
      "width": 100
    }
  ],
  "moduleStatus": [
    {
      "code": "01",
      "name": "市场风控",
      "state": "风险偏高",
      "tone": "yellow",
      "desc": "6项预警"
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
      "desc": "1项新增"
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
    "4.75%（FRED，2026-07-31）",
    "yellow",
    "4.3% ~ 4.7%",
    "指标日期 2026-07-31，沿用最近可得数据（滞后4天）",
    "2026-07-31"
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
    "联邦基金有效利率3.63%（FRED，2026-07-31）",
    "green",
    "维持利率不变，释放降息预期",
    "指标日期 2026-07-31，沿用最近可得数据（滞后4天）",
    "2026-07-31"
  ],
  [
    "美元指数",
    "DXY约100.04（东方财富美元指数口径，2026年8月3日）",
    "green",
    "DXY < 103",
    "指标日期 2026-08-03，沿用最近可得数据（滞后1天）",
    "2026-08-03"
  ],
  [
    "实际利率",
    "10年期TIPS实际利率2.47%（FRED，2026-07-31）",
    "yellow",
    "10Y TIPS < 2.2%",
    "指标日期 2026-07-31，沿用最近可得数据（滞后4天）",
    "2026-07-31"
  ],
  [
    "信用利差",
    "美国高收益债OAS 2.84%（FRED，2026-07-30）",
    "green",
    "高收益OAS < 3.5%",
    "指标日期 2026-07-30，沿用最近可得数据（滞后5天）",
    "2026-07-30"
  ],
  [
    "VIX",
    "VIX 15.99（FRED，2026-07-31）",
    "green",
    "< 18",
    "指标日期 2026-07-31，沿用最近可得数据（滞后4天）",
    "2026-07-31"
  ],
  [
    "全球流动性",
    "美联储总资产6.738万亿美元，周变动-9.2亿美元（FRED，2026-07-29）",
    "yellow",
    "主要央行流动性企稳/扩张",
    "指标日期 2026-07-29，沿用最近可得数据（滞后6天）",
    "2026-07-29"
  ],
  [
    "A股成交额",
    "沪深两市成交约2.09万亿元（东方财富指数口径，2026年8月3日）",
    "green",
    ">1.0万亿",
    "指标日期 2026-08-03，沿用最近可得数据（滞后1天）",
    "2026-08-03"
  ],
  [
    "港股成交额",
    "恒生指数成分成交约2056亿港元（非港股全市场口径，2026年8月3日）",
    "yellow",
    ">1500亿港元",
    "指标日期 2026-08-03，沿用最近可得数据（滞后1天）",
    "2026-08-03"
  ],
  [
    "行业轮动强弱",
    "A股前3赛道：先进封装、AI芯片/半导体、存储/HBM；平均研究分94.0",
    "green",
    "主线清晰且扩散",
    "指标日期 2026-08-04，今日可用",
    "2026-08-04"
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
    "execute": "green",
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
    "execute": "green",
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
    "execute": "green",
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
    "execute": "green",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
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
    "execute": "yellow",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "OLED",
    "score": 64,
    "trend": 20,
    "flow": 20,
    "fundamental": 20,
    "hf": 0,
    "value": 4,
    "research": "yellow",
    "execute": "yellow",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "东方财富热股",
    "score": 64,
    "trend": 20,
    "flow": 20,
    "fundamental": 20,
    "hf": 0,
    "value": 4,
    "research": "yellow",
    "execute": "yellow",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "光纤概念",
    "score": 64,
    "trend": 20,
    "flow": 20,
    "fundamental": 20,
    "hf": 0,
    "value": 4,
    "research": "yellow",
    "execute": "yellow",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "玻璃基板",
    "score": 64,
    "trend": 20,
    "flow": 20,
    "fundamental": 20,
    "hf": 0,
    "value": 4,
    "research": "yellow",
    "execute": "yellow",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  },
  {
    "name": "科技风格",
    "score": 64,
    "trend": 20,
    "flow": 20,
    "fundamental": 20,
    "hf": 0,
    "value": 4,
    "research": "yellow",
    "execute": "yellow",
    "risk": "板块涨跌、上涨家数占比、主力净流入、成交活跃度、新闻催化",
    "operation": "继续观察",
    "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。"
  }
] as const;

export const events = [
  {
    "title": "中东与地缘风险仍在扰动市场，原油、黄金和风险偏好需要重点跟踪",
    "priority": 9,
    "direction": 1,
    "confidence": "中高",
    "source": "公开新闻聚合源",
    "date": "2026/8/3",
    "watch": "中东局势、原油运输、布伦特油价、黄金价格、美元指数和军工板块表现"
  },
  {
    "title": "美联储政策与利率预期再受关注，市场等待官员表态和收益率确认",
    "priority": 7,
    "direction": 0,
    "confidence": "中高",
    "source": "美国财经电视台",
    "date": "2026/8/4",
    "watch": "美联储官员讲话、10年期美债收益率、实际利率、美元指数、黄金和纳指表现"
  },
  {
    "title": "油价与能源供给变量继续影响通胀预期，资源品和风险偏好需同步观察",
    "priority": 6,
    "direction": 1,
    "confidence": "中高",
    "source": "公开新闻聚合源",
    "date": "2026/8/3",
    "watch": "布伦特油价、美国原油库存、产油国政策、通胀预期、航空和化工板块"
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
    "title": "人工智能和半导体仍是市场主线，但高估值与拥挤交易需要财报验证",
    "priority": 5,
    "direction": 1,
    "confidence": "中高",
    "source": "公开新闻聚合源",
    "date": "2026/8/3",
    "watch": "费半指数、英伟达链条、云厂资本开支、芯片订单、毛利率和成交额"
  },
  {
    "title": "贸易和关税变量继续影响制造业利润，订单、成本和供应链风险需跟踪",
    "priority": 5,
    "direction": 0,
    "confidence": "中高",
    "source": "美国财经电视台",
    "date": "2026/8/4",
    "watch": "关税政策、制造业订单、企业毛利率、出口数据、汽车和工业品板块"
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
  "newCount": 1,
  "strongCount": 7,
  "leading": [
    "巴菲特 / Berkshire Hathaway",
    "霍华德·马克斯 / Oaktree",
    "比尔·阿克曼 / Pershing Square"
  ],
  "note": "机构观点只作佐证，不能独立触发买入。"
} as const;

export const stocks = [
  {
    "code": "002837",
    "name": "英维克",
    "sector": "电力/数据中心能源",
    "signal": "red",
    "direction": "转弱",
    "watch": "能否放量站回20日线并连续2日强于沪深300",
    "latestPrice": 46.45,
    "day": -2.11,
    "fiveDay": -24.18,
    "marketDate": "2026-08-03",
    "risk": "高"
  },
  {
    "code": "002555",
    "name": "三七互娱",
    "sector": "游戏传媒/AI应用",
    "signal": "green",
    "direction": "偏强",
    "watch": "游戏ETF与个股是否同步放量、连续强于沪深300",
    "latestPrice": 19.99,
    "day": 0.4,
    "fiveDay": 8.29,
    "marketDate": "2026-08-03",
    "risk": "低"
  }
] as const;

export const funds = [
  {
    "code": "012733",
    "name": "易方达中证人工智能主题ETF联接A",
    "sector": "AI/半导体",
    "day": -2.3,
    "week": -9.85,
    "risk": "高",
    "decision": "暂不加仓",
    "direction": "AI/半导体短线承压明显，等待企稳和成交确认。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "100055",
    "name": "富国全球科技互联网股票(QDII)A",
    "sector": "全球科技互联网",
    "day": 4.75,
    "week": -0.21,
    "risk": "中高",
    "decision": "观察等待",
    "direction": "全球科技互联网短线涨幅较快，先看持续性和回撤，不追高。 净值日期 2026-07-31，沿用最近可得数据（滞后4天）；数据源：东方财富基金历史净值API。",
    "date": "2026-07-31"
  },
  {
    "code": "006751",
    "name": "富国互联科技股票A",
    "sector": "AI/互联网",
    "day": -3.2,
    "week": -17.15,
    "risk": "中高",
    "decision": "暂不加仓",
    "direction": "AI/互联网短线承压明显，等待企稳和成交确认。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "014344",
    "name": "鹏华中证500指数增强A",
    "sector": "A股宽基",
    "day": -0.79,
    "week": -3.22,
    "risk": "中",
    "decision": "观察等待",
    "direction": "A股宽基信号不够强，维持观察。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "007818",
    "name": "国泰中证全指通信设备ETF联接C",
    "sector": "通信/设备",
    "day": 0.33,
    "week": -11.51,
    "risk": "高",
    "decision": "暂不加仓",
    "direction": "通信/设备短线承压明显，等待企稳和成交确认。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "013180",
    "name": "广发国证新能源车电池ETF联接C",
    "sector": "新能源车/电池",
    "day": -0.51,
    "week": -0.98,
    "risk": "中",
    "decision": "观察等待",
    "direction": "新能源车/电池信号不够强，维持观察。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "004432",
    "name": "南方有色金属ETF联接A",
    "sector": "有色金属",
    "day": -0.62,
    "week": 0.27,
    "risk": "中高",
    "decision": "观察等待",
    "direction": "有色金属信号不够强，维持观察。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "519704",
    "name": "交银先进制造混合A",
    "sector": "先进制造",
    "day": -1.17,
    "week": -4.81,
    "risk": "中",
    "decision": "观察等待",
    "direction": "先进制造信号不够强，维持观察。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "018125",
    "name": "永赢先进制造智选混合发起C",
    "sector": "先进制造",
    "day": 1.47,
    "week": 0.26,
    "risk": "高",
    "decision": "继续观察",
    "direction": "先进制造短线修复，但仍需要验证趋势延续。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "011103",
    "name": "天弘中证光伏产业指数C",
    "sector": "光伏产业",
    "day": 1.7,
    "week": -0.25,
    "risk": "高",
    "decision": "观察等待",
    "direction": "光伏产业信号不够强，维持观察。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "025856",
    "name": "华夏中证电网设备主题ETF发起式联接A",
    "sector": "电网设备",
    "day": 1.57,
    "week": -2.03,
    "risk": "中高",
    "decision": "观察等待",
    "direction": "电网设备信号不够强，维持观察。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  },
  {
    "code": "018896",
    "name": "易方达消费电子ETF联接A",
    "sector": "消费电子",
    "day": -3.71,
    "week": -13.25,
    "risk": "中高",
    "decision": "暂不加仓",
    "direction": "消费电子短线承压明显，等待企稳和成交确认。 净值日期 2026-08-03，沿用最近可得数据（滞后1天）；数据源：东方财富基金历史净值API。",
    "date": "2026-08-03"
  }
] as const;

