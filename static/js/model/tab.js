// Generated by CoffeeScript 1.9.0
(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  define(['jquery', 'underscore', 'knockout'], function($, _, ko) {
    var viewModel;
    viewModel = (function() {
      function viewModel(context) {
        this.data = __bind(this.data, this);
        this.tabSelected = __bind(this.tabSelected, this);
        var self;
        self = this;
        self.tabs = ko.observableArray();
        self.selectedTab = ko.observable();
        self.events = {};
        this.data(context);
      }

      viewModel.prototype.tabSelected = function(data, event) {
        this.selectedTab(data);
        if (_.has(this.events, 'tabSelected')) {
          return this.events.tabSelected(data, event);
        } else {
          if (typeof console !== "undefined" && console !== null) {
            return console.log('tab selected ' + data);
          }
        }
      };

      viewModel.prototype.data = function(context) {
        if (context) {
          if (_.has(context, 'events')) {
            _(this.events).extend(context.events);
          }
          if (_.has(context, 'tabs')) {
            this.tabs(context.tabs);
            return this.tabSelected(this.tabs()[0]);
          }
        }
      };

      return viewModel;

    })();
    return {
      viewModel: viewModel
    };
  });

}).call(this);

//# sourceMappingURL=tab.js.map
