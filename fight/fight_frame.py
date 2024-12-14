from .role_base import RoleBase
from .types import FightResult, StatsResult
from .roles import (
    Hua,
    Elysia,
    KaiWen,
    KeSiMo,
    Sakura,
    YiDian,
    ABoNiYa,
    QianJie,
    GeLeiXiu,
    WeiErWei,
    MeiBiWuSi,
    PaDuoFeiLiSi,
)


def stats(
    left: int, right: int, is_display: bool, n: int
) -> StatsResult:
    count_l = 0
    count_r = 0
    role1 = get_role(left)
    role2 = get_role(right)
    result: FightResult
    for _ in range(n):
        result = fight(left, right, is_display)
        if role1.name == result.winner_name:
            count_l += 1
        else:
            count_r += 1
    winner_idx = 0 if result.winner_name == role1.name else 1 # type: ignore

    return StatsResult(
        role1_name=role1.name,
        count_l=count_l,
        role2_name=role2.name,
        count_r=count_r,
        winner_idx=winner_idx,
        txtss=result.txtss, # type: ignore
        role1=role1,
        role2=role2,
    )


def fight(left: int, right: int, is_display: bool) -> FightResult:
    result:dict[str, str] = {}
    txtss: list[list[str]] = []
    role1 = get_role(left)
    role2 = get_role(right)
    role1.enemy = role2
    role2.enemy = role1
    role1.init()
    role2.init()
    role1.is_display = is_display
    role2.is_display = is_display
    #传入同一个结果记录字典
    role1.result = result
    role2.result = result
    roles: list[RoleBase] = [role1, role2]
    count_turn = 0

    while role1.blood > 0 and role2.blood > 0:
        count_turn += 1
        txts: list[str] = []
        txts.append(f"第{count_turn}回合")
        if role1.speed >= role2.speed:
            roles[0], roles[1] = role1, role2
        else:
            roles[0], roles[1] = role2, role1

        for role in roles:
            role.turn_init()
            #传入同一个文本记录列表
            role.txts = txts

        for role in roles:
            if role.blood > 0:
                role.turn_begin()
        if is_display:
            txtss.append(txts)
    return FightResult(txtss, count_turn, result["winner_name"])


def get_role(id: int) -> RoleBase:
    if id == 0:
        return KaiWen(id, "凯文", 21, 20, 11, 3, 0.3, 1)
    elif id == 1:
        return Elysia(id, "爱莉希雅", 20, 21, 8, 2, 0.35, 1)
    elif id == 2:
        return GeLeiXiu(id, "格蕾修", 18, 16, 11, 3, 0.4, 1)
    elif id == 3:
        return Sakura(id, "樱", 27, 24, 10, 2, 0.15, 0)
    elif id == 4:
        return ABoNiYa(id, "阿布尼亚", 30, 21, 10, 4, 0.3, 1)
    elif id == 5:
        return Hua(id, "华", 15, 21, 12, 2, 1, 0)
    elif id == 6:
        return WeiErWei(id, "维尔薇", 25, 20, 12, 3, 1, 0)
    elif id == 7:
        return KeSiMo(id, "科斯魔", 19, 19, 11, 2, 0.15, 1)
    elif id == 8:
        return MeiBiWuSi(id, "梅比乌斯", 23, 21, 11, 3, 0.33, 1)
    elif id == 9:
        return QianJie(id, "千劫", 26, 23, 9, 3, 1, -1)
    elif id == 10:
        return PaDuoFeiLiSi(id, "帕朵菲利斯", 24, 17, 10, 3, 0.3, 1)
    elif id == 11:
        return YiDian(id, "伊甸", 16, 16, 12, 2, 0.5, 1)
    return RoleBase(id, "未知", 0, 0, 0, 0, 0, 0)


# if __name__ == "__main__":
#     # for i in range(1, 12):
#     #     for j in range(1, 12):
#     #         if i != j:
#     #             stats(i,j,0,1,[])
#     #             pass

#     fight(1, 3, 1)
