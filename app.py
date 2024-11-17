import asyncio
from sanic import Sanic, Request
from sqlalchemy.ext.asyncio import create_async_engine
from contextvars import ContextVar

from sqlalchemy import select, delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Student

app = Sanic("SMYApp")

# region ORM Session
bind = create_async_engine("mysql+aiomysql://root:root@localhost/test", echo=True)
_session_maker = sessionmaker(bind, AsyncSession, expire_on_commit=False)  # noqa
_base_model_session_ctx = ContextVar("session")


@app.middleware("request")
async def inject_session(request):
    request.ctx.session = _session_maker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request: Request, _):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


# endregion ORM Session

@app.get("/")
@app.ext.template("index.j2")
async def index(req: Request):
    session = req.ctx.session

    async with session.begin():
        student_list = await session.execute(select(Student))
        student_list = student_list.scalars().all()

    return {"student_list": student_list}


@app.get("/delete/<key:int>")
async def delete(req: Request, key: int):
    session = req.ctx.session
    if not key:
        await req.respond(status=302, headers={"Location": "/"})
        return None

    async with session.begin():
        await session.execute(delete(Student).where(Student.id == key))

    await req.respond(status=302, headers={"Location": "/"})


@app.get("/new")
@app.ext.template("upsert.j2")
async def new(_: Request):
    return {"action_title": "Add"}


@app.get("/update/<key:int>")
@app.ext.template("upsert.j2")
async def update(req: Request, key: int):
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
async def upsert(req: Request):
    form_data = req.form
    record_id = form_data.get("id")
    session = req.ctx.session
    try:
        record_id = int(record_id)
    except ValueError:
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
    app.run(
        host="127.0.0.1",
        port=8080,
        debug=True,
        auto_reload=True,
        backlog=100,
        access_log=True,
        workers=1
    )


if __name__ == '__main__':
    asyncio.run(main())
