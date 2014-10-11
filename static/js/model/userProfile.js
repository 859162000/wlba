(function() {
  define([], function() {
    var viewModel;
    viewModel = (function() {
      function viewModel(context) {
        var self;
        self = this;
        self.name = ko.observable();
        self.phone = ko.observable();
        self.asset = ko.observable();
        self.riskScore = ko.observable();
        self.period = ko.observable();
      }
      return viewModel;
    })();
    return {
      viewModel: viewModel
    };
  });
}).call(this);
