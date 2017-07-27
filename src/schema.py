import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .models import UserModel, TodoModel
from graphene import relay, resolve_only_args


class NewSQLAlchemyConnectionString(SQLAlchemyConnectionField):
    RELAY_ARGS = ['first', 'last', 'before', 'after']

    @classmethod
    def get_query(cls, model, context, info, args):
        """"Overiding the default query method of the connection class
        so that we have the default filtering that relay supports as well
        as our own custom filtering"""
        query = super(NewSQLAlchemyConnectionString, cls).get_query(model, context, info, args)
        for field, value in args.items():
            if field not in cls.RELAY_ARGS:
                query = query.filter(getattr(model, field) == value)
        return query

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
    todos = NewSQLAlchemyConnectionString(Todo, completed=graphene.Boolean())

    class Meta:
        model = UserModel
        interfaces = [relay.Node]
        
    @resolve_only_args
    def resolve_todos(self, **args):
        # Transform the instance ship_ids into real instances
        if args:
            return self.todos.filter_by(**args).all()
        return self.todos.all()

    @classmethod
    def get_node(cls, id, context, info):
        # import pdb; pdb.set_trace()
        query = cls.get_query(context)
        return query.get(id)

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    users = NewSQLAlchemyConnectionString(
        User, name=graphene.String())
    todos = NewSQLAlchemyConnectionString(Todo, completed=graphene.Boolean())
    default_users = graphene.List(User)
    default_user = graphene.Field(User, id=graphene.Int())
    
    def resolve_default_users(self, args, context, info):
        query = User.get_query(context)  # SQLAlchemy query
        return query.all()

    def resolve_default_user(self, args, context, info):
        query = User.get_query(context)
        return query.filter(UserModel.id == args['id']).first()


schema = graphene.Schema(query=Query, types=[User,Todo])
