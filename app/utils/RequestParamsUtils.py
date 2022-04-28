"""
@File:RequestParamsUtils.py
@author:yangwuxie
@date: 2020/12/30
"""
import json
import re

from app.models import Interface

"""
处理入库的interface对象参数，headers转成dict对象
type为blob类型的数据取出来之后为str类型的数据，需要处理成dict数据，方便后续请求
"""


class ParamsMatcher:
    """
    将字符串中的元素按照指定的分隔符准确地分离.

    示例:
        按逗号分隔
        输入: '"A, B", C(D(E))'
        输出: ['"A, B"', 'C(D(E))']

    原理:
        基本方案是遍历字符串中的每一个字符, 当遇到配对符号时, 就完成配对 (当然要处理假配对的干扰情况). 最终将配好的
        元素加入到列表中返回.
        假设字符串中每一个 "参数" 均是由逗号分隔, 则在遍历字符的过程中, 我们可以设逗号为截停点. 每当遇到截停点时, 就
        观察之前的字符串是否可以形成一个独立的元素了.
        如果可以, 就 "提交" 字符串给收集器, 这样一个元素就被抽取出来了.
        观察的方法也很简单, 就是看最后一个配对符号和最初一个配对符号是否能配对.
        基本的方法知道后, 接下来主要是将一些细节的情况处理掉, 因为涉及到很多特殊情况, 所以会遇到很多坑. 我会尽可能详
        细的说明.
    流程:
        match(phrase) --> reset() --> sanitize() --> (循环处理) update(), checkpoint(), submit() -->
        return self.result

    """

    def __init__(self, pause=','):
        # 截停标记
        self.pause = pause  # 停顿标记, 每一个停顿标记, 就相当于一个检查点. 每遇到停顿标记, 就执行检查点事件
        """
        截停标记默认使用的是逗号. 用来分隔字符串内的参数.
        在遍历字符的过程中, 每当遇到截停标记, 都会触发 self.checkpoint() 来观察是否可结成对.
        详见 self.checkpoint() 方法.
        """

        # 配对符号 (元组). 相关函数: self.match() (只有一处被用到)
        self.parenthesis = ("'", '"', '(', ')', '[', ']', '{', '}')
        # 配对符号 (字典). 相关函数: self.checkpoint().make_pair() (只有一处被用到)
        self.pairs = {"'": "'", '"': '"', '(': ')', '[': ']', '{': '}'}
        # 引号
        self.quotes = ("'", '"')

        # 配对符号记录器
        self.parenthesis_track = []  # 配对符号记录, 记录格式的为 `(index, char)`
        """
        每当遇到任一配对符号 (指 配对符号 (元组) 中的任一个) 时, 记录器就会记录下它们的位置和符号值.
        记录格式为:
            self.parenthesis_track = [({index}, {char}), ...]
        示例:
            假设有文本 '(A, B), "C[D]"', 则有:
            self.parenthesis_track = [
                (0, '('), (5, ')'), (8, '"'), (10, '['), (12, ']'), (13, '"')
            ]
        """

        # 特殊标志
        self.uniq_mark = '◆'
        """
        特殊标志主要用于解决以下情况:
            1. 对原字符串中的转义字符进行替换
            2. 对 'ABC'.format(), 'ABC'.zfill(), 'ABC'[2:3] 这些情况进行预替换处理
        具体的将在 self.sanitize() 中说明.
        """

        # 截停位置记录器
        self.pause_track = -1  # 停顿处光标记录 (记录的是上一次的光标位置)
        """
        每当遇到一个截停标志时, 就会观察是否可对前面的字符结对提交.
        当提交成功后, 这个截停标志所在的位置就会被记录到 self.pause_track.
        不同于 self.parenthesis_track, self.pause_track 每次记录的新位置会覆盖旧位置.
        也就是说 self.pause_track 只记录最新一次的截停位置.

        关于它的具体的作用, 详见 self.match()
        """

        # 收集到的结果
        self.result = []
        """
        对收集到的结果, 加入到 self.result 列表中. 每一个元素均为一个独立的 "参数".
        相关函数: self.submit()
        """

        # 拖尾控制
        self.trailing = False  # 卷动控制. 用来控制提交方式
        """
        用于控制提交的方式.
        该变量把 'ABC'.format(), 'ABC'.zfill(), 'ABC'[2:3] 中的 `.format()`, `.zfill()`, `[2:3]` 形象
        地看作 "尾巴", 因此在提交 "尾巴" 的时候, 用的不是
            self.result.append(word)
        而是
            self.result[-1] += word
        self.trailing 就是控制这两种提交方式的识别与切换的控制类变量.
        """

    def sanitize(self, phrase: str):
        """
        简化字符串内容.

        :param phrase:
        :return:
        """
        # 消除编码符
        if phrase[0] in ('f', 'b', 'r') and phrase[1] in self.quotes:
            phrase = phrase[1:]  # `f"A"` --> `"A"`

        # 为了让最后一个字符也能被结算, 因此在末尾增加一个截停标志
        safety_pad = self.pause + ' '
        phrase = phrase.strip(safety_pad) + safety_pad
        # 示例1: `A, B` --> `A, B`  --> `A, B, `
        # 示例2: `A, B   ` --> `A, B` --> `A, B, `
        # 示例3: `A, B  ,, ` --> `A, B` --> `A, B, `
        """
        注意末尾加的是 ", " 而不是 ",".
        空格的作用是做一个缓冲.
        在 self.match() 中, 有一个步骤是每次遇到截停点, 都会检查它的前一个符号和后一个符号.
        比如设原始字符串为 'A, B', 当末尾加上 ", " 变成 "A, B, " 后, 在最后一次检查逗号时, 会看前一个字符
        (B) 和后一个字符 (空格). 如果没有这个空格, 就会导致 IndexError.
        所以这个空格是有意义的, 不要省略.
        """

        # 解决转义字符的大麻烦
        if '\\"' in phrase:
            phrase = phrase.replace('\\"', self.uniq_mark)  # `"A\"B"` --> `"A◆B"`
        if "\\'" in phrase:
            phrase = phrase.replace("\\'", self.uniq_mark)  # `'A\'B'` --> `'A◆B'`

        # 解决字符串后缀函数的问题, 例如 zfill() 函数, format() 函数等
        p1 = re.compile(r'(?<=["\'])\.(?=[a-z]+\()')
        p2 = re.compile(r'(?<=["\'])\[(?=[0-9a-zA-Z]+:[0-9a-zA-Z]+)')
        phrase = re.sub(p1, self.pause + self.uniq_mark + '.', phrase)
        # 示例: `"A = {}".format(B)` --> `"A = {}",◆.format(B)`
        phrase = re.sub(p2, self.pause + self.uniq_mark + '[', phrase)
        # 示例: `"ABC"[0:b]` --> `"ABC",◆[0:b]`

        return phrase

    def reset(self):
        """
        重置.
        """
        self.result.clear()  # 将上次任务可能遗留的收集记录清空
        self.pause_track = -1  # 将截停标志位置重置到-1处
        self.trailing = False  # 将拖尾控制器初始化为 False

    def match(self, phrase: str) -> list:
        """
        用户传入原始字符串, 将其按照截停点切分后以列表形式返回.

        示例:
            按逗号分隔
            输入: '"A, B", C(D(E))'
            输出: ['"A, B"', 'C(D(E))']

        流程:
            match(phrase)
            --> reset() 将历史痕迹清空, 进入初始化状态
            --> sanitize() 将原始字符串中的干扰性强的符号进行替换和变形, 以利于接下来的工作
            --> (循环处理) for index, char in enumerate(phrase)
                update() 每当遇到配对符号时, 就将它更新到配对符号记录器 (self.parenthesis_track) 中
                checkpoint() 每当遇到截停标记时, 就触发检查点事件
                submit() 当判断可以结成完整的配对符号后, 就可以将这段字符串作为一个独立完整的参数提交上去
            --> return self.result 最终返回收集到的结果

        """
        # 将历史痕迹清空, 进入初始化状态
        self.reset()

        # 净化原始字符串
        phrase = self.sanitize(phrase)
        """
        净化效果:
            1. 消除编码符: `f"A"` --> `"A"`
            2. 在末尾增加一个截停标志: `A, B` --> `A, B, `
            3. 消除转义字符: `"A\"B"` --> `"A◆B"`
            4. 解决字符串后缀函数的问题: `"A = {}".format(B)` --> `"A = {}",◆.format(B)`
        """

        # 遍历字符串中的字符
        for index, char in enumerate(phrase):

            if char in self.parenthesis:
                # 当遇到任一配对符号时, 更新到配对符号记录器 (self.parenthesis_track) 中
                self.update(index, char)

            elif char == self.pause:
                # 当遇到截停标志时, 触发检查点事件
                result = self.checkpoint()

                if result:
                    # 如果判断可以形成结对, 则提交 (submit())
                    start, end = self.pause_track + 1, index
                    self.submit(phrase[start:end])
                    self.pause_track = index
                    """
                    示例: phrase = 'A(B), C[D], "E, F", '
                        第一次提交: start = 0, end = 4 --> `A(B)` --> self.pause_track = 4
                        第二次提交: start = 5, end = 10 --> ` C[D]` --> self.pause_track = 10
                        第三次提交: start = 11, end = 18 --> ` "E, F"` --> self.pause_track = 19
                    """

                    # 观察接下来要提交的是不是 "尾巴"
                    if phrase[end - 1] in self.quotes and phrase[end + 1] == self.uniq_mark:
                        self.trailing = True
                        """
                        示例: phrase = '"A = {}",◆.format(B), C, '
                            第一次提交: `"A = {}"`, 并认定下次提交的是 "尾巴"
                            第二次提交: `◆.format(B)` submit() 会将它当作 "尾巴" 处理, 并重置
                            self.trailing 为 False (具体可见 self.submit())
                            第三次提交: ` C`, 不会被认定为 "尾巴", 属于正常提交动作
                        """
        # 返回结果 (是一个列表, 每个元素就是抽取到的 "参数")
        return self.result

    def checkpoint(self):
        def make_pair(a, b) -> bool:
            """
                        示例: phrase = '(A, [B]), "C[D]", ',

                        结算第一个逗号时, 有:
                            self.parenthesis_track = [
                                (0, '('),
                            ]
                            因此有
                                self.parenthesis_track[0][1] --> a = '('
                                self.parenthesis_track[-1][1] --> b = '('
                            二者不能配对, 返回 False;

                        结算第二个逗号时, 有:
                            self.parenthesis_track = [
                                (0, '('), (4, '['), (6, ']'), (7, ')')
                            ]
                            因此有
                                self.parenthesis_track[0][1] --> a = '('
                                self.parenthesis_track[-1][1] --> b = ')'
                            二者可以配对, 返回 True.


                        结算第三个逗号时, 有:
                            self.parenthesis_track = [
                                (10, '"'), (12, '['), (14, ']'), (15, '"')
                            ]  # 注: 之前的 track 记录已经在结对成功后被清空了
                            因此有
                                self.parenthesis_track[0][1] --> a = '"'
                                self.parenthesis_track[-1][1] --> b = '"'
                            二者可以配对, 返回 True.

                        """
            return self.pairs[a] == b  # self.pairs 是在 self.__init__() 中定义好的

        if not self.parenthesis_track:
            """
            示例: phrase = 'A + B, (C), ', 当结算 `A + B` 的时候, self.parenthesis_track 尚为空列表.
            这种情况是可以提交的, 所以返回 True.
            """
            return True

        return make_pair(self.parenthesis_track[0][1], self.parenthesis_track[-1][1])

    def update(self, index: int, char: str):
        self.parenthesis_track.append((index, char))

    def submit(self, element: str):
        if self.trailing:
            # 示例: element = '◆.format(B)'
            self.result[-1] += element.strip(self.uniq_mark)
            self.trailing = False
        else:
            # 示例: element = ' "B"'
            self.result.append(element.strip())

        # 结算成功后, 之前的配对记录就清空掉
        self.parenthesis_track.clear()


