# encoding: utf-8
from datetime import *
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from order.mixins import KeeperBaseMixin
from wanglibao_account.utils import generate_contract
from wanglibao_margin.marginkeeper import MarginKeeper
from models import P2PProduct, P2PRecord, P2PEquity, EquityRecord, AmortizationRecord, ProductAmortization,\
    UserAmortization
from exceptions import ProductLack, P2PException
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message


class ProductKeeper(KeeperBaseMixin):

    def __init__(self, product, order_id=None):
        super(ProductKeeper, self).__init__(product=product, order_id=order_id)
        self.product = product

    def reserve(self, amount, user, savepoint=True):
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            self.product = P2PProduct.objects.select_for_update().filter(pk=self.product.pk).first()
            if amount > self.product.remain:
                raise ProductLack()
            self.product.ordered_amount += amount

            if self.product.ordered_amount == self.product.total_amount:
                self.product.status = u'满标待打款'
                self.product.soldout_time = timezone.now()

            self.product.save()
            catalog = u'申购'
            record = self.__tracer(catalog, amount, user, self.product.remain)
            return record

    def audit(self, user):
        if self.product.status == u'满标待审核':
            self.product.status = u'满标已审核'
            self.product.save()
            self.__tracer(u'状态变化', 0, user, self.product.remain, u'满标待审核 -> 满标已审核')

    def finish(self, user):
        if self.product.status == u'还款中':
            self.product.status = u'已完成'
            self.product.save()
            self.__tracer(u'状态变化', 0, user, self.product.remain, u'还款中 -> 已完成')

    def fail(self):
        prev_status = self.product.status

        self.product.status = u'流标'
        self.product.save()
        self.__tracer(u'状态变化', 0, None, self.product.remain, u'%s -> 流标' % prev_status)

    def __tracer(self, catalog, amount, user, product_balance_after, description=u''):
        trace = P2PRecord(catalog=catalog, amount=amount, product_balance_after=product_balance_after, user=user,
                          description=description, order_id=self.order_id, product=self.product)
        trace.save()
        return trace


class EquityKeeperDecorator():

    def __init__(self, product, order_id=None):
        self.product = product
        self.order_id = order_id
        pass

    @transaction.commit_manually
    def generate_contract(self, savepoint=True):

        with transaction.atomic(savepoint=savepoint):
            equity_list = list()
            for p2p_equity in self.product.equities.all():
                #EquityKeeper(equity.user, equity.product, order_id=order.id).generate_contract(savepoint=False)

                product = p2p_equity.product
                user = p2p_equity.user
                equity_query = P2PEquity.objects.filter(user=user, product=product)
                if (not equity_query.exists()) or (len(equity_query) != 1):
                    raise P2PException('can not get equity info.')

                equity = equity_query.first()
                contract_string = generate_contract(equity)
                equity.contract.save(str(equity.id)+'.html', ContentFile(contract_string))
                equity_list.append(equity)
                equity.save()

            #P2PEquity.objects.bulk_create(equity_list)
            transaction.commit()



