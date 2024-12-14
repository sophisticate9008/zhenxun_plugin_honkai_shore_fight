from .role_base import RoleBase


class StatsResult:
    role1_name: str
    count_l: int
    role2_name: str
    count_r: int
    winner_idx: int
    txtss: list[list[str]]
    role1: RoleBase
    role2: RoleBase

    def __init__(
        self,
        role1_name: str,
        count_l: int,
        role2_name: str,
        count_r: int,
        winner_idx: int,
        txtss: list[list[str]],
        role1: "RoleBase",
        role2: "RoleBase",
    ):
        self.role1_name = role1_name
        self.count_l = count_l
        self.role2_name = role2_name
        self.count_r = count_r
        self.winner_idx = winner_idx
        self.txtss = txtss
        self.role1 = role1
        self.role2 = role2


# StatsResult 类型


class FightResult:
    txtss: list[list[str]]
    turn_count: int
    winner_name: str
    def __init__(self, txtss: list[list[str]], turn_count: int, winner_name: str):
        self.txtss = txtss  # 战斗过程记录
        self.turn_count = turn_count  # 回合数
        self.winner_name = winner_name
