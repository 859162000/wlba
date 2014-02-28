from trust.mock_generator import MockGenerator as TrustMockGenerator
from wanglibao_fund.mock_generator import MockGenerator as FundMockGenerator
from wanglibao_bank_financing.mock_generator import BankFinancingMockGenerator
from wanglibao_portfolio.mock_generator import MockGenerator as PortfolioMockGenerator

class MockGenerator(object):

    @classmethod
    def generate(cls, clean=False):
        print 'Generating trust issuer and trusts'
        TrustMockGenerator.generate_issuer(clean)
        TrustMockGenerator.generate_trust(clean)

        print 'Generating issuer and funds'
        FundMockGenerator.generate_fund_issuers(clean)
        FundMockGenerator.generate_fund(clean)

        print 'Generating bank and financings'
        BankFinancingMockGenerator.generateBank(clean)
        BankFinancingMockGenerator.generateBankFinancing(clean)

        print 'Generating portfolios'
        PortfolioMockGenerator.generate_products(clean)
        PortfolioMockGenerator.load_portfolio_from_file('fixture/portfolio.csv')

