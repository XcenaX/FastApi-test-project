from .utils import *
from app.db import *
from .ai import load_model

from typing import Union

from fastapi import FastAPI, File, Request, UploadFile, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel

from passlib.context import CryptContext

from jose import JWTError, jwt

from datetime import timedelta

data_path = "dataset_train.csv"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
app.mount("/static", StaticFiles(directory=main_route+"static"), name="static")

templates = Jinja2Templates(directory=main_route+"templates")

# ALL URLS
# /             | GET
# /token        | POST
# /users/me     | GET
# /predictions  | GET
# /predict      | POST
# /login        | GET
# /register     | GET

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request): #token: str = Depends(oauth2_scheme)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/predictions")
async def data_root(request: Request):        
    return await Prediction.objects.all()


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.filename.split(".")[1] not in allowed_file_types:
        return {"error": file.content_type+" type is not allowed file type!"}
    
    contents = file.file.read()
    contents = contents.decode('utf-8')[2:]
    rows = contents.splitlines()
    count = 0
    _data = []
    try:
        for row in rows:
            _data.append([])
            numbers = row.split(", ")
            for number in numbers:
                _data[count].append(int(number))
            count+=1
    except Exception as e:
        return {"error": str(e)}
    
    model = load_model()
    df = pd.DataFrame(_data)

    print(type(model), model)

    predicts = model.predict(df)

    # Сделать добавление
    Prediction.objects.create()

    return {"predictions": predicts}


@app.post("/register")
async def post_register(username: str, password: str):
    try:
        user = await User.objects.get(username=username, password=password)
        if(user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Такой пользователь уже существует!",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except:
        User.object.create(username=username, password=password)
        return {"success": True}
        

@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()
    

@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
