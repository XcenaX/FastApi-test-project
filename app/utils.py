import datetime
import xlrd
import pandas as pd
from .db import *
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Debug = False
main_route = "/code/./app/" if Debug == False else ""

allowed_file_types = ["txt", "csv", "json", "xml"]

# Получаем данные из .env файла
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_data_xlrd(data_path):
    d = {
        "data": []
    }
    wb = xlrd.open_workbook(main_route+data_path)
    sheet = wb.sheet_by_index(0)
    row_count = sheet.nrows
    for i in range(1, row_count):
        item = {}
        item["name"] = sheet.cell(i, 0)
        item["test_index"] = sheet.cell(i, 1)
        item["presentation"] = sheet.cell(i, 2)
        item["question"] = sheet.cell(i, 3)
        item["data"] = sheet.cell(i, 4)
        item["class_label_FPG"] = sheet.cell(i, 5)
        d["data"].append(item)
    return d


def get_data_csv(data_path):
    df = pd.read_csv(main_route+data_path, delimiter=';')
    return df.to_dict()


def get_user(username: str):
    try:
        return User.objects.get(username=username)
    except:
        return None


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[datetime.timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt