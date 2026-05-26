"""行程规划工具 - 为旅行目的地生成详细的行程安排"""


def plan_itinerary(destination: str, days: int) -> dict:
    """
    为指定目的地生成旅行行程规划
    
    Args:
        destination: 旅行目的地名称
        days: 旅行天数
        
    Returns:
        包含行程安排、美食推荐和旅行小贴士的字典
    """
    # 参数验证
    if not destination or not isinstance(destination, str):
        return {"error": "请输入有效的目的地名称"}
    if not isinstance(days, int) or days <= 0 or days > 30:
        return {"error": "旅行天数应为1-30之间的整数"}
    
    # 热门目的地行程模板
    itineraries = {
        "三亚": {
            "description": "中国著名的热带海滨度假胜地",
            "best_season": "10月至次年4月",
            "budget": "约3000-8000元/人（含住宿餐饮）",
            "days": {
                1: {
                    "morning": "抵达三亚，入住酒店，亚龙湾沙滩漫步",
                    "afternoon": "亚龙湾热带天堂森林公园游览",
                    "evening": "第一市场品尝海鲜大餐",
                    "food": "清蒸石斑鱼、椰子饭、海南鸡饭"
                },
                2: {
                    "morning": "蜈支洲岛潜水或浮潜体验",
                    "afternoon": "蜈支洲岛环岛游，观海景",
                    "evening": "三亚湾看日落，椰梦长廊散步",
                    "food": "抱罗粉、文昌鸡、椰子冻"
                },
                3: {
                    "morning": "南山文化旅游区，参观108米观音像",
                    "afternoon": "天涯海角景区游览",
                    "evening": "三亚千古情景区演出",
                    "food": "加积鸭、东山羊、和乐蟹"
                },
                4: {
                    "morning": "呀诺达雨林探险",
                    "afternoon": "槟榔谷黎苗文化体验",
                    "evening": "大东海酒吧街休闲",
                    "food": "海南粉、清补凉、椰子鸡火锅"
                },
                5: {
                    "morning": "亚特兰蒂斯水世界畅玩",
                    "afternoon": "海棠湾免税店购物",
                    "evening": "返程",
                    "food": "后安粉、陵水酸粉、芒果肠粉"
                }
            },
            "tips": [
                "防晒霜SPF50+必备，三亚紫外线强烈",
                "第一市场买海鲜可找加工店代加工，性价比更高",
                "旺季酒店需提前预订",
                "蜈支洲岛建议提前一天购买船票"
            ]
        },
        "北京": {
            "description": "中国首都，历史文化名城",
            "best_season": "9月至11月（秋高气爽）",
            "budget": "约2500-6000元/人（含住宿餐饮）",
            "days": {
                1: {
                    "morning": "天安门广场观升旗仪式，故宫博物院游览",
                    "afternoon": "景山公园俯瞰故宫全景",
                    "evening": "南锣鼓巷逛街，品尝小吃",
                    "food": "北京烤鸭、炸酱面、豆汁焦圈"
                },
                2: {
                    "morning": "八达岭长城登城",
                    "afternoon": "长城周边游览",
                    "evening": "簋街夜市吃小龙虾",
                    "food": "涮羊肉、卤煮火烧、炒肝"
                },
                3: {
                    "morning": "颐和园游览",
                    "afternoon": "圆明园遗址公园",
                    "evening": "三里屯太古里逛街",
                    "food": "铜锅涮肉、爆肚、门钉肉饼"
                },
                4: {
                    "morning": "天坛公园祈年殿",
                    "afternoon": "前门大街、大栅栏",
                    "evening": "国家大剧院看演出",
                    "food": "老北京炸酱面、驴打滚、艾窝窝"
                },
                5: {
                    "morning": "798艺术区参观",
                    "afternoon": "鸟巢、水立方外景",
                    "evening": "王府井大街购物，返程",
                    "food": "烤肉季、奶酪魏、糖葫芦"
                }
            },
            "tips": [
                "故宫需提前在网上预约门票",
                "长城建议早上出发，避开人流高峰",
                "地铁出行最方便，办理一卡通",
                "秋季是最佳旅游季节，香山红叶很美"
            ]
        },
        "上海": {
            "description": "国际化大都市，东方明珠",
            "best_season": "3月至5月、9月至11月",
            "budget": "约3000-7000元/人（含住宿餐饮）",
            "days": {
                1: {
                    "morning": "外滩万国建筑博览群，黄浦江游船",
                    "afternoon": "南京路步行街购物",
                    "evening": "陆家嘴东方明珠塔夜景",
                    "food": "生煎包、小笼包、蟹壳黄"
                },
                2: {
                    "morning": "豫园、城隍庙游览",
                    "afternoon": "田子坊创意街区",
                    "evening": "新天地酒吧街",
                    "food": "南翔小笼、排骨年糕、白斩鸡"
                },
                3: {
                    "morning": "迪士尼乐园全天游玩",
                    "afternoon": "迪士尼乐园（续）",
                    "evening": "迪士尼烟花表演",
                    "food": "园区内主题餐厅"
                },
                4: {
                    "morning": "武康路、安福路文艺漫步",
                    "afternoon": "上海博物馆",
                    "evening": "黄浦江夜游",
                    "food": "本帮红烧肉、油爆虾、葱油拌面"
                },
                5: {
                    "morning": "朱家角古镇水乡游",
                    "afternoon": "静安寺、愚园路",
                    "evening": "返程",
                    "food": "大闸蟹（秋季）、腌笃鲜、八宝辣酱"
                }
            },
            "tips": [
                "迪士尼乐园工作日人少，体验更好",
                "外滩夜景比白天更值得看",
                "上海地铁线路密集，出行首选",
                "秋季是大闸蟹最佳品尝季节"
            ]
        },
        "成都": {
            "description": "天府之国，美食之都，大熊猫故乡",
            "best_season": "3月至6月、9月至11月",
            "budget": "约2000-5000元/人（含住宿餐饮）",
            "days": {
                1: {
                    "morning": "大熊猫繁育研究基地看熊猫",
                    "afternoon": "武侯祠、锦里古街",
                    "evening": "锦里夜市小吃",
                    "food": "火锅、串串香、担担面"
                },
                2: {
                    "morning": "都江堰水利工程",
                    "afternoon": "青城山前山游览",
                    "evening": "返回成都，春熙路逛街",
                    "food": "麻婆豆腐、夫妻肺片、龙抄手"
                },
                3: {
                    "morning": "杜甫草堂",
                    "afternoon": "宽窄巷子闲逛",
                    "evening": "人民公园喝茶，体验成都慢生活",
                    "food": "钟水饺、赖汤圆、甜水面"
                },
                4: {
                    "morning": "金沙遗址博物馆",
                    "afternoon": "太古里、IFS购物",
                    "evening": "九眼桥酒吧街",
                    "food": "兔头、钵钵鸡、蛋烘糕"
                },
                5: {
                    "morning": "峨眉山一日游（可选乐山大佛）",
                    "afternoon": "峨眉山（续）",
                    "evening": "返程",
                    "food": "跷脚牛肉、叶儿粑、冰粉"
                }
            },
            "tips": [
                "看熊猫建议早上8点前到达，上午最活跃",
                "火锅建议微辣起步，成都辣度不容小觑",
                "人民公园鹤鸣茶社是体验成都茶文化的好去处",
                "成都美食集中在玉林路、建设路一带"
            ]
        },
        "西安": {
            "description": "十三朝古都，丝绸之路起点",
            "best_season": "3月至5月、9月至11月",
            "budget": "约2000-5000元/人（含住宿餐饮）",
            "days": {
                1: {
                    "morning": "秦始皇兵马俑博物馆",
                    "afternoon": "华清宫",
                    "evening": "回民街美食之旅",
                    "food": "肉夹馍、羊肉泡馍、凉皮"
                },
                2: {
                    "morning": "西安古城墙骑行",
                    "afternoon": "碑林博物馆",
                    "evening": "永宁门城墙灯光秀",
                    "food": "biangbiang面、灌汤包、甑糕"
                },
                3: {
                    "morning": "陕西历史博物馆",
                    "afternoon": "大雁塔、大唐不夜城",
                    "evening": "大唐不夜城夜景",
                    "food": "水盆羊肉、葫芦鸡、镜糕"
                },
                4: {
                    "morning": "华山一日游（西峰索道上）",
                    "afternoon": "华山长空栈道、东峰",
                    "evening": "返回西安",
                    "food": "华阴老腔表演配当地小吃"
                },
                5: {
                    "morning": "钟鼓楼广场",
                    "afternoon": "书院门古文化街",
                    "evening": "返程",
                    "food": "贾三灌汤包、胡辣汤、油泼面"
                }
            },
            "tips": [
                "兵马俑建议请导游讲解，否则只是看泥人",
                "陕西历史博物馆免费但需提前预约",
                "华山体力要求高，量力而行",
                "回民街适合逛，但正宗美食在洒金桥"
            ]
        },
        "张家界": {
            "description": "世界自然遗产，阿凡达取景地",
            "best_season": "4月至6月、9月至11月",
            "budget": "约2500-5000元/人（含住宿餐饮）",
            "days": {
                1: {
                    "morning": "张家界国家森林公园，金鞭溪",
                    "afternoon": "袁家界，哈利路亚山（乾坤柱）",
                    "evening": "入住武陵源",
                    "food": "土家三下锅、酸鱼肉、葛根粉"
                },
                2: {
                    "morning": "天子山日出，贺龙公园",
                    "afternoon": "十里画廊小火车",
                    "evening": "溪布街休闲",
                    "food": "腊肉、血豆腐、土家糍粑"
                },
                3: {
                    "morning": "天门山玻璃栈道",
                    "afternoon": "天门洞999级台阶",
                    "evening": "天门山索道下山",
                    "food": "岩耳炖鸡、枞菌炖肉"
                },
                4: {
                    "morning": "大峡谷玻璃桥",
                    "afternoon": "黄龙洞",
                    "evening": "宝峰湖",
                    "food": "土家合渣、社饭"
                },
                5: {
                    "morning": "芙蓉镇（挂在瀑布上的古镇）",
                    "afternoon": "凤凰古城半日游",
                    "evening": "返程",
                    "food": "米豆腐、酸萝卜、苗家酸汤鱼"
                }
            },
            "tips": [
                "山上天气多变，雨具必备",
                "玻璃栈道需要穿鞋套，现场购买",
                "旺季索道排队可能超过2小时",
                "建议请当地向导，景区较大容易迷路"
            ]
        },
        "凤凰古城": {
            "description": "沈从文笔下的边城，湘西明珠",
            "best_season": "3月至11月",
            "budget": "约1500-3500元/人（含住宿餐饮）",
            "days": {
                1: {
                    "morning": "抵达凤凰，入住沱江边客栈",
                    "afternoon": "沱江泛舟，虹桥风雨楼",
                    "evening": "沱江边放河灯，酒吧街",
                    "food": "血粑鸭、苗家酸汤鱼、社饭"
                },
                2: {
                    "morning": "沈从文故居、熊希龄故居",
                    "afternoon": "东门城楼、古城墙漫步",
                    "evening": "沱江边篝火晚会（周末）",
                    "food": "米豆腐、酸萝卜、罐罐菌"
                },
                3: {
                    "morning": "奇梁洞溶洞探险",
                    "afternoon": "山江苗寨体验苗族文化",
                    "evening": "古城夜景，吊脚楼灯火",
                    "food": "腊肉炒蕨菜、糯米酸辣子、凤凰姜糖"
                }
            },
            "tips": [
                "沱江边住宿体验最好，但旺季需提前预订",
                "古城不收门票，但部分景点需要",
                "苗寨银饰购买需谨慎，辨别真假",
                "清晨的凤凰最安静最美，建议早起"
            ]
        }
    }
    
    # 查找目的地
    destination_lower = destination.strip()
    if destination_lower in itineraries:
        dest_info = itineraries[destination_lower]
    else:
        # 为未知目的地生成通用行程模板
        dest_info = _generate_generic_itinerary(destination_lower)
    
    # 构建指定天数的行程
    available_days = dest_info.get("days", {})
    itinerary_list = []
    
    for day in range(1, days + 1):
        if day in available_days:
            day_plan = available_days[day]
        else:
            # 循环使用已有天数的行程
            cycle_day = ((day - 1) % len(available_days)) + 1 if available_days else day
            day_plan = available_days.get(cycle_day, {
                "morning": f"探索{destination}的当地景点",
                "afternoon": f"体验{destination}的文化特色",
                "evening": f"品尝{destination}当地美食",
                "food": "当地特色菜肴"
            })
        
        itinerary_list.append({
            "day": day,
            "morning": day_plan.get("morning", "自由活动"),
            "afternoon": day_plan.get("afternoon", "自由活动"),
            "evening": day_plan.get("evening", "自由活动"),
            "food": day_plan.get("food", "当地特色美食")
        })
    
    return {
        "destination": destination,
        "days": days,
        "description": dest_info.get("description", f"{destination}之旅"),
        "best_season": dest_info.get("best_season", "四季皆宜"),
        "budget": dest_info.get("budget", "根据个人消费水平而定"),
        "itinerary": itinerary_list,
        "tips": dest_info.get("tips", [
            "提前预订机票和酒店可节省费用",
            "了解当地天气，准备合适衣物",
            "尊重当地风俗习惯",
            "保管好个人财物"
        ])
    }