class EquityKeeper(KeeperBaseMixin):

    def __init__(self, user, product, order_id=None):
        super(EquityKeeper, self).__init__(user=user, product=product, order_id=order_id)
        self.product = product
        self.equity = None

    def reserve(self, amount, description=u'', savepoint=True):
        check_amount(amount)
        with transaction.atomic(savepoint=savepoint):
            self.equity, _ = P2PEquity.objects.get_or_create(user=self.user, product=self.product)
            self.equity = P2PEquity.objects.select_for_update().filter(pk=self.equity.id).first()

            limit = self.limit

            if amount > limit:
                # raise P2PException(u'已超过可认购份额限制，该产品每个客户最大投资金额为%s元' % str(limit))
                raise P2PException(u'已超过可认购份额限制，'
                                   u'该产品每个客户最大投资金额为%s元' % str(self.product.limit_amount_per_user))



            self.equity.equity += amount
            self.equity.created_at = datetime.now()
            self.equity.save()
            catalog = u'申购'
            record = self.__tracer(catalog, amount, description)
            return record

    def rollback(self, description=u'', savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            equity = P2PEquity.objects.select_for_update().filter(user=self.user, product=self.product).first()
            if not equity:
                raise P2PException(u'No equity available for user')
            if equity.confirm:
                raise P2PException(u'The equity already confirmed, no way to revert')
            amount = equity.equity
            equity.delete()
            catalog = u'流标取消'
            record = self.__tracer(catalog, amount)
            user_margin_keeper = MarginKeeper(self.user, self.order_id)
            user_margin_keeper.unfreeze(amount, savepoint=False)
            return record

    def settle(self, savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            equity_query = P2PEquity.objects.filter(user=self.user, product=self.product)
            if (not equity_query.exists()) or (len(equity_query) != 1):
                raise P2PException('can not get equity info.')
            equity = equity_query.first()
            equity.confirm = True
            equity.confirm_at = timezone.now()
            equity.save()
            catalog = u'申购确认'
            description = u'用户份额确认(%d)' % equity.equity
            self.__tracer(catalog, equity.equity, description)
            user_margin_keeper = MarginKeeper(self.user)
            user_margin_keeper.settle(equity.equity, savepoint=False)

    def generate_contract(self, savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            product = self.product
            user = self.user
            equity_query = P2PEquity.objects.filter(user=user, product=product)
            if (not equity_query.exists()) or (len(equity_query) != 1):
                raise P2PException('can not get equity info.')
            equity = equity_query.first()
            contract_string = generate_contract(equity)
            equity.contract.save(str(equity.id)+'.html', ContentFile(contract_string))
            equity.save()

    def __tracer(self, catalog, amount, description=u''):
        trace = EquityRecord(catalog=catalog, amount=amount, description=description, user=self.user,
                             product=self.product, order_id=self.order_id)
        trace.save()
        return trace

    @property
    def limit(self):
        limit = self.product.limit_amount_per_user - self.get_equity()
        return limit

    def get_equity(self):
        if hasattr(self, 'equity'):
            equity = self.equity
        else:
            equity = P2PEquity.objects.filter(user=self.user, product=self.product).first()
        if equity:
            return equity.equity
        return 0


class AmortizationKeeper(KeeperBaseMixin):

    def __init__(self, product, order_id=None):
        super(AmortizationKeeper, self).__init__(product=product, order_id=order_id)
        self.product = product

    def generate_amortization_plan(self, savepoint=True):
        if self.product.status != u'满标已打款':
            raise P2PException('invalid product status.')
        self.amortizations = self.product.amortizations.all()
        self.product_interest = self.amortizations.aggregate(Sum('interest'))['interest__sum']
        equities = self.product.equities.all()

        get_amortization_plan(self.product.pay_method).calculate_term_date(self.product)
        # Delete all old user amortizations
        with transaction.atomic(savepoint=savepoint):
            UserAmortization.objects.filter(product_amortization__in=self.amortizations).delete()

            ProductAmortization.objects.select_for_update().filter(product=self.product)
            for equity in equities:
                self.__dispatch(equity)

    @transaction.commit_manually
    def __dispatch(self, equity):
        total_principal = equity.equity
        total_interest = self.product_interest * equity.ratio
        paid_principal = Decimal('0')
        paid_interest = Decimal('0')
        count = len(self.amortizations)
        user_amos = list()
        for i, amo in enumerate(self.amortizations):
            if i+1 != count:
                principal = equity.ratio * amo.principal
                interest = equity.ratio * amo.interest
                principal = principal.quantize(Decimal('.01'))
                interest = interest.quantize(Decimal('.01'))
                paid_interest += interest
                paid_principal += principal
            else:
                principal = total_principal - paid_principal
                interest = total_interest - paid_interest

            user_amo = UserAmortization(
                product_amortization=amo, user=equity.user, term=amo.term, term_date=amo.term_date,
                principal=principal, interest=interest
            )
            user_amos.append(user_amo)
            user_amo.save()

        print '#####', user_amos, '----------'

        #UserAmortization.objects.bulk_create(user_amos)
        transaction.commit()



    @classmethod
    def get_ready_for_settle(self):
        amos = ProductAmortization.is_ready.all()
        return amos

    def amortize(self, amortization, savepoint=True):
        with transaction.atomic(savepoint=savepoint):
            if amortization.settled:
                raise P2PException('amortization %s already settled.' % amortization)
            sub_amortizations = amortization.subs.all()
            description = unicode(amortization)
            catalog = u'分期还款'
            product = amortization.product
            pname = u"%s,期限%s个月" % (product.name, product.period)
            for sub_amo in sub_amortizations:
                user_margin_keeper = MarginKeeper(sub_amo.user)
                user_margin_keeper.amortize(sub_amo.principal, sub_amo.interest,
                                            sub_amo.penal_interest, savepoint=False, description=description)

                sub_amo.settled = True
                sub_amo.settlement_time = timezone.now()
                sub_amo.save()
                
                amo_amount = sub_amo.principal + sub_amo.interest + sub_amo.penal_interest
                send_messages.apply_async(kwargs={
                    "phones": [sub_amo.user.wanglibaouserprofile.phone],
                    #"messages": [messages.product_amortize(amortization.product, sub_amo.settlement_time, sub_amo.principal + sub_amo.interest + sub_amo.penal_interest)]
                    "messages": [messages.product_amortize(amortization.product, sub_amo.settlement_time, amo_amount)]
                })

                title,content = messages.msg_bid_amortize(pname, timezone.now(), amo_amount)
                inside_message.send_one.apply_async(kwargs={
                    "user_id":sub_amo.user.id,
                    "title":title,
                    "content":content,
                    "mtype":"amortize"
                })

                self.__tracer(catalog, sub_amo.user, sub_amo.principal, sub_amo.interest, sub_amo.penal_interest,
                              amortization, description)

            amortization.settled = True
            amortization.save()
            catalog = u'还款入账'
            self.__tracer(catalog, None, amortization.principal, amortization.interest, amortization.penal_interest, amortization)

    def __tracer(self, catalog, user, principal, interest, penal_interest, amortization, description=u''):
        trace = AmortizationRecord(
            amortization=amortization, term=amortization.term, principal=principal, interest=interest,
            penal_interest=penal_interest, description=description, user=user, catalog=catalog, order_id=self.order_id
        )
        trace.save()
        return trace


def check_amount(amount):
    pass

