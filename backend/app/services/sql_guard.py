
import sqlglot
from sqlglot import exp
#被禁止的，不许做的
_FORBIDDEN = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
    exp.TruncateTable,
    exp.Command,
    exp.Grant,
)

_READ_ONLY = (
    exp.Select,
    exp.Union,
    exp.Intersect,
    exp.Except,
)

class SQLGuardError(ValueError):
    pass

def secure_sql(sql:str,max_rows:int) ->str:
    # select * from a;select * from b;
    # # 从字符串的右侧（末尾），删除所有连续的分号 `;` 。只删结尾，开头、中间分号不动。
    sql = sql.strip().rstrip(";")
    # 这个是一个语法树
    statements = sqlglot.parse(sql, dialect='postgres')
    
    # print(statements)
    if len(statements) != 1:
        raise SQLGuardError("sql只允许执行一条")
    statement = statements[0]
    # 想直观感受statement是什么？
    
    # print(statement.dump())
    
    # 校验2 三层判断
    if (
            not isinstance(statement, _READ_ONLY)  # 根节点不是允许的只读类型
            or isinstance(statement, _FORBIDDEN)  # 根节点直接是禁止类型
            or statement.find(*_FORBIDDEN)  # ⭐递归遍历AST，子节点包含禁止节点！
    ):
        raise SQLGuardError("只允许只读 SELECT 查询")
    safesql=statement.sql(dialect='postgres')  # 按PostgreSQL方言解析

    final_sql=f'select * from ({safesql}) _bi_result limit {max_rows} '

    return final_sql


if __name__ == '__main__':
    print(secure_sql("delete from a",max_rows=500))