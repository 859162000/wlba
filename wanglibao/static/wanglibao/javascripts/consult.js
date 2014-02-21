// Generated by CoffeeScript 1.7.1
(function() {
  $(document).ready(function() {
    var ViewModel, model;
    ViewModel = (function() {
      function ViewModel() {
        var self;
        self = this;

        /*
        The user data: asset, risk, period, preference
         */
        self.asset = ko.observable(30);
        self.riskScore = ko.observable(2);
        self.period = ko.observable(6);
        self.preference = ko.observable(null);
        self.finishSurvey = function(data, event) {
          var asset, period, risk;
          asset = self.questions[0].answer();
          if (asset !== null && parseInt(asset) > 0) {
            self.asset(parseInt(asset));
          }
          period = self.questions[1].answer();
          if (period !== null && parseInt(period) > 0) {
            self.period(period);
          }
          risk = self.questions[2].answer();
          if (risk !== null) {
            self.riskScore(risk.value.risk_score);
          }
          return $.modal.close();
        };
        self.questions = [
          {
            question: '您的可投资资产是多少？',
            answer: ko.observable(),
            input: {
              suffix: '万元'
            }
          }, {
            question: '可以投资的期限是？',
            answer: ko.observable(),
            input: {
              suffix: '个月'
            }
          }, {
            question: '您的投资目标是？',
            answer: ko.observable(),
            options: [
              {
                title: '不能承担任何风险',
                value: {
                  risk_score: 2
                }
              }, {
                title: '可承担一定的风险来换取较高的收益',
                value: {
                  risk_score: 3
                }
              }, {
                title: '可以承担很大的风险来追求高收益',
                value: {
                  risk_score: 4
                }
              }, {
                title: '绝对追求高收益',
                value: {
                  risk_score: 5
                }
              }
            ]
          }
        ];

        /*
        The portfolio related stuff
         */
        self.titleWidthPercent = 10;
        self.portfolios = ko.observableArray([]);
        ko.computed(function() {
          var params, url;
          params = {
            asset_min: self.asset(),
            asset_max: self.asset(),
            period_min: self.period(),
            period_max: self.period(),
            risk_score: self.riskScore(),
            investment_preference: self.preference()
          };
          url = 'http://127.0.0.1:8000/api/portfolios/.jsonp?' + $.param(params);
          return $.ajax(url, {
            dataType: 'jsonp'
          }).done(function(data) {
            return self.portfolios(data.results);
          });
        }).extend({
          throttle: 1
        });
        self.productDescription = function(productEntry) {
          var amount, percent;
          percent = 0;
          amount = 0;
          if (productEntry.type === 'percent') {
            percent = productEntry.value;
            amount = percent / 100 * self.asset();
          } else {
            amount = productEntry.value;
            percent = amount / self.asset() * 100;
          }
          return amount.toFixed(0) + '万 ' + percent.toFixed(0) + '%';
        };
        self.productWidth = function(productEntry, portfolio) {
          return (100 - self.titleWidthPercent) / portfolio.products.length + '%';
        };

        /*
        The filtered products related stuff
         */
        self.products = null;
        self.productsType = ko.observable('trusts');
        self.template_name = ko.observable('trust-table');
        self.amount = ko.observable(0);
        self.setSelectedProduct = function(value, event) {
          var amount, productTypeName;
          amount = value.value;
          if (value.type === 'percent') {
            amount = amount / 100 * self.asset();
          }
          self.amount(amount);
          productTypeName = value.product.name;
          if (productTypeName === '信托') {
            return self.productsType('trusts');
          } else if (productTypeName === '银行理财') {
            return self.productsType('bank_financings');
          } else {
            return self.productsType(null);
          }
        };
        self.productMapping = {
          trusts: {
            template: 'trust-table'
          },
          bank_financings: {
            template: 'financing-table'
          }
        };
        ko.computed(function() {
          var amount, type, url;
          type = self.productsType();
          amount = self.amount();
          if (type) {
            url = 'http://127.0.0.1:8000/api/' + type + '/.jsonp?count=10&max_threshold=' + amount;
            return $.ajax(url, {
              dataType: 'jsonp'
            }).done(function(data) {
              self.products = data.results;
              if (self.products.length > 0) {
                self.template_name('');
                return self.template_name(self.productMapping[type].template);
              } else {
                return self.template_name('no-products-available');
              }
            });
          } else {
            return console.log('The type not supported');
          }
        }).extend({
          throttle: 1
        });
      }

      return ViewModel;

    })();
    model = new ViewModel();
    return ko.applyBindings(model);
  });

}).call(this);

//# sourceMappingURL=consult.map
