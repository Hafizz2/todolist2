from aiogram import Router

from . import group, private


def build_router() -> Router:
    router = Router()
    router.include_routers(private.build_router(), group.build_router())
    return router
