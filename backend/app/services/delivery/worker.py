import asyncio
import logging
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError

from app.database.config import load_environment
from app.database.session import get_engine
from app.models.enums import Channel
from app.repositories import outbox
from app.services.delivery.adapters import adapter_for
from app.services.delivery.settings import DeliveryError, Mode, Policy, channel_mode

logger = logging.getLogger(__name__)


def send(adapter, message):
    try:
        adapter.send(message)
    except DeliveryError as exc:
        return str(exc)
    except Exception:
        # Exceções de terceiros podem conter credenciais, payload ou URL do webhook.
        return "Falha interna no adaptador de entrega."
    return None


async def process_one(engine, channel, mode, adapter, policy):
    claim = await asyncio.to_thread(outbox.claim_one, engine, channel, mode, policy)
    if claim is None:
        return False
    operation = asyncio.create_task(asyncio.to_thread(send, adapter, claim.message))
    while not operation.done():
        done, _ = await asyncio.wait({operation}, timeout=policy.lease / 3)
        if not done:
            await asyncio.to_thread(outbox.renew, engine, claim, policy)
    await asyncio.to_thread(outbox.complete, engine, claim, operation.result(), policy)
    return True


async def run_channel(channel, mode, policy, stop):
    adapter = adapter_for(channel, mode)
    while not stop.is_set():
        try:
            if await process_one(get_engine(), channel, mode, adapter, policy):
                continue
        except SQLAlchemyError:
            logger.error("Banco indisponível para o processador %s.", channel.value)
        try:
            await asyncio.wait_for(stop.wait(), timeout=policy.poll)
        except asyncio.TimeoutError:
            pass


@asynccontextmanager
async def lifespan(app):
    load_environment()
    app.state.channel_modes = dict.fromkeys(Channel, Mode.DISABLED)
    try:
        policy = Policy.load()
    except DeliveryError as exc:
        logger.error("Processamento de notificações desativado. %s", exc)
        yield
        return
    stop = asyncio.Event()
    workers = []
    for channel in Channel:
        try:
            mode = channel_mode(channel)
        except DeliveryError:
            logger.error("Modo inválido; processador %s desativado.", channel.value)
            continue
        app.state.channel_modes[channel] = mode
        if mode != Mode.DISABLED:
            workers.append(
                asyncio.create_task(run_channel(channel, mode, policy, stop))
            )
    try:
        yield
    finally:
        stop.set()
        await asyncio.gather(*workers)
