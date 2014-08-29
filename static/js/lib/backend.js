// Generated by CoffeeScript 1.7.1
(function() {
  define(['jquery'], function($) {
    var addToFavorite, apiurl, changePassword, checkBalance, checkCardNo, checkEmail, checkMobile, checkMoney, createPreOrder, fundInfo, isInRange, isValidType, joinFavorites, loadData, loadFavorites, loadPortfolio, normalizeType, purchaseP2P, typeMapping, userExists, userProfile;
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
      'p2p': 'p2ps',
      'P2P': 'p2ps',
      'p2ps': 'p2ps',
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
    addToFavorite = function(target, type) {
      var id, is_favorited, url;
      id = $(target).data('id');
      is_favorited = $(target).attr('data-is-favorited');
      url = apiurl + 'favorite/' + type + '/';
      if (is_favorited !== '1') {
        return $.post(url, {
          item: id
        }).done(function() {
          $(target).html('取消收藏');
          $(target).addClass('button-no-border');
          return $(target).attr('data-is-favorited', '1');
        }).fail(function(xhr) {
          if (xhr.status === 403) {
            return window.location.href = '/accounts/register/?next=' + window.location.href;
          } else if (xhr.status === 409) {
            $(target).html('取消');
            $(target).addClass('button-no-border');
            return $(target).attr('data-is-favorited', '1');
          } else {
            return alert('收藏失败');
          }
        });
      } else {
        return $.ajax({
          url: url + id + '/',
          type: 'DELETE'
        }).done(function() {
          $(target).html('收藏');
          $(target).attr('data-is-favorited', '0');
          return $(target).removeClass('button-no-border');
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
          table.data(data);
        } else {
          table.data(products.results);
        }
        return table.isEmpty(table.data().length === 0);
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
    fundInfo = function() {
      var url;
      url = apiurl + 'fund_info/';
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
      var target;
      e = e || window.event;
      target = e.target || e.srcElement;
      if (e.preventDefault) {
        e.preventDefault();
      }
      return addToFavorite(target, type);
    };
    isInRange = function(param, range) {
      var params, ranges;
      if (param === range) {
        return true;
      }
      if (!range) {
        return false;
      }
      params = param.split('-');
      ranges = range.split('-');
      if (ranges.length === 1) {
        ranges[0] = ranges[0].substr(1);
      }
      if (params.length === 1) {
        if (params[0][0] === '>') {
          params[0] = params[0].substr(1);
        }
        params[0] = parseInt(params[0]);
        if (ranges.length === 2) {
          if (params[0] >= ranges[0] && params[0] <= ranges[1]) {
            return true;
          } else {
            return false;
          }
        }
        if (ranges.length === 1) {
          if (params[0] >= ranges[0]) {
            return true;
          } else {
            return false;
          }
        }
      }
      if (params.length === 2) {
        params[0] = parseInt(params[0]);
        params[1] = parseInt(params[1]);
        if (ranges.length === 2) {
          if (params[0] >= ranges[0] && params[1] <= ranges[1]) {
            return true;
          } else {
            return false;
          }
        }
        if (ranges.length === 1) {
          if (params[0] >= ranges[0]) {
            return true;
          } else {
            return false;
          }
        }
      }
    };
    checkEmail = function(identifier) {
      var re;
      re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(identifier);
    };
    checkMobile = function(identifier) {
      var re;
      re = /^1\d{10}$/;
      return re.test(identifier);
    };
    checkBalance = function(amount, element) {
      var balance;
      balance = $(element).attr('data-balance');
      return (amount - balance).toFixed(2) <= 0;
    };
    checkMoney = function(amount, element) {
      var re;
      re = /^\d+(\.\d{0,2})?$/;
      return re.test(amount);
    };
    checkCardNo = function(card_no) {
      var re;
      re = /^\d{10,20}$/;
      return re.test(card_no);
    };
    purchaseP2P = function(data) {
      return $.post('/api/p2p/purchase/', data);
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
      fundInfo: fundInfo,
      userProfile: userProfile,
      isInRange: isInRange,
      checkEmail: checkEmail,
      checkMobile: checkMobile,
      purchaseP2P: purchaseP2P,
      checkBalance: checkBalance,
      checkMoney: checkMoney,
      checkCardNo: checkCardNo
    };
  });

}).call(this);

//# sourceMappingURL=backend.map
