// Generated by CoffeeScript 1.7.1
(function() {
  define(['jquery'], function($) {
    var addToFavorite, apiurl, changePassword, createPreOrder, deepCompare, isValidType, joinFavorites, loadData, loadFavorites, loadPortfolio, normalizeType, parseQuery, typeMapping, userExists, userProfile;
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
      '货币基金': [
        'funds', {
          type: '货币型'
        }
      ],
      'cashs': 'cashes',
      'cashes': 'cashes',
      '现金类理财产品': 'cashes',
      '现金': 'cashes',
      'favorite/trusts': 'favorite/trusts',
      'favorite/funds': 'favorite/funds',
      'favorite/cashes': 'favorite/cashes',
      'favorite/financings': 'favorite/financings'
    };
    normalizeType = function(type) {
      var typeRecord;
      typeRecord = typeMapping[type];
      if (typeof typeRecord === 'string') {
        return typeRecord;
      } else {
        return typeRecord[0];
      }
    };
    loadData = function(type, params) {
      var normalizedType, typeRecord, url;
      if (_.has(typeMapping, type)) {
        typeRecord = typeMapping[type];
        normalizedType = typeRecord;
        if (typeof typeRecord !== 'string') {
          normalizedType = typeRecord[0];
          params = _.extend(params, typeRecord[1]);
        }
        url = apiurl + normalizedType + '/.jsonp?' + $.param(params);
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
    addToFavorite = function(e, type) {
      var id, is_favorited, url;
      e.preventDefault();
      id = $(e.target).attr('data-id');
      is_favorited = $(e.target).attr('data-is-favorited');
      url = apiurl + 'favorite/' + type + '/';
      if (is_favorited !== '1') {
        return $.post(url, {
          item: id
        }).done(function() {
          $(e.target).html('取消');
          return $(e.target).attr('data-is-favorited', '1');
        }).fail(function(xhr) {
          if (xhr.status === 403) {
            return window.location.href = '/accounts/login/?next=' + window.location.href;
          } else if (xhr.status === 409) {
            $(e.target).html('取消');
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
    joinFavorites = function(products, type, table, transformer) {
      return loadData('favorite/' + type, {}).done(function(favorites) {
        var i, ids, product, _ref, _results;
        ids = _.map(favorites.results, function(f) {
          return f.item.id;
        });
        _ref = products.results;
        _results = [];
        for (i in _ref) {
          product = _ref[i];
          if (_.contains(ids, product.id)) {
            _results.push(product.is_favorited = 1);
          } else {
            _results.push(void 0);
          }
        }
        return _results;
      }).always(function() {
        var data;
        if (transformer) {
          data = transformer(products);
          return table.data(data);
        } else {
          return table.data(products.results);
        }
      });
    };
    loadFavorites = function(type) {
      var url;
      url = apiurl + 'favorite/' + type + '/';
      return $.get(url);
    };
    userExists = function(identifier) {
      var url;
      url = apiurl + 'user_exists/' + identifier + '/';
      return $.get(url);
    };
    userProfile = function(data) {
      var url;
      url = apiurl + 'profile/';
      if (data == null) {
        return $.get(url);
      } else {
        return $.ajax({
          url: url,
          type: 'PUT',
          data: data
        });
      }
    };
    window.addToFavorite = function(e, type) {
      var id, is_favorited;
      e.preventDefault();
      id = $(e.target).attr('data-id');
      is_favorited = $(e.target).attr('data-is-favorited');
      return addToFavorite(e, type, id, is_favorited);
    };
    parseQuery = function(search) {
      var queries;
      queries = {};
      $.each(search.substr(1).split('&'), function(index, value) {
        var pair;
        pair = value.split('=');
        if (pair.length === 2) {
          return queries[pair[0].toString()] = pair[1].toString();
        }
      });
      return queries;
    };
    deepCompare = function(x, y) {
      var compare2Objects, leftChain, rightChain;
      compare2Objects = function(x, y) {
        var p;
        p = void 0;
        if (isNaN(x) && isNaN(y) && typeof x === "number" && typeof y === "number") {
          return true;
        }
        if (x === y) {
          return true;
        }
        if ((typeof x === "function" && typeof y === "function") || (x instanceof Date && y instanceof Date) || (x instanceof RegExp && y instanceof RegExp) || (x instanceof String && y instanceof String) || (x instanceof Number && y instanceof Number)) {
          return x.toString() === y.toString();
        }
        if (!(x instanceof Object && y instanceof Object)) {
          return false;
        }
        if (x.isPrototypeOf(y) || y.isPrototypeOf(x)) {
          return false;
        }
        if (leftChain.indexOf(x) > -1 || rightChain.indexOf(y) > -1) {
          return false;
        }
        for (p in y) {
          if (y.hasOwnProperty(p) !== x.hasOwnProperty(p)) {
            return false;
          } else {
            if (typeof y[p] !== typeof x[p]) {
              return false;
            }
          }
        }
        for (p in x) {
          if (y.hasOwnProperty(p) !== x.hasOwnProperty(p)) {
            return false;
          } else {
            if (typeof y[p] !== typeof x[p]) {
              return false;
            }
          }
          switch (typeof x[p]) {
            case "object":
            case "function":
              leftChain.push(x);
              rightChain.push(y);
              if (!compare2Objects(x[p], y[p])) {
                return false;
              }
              leftChain.pop();
              rightChain.pop();
              break;
            default:
              if (x[p] !== y[p]) {
                return false;
              }
          }
        }
        return true;
      };
      leftChain = [];
      rightChain = [];
      return compare2Objects(x, y);
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
      normalizeType: normalizeType,
      userExists: userExists,
      userProfile: userProfile,
      parseQuery: parseQuery,
      deepCompare: deepCompare
    };
  });

}).call(this);

//# sourceMappingURL=backend.map
