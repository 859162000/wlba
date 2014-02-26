// Generated by CoffeeScript 1.7.1
(function() {
  define(['jquery'], function($) {
    var apiurl, createPreOrder, isValidType, loadData, loadPortfolio, typeMapping;
    $(document).ajaxSend(function(event, xhr, settings) {
      var getCookie, safeMethod, sameOrigin;
      getCookie = function(name) {
        var cookie, cookieValue, cookies, i, _i, _ref;
        cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          cookies = document.cookie.split(';');
          for (i = _i = 0, _ref = document.cookie.length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
            cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      };
      sameOrigin = function(url) {
        var host, origin, protocol, sr_origin;
        host = document.location.host;
        protocol = document.location.protocol;
        sr_origin = '//' + host;
        origin = protocol + sr_origin;
        return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
      };
      safeMethod = function(method) {
        return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
      };
      if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        return xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    });
    apiurl = '/api/';
    if (document.location.protocol === 'file:') {
      apiurl = 'http://127.0.0.1:8000/api/';
    }
    typeMapping = {
      '信托': 'trusts',
      'trust': 'trusts',
      'trusts': 'trusts',
      '银行理财': 'bank_financings',
      'bank': 'bank_financings',
      'financing': 'bank_financings',
      'financings': 'bank_financings',
      'bank_financings': 'bank_financings',
      'fund': 'funds',
      'funds': 'funds',
      '基金': 'funds'
    };
    loadData = function(type, params) {
      var url;
      if (_.has(typeMapping, type)) {
        url = apiurl + typeMapping[type] + '/.jsonp?' + $.param(params);
        return $.ajax(url, {
          dataType: 'jsonp'
        });
      } else {
        return console.log("The type not supported");
      }
    };
    loadPortfolio = function(params) {
      var url;
      url = apiurl + 'portfolios/.jsonp?' + $.param(params);
      return $.ajax(url, {
        dataType: 'jsonp'
      });
    };
    isValidType = function(type) {
      return _.has(typeMapping, type);
    };
    createPreOrder = function(params) {
      var url;
      url = apiurl + 'pre_orders/';
      return $.post(url, {
        product_url: params.product_url,
        product_type: params.product_type,
        product_name: params.product_name,
        user_name: params.user_name,
        phone: params.phone
      });
    };
    return {
      loadData: loadData,
      isValidType: isValidType,
      loadPortfolio: loadPortfolio,
      createPreOrder: createPreOrder
    };
  });

}).call(this);

//# sourceMappingURL=backend.map
