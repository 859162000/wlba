// Generated by CoffeeScript 1.7.1
(function() {
  $(document).ready(function() {
    var DataViewModel, viewModel;
    DataViewModel = (function() {
      function DataViewModel() {
        var self;
        self = this;
        self.tabTree = [
          {
            name: '全部'
          }, {
            name: '股票型',
            values: {
              type: '股票型'
            }
          }, {
            name: '债券型',
            values: {
              type: '债券型'
            }
          }, {
            name: '货币型',
            values: {
              type: '货币型'
            }
          }, {
            name: '混合型',
            values: {
              type: '混合型'
            }
          }, {
            name: '保本型',
            values: {
              type: '保本型'
            }
          }, {
            name: '短期理财',
            values: {
              type: '短期理财'
            }
          }
        ];
        self.selectedTab = ko.observable(self.tabTree[0]);
        self.products = ko.observable();
        self.frontEndRate = function(value) {
          if (value.issue_front_end_charge_rates.length > 0) {
            return value.issue_front_end_charge_rates[0].value.toFixed(2) + '%';
          }
          return '--';
        };
        self.backEndRate = function(value) {
          if (value.issue_back_end_charge_rates.length > 0) {
            return value.issue_back_end_charge_rates[0].value.toFixed(2) + '%';
          }
          return '--';
        };
        ko.computed(function() {
          var params, queryString, url;
          params = _.extend({
            count: 10
          }, self.selectedTab().values);
          queryString = $.param(params);
          url = 'http://127.0.0.1:8000/api/funds/.jsonp?&' + queryString;
          console.log(url);
          return $.ajax(url, {
            dataType: 'jsonp'
          }).done(function(data) {
            return self.products(data.results);
          });
        }).extend({
          throttle: 1
        });
      }

      return DataViewModel;

    })();
    viewModel = new DataViewModel();
    return ko.applyBindings(viewModel);
  });

}).call(this);

//# sourceMappingURL=fund_home.map
