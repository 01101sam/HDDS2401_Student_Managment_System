import asyncio
import os
import base64
from sanic import Sanic, Request, text
from sqlalchemy.ext.asyncio import create_async_engine
from contextvars import ContextVar

from dotenv import load_dotenv
from sqlalchemy import select, delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from models import Student

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
HTTP_BASIC_AUTH_USER = os.getenv('HTTP_BASIC_AUTH_USER') or ""
HTTP_BASIC_AUTH_PWD = os.getenv('HTTP_BASIC_AUTH_PWD') or ""

app = Sanic("SMYApp")

# region ORM
bind = create_async_engine(DATABASE_URL, echo=True)
_session_maker = sessionmaker(bind, class_=AsyncSession, expire_on_commit=False)  # noqa
_base_model_session_ctx = ContextVar("session")

Base = declarative_base()


# Base.query = _session_maker.query_property()


@app.middleware("request")
async def inject_session(request):
    request.ctx.session = _session_maker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request: Request, _):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


async def init_db():
    from sqlalchemy import inspect
    from models import Student

    async with bind.begin() as conn:
        # Clear out the database
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        # Create student table if not exists
        if not await conn.run_sync(lambda sync_conn: inspect(sync_conn).has_table(Student.__tablename__)):
            await conn.run_sync(Student.__table__.create)  # noqa


# endregion ORM

# region Basic HTTP Auth
@app.middleware("request")
async def basic_auth_middleware(request):
    if not HTTP_BASIC_AUTH_USER and not HTTP_BASIC_AUTH_PWD:
        return

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        request.ctx.auth_error = True
        return

    auth_type, auth_value = auth_header.split(" ", 1)
    if auth_type.lower() != "basic":
        request.ctx.auth_error = True
        return

    auth_value = auth_value.strip()
    auth_value = auth_value.encode("utf-8")
    auth_value = base64.b64decode(auth_value).decode("utf-8")
    username, password = auth_value.split(":", 1)

    if username != HTTP_BASIC_AUTH_USER or password != HTTP_BASIC_AUTH_PWD:
        request.ctx.auth_error = True
        return


@app.middleware("request")
async def basic_auth_response(request: Request):
    if hasattr(request.ctx, "auth_error"):
        return text("Unauthorized", status=401, headers={"WWW-Authenticate": 'Basic realm="Login Required"'})


# endregion Basic Auth

@app.get("/")
@app.ext.template("index.j2")
async def handle_index(req: Request):
    session = req.ctx.session

    async with session.begin():
        student_list = await session.execute(select(Student))
        student_list = student_list.scalars().all()

    return {"student_list": student_list}


@app.get("/delete/<key:int>")
async def handle_delete(req: Request, key: int):
    session = req.ctx.session
    if not key:
        await req.respond(status=302, headers={"Location": "/"})
        return None

    async with session.begin():
        student = await session.execute(select(Student).where(Student.id == key))
        student = student.scalar_one_or_none()

        if student:
            await session.execute(delete(Student).where(Student.id == key))

    await req.respond(status=302, headers={"Location": "/"})


@app.get("/new")
@app.ext.template("upsert.j2")
async def handle_new(_: Request):
    return {"action_title": "Add"}


@app.get("/update/<key:int>")
@app.ext.template("upsert.j2")
async def handle_update(req: Request, key: int):
    session = req.ctx.session
    if not key:
        await req.respond(status=302, headers={"Location": "/"})
        return None

    async with session.begin():
        student = await session.execute(select(Student).where(Student.id == key))
        student = student.scalar_one_or_none()

    if not student:
        await req.respond(status=302, headers={"Location": "/"})
        return None

    return {
        "action_title": "Update",
        "student": student
    }


@app.post("/api/upsert")
async def handle_upsert(req: Request):
    form_data = req.form
    record_id = form_data.get("id")
    session = req.ctx.session
    try:
        record_id = int(record_id)
    except (ValueError, TypeError):
        record_id = None

    async with session.begin():
        payload = {
            "name": form_data.get("name"),
            "gender": form_data.get("gender"),
            "birth": form_data.get("birth"),
            "study_year": form_data.get("study_year"),
            "class_id": form_data.get("class_id")
        }

        if record_id:
            statement = update(Student).where(Student.id == record_id).values(**payload)
        else:
            statement = insert(Student).values(**payload)

        await session.execute(statement)

    await req.respond(status=302, headers={"Location": "/"})


async def main():
    global DATABASE_URL

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set")

    await init_db()
    app.run(host="0.0.0.0", port=8080)


if __name__ == '__main__':
    asyncio.run(main())
