import graphene

# 定义一个简单的对象类型
class Person(graphene.ObjectType):
    name = graphene.String()
    age = graphene.Int()

# 定义 Query 类，包含查询字段
class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="World"))
    person = graphene.Field(Person, name=graphene.String(required=True))

    def resolve_hello(self, info, name):
        return f"Hello, {name}!"

    def resolve_person(self, info, name):
        # 这里可以查询数据库，这里简单返回一个模拟数据
        return Person(name=name, age=30)

# 创建 Schema 对象
schema = graphene.Schema(query=Query)