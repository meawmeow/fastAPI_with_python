from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "ae4cc7b96ee60ace7238e4cd7927a025c8cb106f27072793a271df12b58c7f23"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#password = catmeaw
fake_users_db = {
    "mycat": {
        "username": "mycat",
        "full_name": "cat meaw",
        "email": "catmeaw@gmail.com",
        "hashed_password": "$2b$12$t0jXI5Itw11rCX8cvX8.X.CrYpKW9XMIKvtbNDiekvzqqZxuMU7My",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

#ค้นหาในฐานข้อมูล
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

#ตรวจสอบข้อมูลผู้ใช่จากฐานข้อมูล
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    #ตรวจสอบความตรงกันของpassword จากการป้อนเพื่อเช็คpasswordในฐานข้อมูล
    ispass = verify_password(password, user.hashed_password)
    print(ispass)
    if not ispass:
        return False
    return user

#สร้าง Jwt token มีการกำหนดเวลาหมดอายุของtoken และ แนบข้อมูล user เพื่อสร้าง token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#ค้นหาชื่อผู้ใช้
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        #ทำการ decode jwt token จากนั้นทำการ แกะชื่อ user ออกมา 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    #นำชื่อ user ที่ได้จากการ decode ไปค้นหาในฐานข้อมูล
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

#ตรวจสอบสถานะชื่อผู้ใช่
async def get_current_active_user(current_user: User = Depends(get_current_user)):#get_current_user ตรวจสอบสิทธิ์ผู้ใช่ว่ามีการลงชื่อเข้าใช้งานหรือยัง
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

#login
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    #ตรวจสอบข้อมูลผู้ใช่จากฐานข้อมูล
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #เริ่มเวลาอายุของtoken
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #สร้าง Jwt token 
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):#ตรวจสอบสิทธิ์ผู้ใช่
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):#ตรวจสอบสิทธิ์ผู้ใช่
    return [{"name": current_user.full_name,"email":current_user.email}]