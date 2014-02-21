// Generated by CoffeeScript 1.7.1
(function() {
  $(document).ready(function() {
    var DataViewModel, model;
    DataViewModel = function() {
      var self;
      self = this;
      self.trusts = ko.observable([]);
      self.tabTree = [
        {
          name: '按期限',
          values: [
            {
              name: '12个月以内',
              filter: {
                max_period: 12
              }
            }, {
              name: '12个月-24个月',
              filter: {
                min_period: 12,
                max_period: 24
              }
            }, {
              name: '24个月以上',
              filter: {
                min_period: 24
              }
            }
          ]
        }, {
          name: '按起点',
          values: [
            {
              name: '100万以下',
              filter: {
                'max_threshold': 100.0
              }
            }, {
              name: '100万-300万',
              filter: {
                min_threshold: 100.0,
                max_threshold: 300.0
              }
            }, {
              name: '300万以上',
              filter: {
                min_threshold: 300
              }
            }
          ]
        }, {
          name: '按收益',
          values: [
            {
              name: '13%以上',
              filter: {
                min_rate: 13
              }
            }, {
              name: '10%-13%',
              filter: {
                min_rate: 10,
                max_rate: 13
              }
            }, {
              name: '低于10%',
              filter: {
                max_rate: 10
              }
            }
          ]
        }
      ];
      self.selectedTab = ko.observable(self.tabTree[0]);
      self.selectedValue = ko.observable(self.selectedTab().values[0]);
      self.setSelectedTab = function(tab) {
        return self.selectedTab(tab);
      };
      self.setSelectedValue = function(value) {
        var filter, url;
        self.selectedValue(value);
        filter = $.param(value.filter);
        url = 'http://127.0.0.1:8000/api/trusts/.jsonp?&ordering=-issue_date&' + filter;
        return $.ajax(url, {
          dataType: 'jsonp'
        }).done(function(data) {
          return model.trusts(data.results);
        }).fail(function(xhr, status, error) {
          return alert(status + error);
        });
      };
    };
    model = new DataViewModel();
    return ko.applyBindings(model);
  });

}).call(this);

//# sourceMappingURL=trust_home.map
