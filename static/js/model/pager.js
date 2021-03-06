// Generated by CoffeeScript 1.8.0
(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  define(['underscore', 'knockout'], function(_, ko) {
    var viewModel;
    viewModel = (function() {
      function viewModel(context) {
        this.increasePageNumber = __bind(this.increasePageNumber, this);
        this.decreasePageNumber = __bind(this.decreasePageNumber, this);
        this.currentPageNumber = __bind(this.currentPageNumber, this);
        this.pageNumberChanged = __bind(this.pageNumberChanged, this);
        var self;
        self = this;
        self.totalPageNumber = ko.observable(10);
        self._currentPageNumber = ko.observable(1);
        self.events = {};
        if (context && _.has(context, 'events')) {
          _(self.events).extend(context.events);
        }
      }

      viewModel.prototype.pageNumberChanged = function(data, event) {
        if (data > 0 && data <= this.totalPageNumber()) {
          this._currentPageNumber(data);
          if (_.has(this.events, 'pageNumberChanged')) {
            return this.events.pageNumberChanged(data, event);
          } else {
            if (typeof console !== "undefined" && console !== null) {
              return console.log('page number changed: ' + data);
            }
          }
        }
      };

      viewModel.prototype.currentPageNumber = function(data) {
        if (data) {
          return this.pageNumberChanged(data);
        } else {
          return this._currentPageNumber();
        }
      };

      viewModel.prototype.decreasePageNumber = function(data, event) {
        return this.currentPageNumber(this._currentPageNumber() - 1);
      };

      viewModel.prototype.increasePageNumber = function(data, event) {
        return this.currentPageNumber(this._currentPageNumber() + 1);
      };

      return viewModel;

    })();
    return {
      viewModel: viewModel
    };
  });

}).call(this);
