from sanic import HTTPResponse, Request, response

from src.bot.singal_dispatcher_spawner import spawn_and_dispatch


async def handler(request: Request) -> HTTPResponse:
    spawn_and_dispatch(request.body)

    return response.empty()
