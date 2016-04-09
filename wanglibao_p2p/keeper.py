# encoding: utf-8
import logging
from datetime import *
from decimal import *
from dateutil.relativedelta import relativedelta
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from order.mixins import KeeperBaseMixin
from wanglibao_account.utils import generate_contract
from wanglibao_margin.marginkeeper import MarginKeeper
from models import P2PProduct, P2PRecord, P2PEquity, EquityRecord, AmortizationRecord, ProductAmortization,\
    UserAmortization, P2PContract, InterestPrecisionBalance, P2PProductContract, ProductInterestPrecision,\
    InterestInAdvance, P2PEquityJiuxian
from exceptions import ProductLack, P2PException
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao_redpack import backends as redpack_backends
from wanglibao_redpack.models import RedPackRecord
from wanglibao_activity import backends as activity_backends
import re
import json

from weixin.constant import PRODUCT_AMORTIZATION_TEMPLATE_ID
from weixin.models import WeixinUser
from weixin.tasks import sentTemplate
from wanglibao_profile.models import RepeatPaymentUser, RepeatPaymentUserRecords


logger = logging.getLogger(__name__)

class ProductKeeper(KeeperBaseMixin):

    def __init__(self, product, order_id=None):
        super(ProductKeeper, self).__init__(product=product, order_id=order_id)
        self.product = product

    def reserve(self, amount, user, savepoint=True, platform=u''):
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
            record = self.__tracer(catalog, amount, user, self.product.remain, platform=platform)
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

    def __tracer(self, catalog, amount, user, product_balance_after, description=u'', platform=u''):
        trace = P2PRecord(catalog=catalog, amount=amount, product_balance_after=product_balance_after, user=user,
                          description=description, order_id=self.order_id, product=self.product, platform=platform)
        trace.save()
        return trace


class EquityKeeperDecorator():

    def __init__(self, product, order_id=None):
        self.product = product
        self.order_id = order_id
        pass

    def generate_contract(self, savepoint=True):

        with transaction.atomic(savepoint=savepoint):
            contract_list = list()
            #p2p_quities = self.product.equities.select_related('user', 'product').all()
            p2p_equities = P2PEquity.objects.select_related('user__wanglibaouserprofile', 'product__contract_template').filter(product=self.product)
            for p2p_equity in p2p_equities:
                #EquityKeeper(equity.user, equity.product, order_id=order.id).generate_contract(savepoint=False)

                # product = p2p_equity.product
                # user = p2p_equity.user
                # equity_query = P2PEquity.objects.filter(user=user, product=product)
                # if (not equity_query.exists()) or (len(equity_query) != 1):
                #     raise P2PException('can not get equity info.')
                #
                # equity = equity_query.first()
                contract_string = generate_contract(p2p_equity, None, p2p_equities)

                contract = P2PContract()
                contract.contract_path.save(str(p2p_equity.id)+'.html', ContentFile(contract_string), False)
                contract.equity = p2p_equity
                contract_list.append(contract)

            P2PContract.objects.bulk_create(contract_list)

    def generate_contract_one(self, equity_id, savepoint=True):

        with transaction.atomic(savepoint=savepoint):
            # p2p_equities = P2PEquity.objects.select_related('user__wanglibaouserprofile', 'product__contract_template').filter(product=self.product)
            p2p_equity = P2PEquity.objects.select_related('user__wanglibaouserprofile', 'product__contract_template')\
                                          .select_related('product').filter(id=equity_id).first()
            amortizations = UserAmortization.objects.filter(user=p2p_equity.user, product_amortization__product=p2p_equity.product)
            productAmortizations = ProductAmortization.objects.filter(product=p2p_equity.product).select_related('product').all()
            contract_info = P2PProductContract.objects.filter(product=p2p_equity.product).first()

            #酒仙众筹标信息
            jiuxian_equity = P2PEquityJiuxian.objects.filter(user=p2p_equity.user, equity=p2p_equity).first()
            if jiuxian_equity:
                p2p_equity.jiuxian = jiuxian_equity

            p2p_equity.contract_info = contract_info
            p2p_equity.amortizations_all = amortizations
            p2p_equity.productAmortizations = productAmortizations

            contract_string = generate_contract(p2p_equity, None, None)

            contract = P2PContract()
            contract.contract_path.save(str(p2p_equity.id)+'.html', ContentFile(contract_string), False)
            contract.equity = p2p_equity
            contract.save()


