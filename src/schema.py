import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .models import UserModel, TodoModel
from graphene import relay, resolve_only_args

class Todo(SQLAlchemyObjectType):

    class Meta:
        model = TodoModel
        interfaces = [relay.Node]

    @classmethod
    def get_node(cls, id, context, info):
        # import pdb; pdb.set_trace()
        query = Todo.get_query(context)
        return query.get(id)

class User(SQLAlchemyObjectType):
    todos = SQLAlchemyConnectionField(Todo)

    class Meta:
        model = UserModel
        interfaces = [relay.Node]
        
    @resolve_only_args
    def resolve_ships(self, **args):
        # Transform the instance ship_ids into real instances
        return self.todos.all()

    @classmethod
    def get_node(cls, id, context, info):
        # import pdb; pdb.set_trace()
        query = cls.get_query(context)
        return query.get(id)

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    users = SQLAlchemyConnectionField(User)
    todos = SQLAlchemyConnectionField(Todo)
    default_users = graphene.List(User)
    default_user = graphene.Field(User, id=graphene.Int())
    
    def resolve_default_users(self, args, context, info):
        query = User.get_query(context)  # SQLAlchemy query
        return query.all()

    def resolve_default_user(self, args, context, info):
        query = User.get_query(context)
        return query.filter(UserModel.id == args['id']).first()


schema = graphene.Schema(query=Query, types=[User,Todo])
