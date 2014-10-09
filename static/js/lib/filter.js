(function() {
  define(["underscore"], function(_) {
    var arrayToFilter;
    arrayToFilter = function(names, field, defaultName) {
      var filters;
      if (defaultName == null) {
        defaultName = '不限';
      }
      filters = _.map(names, function(val, index) {
        return {
          name: val,
          values: _.object([[field, val]])
        };
      });
      return [
        {
          name: defaultName
        }
      ].concat(filters);
    };
    return {
      arrayToFilter: arrayToFilter
    };
  });
}).call(this);
