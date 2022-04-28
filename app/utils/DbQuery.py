"""
@File: DbQuery.py
@author: guoweiliang
@date: 2021/6/25
"""
import pymysql

from error_message import QueryElementNotSupply


class DbQuery(object):

    def __init__(self, host, user, pwd, port, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        if not isinstance(port, int):
            try:
                self.port = int(port)
            except:
                raise ValueError("port can not convert to integer!")
        else:
            self.port = port
        self.db = db
        self.conn = self._getQueryInstance()

    def _getQueryInstance(self):
        return pymysql.connect(host=self.host,
                               user=self.user,
                               password=self.pwd,
                               database=self.db,
                               port=self.port,
                               cursorclass=pymysql.cursors.DictCursor)

    def query(self, query: dict):
        """
        执行sql
        :param query:
        :return: 查询到结果返回受影响的行数
        """
        try:
            parser = self.sqlParser(query)
        except QueryElementNotSupply:
            return None
        return self.conn.cursor().execute(parser)

    def sqlParser(self, query: dict):
        """
        查询语句 "table.column.condition=***&table.collum=***"
        dbAssert:
            table: ins_order
            column: link_no
            condition: id=**&name=**
        查询出结果表示断言成功，否则断言失败
        condition 查询条件
        :param query:
        :return:
        """
        table = query.get("table") or None
        column = query.get("column") or None
        condition: str = query.get("condition") or None
        if table is None or column is None or condition is None:
            raise QueryElementNotSupply(f"sql查询的要素未提供完全！table:{table},column:{column},condition:{condition}")
        parsedCondition = " and ".join(condition.split("&"))
        return f"select {column} from {table} where {parsedCondition}"



if __name__ == '__main__':
    # print(DbQuery.sqlParser({"table": 'ins_order',
    #                    "column": "link_no",
    #                    "condition": "id=123"}))
    db = DbQuery(host='192.168.1.190', user='root', pwd="123456", db='zh_portal', port=3306)
    print(db.query({"table":"dalaran_agent", "column": "id", "condition": "id=100415"}))
