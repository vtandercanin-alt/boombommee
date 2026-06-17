"""Mini App web server: serves static frontend + JSON API.

Routes:
- GET  /                  -> index.html (the Mini App)
- GET  /static/{file}     -> css/js assets
- GET  /health            -> {"status":"ok"}
- POST /api/me            -> current user stats (auth via initData)
- POST /api/open_case     -> open a case (auth via initData)
- GET  /api/leaderboard   -> top 10 players (public)
"""
import json
import logging
import os
from aiohttp import web

from app.config import config
from app.database.db import db
from app.database.user_repo import UserRepository
from app.utils.cases import CaseManager, RankSystem
from app.web.security import validate_init_data

logger = logging.getLogger(__name__)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


async def _get_user_from_body(body: dict):
    """Validate initData from request body, ensure user exists, return (user_obj, error_json)."""
    init_data = body.get("init_data") or ""
    data = validate_init_data(init_data, config.BOT_TOKEN)
    if not data or not data.get("user"):
        return None, web.json_response({"error": "unauthorized"}, status=401)

    tg_user = data["user"]
    user_id = tg_user.get("id")
    if not user_id:
        return None, web.json_response({"error": "no user"}, status=400)

    session = await db.get_session()
    try:
        user = await UserRepository.get_or_create_user(
            session,
            user_id,
            tg_user.get("username"),
            tg_user.get("first_name"),
        )
        return user, None
    finally:
        await session.close()


# --- Routes ---

async def index_handler(request: web.Request) -> web.Response:
    return web.FileResponse(os.path.join(STATIC_DIR, "index.html"))


async def health_handler(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "bot": "kraken_case"})


async def api_me(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "bad json"}, status=400)

    user, err = await _get_user_from_body(body)
    if err is not None:
        return err
    if user is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    session = await db.get_session()
    try:
        stats = await UserRepository.get_user_stats(session, user.telegram_id)
    finally:
        await session.close()

    if not stats:
        return web.json_response({"error": "not found"}, status=404)

    return web.json_response({
        "user_id": stats["user_id"],
        "username": stats.get("username"),
        "first_name": stats.get("first_name"),
        "balance": stats["stars_balance"],
        "total_earned": stats["total_earned"],
        "cases_opened": stats["cases_opened"],
        "rank": stats["rank"],
        "level": stats["level"],
    })


async def api_open_case(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "bad json"}, status=400)

    user, err = await _get_user_from_body(body)
    if err is not None:
        return err
    if user is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    case_type = body.get("case_type", "test")
    price = CaseManager.get_case_price(case_type)

    if user.stars_balance < price:
        return web.json_response(
            {"error": "not_enough_stars", "balance": user.stars_balance, "price": price},
            status=402,
        )

    session = await db.get_session()
    try:
        # Deduct price first, then add reward via add_case_opening (reward - price = profit)
        user.stars_balance -= price
        await session.commit()

        opening = await UserRepository.add_case_opening(
            session, user.telegram_id, case_type, price, CaseManager.open_case(case_type)
        )
        if not opening:
            return web.json_response({"error": "failed"}, status=500)

        # Recompute rank/level
        refreshed = await UserRepository.get_user(session, user.telegram_id)
        rank_info = RankSystem.get_rank(refreshed.total_earned if refreshed else 0)

        if refreshed and (refreshed.rank != rank_info["name"]):
            refreshed.rank = rank_info["name"]
            refreshed.level = rank_info["level"]
            await session.commit()

        return web.json_response({
            "reward": opening.reward,
            "profit": opening.profit,
            "balance": refreshed.stars_balance if refreshed else None,
            "rank": rank_info["name"],
            "level": rank_info["level"],
        })
    finally:
        await session.close()


async def api_leaderboard(request: web.Request) -> web.Response:
    session = await db.get_session()
    try:
        top = await UserRepository.get_leaderboard(session, limit=10)
    finally:
        await session.close()

    result = []
    for i, u in enumerate(top, start=1):
        result.append({
            "place": i,
            "username": u.username or "Игрок",
            "first_name": u.first_name,
            "total_earned": u.total_earned,
            "cases_opened": u.cases_opened,
            "rank": u.rank,
        })
    return web.json_response({"leaderboard": result})


def create_web_app() -> web.Application:
    """Build the aiohttp application that serves the Mini App + API."""
    app = web.Application()

    # Static assets (css/js)
    if os.path.isdir(STATIC_DIR):
        app.router.add_static("/static", STATIC_DIR, show_index=False)

    # Mini App entry + API
    app.router.add_get("/", index_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_post("/api/me", api_me)
    app.router.add_post("/api/open_case", api_open_case)
    app.router.add_get("/api/leaderboard", api_leaderboard)
    return app
