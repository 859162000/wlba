from wanglibao.celery import app
from wanglibao_p2p.trade import P2POperator


@app.task
def p2p_watchdog():
    P2POperator().watchdog()
