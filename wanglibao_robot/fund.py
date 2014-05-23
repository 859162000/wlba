# -*- coding: utf-8 -*-
from wanglibao_fund.models import Fund, FundIssuer
from shumi_backend.fetch import AppLevel
from shumi_backend.utility import mapping_fund_details, mapping_fund_issuer, mapping_fund_details_plus
from shumi_backend.exception import FetchException

class FundRobot(object):

    def __init__(self):
        self.fetcher = AppLevel()

    def run_robot(self):
        # run sync_issuer before run_robot, in case guarantee related fund issuers existed.
        info = self.fetcher.fund_details()
        cash_info = [fund for fund in info if fund['fund_type'] == 7]

        funds = Fund.objects.all()
        funds_dict = {fund.product_code: fund for fund in funds}

        issuer_info = self.fetcher.fund_issuers()
        issuer_dict = {issuer_record['guid']: issuer_record for issuer_record in issuer_info}

        for cash in cash_info:
            print cash
            issuer = FundIssuer.objects.filter(uuid=cash['invest_advisor_guid']).first()

            if not issuer:
                # try retrieve fund issuer object by uuid.
                try:
                    issuer = FundIssuer(**mapping_fund_issuer(issuer_dict[cash['invest_advisor_guid']]))
                    issuer.save()
                # if no match uuid, log and continue.
                except KeyError:
                    continue
                except Exception, e:
                    print(e)
                    continue

            try:
                target_fund = funds_dict[cash['fund_code']]
                self.model_setter(target_fund, mapping_fund_details(cash, False))
                target_fund.issuer = issuer

            except KeyError:
                target_fund = Fund(issuer=issuer, **mapping_fund_details(cash))
                print('create new fund')

            # retrieve cash fund detail plus info
            try:
                detail_plus = self.fetcher.fund_details_plus(target_fund.product_code)
                self.model_setter(target_fund, mapping_fund_details_plus(detail_plus[0]))
            except FetchException:
                pass
            except KeyError:
                pass

            try:
                target_fund.save()
            except Exception, e:
                print(e)

    def sync_issuer(self):
        try:
            info = self.fetcher.fund_issuers()
        except FetchException:
            pass

        issuers = FundIssuer.objects.all()
        issuers_dict = {issuer.name: issuer for issuer in issuers}
        for issuer_info in info:
            try:
                target_issuer = issuers_dict[issuer_info['name']]
                target_issuer.uuid = issuer_info['guid']
            except KeyError:
                target_issuer = FundIssuer(name=issuer_info['name'], description=issuer_info['background'] or '',
                                           home_page=issuer_info['direct_sell_url'] or '', uuid=issuer_info['guid'])

            target_issuer.save()

    def update_issuer(self):
        try:
            info = self.fetcher.fund_issuers()
        except FetchException:
            pass

        issuers = FundIssuer.objects.all()
        issuers_dict = {issuer.uuid: issuer for issuer in issuers}
        for issuer_info in info:
            try:
                target_issuer = issuers_dict[issuer_info['guid']]
                target_issuer.description= issuer_info['background'] or ''
                target_issuer.name = issuer_info['name']
                target_issuer.home_page = issuer_info['direct_sell_url'] or ''
            except KeyError:
                target_issuer = FundIssuer(name=issuer_info['name'], description=issuer_info['background'] or '',
                                           home_page=issuer_info['direct_sell_url'] or '', uuid=issuer_info['guid'])

            target_issuer.save()


    def model_setter(self, model, value_dict):
        for key in value_dict.keys():
            setattr(model, key, value_dict[key])
