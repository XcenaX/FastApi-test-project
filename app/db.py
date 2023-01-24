from typing import Union
import databases
import ormar
import sqlalchemy

from typing import Optional

from .config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


# class User(ormar.Model):
#     class Meta(BaseMeta):
#         tablename = "users"

#     id: int = ormar.Integer(primary_key=True)
#     obfuscated_name: str = ormar.String(max_length=36, unique=False, nullable=False)
#     test_index: int = ormar.Integer()
#     presentation: int = ormar.Integer()
#     question: int = ormar.Integer()
#     class_label_fpg: int = ormar.Integer()


# class Data(ormar.Model):
#     class Meta(BaseMeta):
#         tablename = "datas"

#     id: int = ormar.Integer(primary_key=True)
#     user: Optional[User] = ormar.ForeignKey(User)
#     numbers: str = ormar.String(max_length=3000)


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=20)
    password: str = ormar.String(max_length=20)


class Prediction(ormar.Model):
    class Meta(BaseMeta):
        tablename = "predictions"

    id: int = ormar.Integer(primary_key=True)
    data: str = ormar.String(max_length=3000)
    user: User = ormar.ForeignKey(User) 


class Token(ormar.Model):
    class Meta(BaseMeta):
        tablename = "tokens"

    access_token: str
    token_type: str


class TokenData(ormar.Model):
    class Meta(BaseMeta):
        tablename = "tokendatas"

    username: Union[str, None] = None
    

engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)