class EquityKeeper(KeeperBaseMixin):

    def __init__(self, user, product, order_id=None):
        super(EquityKeeper, self).__init__(user=user, product=product, order_id=order_id)
        self.product = product
        self.equity = None
        self.equity_jiuxian = None

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

            #酒仙网众筹用户增加额外的记录
            # if self.product.category == u'酒仙众筹标':
            #     self.equity_jiuxian, created = P2PEquityJiuxian.objects\
            #         .get_or_create(user=self.user, product=self.product, equity=self.equity)
            #     self.equity_jiuxian = P2PEquityJiuxian.objects.select_for_update().filter(pk=self.equity_jiuxian.id).first()
            #     self.equity_jiuxian.equity_amount += amount
            #     self.equity_jiuxian.created_at = datetime.now()
            #     self.equity_jiuxian.save()

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
            #流标要将红包退回账号
            p2precord = P2PRecord.objects.filter(user=self.user, product=self.product, catalog=u"申购")
            if p2precord:
                for p2p in p2precord:
                    result = redpack_backends.restore(p2p.order_id, p2p.amount, p2p.user)
                    if result['ret_code'] == 0:
                        user_margin_keeper.redpack_return(result['deduct'], description=u"%s 流标 红包退回%s元" % (self.product.short_name, result['deduct']))
            #酒仙网流标后删除酒仙标用户持仓记录
            # if self.product.category == u'酒仙众筹标':
            #     equity_jiuxian = P2PEquityJiuxian.objects.select_for_update().filter(user=self.user, product=self.product).first()
            #     if equity_jiuxian and equity_jiuxian.confirm is False:
            #         equity_jiuxian.delete()
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

            #酒仙网众筹用户增加额外的记录
            # if self.product.category == u'酒仙众筹标':
            #     equity_jiuxian = P2PEquityJiuxian.objects.filter(user=self.user, product=self.product).first()
            #     if equity_jiuxian:
            #         equity_jiuxian.confirm = True
            #         equity_jiuxian.confirm_at = datetime.now()
            #         equity_jiuxian.save()

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

        get_amortization_plan(self.product.pay_method).calculate_term_date(self.product) #每期还款日期不在单独生成

        # Delete all old user amortizations
        with transaction.atomic(savepoint=savepoint):
            #UserAmortization.objects.filter(product_amortization__in=self.amortizations).delete() 生成产品还款计划时，删除的时候就已经删除了

            self.amortizations = self.product.amortizations.all()

            #self.amortizations = self.__generate_product_amortization(self.product)
            self.product_interest = self.amortizations.aggregate(Sum('interest'))['interest__sum']
            equities = self.product.equities.select_related('user').all()

            #ProductAmortization.objects.select_for_update().filter(product=self.product)
            # for equity in equities:
            #     self.__dispatch(equity)
            #self.__generate_useramortization(equities)
            
            self.__generate_user_amortization(equities)

    def __generate_product_amortization(self, product):
        product_amo = ProductAmortization.objects.filter(product_id=product.pk).values('id')
        if product_amo:
            pa_list = [int(i['id']) for i in product_amo]
            product.amortizations.clear()
            from celery.execute import send_task
            send_task("wanglibao_p2p.tasks.delete_old_product_amortization", kwargs={
                        'pa_list': pa_list,
                })

        logger.info(u'The product status is 录标完成, start to generate amortization plan')

        terms = get_amortization_plan(product.pay_method).generate(product.total_amount,
                product.expected_earning_rate / 100,
                datetime.now(), product.period)

        for index, term in enumerate(terms['terms']):
            amortization = ProductAmortization()
            amortization.description = u'第%d期' % (index + 1)
            amortization.principal = term[1]
            amortization.interest = term[2]
            amortization.term = index + 1

            if len(terms) == 6:
                amortization.term_date = term[5]

            product.amortizations.add(amortization)
            amortization.save()

        product.amortization_count = len(terms['terms'])

        product.status = u'待审核'
        product.priority = product.id * 10
        product.save()

        return product.amortizations

    def __generate_user_amortization(self, equities):

        product = self.product

        product_amortizations = []
        interest_precisions = list()

        for product_amortization in self.amortizations.all():
            product_amortizations.append(product_amortization)

        user_amos = list()

        amortization_cls = get_amortization_plan(product.pay_method)
        product_interest_start = timezone.now()

        pay_method = product.pay_method
        subscription_date = None
        product_interest = Decimal(0)

        for equity in equities:
            # 查询用户是否使用加息券
            coupon = RedPackRecord.objects.filter(user=equity.user, product_id=product.id)\
                .filter(redpack__event__rtype='interest_coupon').first()
            if coupon:
                coupon_year_rate = coupon.redpack.event.amount
            else:
                coupon_year_rate = 0

            terms = amortization_cls.generate(equity.equity, product.expected_earning_rate / 100,
                                              product_interest_start, product.period, coupon_year_rate / 100)

            for index, term in enumerate(terms['terms']):
                amortization = UserAmortization()
                amortization.description = u'第%d期' % (index + 1)
                amortization.principal = term[1]
                amortization.interest = term[2]
                amortization.coupon_interest = term[4]
                amortization.term = index + 1
                amortization.user = equity.user
                try:
                    amortization.product_amortization = product_amortizations[index]
                except IndexError:
                    logger.error('generate amortization for product %s failed' % self.product)

                if len(term) == 7:
                    amortization.term_date = term[6]
                else:
                    amortization.term_date = timezone.now()

                user_amos.append(amortization)
            
            if terms['interest_arguments']:
                args = terms['interest_arguments'].update({"equity":equity})
                args = terms['interest_arguments']
                interest_precision = InterestPrecisionBalance(**args)
                interest_precisions.append(interest_precision)

        UserAmortization.objects.bulk_create(user_amos)
        InterestPrecisionBalance.objects.bulk_create(interest_precisions)

    # def __generate_useramortization(self, equities):
    #     """
    #     :param equities: 批量生成用户还款计划提高数据库存储性能
    #     :return:
    #     """
    #     user_amos = list()
    #     interest_precisions = list()
    #     exp = Decimal('0.00000001')
    #
    #     total_actual = Decimal('0')
    #
    #     for equity in equities:
    #         total_principal = equity.equity
    #         # total_interest = self.product_interest * equity.ratio
    #         paid_principal = Decimal('0')
    #         # paid_interest = Decimal('0')
    #         count = len(self.amortizations)
    #         for i, amo in enumerate(self.amortizations):
    #             if i+1 != count:
    #                 principal = equity.ratio * amo.principal
    #
    #             # paid_interest += interest
    #                 paid_principal += principal
    #             else:
    #                 principal = total_principal - paid_principal
    #                 # interest = total_interest - paid_interest
    #
    #             interest = equity.ratio * amo.interest
    #             principal_actual = principal.quantize(Decimal('.01'))
    #             interest_actual = interest.quantize(Decimal('.01'), ROUND_DOWN)
    #
    #             total_actual += interest_actual
    #
    #             user_amo = UserAmortization(
    #                 product_amortization=amo, user=equity.user, term=amo.term, term_date=amo.term_date,
    #                 principal=principal_actual, interest=interest_actual
    #             )
    #
    #             interest_precision = InterestPrecisionBalance(
    #                 equity=equity, principal=principal.quantize(exp),
    #                 interest_actual=interest_actual, interest_receivable=interest,
    #                 interest_precision_balance=(interest-interest_actual).quantize(exp)
    #             )
    #
    #             user_amos.append(user_amo)
    #             interest_precisions.append(interest_precision)
    #
    #     #记录某个标的总精度差额 author:hetao
    #     self.__precision(total_actual)
    #
    #     UserAmortization.objects.bulk_create(user_amos)
    #     InterestPrecisionBalance.objects.bulk_create(interest_precisions)

    def __precision(self, interest_actual):
        """
        记录某个标的总精度差额 author:hetao
        :param interest_actual: 实际支付利息
        :return:
        """

        total_receivable = Decimal('0')
        product_total_principal = Decimal('0')

        for amortization in self.amortizations:
            total_receivable += amortization.interest
            product_total_principal += amortization.principal

        total_precision = total_receivable - interest_actual
        product_precision = ProductInterestPrecision(
            product=self.product, principal=product_total_principal,
            interest_actual=interest_actual, interest_receivable=total_receivable,
            interest_precision_balance=total_precision
        )
        product_precision.save()

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
            #user_amo.save()

        UserAmortization.objects.bulk_create(user_amos)

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

            matches = re.search(u'日计息', product.pay_method)
            if matches and matches.group():
                pname = u"%s,期限%s天" % (product.name, product.period)
            else:
                pname = u"%s,期限%s个月" % (product.name, product.period)

            phone_list = list()
            message_list = list()
            for sub_amo in sub_amortizations:
                user_margin_keeper = MarginKeeper(sub_amo.user)
                user_margin_keeper.amortize(sub_amo.principal, sub_amo.interest, sub_amo.penal_interest,
                                            sub_amo.coupon_interest, savepoint=False, description=description)

                sub_amo.settled = True
                sub_amo.settlement_time = timezone.now()
                sub_amo.save()
                
                amo_amount = sub_amo.principal + sub_amo.interest + sub_amo.penal_interest + sub_amo.coupon_interest

                # 加入重复回款的用户还需要扣回的金额及扣款操作
                try:
                    repeat_user = RepeatPaymentUser.objects.select_for_update()\
                        .filter(user_id=sub_amo.user.id, amount__gt=0).first()
                    if repeat_user:
                        repeat_amount = repeat_user.amount
                        # if repeat_amount > 0:
                        # 判断是否每天从回款中扣款
                        is_every_day = True
                        if not repeat_user.is_every_day:
                            product_ids = repeat_user.product_ids.split(',')
                            product_ids = [int(p_id) for p_id in product_ids if p_id.strip() != '']
                            # 判断当期还款的产品id是否在用户新购标的id中, 不在说明该标不用扣款
                            if product.id not in product_ids:
                                is_every_day = False

                        if is_every_day:
                            # 判断剩余应扣金额是否大于等于本期回款本息之合, 大于等于,则扣本息,否则扣剩余应扣金额
                            if repeat_amount >= amo_amount:
                                reduce_amount = amo_amount
                                reduce_amount_current = repeat_amount - amo_amount  # 剩余应扣金额-本次扣除的本息之合
                            else:
                                reduce_amount = repeat_amount
                                reduce_amount_current = 0

                            print ("repeat_amount: %s, amo_amount: %s, type1:%s, type2:%s" % (
                                repeat_amount, amo_amount, type(repeat_amount), type(amo_amount)))

                            # 减账户余额
                            user_margin_keeper.reduce_margin(reduce_amount, u'系统重复回款扣回%s元' % reduce_amount)

                            # 更新剩余应扣金额
                            repeat_user.amount = reduce_amount_current
                            repeat_user.save()

                            # 记录扣款流水
                            repeat_record = RepeatPaymentUserRecords(user_id=sub_amo.user.id,
                                                                     name=sub_amo.user.wanglibaouserprofile.name,
                                                                     phone=sub_amo.user.wanglibaouserprofile.phone,
                                                                     amount=reduce_amount,
                                                                     amount_current=reduce_amount_current,
                                                                     description=description)
                            repeat_record.save()
                except Exception:
                    logger.exception('err')
                    logger.error("用户扣款失败,用户id:[%s], 回款本息合计:[%s]" % (sub_amo.user, amo_amount))
                    pass

                phone_list.append(sub_amo.user.wanglibaouserprofile.phone)
                message_list.append(messages.product_amortize(sub_amo.user.wanglibaouserprofile.name,
                                                              amortization.product,
                                                              # sub_amo.settlement_time,
                                                              amo_amount))
                title, content = messages.msg_bid_amortize(pname, timezone.now(), amo_amount)
                inside_message.send_one.apply_async(kwargs={
                    "user_id": sub_amo.user.id,
                    "title": title,
                    "content": content,
                    "mtype": "amortize"
                })
                self.__tracer(catalog, sub_amo.user, sub_amo.principal, sub_amo.interest, sub_amo.penal_interest,
                              amortization, description, sub_amo.coupon_interest)

                # 标的每一期还款完成后,检测该用户还款的本金是否有符合活动的规则,有的话触发活动规则
                try:
                    if sub_amo.principal > 0:
                        activity_backends.check_activity(sub_amo.user, 'repaid', 'pc', sub_amo.principal, product.id)
                except Exception:
                    logger.debug("check activity on repaid, user: {}, principal: {}, product_id: {}".format(
                        sub_amo.user, sub_amo.principal, product.id
                    ))
                try:
                    weixin_user = WeixinUser.objects.filter(user=sub_amo.user).first()
        #             {{first.DATA}} 项目名称：{{keyword1.DATA}} 还款金额：{{keyword2.DATA}} 还款时间：{{keyword3.DATA}} {{remark.DATA}}

                    if weixin_user and weixin_user.subscribe:
                        now = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
                        sentTemplate.apply_async(kwargs={
                                        "kwargs":json.dumps({
                                                        "openid": weixin_user.openid,
                                                        "template_id": PRODUCT_AMORTIZATION_TEMPLATE_ID,
                                                        "keyword1": product.name,
                                                        "keyword2": "%s 元"%str(amo_amount),
                                                        "keyword3": now,
                                                            })},
                                                        queue='celery02')

                except Exception,e:
                    pass
            amortization.settled = True
            amortization.save()
            catalog = u'还款入账'

            send_messages.apply_async(kwargs={
                "phones": phone_list,
                "messages": message_list
            })

            self.__tracer(catalog, None, amortization.principal, amortization.interest, amortization.penal_interest, amortization)

    def __tracer(self, catalog, user, principal, interest, penal_interest, amortization, description=u'', coupon_interest=0):
        trace = AmortizationRecord(
            amortization=amortization, term=amortization.term, principal=principal, interest=interest,
            penal_interest=penal_interest, coupon_interest=coupon_interest, description=description,
            user=user, catalog=catalog, order_id=self.order_id
        )
        trace.save()
        return trace


def check_amount(amount):
    pass
