from fastapi import FastAPI
import users
import authentication


app = FastAPI(
    title='school management system'
)

app.include_router(users.router)
app.include_router(authentication.router)
