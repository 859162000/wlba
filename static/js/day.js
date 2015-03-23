// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    var Y, count_down, data, date, day, fmoney, hight, init, m, shuju;
    init = function(time) {
      var csrfSafeMethod, getCookie, sameOrigin;
      csrfSafeMethod = void 0;
      getCookie = void 0;
      sameOrigin = void 0;
      getCookie = function(name) {
        var cookie, cookieValue, cookies, i;
        cookie = void 0;
        cookieValue = void 0;
        cookies = void 0;
        i = void 0;
        cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          cookies = document.cookie.split(';');
          i = 0;
          while (i < cookies.length) {
            cookie = $.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === name + '=') {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
            i++;
          }
        }
        return cookieValue;
      };
      csrfSafeMethod = function(method) {
        return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
      };
      sameOrigin = function(url) {
        var host, origin, protocol, sr_origin;
        host = void 0;
        origin = void 0;
        protocol = void 0;
        sr_origin = void 0;
        host = document.location.host;
        protocol = document.location.protocol;
        sr_origin = '//' + host;
        origin = protocol + sr_origin;
        return url === origin || url.slice(0, origin.length + 1) === origin + '/' || url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/' || !/^(\/\/|http:|https:).*/.test(url);
      };
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
          }
        }
      });
      shuju(time);
    };
    count_down = function(o) {
      var sec, timer;
      sec = (new Date(o.replace(/-/ig, '/')).getTime() - new Date().getTime()) / 1000;
      sec = parseInt(sec);
      timer = setTimeout((function() {
        count_down(o);
      }), 1000);
      if (sec <= 0) {
        $('.mon').html('4 月');
        $('.day-long').animate({
          'left': '-357px'
        }, 500);
        hight(m, '.day-si');
        clearTimeout(timer);
        count_down('2015-04-31 24:00:00');
      }
    };
    hight = function(high_m, ele) {
      var g, k, _results;
      g = 0;
      _results = [];
      while (g < $('.day-yue li').length - 2) {
        k = 0;
        while (k < $(ele + ' li:eq(' + g + ')').children('span').length) {
          if (m === high_m && day === parseInt($(ele + ' li:eq(' + g + ')').children('span:eq(' + k + ')').text())) {
            $(ele + ' li:eq(' + g + ')').children('span:eq(' + k + ')').addClass('tap-hight2').siblings().removeClass('tap-hight2');
            $(ele + ' li:eq(' + g + ')').children('span:eq(' + k + ')').css({
              'background': 'rgb(244, 136, 144)',
              'color': '#000'
            });
          }
          k++;
        }
        _results.push(g++);
      }
      return _results;
    };
    fmoney = function(s, n) {
      var i, l, r, t;
      n = n > 0 && n <= 20 ? n : 2;
      s = parseFloat((s + '').replace(/[^\d\.-]/g, '')).toFixed(n) + '';
      l = s.split('.')[0].split('').reverse();
      r = s.split('.')[1];
      t = '';
      i = 0;
      while (i < l.length) {
        t += l[i] + ((i + 1) % 3 === 0 && i + 1 !== l.length ? ',' : '');
        i++;
      }
      return t.split('').reverse().join('');
    };
    shuju = function(time) {
      return $.ajax({
        url: '/api/investment_history/',
        data: {
          day: time
        },
        type: 'POST'
      }).done(function(data) {
        var Y, date, day, j, m, str, str2, str3, str4, str5, _results, _results1;
        data = JSON.parse(data);
        date = new Date();
        Y = date.getFullYear();
        m = date.getMonth() + 1;
        day = date.getDate();
        if (day.length < 2) {
          day = '0' + day;
        }
        date = Y + '-0' + m + "-" + day;
        j = 0;
        str = '<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>';
        str2 = '<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>';
        str3 = '<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>';
        str4 = '<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>';
        str5 = '<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>';
        if (date !== time) {
          _results = [];
          while (j < 10) {
            if (data[0]['tops_len'] === 0) {
              console.log(time);
              if (j % 2 === 0) {
                str3 += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>－－</span><span>－－</span></li>';
                $('#dan').html(str3);
              }
              if (j % 2 !== 0) {
                str4 += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>－－</span><span>－－</span></li>';
                $('#shuang').html(str4);
              }
            }
            if (data[0]['tops_len'] !== 0) {
              if (data[0]['tops_len'] === 1) {
                if (j % 2 === 0) {
                  if (j < data[0]['tops_len']) {
                    str += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>' + data[0]['tops'][j]['phone'] + '</span><span>' + fmoney(data[0]['tops'][j]['amount_sum']) + ' 元</span></li>';
                    $('#dan').html(str);
                  }
                  if (j > data[0]['tops_len']) {
                    str3 = '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>－－</span><span>－－</span></li>';
                    $('#dan').append(str3);
                  }
                }
                if (j % 2 !== 0) {
                  str5 += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>－－</span><span>－－</span></li>';
                  $('#shuang').html(str5);
                }
              } else {
                if (j % 2 === 0) {
                  if (j < data[0]['tops_len']) {
                    str += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>' + data[0]['tops'][j]['phone'] + '</span><span>' + fmoney(data[0]['tops'][j]['amount_sum']) + ' 元</span></li>';
                    $('#dan').html(str);
                  }
                  if (j >= data[0]['tops_len']) {
                    str3 = '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>－－</span><span>－－</span></li>';
                    $('#dan').append(str3);
                  }
                }
                if (j % 2 !== 0) {
                  if (j < data[0]['tops_len']) {
                    str2 += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>' + data[0]['tops'][j]['phone'] + '</span><span>' + fmoney(data[0]['tops'][j]['amount_sum']) + ' 元</span></li>';
                    $('#shuang').html(str2);
                  }
                  if (j >= data[0]['tops_len']) {
                    str3 = '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>－－</span><span>－－</span></li>';
                    $('#shuang').append(str3);
                  }
                }
              }
            }
            _results.push(j++);
          }
          return _results;
        } else {
          _results1 = [];
          while (j < 10) {
            if (data[0]['tops_len'] === 0) {
              if (j % 2 === 0) {
                str3 += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>虚位以待</span><span>虚位以待</span></li>';
                $('#dan').html(str3);
              }
              if (j % 2 !== 0) {
                str4 += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>虚位以待</span><span>虚位以待</span></li>';
                $('#shuang').html(str4);
              }
            }
            if (data[0]['tops_len'] !== 0) {
              if (data[0]['tops_len'] === 1) {
                if (j % 2 === 0) {
                  if (j < data[0]['tops_len']) {
                    str += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>' + data[0]['tops'][j]['phone'] + '</span><span>' + fmoney(data[0]['tops'][j]['amount_sum']) + ' 元</span></li>';
                    $('#dan').html(str);
                  }
                  if (j > data[0]['tops_len']) {
                    str3 = '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>虚位以待</span><span>虚位以待</span></li>';
                    $('#dan').append(str3);
                  }
                }
                if (j % 2 !== 0) {
                  str5 += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>虚位以待</span><span>虚位以待</span></li>';
                  $('#shuang').html(str5);
                }
              } else {
                if (j % 2 === 0) {
                  if (j < data[0]['tops_len']) {
                    str += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>' + data[0]['tops'][j]['phone'] + '</span><span>' + fmoney(data[0]['tops'][j]['amount_sum']) + ' 元</span></li>';
                    $('#dan').html(str);
                  }
                  if (j >= data[0]['tops_len']) {
                    str3 = '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>虚位以待</span><span>虚位以待</span></li>';
                    $('#dan').append(str3);
                  }
                }
                if (j % 2 !== 0) {
                  if (j < data[0]['tops_len']) {
                    str2 += '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>' + data[0]['tops'][j]['phone'] + '</span><span>' + fmoney(data[0]['tops'][j]['amount_sum']) + ' 元</span></li>';
                    $('#shuang').html(str2);
                  }
                  if (j >= data[0]['tops_len']) {
                    str3 = '<li><span class="day-user-hight2">' + (j + 1) + '</span><span>虚位以待</span><span>虚位以待</span></li>';
                    $('#shuang').append(str3);
                  }
                }
              }
            }
            _results1.push(j++);
          }
          return _results1;
        }
      });
    };
    data = new Date();
    Y = data.getFullYear();
    m = data.getMonth() + 1;
    day = data.getDate();
    if (day.length < 2) {
      day = '0' + day;
    }
    date = Y + '-0' + m + "-" + day;
    hight(m, '.day-san');
    init(date);
    $('#left-h1').html('－－' + m + '月' + day + '日用户榜单－－');
    count_down('2015-04-01 00:00:00');
    $('.left-btn').on('click', function() {
      var high_m;
      $('.mon').html('3 月');
      $('.day-long').animate({
        'left': '0px'
      }, 500);
      $('.day-si span').removeClass('tap-hight2');
      high_m = parseInt($('.mon').text());
      return hight(high_m, '.day-san');
    });
    $('.right-btn').on('click', function() {
      var high_m;
      $('.mon').html('4 月');
      $('.day-long').animate({
        'left': '-357px'
      }, 500);
      $('.day-san span').removeClass('tap-hight2');
      high_m = parseInt($('.mon').text());
      return hight(high_m, '.day-si');
    });
    return $('.day-yue span').on('click', function() {
      var d, time;
      m = parseInt($('.mon').text());
      d = $(this).text();
      if (d.length < 2) {
        d = '0' + d;
      }
      time = '2015-0' + m + '-' + d;
      data = new Date();
      Y = data.getFullYear();
      m = data.getMonth() + 1;
      day = data.getDate();
      date = Y + '-0' + m + "-" + day;
      if (time >= '2015-03-17' && time <= '2015-04-30' && time <= date) {
        $(this).addClass('tap-hight2').siblings().removeClass('tap-hight2');
        $(this).parent().siblings().children('span').removeClass('tap-hight2');
        $('#left-h1').html('－－' + m + '月' + d + '日用户榜单－－');
        return shuju(time);
      }
    });
  });

}).call(this);

//# sourceMappingURL=day.js.map
