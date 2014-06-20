from trust.mock_generator import MockGenerator as TrustMockGenerator
from wanglibao_fund.mock_generator import MockGenerator as FundMockGenerator
from wanglibao_pay.mock_generator import PayMockGenerator
from wanglibao_portfolio.mock_generator import MockGenerator as PortfolioMockGenerator
from wanglibao_hotlist.mock_generator import MockGenerator as HotlistMockGenerator
from wanglibao_p2p.mock_generator import MockGenerator as P2PMockGenerator


class MockGenerator(object):

    @classmethod
    def generate(cls, clean=False):
        print 'Generating trust issuer and trusts'
        TrustMockGenerator.generate_issuer(clean)
        TrustMockGenerator.generate_trust(clean)

        print 'Generating issuer and funds'
        FundMockGenerator.generate_fund_issuers(clean)
        FundMockGenerator.generate_fund(clean)

        print 'Generating portfolios'
        PortfolioMockGenerator.generate_products(clean)
        PortfolioMockGenerator.load_portfolio_from_file('fixture/portfolio.csv', clean)

        print 'Generating hot list'
        HotlistMockGenerator.generate(clean)

        print 'Generating pay info'
        PayMockGenerator.generate_bank(clean)
        PayMockGenerator.generate_card(clean)

        print 'Generating p2p'
        P2PMockGenerator.generate_p2p(clean)
