"""
@File: ProgramEnum.py
@author: guoweiliang
@date: 2021/11/10
"""
import enum
import operator
from types import DynamicClassAttribute


class ProgramEnum(enum.Enum):
    """
    存放项目与路径的对应关系
    """
    #  寿险铁炉堡
    IRON_FORGE = "ironforge"
    #  智慧驾驶
    WAKANDA = "wakanda"
    #  车主会商品相关
    INN = "inn"
    #  企团险相关
    NORTHEND = "northrend"
    #  寿险喂小保管理后台
    DALARAN = "dalaran"
    #  寿险客户相关
    CUSTOMER_CENTER_ORGRIMMAR = "customer"
    #  寿险小保贝
    SHATTRATH = "xbb"
    #  寿险网关
    GATEWAY_PROTAL = "gateway"
    #  寿险微信相关业务
    DUROTAR = "durotar"
    #  寿险质检相关业务
    MULGORE = "mulgore"
    #  todo
    BLACKSTONE = "blackstone"
    #  核心订单佣金计算
    STORM = "STORM"
    # 车主会订单相关
    MARSHAL_CANOPY = "marshal"

    @DynamicClassAttribute
    def name(self):
        replace = self._name_
        if operator.contains(self._name_, "_"):
            replace = self._name_.replace("_", "-")
        return replace

    @classmethod
    def get(cls, name):
        try:
            return ProgramEnum.__getitem__(name).value
        except KeyError:
            return None



if __name__ == '__main__':
    print(ProgramEnum.get("DALARAN"))
