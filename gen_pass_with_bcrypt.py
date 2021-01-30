import bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password ='catmeaw'
pass_hash = pwd_context.hash(password)
print(pass_hash)
