// Generated by CoffeeScript 1.7.1
(function() {
  define(['jquery'], function($) {
    var addToFavorite, apiurl, changePassword, createPreOrder, isValidType, joinFavorites, loadData, loadFavorites, loadPortfolio, normalizeType, typeMapping;
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
      '基金': 'funds',
      '公募基金': 'funds',
      'cashs': 'cashes',
      'cashes': 'cashes',
      '现金类理财产品': 'cashes',
      '现金': 'cashes',
      'favorite/trusts': 'favorite/trusts'
    };
    normalizeType = function(type) {
      return typeMapping[type];
    };
    loadData = function(type, params) {
      var url;
      if (_.has(typeMapping, type)) {
        url = apiurl + typeMapping[type] + '/.jsonp?' + $.param(params);
        return $.ajax(url, {
          dataType: 'jsonp'
        });
      } else {
        if (typeof console !== "undefined" && console !== null) {
          return console.log("The type not supported");
        }
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
    changePassword = function(params) {
      var url;
      url = '/accounts/password/change/';
      return $.post(url, params);
    };
    addToFavorite = function(e, type, id, is_favorited) {
      var url;
      url = apiurl + 'favorite/' + type + '/';
      if (is_favorited !== '1') {
        return $.post(url, {
          item: id
        }).done(function() {
          $(e.target).html('取消收藏');
          return $(e.target).attr('data-is-favorited', '1');
        }).fail(function(xhr) {
          if (xhr.status === 403) {
            return window.location.href = '/accounts/login/?next=' + window.location.href;
          } else if (xhr.status === 409) {
            $(e.target).html('取消收藏');
            return $(e.target).attr('data-is-favorited', '1');
          } else {
            return alert('收藏失败');
          }
        });
      } else {
        return $.ajax({
          url: url + id + '/',
          type: 'DELETE'
        }).done(function() {
          e.target.textContent = '收藏';
          return $(e.target).attr('data-is-favorited', '0');
        }).fail(function() {
          return alert('取消收藏失败');
        });
      }
    };
    joinFavorites = function(products, type, table) {
      return loadData('favorite/' + type, {}).done(function(favorites) {
        var i, ids, product, _ref;
        ids = _.map(favorites.results, function(f) {
          return f.item.id;
        });
        _ref = products.results;
        for (i in _ref) {
          product = _ref[i];
          if (_.contains(ids, product.id)) {
            product.is_favorited = 1;
          }
        }
        return table.data(products.results);
      });
    };
    loadFavorites = function(type) {
      var url;
      url = apiurl + 'favorite/' + type + '/';
      return $.get(url);
    };
    window.addToFavorite = function(e) {
      var id, is_favorited;
      e.preventDefault();
      id = $(e.target).attr('data-id');
      is_favorited = $(e.target).attr('data-is-favorited');
      return addToFavorite(e, 'trusts', id, is_favorited);
    };
    return {
      loadData: loadData,
      isValidType: isValidType,
      loadPortfolio: loadPortfolio,
      createPreOrder: createPreOrder,
      changePassword: changePassword,
      addToFavorite: addToFavorite,
      loadFavorites: loadFavorites,
      joinFavorites: joinFavorites,
      normalizeType: normalizeType
    };
  });

}).call(this);

//# sourceMappingURL=backend.map
