### Running the project

This project uses python 3 but should run with python 2 without any issues.

    $ virtualenv venv
    $ source venv/bin/activate # if using windows venv/Scripts/activate
    $ pip install -r requirements.txt
    $ export FLASK_APP=src/__init__.py
    $ export FLASK_DEBUG=1 # puts production server in debug mode

The database already consist of some demo data. I made use of sqlite but it shouldn't matter which database is used.

    $ flask run

## Querying Data
I implemented querying of data using both the default graphql way as well as with the assumption of using relay

### a. Using default graphql method

assumming a query like this

    query{
        defaultUsers{
            name
        }
    }

We would end up with the result 

    {
        "data":{
            "defaultUsers":[
                {
                    "name": "James"
                },
                {
                    "name": "Charlie"
                }
            ]
        }
    }

If we wanted to fetch the record of a single user 

    
    query{
        defaultUser(id:2):{ # this is the actual id of the database row.
            name
        }
    }


We end up with
    
    {
        "data":{
            "defaultUser":{
                "name": "Charlie"
            }
        }
    }

### b. Using relay 
Even though the ids on our sqlalchemy models are integers, Making use of the `Relay` interface changes this ids to unique strings that can be queried independently

So for example if we wanted to query all users

    query{        
        users{
            edges{
                node{
                    id
                    name
                }
            }
        }
    }

We end up with the following result

    {
        "data": {
            "users": {
                "edges": [
                    {
                    "node": {
                        "id": "VXNlcjox",
                        "name": "James"
                    }
                    },
                    {
                    "node": {
                        "id": "VXNlcjoy",
                        "name": "Charlie"
                    }
                    }
                ]
            },
        }
    }

If i am interested in the result for a single user, because we are using the `Relay` interface here, the query would look like this

    query{
        node(id:"VXNlcjox"){ # not we are making use of the string id provided by relay and not the integer id
            ... on User{
                name
                lastName
                todos{
                    edges{
                        node{
                            id
                            task
                        }
                    }
                }

            }
        }
    }

We would end up with the following result

    {
        "data":{
            "node": {
                "id": "VXNlcjox",
                "name": "James",
                "lastName": "Bond",
                "todos": {
                    "edges": [
                    {
                        "node": {
                        "id": "VG9kbzox",
                        "task": "Task 1"
                        }
                    }
                    ]
                }
                },
        }
    }

As long as we know the relay `id` for any particular record and we know the type, we can query it easily.

If we wanted to get the result for a particular `Todo` along with its user, the query would be like this

    query{
        node(id:"VG9kbzox"){
            ... on Todo{
                task
                completed
                user{
                    name
                    lastName
                }
            }
        }
    }


## Adding Filtering Support

By using the default `SQLAlchemyConnectionField` provided by `graphene_sqlalchemy`, we can use the default filters `first`, `last`, `before` and `after` as required in the relay specification. 

But if we wanted to support additional custom filtering while still conforming to the relay specs, then we would need to overide the `SQLAlchemyConnectionField.get_query` classmethod.

Right now, the current implementation only does an equal to comparison for a predefined field e.g

    query{
        users(name:"James"){
            edges{
                node{
                    id
                    name
                    lastName
                    todos{
                    edges{
                        node{
                        completed
                        }
                    }
                    }
                }
            }
        }
        todos(completed:false){
            edges{
            node{
                task
            }
            }
        }
    }

We should end up with the following 

    {
        "data": {
            "users": {
                "edges": [
                    {
                        "node": {
                            "id": "VXNlcjox",
                            "name": "James",
                            "lastName": "Bond",
                            "todos": {
                                "edges": [
                                    {
                                    "node": {
                                        "completed": false
                                    }
                                    },
                                    {
                                    "node": {
                                        "completed": true
                                    }
                                    },
                                    {
                                    "node": {
                                        "completed": true
                                    }
                                    }
                                ]
                            }
                        }
                    }
                ]
            },
            "todos": {
                "edges": [
                    {
                    "node": {
                        "task": "Task 1"
                    }
                    },
                    {
                    "node": {
                        "task": "Task 4.0"
                    }
                    }
                ]
            }
        }
    }

If we wanted for example to filter the `todos` returned by a single user, we would overide the `resolve_todos` instance method
and account for the filter.

In the example below, I am fetching the result of a single user
with only completed todos

    fragment TodoDetail on Todo {
        id
        task
        completed
    }
    query{
        node(id:"VXNlcjox"){
            ... on User{
                completedTodos: todos(completed:true){
                    edges{
                        node{
                            ...TodoDetail
                        }
                    }
                }
                uncompletedTodos: todos(completed:false){
                    edges{
                        node{
                            ...TodoDetail
                        }
                    }
                }
            }
        }
    }

We end up with the following result. 

    {
        "data": {
            "node": {
            "completedTodos": {
                "edges": [
                {
                    "node": {
                    "id": "VG9kbzoy",
                    "task": "Task 2.0",
                    "completed": true
                    }
                },
                {
                    "node": {
                    "id": "VG9kbzoz",
                    "task": "Task 3.0",
                    "completed": true
                    }
                }
                ]
            },
            "uncompletedTodos": {
                "edges": [
                {
                    "node": {
                    "id": "VG9kbzox",
                    "task": "Task 1",
                    "completed": false
                    }
                }
                ]
            }
            }
        }
        }