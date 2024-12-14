import random
from pathlib import Path

from nonebot.adapters import Bot
from nonebot.typing import T_State
from nonebot_plugin_uninfo import Uninfo
from nonebot.plugin import PluginMetadata
from nonebot_plugin_session import EventSession
from nonebot_plugin_alconna import (
    Args,
    CustomNode,
    Match,
    Alconna,
    Reference,
    UniMessage,
    on_alconna,
)

from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils
from zhenxun.models.user_console import UserConsole
from zhenxun.configs.config import Config, BotConfig
from zhenxun.utils.enum import GoldHandle, PluginType
from zhenxun.utils.withdraw_manage import WithdrawManager
from zhenxun.configs.utils import RegisterConfig, PluginExtraData

from .fight.fight_frame import stats
from .fight.pic_make import image_add_text

__plugin_meta__ = PluginMetadata(
    name="海滨的灼热乱斗",
    description="崩坏三曾经的网页赛制押注活动,插件以文字方式展示战斗过程并可以押注金币(仅限qq平台)",
    usage="""
    海滨乱斗(?静默)
    """,
    extra=PluginExtraData(
        author="sophisticate9008",
        version="0.1",
        menu_type="群内小游戏",
        plugin_type=PluginType.NORMAL,
        configs=[
            RegisterConfig(
                key="WITHDRAW_SHORE_FIGHT",
                value=(100, 1),
                help="自动撤回，参1：延迟撤回时间(秒)，0 为关闭 | 参2：监控聊天类型，0(私聊) 1(群聊) 2(群聊+私聊)",  # noqa: E501
                default_value=(100, 1),
                type=tuple[int, int],
            ),
        ],
    ).dict(),
)

fight_num = 500
resource_path = Path(__file__).parent / "resource"
plugin_config = Config.get("zhenxun_plugin_honkai_shore_fight")
shore_fight_matcher = on_alconna(
    Alconna(
        "海滨乱斗",
        Args["silence?", str]["idx_and_money?", str],
    ),
    priority=5,
    block=True,
)

shore_fight_matcher.shortcut(
    r"^海滨乱斗(?P<silence>.*)",
    command="海滨乱斗",
    arguments=["{silence}"],
)


@shore_fight_matcher.handle()
async def _(silence: Match[str], state: T_State):
    if silence.available:
        logger.info("海滨乱斗静默模式")
        state["silence"] = silence.result
        shore_fight_matcher.set_path_arg("silence", silence.result)
    rands1, rands2 = random.sample(range(12), 2)
    state["roles_idx"] = (rands1, rands2)
    stats_result = stats(rands1, rands2, False, fight_num)
    if stats_result.count_l < fight_num / 100:
        beilv_l = 100.0
    else:
        beilv_l = fight_num / (stats_result.count_l + 1)

    if stats_result.count_r < fight_num / 100:
        beilv_r = 100.0
    else:
        beilv_r = fight_num / (stats_result.count_r + 1)
    state["beilvs"] = (beilv_l, beilv_r)
    text = f"""    随机到的两名英桀是
    {stats_result.role1_name}  {stats_result.role2_name}
    胜率分别为{1 / beilv_l:.2f}  {1 / beilv_r:.2f}
    乘数分别为{beilv_l:.2f}  {beilv_r:.2f}
    发送目标和金币数量
    eg. 0 100 """
    await MessageUtils.build_message(text).send(reply_to=True)


@shore_fight_matcher.got_path("idx_and_money")
async def _(
    idx_and_money: str,
    bot: Bot,
    session: EventSession,
    uninfo_session: Uninfo,
    state: T_State,
):
    user_id = str(session.id1)
    logger.info(idx_and_money)
    args = idx_and_money.split()
    if (
        len(args) == 2
        and args[0].isdigit()
        and args[1].isdigit()
        and int(args[0]) in {0, 1}
        and int(args[1]) > 0
    ):
        idx = int(args[0])
        money = int(args[1])
        shore_fight_matcher.set_path_arg("idx_and_money", idx_and_money)
        if money > (await UserConsole.get_user(user_id)).gold:
            await MessageUtils.build_message("金币不足").finish(reply_to=True)
        roles_idx = state["roles_idx"]
        stats_result = stats(roles_idx[0], roles_idx[1], True, 1)
        if not state.get("silence"):
            msg_list = [
                resource_path / f"{roles_idx[0]}.jpg",
                resource_path / f"{roles_idx[1]}.jpg",
            ]

            msg_list.extend(image_add_text(txts) for txts in stats_result.txtss)  # type: ignore
            unimessage_list = [MessageUtils.build_message(msg) for msg in msg_list]
            node_list = [
                CustomNode(
                    uid=uninfo_session.self_id,
                    name=BotConfig.self_nickname,
                    content=unimessage,
                )
                for unimessage in unimessage_list
            ]
            alc_forward_msg = UniMessage(Reference(nodes=node_list))
            receipt = await alc_forward_msg.send()
            if receipt:
                state["message_id"] = receipt.msg_ids[0]["message_id"]
        await UserConsole.reduce_gold(
            user_id, money, GoldHandle.PLUGIN, "zhenxun_plugin_honkai_shore_fight"
        )
        money_add = 0
        if stats_result.winner_idx == idx:
            money_add = int(money * state["beilvs"][idx])
            await UserConsole.add_gold(
                user_id,
                money_add,
                GoldHandle.PLUGIN,
                "zhenxun_plugin_honkai_shore_fight",
            )
            result_text = f"你支持的英桀获胜, 你获得 {money_add} 金币"
        else:
            result_text = "你支持的英桀惜败, 你一无所获"

        # 统一获取当前金币数
        money_have = (await UserConsole.get_user(user_id)).gold
        text = f"{result_text}, 当前金币为 {money_have}"
        await MessageUtils.build_message(text).send(reply_to=True)
        # 构造并发送消息
        if message_id := state.get("message_id"):
            await WithdrawManager.withdraw_message(
                bot,
                message_id,
                plugin_config.get("WITHDRAW_SHORE_FIGHT"),
                session,
            )
    else:
        await shore_fight_matcher.reject_path("idx_and_money", "仔细检查参数")
