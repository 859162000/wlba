from wanglibao.celery import app
from wanglibao_p2p.models import P2PProduct
from wanglibao_p2p.trade import P2POperator


@app.task
def p2p_watchdog():
    P2POperator().watchdog()


@app.task
def process_paid_product(product_id):
    P2POperator.preprocess_for_settle(P2PProduct.objects.get(pk=product_id))

import os
@app.task
def build_earning():

    os.system('touch ~/workspace/test.txt')