def _generate_generic_itinerary(destination: str) -> dict:
    """
    为未知目的地生成通用行程模板
    
    Args:
        destination: 目的地名称
        
    Returns:
        通用行程模板字典
    """
    return {
        "description": f"{destination}之旅",
        "best_season": "春季或秋季",
        "budget": "约2000-5000元/人（根据消费水平）",
        "days": {
            1: {
                "morning": f"抵达{destination}，入住酒店，周边闲逛熟悉环境",
                "afternoon": f"参观{destination}标志性景点",
                "evening": f"品尝{destination}当地特色美食",
                "food": "当地特色菜肴"
            },
            2: {
                "morning": f"深入了解{destination}的历史文化景点",
                "afternoon": f"体验{destination}的自然风光",
                "evening": f"逛{destination}的夜市或商业街",
                "food": "当地小吃和特色美食"
            },
            3: {
                "morning": f"探索{destination}的周边景点",
                "afternoon": "购买伴手礼和纪念品",
                "evening": "整理行李，准备返程",
                "food": "当地特色餐厅用餐"
            }
        },
        "tips": [
            "提前了解当地天气，准备合适衣物",
            "预订酒店时考虑交通便利性",
            "尊重当地风俗习惯",
            "保管好个人财物和证件"
        ]
    }


# 工具描述信息（用于Agent工具调用）
TOOL_DESCRIPTION = {
    "name": "plan_itinerary",
    "description": "为旅行目的地生成详细的行程规划，包括每日活动安排、美食推荐和旅行小贴士",
    "parameters": {
        "type": "object",
        "properties": {
            "destination": {
                "type": "string",
                "description": "旅行目的地，如：三亚、北京、上海、成都、西安"
            },
            "days": {
                "type": "integer",
                "description": "旅行天数，如：3、5、7"
            }
        },
        "required": ["destination", "days"]
    }
}