def str2Dict(content: str):
    """
    手动转换成dict对象
    :param content: "key:value,key:value"或者"{key:value,key:value}"或者{key:,key:value}
    >>> str2Dict([{'categoryId': '${categoryId}', 'sensitiveId': '${sensitiveId}'}])
    :return:
    """
    if not content:
        return False
    try:
        # return dict(map(lambda x: x.split("="), content.split("$")))
        return json.loads(content)
    except Exception as e:
        if not isinstance(content, str):
            if isinstance(content, list):
                return content[0] if len(content) == 1 and isinstance(content[0], dict) else str2Dict(str(content))
        copy = content.strip('"')
        outDict = {}
        matcher = ParamsMatcher()
        match = matcher.match(copy)
        for origin in match:
            outDict[origin.split(":")[0]] = origin.split(":")[1]
        return outDict


def matchKeyValue(waitStr):
    return True if len(waitStr.split(":")) == 2 else False


if __name__ == '__main__':
    # print(str2Dict("content-type:application/json,Admin-Token:$get_jwt(admin123,admin123)"))
    # print(str2Dict([{'categoryId': '${categoryId}', 'sensitiveId': '${sensitiveId}'}]))
    st = """
    {"coreGoodsName":{"polGuid":"B022BB3C-83EE-699A-6269-32847ADF02F3","name":"如意尊3.0终身寿险","companyCode":"sinatay","companyShortName":"信泰保险","insureType":101,"insureTypeStr":"寿险","maxCommisionPoint":null,"prodcuts":[{"polGuid":"7F58E4AA-692F-B1E2-4E37-B5D203CF8950","name":"信泰如意尊（3.0版）终身寿险"}]},"coreGoodsCode":"B022BB3C-83EE-699A-6269-32847ADF02F3","companyShortName":"信泰保险","companyCode":"sinatay","coreGoodsTypeStr":"寿险","coreGoodsType":101,"allOrg":0,"showOrgCodes":[],"confType":0,"immediatelyEffective":1,"startTime":null,"endTime":"2021-08-31 23:59:59","ownDealRates":[{"securityPeriod":null,"payPeriod":"10","firstCommissionRate":"50","mrate":null,"drate":null,"orderType":1,"laterRates":[{"laterCount":"2","laterCommissionRate":"","disabled":false},{"laterCount":"3","laterCommissionRate":"","disabled":false},{"laterCount":"4","laterCommissionRate":"","disabled":false},{"laterCount":"5","laterCommissionRate":"","disabled":false}],"securityPerioDisabled":true,"firstRateDisabled":false,"MRateDisabled":false,"DRateDisabled":false}],"plateformRates":[],"securityPeriodExist":0}"""
    print(str2Dict(st))
