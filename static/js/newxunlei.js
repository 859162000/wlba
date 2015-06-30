// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    //banner的主题文字效果
//    $('.xl-small-zc').show()
    $('#xl-text').show();
    $('#xl-text').animate({'top': '37px'},500);
    //banner数字
    $.ajax({
      url: "/api/xunlei/join/count/",
      type: "GET"
    }).done(function(data) {
      var number=parseInt(data['amount_sum']);
      var rednum=500+number/10;
      var str=rednum.toString();
      for(var i=0,len=str.length;i<len;i++){
        console.log(str[i]);
        if(i>=$('#redpacknum li').length){
            $('#redpacknum').append('<li>'+str[i]+'<hr></li>');
        }
      }
    });
    //点击按钮出现注册框
    $('#xl-btn').on('click',function(){
        if ($(this).attr('data-num') == 'false'){
          $('.xl-small-zc').show()
        }else{
          $.ajax({
            url: "/api/xunlei/join/",
            type: "POST"
          }).done(function(data) {
            console.log(data);
            if(data['ret_code']==3002 || data['ret_code']==3001){
//              $('#redpack-fail').show();
              alert(data.message);
            }
            if(data['ret_code']==3000){
              smallgame();
            }
          })
        }
    });
    //游戏
    function smallgame(){
      $('#seven-text').html('准备数钱');
          var n=3;
          var timer;
          if (n!==0){
            timer=setInterval(function(){
              n--;
              $('#seven-time').html(n);
              if (n<0){
                clearInterval(timer);
                $('#seven-text').html('来 点 我');
                $('#seven-time').html('3');
                $('.game-start').show();
                $('#xl-btn').css({'background':'#988B8B','box-shadow':'0px 4px #A09C9B'});
                $('#xl-btn').attr('disabled','false');
              }
            },1000)
          }
      //点击开始游戏
      var num=1;
      $('.game-start').on('click',function(){
        if (!$('.game-start').hasClass('start')){
          $(this).addClass('start');
          //游戏时间倒计时
          var k=3;
          var timer2;
          timer2=setInterval(function(){
            k--;
            $('#seven-time').html(k);
            if (k==0){
              clearInterval(timer2);
              $('#xl-btn').hide();
              $('#give-btn').show();
            }
          },1000);
          setTimeout(function(){
            $('.game-start').removeClass('game-start');
          },3000)
        }
        num++;
        $('#seven-money').html('￥'+num*10);
        $('#money').html(num*10);
      })
    }
    //点击×关闭注册框
    $('.xl-off,#now').on('click',function(){
      $('.xl-small-zc').hide()
    });
    //点击×关闭提示框
    $('.xl-off2,#now').on('click',function(){
      $('.seven-success').hide();
    });

    $('#now').on('click',function(){
      smallgame();
    });
    //弹出领取红包提示
    $('#give-btn').on('click',function(){
      var money=$('#money').html();
      $.ajax({
        url: "/api/xunlei/join/",
        type: "POST",
        data:{'amount':money}
      }).done(function(data){
        alert(data.message)
//        $('#redpack-success').show();
      })
    })
  });


  //固定回到顶部
   function backtop(){
     var k=document.body.clientWidth,
       e=$(".new-xl-big").width();
       q=k-e;
       w=q/2;
       r= e+w;
       a=r+20+'px';
     return a;
   }

  var left;
  left=backtop();
  //浏览器大小改变触发的事件
  window.onresize = function(){
    left = backtop();
  };
  //赋值
  $('.xl-backtop').css({'left':left})

  //显示微信二维码
 $('#xl-weixin').on('mouseover',function(){
   $('.erweima').show();
 });

  $('#xl-weixin').on('mouseout',function(){
   $('.erweima').hide();
 })

  //返回顶部
  $(window).scroll(function () {
      if ($(document).scrollTop() > 0) {
          $(".xl-backtop").fadeIn();
      } else if ($(document).scrollTop() <= 0) {
          $('.xl-backtop').stop().fadeOut();
      }
  });

  $('.backtop').on('click',function(){
    $('body,html').animate({scrollTop: 0}, 600);
    return false
  })

}).call(this);




// 第二个注册
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'jquery.validate': 'lib/jquery.validate.min',
      'jquery.complexify': 'lib/jquery.complexify.min',
      'jquery.placeholder': 'lib/jquery.placeholder',
      'underscore': 'lib/underscore-min',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.validate': ['jquery'],
      'jquery.complexify': ['jquery'],
      'jquery.placeholder': ['jquery']
    }
  });

  require(['jquery', 'lib/modal', 'lib/backend', 'jquery.validate', "tools", 'jquery.complexify', 'jquery.placeholder',
    'underscore'], function($, modal, backend, validate, tool, complexify, placeholder, _) {
    var checkMobile, container, csrfSafeMethod, getCookie, msg_count, sameOrigin, _showModal;
    getCookie = function(name) {
      var cookie, cookieValue, cookies, i;
      cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        cookies = document.cookie.split(";");
        i = 0;
        while (i < cookies.length) {
          cookie = $.trim(cookies[i]);
          if (cookie.substring(0, name.length + 1) === (name + "=")) {
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
      host = document.location.host;
      protocol = document.location.protocol;
      sr_origin = "//" + host;
      origin = protocol + sr_origin;
      return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
    };
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
          xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        }
      }
    });
    $.validator.addMethod("emailOrPhone", function(value, element) {
      return backend.checkEmail(value) || backend.checkMobile(value);
    });

    $('#register-modal-form2').validate({
      rules: {
        identifier: {
          required: true,
          isMobile: true
        },
        validate_code: {
          required: true
        },
        password: {
          required: true,
          minlength: 6,
          maxlength: 20
        },
        password2: {
          equalTo: "#reg_password4"
        },
        agreement: {
          required: true
        }
      },
      messages: {
        identifier: {
          required: '不能为空',
          isMobile: '请输入手机号'
        },
        validate_code: {
          required: '不能为空'
        },
        password: {
          required: '不能为空',
          minlength: $.format("密码需要最少{0}位"),
          maxlength: '密码不能超过20位'
        },
        password2: {
          equalTo: '密码不一致'
        },
        agreement: {
          required: '请勾选注册协议'
        }
      },
      errorPlacement: function(error, element) {
        console.log(error);
        return error.appendTo($(element).parents('.form-row').children('.form-row-error'));
      },
      submitHandler: function(form) {
        $('input[name="identifier"]').trigger('keyup');
        return $.ajax({
          url: $(form).attr('action'),
          type: "POST",
          data: $(form).serialize()
        }).done(function(data, textStatus) {
          return $('#seven-success').show();
        }).fail(function(xhr) {
          var error_message, message, result;
          result = JSON.parse(xhr.responseText);
          message = result.message;
          error_message = _.chain(message).pairs().map(function(e) {
            return e[1];
          }).flatten().value();
          return alert(error_message);
        });
      }
    });
    $('input, textarea').placeholder();
    checkMobile = function(identifier) {
      var re;
      re = void 0;
      re = /^1\d{10}$/;
      return re.test(identifier);
    };
    $("#reg_identifier2").keyup(function(e) {
      var isMobile, value;
      isMobile = void 0;
      value = void 0;
      value = $(this).val();
      isMobile = checkMobile(value);
      if (isMobile) {
        $("#id_type").val("phone");
        return $("#validate-code-container").show();
      }
    });
    $("#reg_identifier2").keyup();
    _showModal = function() {
      return $('#login-modal').modal();
    };
    $("#button-get-validate-code-modal2").click(function(e) {
      var count, element, intervalId, phoneNumber, timerFunction;
      e.preventDefault();
      element = this;
      phoneNumber = $.trim($("#reg_identifier2").val());
      if (checkMobile(phoneNumber)) {
        if (typeof console !== "undefined" && console !== null) {
          console.log("Phone number checked, now send the valdiation code");
        }
        $.ajax({
          url: "/api/phone_validation_code/register/" + phoneNumber + "/",
          type: "POST"
        }).fail(function(xhr) {
          var result;
          $.modal.close();$("#button-get-validate-code-modal2")
          clearInterval(intervalId);
          $(element).text('重新获取');
          $(element).removeAttr('disabled');
          $(element).addClass('button-red');
          $(element).removeClass('huoqu-ma-gray');
          result = JSON.parse(xhr.responseText);
          if (xhr.status === 429) {
            return tool.modalAlert({
              title: '温馨提示',
              msg: "系统繁忙，请稍候重试",
              callback_ok: _showModal
            });
          } else {
            return tool.modalAlert({
              title: '温馨提示',
              msg: result.message,
              callback_ok: _showModal
            });
          }
        });
        intervalId;
        count = 60;
        $(element).attr('disabled', 'disabled');
        $(element).removeClass('button-red');
        $(element).addClass('huoqu-ma-gray');
        $('.voice-validate').attr('disabled', 'disabled');
        timerFunction = function() {
          if (count >= 1) {
            count--;
            return $(element).text('已经发送(' + count + ')');
          } else {
            clearInterval(intervalId);
            $(element).text('重新获取');
            $(element).removeAttr('disabled');
            $(element).addClass('button-red');
            $(element).removeClass('huoqu-ma-gray');
            $('.voice').removeClass('hidden');
            $('.voice-validate').removeAttr('disabled');
            return $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voice-validate">语音验证</a>');
          }
        };
        timerFunction();
        return intervalId = setInterval(timerFunction, 1000);
      }
    });
    $.validator.addMethod("isMobile", function(value, element) {
      return checkMobile(value);
    });
    this.COMPLEXIFY_BANLIST = '123456|password|12345678|1234|pussy|12345|dragon|qwerty|696969|mustang|letmein|baseball|master|michael|football|shadow|monkey|abc123|pass|fuckme|6969|jordan|harley|ranger|iwantu|jennifer|hunter|fuck|2000|test|batman|trustno1|thomas|tigger|robert|access|love|buster|1234567|soccer|hockey|killer|george|sexy|andrew|charlie|superman|asshole|fuckyou|dallas|jessica|panties|pepper|1111|austin|william|daniel|golfer|summer|heather|hammer|yankees|joshua|maggie|biteme|enter|ashley|thunder|cowboy|silver|richard|fucker|orange|merlin|michelle|corvette|bigdog|cheese|matthew|121212|patrick|martin|freedom|ginger|blowjob|nicole|sparky|yellow|camaro|secret|dick|falcon|taylor|111111|131313|123123|bitch|hello|scooter|please|porsche|guitar|chelsea|black|diamond|nascar|jackson|cameron|654321|computer|amanda|wizard|xxxxxxxx|money|phoenix|mickey|bailey|knight|iceman|tigers|purple|andrea|horny|dakota|aaaaaa|player|sunshine|morgan|starwars|boomer|cowboys|edward|charles|girls|booboo|coffee|xxxxxx|bulldog|ncc1701|rabbit|peanut|john|johnny|gandalf|spanky|winter|brandy|compaq|carlos|tennis|james|mike|brandon|fender|anthony|blowme|ferrari|cookie|chicken|maverick|chicago|joseph|diablo|sexsex|hardcore|666666|willie|welcome|chris|panther|yamaha|justin|banana|driver|marine|angels|fishing|david|maddog|hooters|wilson|butthead|dennis|fucking|captain|bigdick|chester|smokey|xavier|steven|viking|snoopy|blue|eagles|winner|samantha|house|miller|flower|jack|firebird|butter|united|turtle|steelers|tiffany|zxcvbn|tomcat|golf|bond007|bear|tiger|doctor|gateway|gators|angel|junior|thx1138|porno|badboy|debbie|spider|melissa|booger|1212|flyers|fish|porn|matrix|teens|scooby|jason|walter|cumshot|boston|braves|yankee|lover|barney|victor|tucker|princess|mercedes|5150|doggie|zzzzzz|gunner|horney|bubba|2112|fred|johnson|xxxxx|tits|member|boobs|donald|bigdaddy|bronco|penis|voyager|rangers|birdie|trouble|white|topgun|bigtits|bitches|green|super|qazwsx|magic|lakers|rachel|slayer|scott|2222|asdf|video|london|7777|marlboro|srinivas|internet|action|carter|jasper|monster|teresa|jeremy|11111111|bill|crystal|peter|pussies|cock|beer|rocket|theman|oliver|prince|beach|amateur|7777777|muffin|redsox|star|testing|shannon|murphy|frank|hannah|dave|eagle1|11111|mother|nathan|raiders|steve|forever|angela|viper|ou812|jake|lovers|suckit|gregory|buddy|whatever|young|nicholas|lucky|helpme|jackie|monica|midnight|college|baby|cunt|brian|mark|startrek|sierra|leather|232323|4444|beavis|bigcock|happy|sophie|ladies|naughty|giants|booty|blonde|fucked|golden|0|fire|sandra|pookie|packers|einstein|dolphins|chevy|winston|warrior|sammy|slut|8675309|zxcvbnm|nipples|power|victoria|asdfgh|vagina|toyota|travis|hotdog|paris|rock|xxxx|extreme|redskins|erotic|dirty|ford|freddy|arsenal|access14|wolf|nipple|iloveyou|alex|florida|eric|legend|movie|success|rosebud|jaguar|great|cool|cooper|1313|scorpio|mountain|madison|987654|brazil|lauren|japan|naked|squirt|stars|apple|alexis|aaaa|bonnie|peaches|jasmine|kevin|matt|qwertyui|danielle|beaver|4321|4128|runner|swimming|dolphin|gordon|casper|stupid|shit|saturn|gemini|apples|august|3333|canada|blazer|cumming|hunting|kitty|rainbow|112233|arthur|cream|calvin|shaved|surfer|samson|kelly|paul|mine|king|racing|5555|eagle|hentai|newyork|little|redwings|smith|sticky|cocacola|animal|broncos|private|skippy|marvin|blondes|enjoy|girl|apollo|parker|qwert|time|sydney|women|voodoo|magnum|juice|abgrtyu|777777|dreams|maxwell|music|rush2112|russia|scorpion|rebecca|tester|mistress|phantom|billy|6666|albert|111111|11111111|112233|121212|123123|123456|1234567|12345678|131313|232323|654321|666666|696969|777777|7777777|8675309|987654|abcdef|password1|password12|password123|twitter'.split('|');
    container = $('.password-strength-container');
    $('#reg_password4').complexify({
      minimumChars: 6,
      strengthScaleFactor: 1
    }, function(valid, complexity) {
      if (complexity === 0) {
        container.removeClass('low');
        container.removeClass('soso');
        return container.removeClass('strong');
      } else if (complexity < 30) {
        container.removeClass('soso');
        container.removeClass('strong');
        return container.addClass('low');
      } else if (complexity < 60) {
        container.removeClass('low');
        container.removeClass('strong');
        return container.addClass('soso');
      } else {
        container.removeClass('low');
        container.removeClass('soso');
        return container.addClass('strong');
      }
    });
    $('.login-modal').click(function(e) {
      var url;
      $("#tab-login").addClass('active');
      $("#tab-register").removeClass('active');
      $("#login-modal-form").show();
      $("#register-modal-form").hide();
      url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
      $.getJSON(url, {}, function(json) {
        $('input[name="captcha_0"]').val(json.key);
        return $('img.captcha').attr('src', json.image_url);
      });
      e.preventDefault();
      return $(this).modal();
    });
    $('.register-modal').click(function(m) {
      var url;
      $("#tab-login").removeClass('active');
      $("#tab-register").addClass('active');
      $("#login-modal-form").hide();
      $("#register-modal-form").show();
      url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
      $.getJSON(url, {}, function(json) {
        $('input[name="captcha_0"]').val(json.key);
        return $('img.captcha').attr('src', json.image_url);
      });
      m.preventDefault();
      return $(this).modal();
    });
    $('.captcha-refresh').click(function() {
      var $form, url;
      $form = $(this).parents('form');
      url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
      return $.getJSON(url, {}, function(json) {
        $form.find('input[name="captcha_0"]').val(json.key);
        return $form.find('img.captcha').attr('src', json.image_url);
      });
    });
    $('.login-modal-tab>li').click(function(e) {
      $('.login-modal-tab>li').removeClass('active');
      $(this).addClass('active');
      if ($("#tab-login").attr('class') === 'active') {
        $("#login-modal-form").show();
        return $("#register-modal-form").hide();
      } else {
        $("#login-modal-form").hide();
        return $("#register-modal-form").show();
      }
    });
    $("#agreement2").change(function(value) {
      if ($(this).attr("checked")) {
        $("#register_submit2").addClass("disabled");
        return $(this).removeAttr("checked");
      } else {
        $("#register_submit2").removeClass("disabled");
        return $(this).attr("checked", "checked");
      }
    });
    $("#register_submit2").click(function(e) {
      if ($(this).hasClass("disabled")) {
        e.preventDefault();
      }
    });
    $('.nologin').click(function(e) {
      e.preventDefault();
      return $('.login-modal').trigger('click');
    });
    $("input:password").bind("copy cut paste", function(e) {
      var element;
      element = this;
      return setTimeout((function() {
        var text;
        text = $(element).val();
        if (!/[^\u4e00-\u9fa5]+/ig.test(text) || /\s+/ig.test(text)) {
          $(element).val('');
        }
      }), 100);
    });
    msg_count = $('#message_count').html();
    if (msg_count > 0) {
      backend.loadMessageCount('unread').done(function(data) {
        if (data.count > 0) {
          $('#message_count').show();
          return $('#message_count').html(data.count);
        }
      });
    }
     myeven();
    return $(".voice").on('click', '.voice-validate', function(e) {
      var element, isMobile, url;
      e.preventDefault();
      isMobile = checkMobile($("#reg_identifier2").val().trim());
      if (!isMobile) {
        $("#id_type").val("phone");
        $("#validate-code-container").show();
        return;
      }
      if ($(this).attr('disabled') && $(this).attr('disabled') === 'disabled') {
        return;
      }
      element = $('.voice .span12-omega');
      url = $(this).attr('href');
      return $.ajax({
        url: url,
        type: "POST",
        data: {
          phone: $("#reg_identifier2").val().trim()
        }
      }).success(function(json) {
        var button, count, intervalId, timerFunction;
        if (json.ret_code === 0) {
          intervalId;
          count = 60;
          button = $("#button-get-validate-modal");
          button.attr('disabled', 'disabled');
          button.addClass('button-gray');
          $('.voice').addClass('tip');
          timerFunction = function() {
            if (count >= 1) {
              count--;
              return element.text('语音验证码已经发送，请注意接听（' + count + '）');
            } else {
              clearInterval(intervalId);
              element.html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voice-validate">语音验证</a>');
              element.removeAttr('disabled');
              button.removeAttr('disabled');
              button.addClass('button-red');
              button.removeClass('button-gray');
              return $('.voice').removeClass('tip');
            }
          };
          timerFunction();
          return intervalId = setInterval(timerFunction, 1000);
        } else {
          return element.html('系统繁忙请尝试短信验证码');
        }
      });
    });


    function myeven() {
      var high = document.body.scrollHeight;
      $('#top-zc').on('click', function () {
        pageScroll();
      });

      function pageScroll() {
        //把内容滚动指定的像素数
        window.scrollBy(0, -high);
        //获取scrollTop值
        var sTop = document.documentElement.scrollTop + document.body.scrollTop;
        //判断当页面到达顶部
        if (sTop == 0) clearTimeout(scrolldelay);
      }

      //文本框的得到和失去光标
      var zhi;
      $('.com-tu').on("focus", function () {
        if ($(this).attr('placeholder')) {
          zhi = $(this).attr('placeholder');
        }
        $(this).attr('placeholder', '');
      });

      $('.com-tu').on('blur', function () {
        $(this).attr('placeholder', zhi)
      })

      $('#button-get-validate-code-modal2').disabled=false;
      $('#button-get-validate-code-modal2').on('click', function () {
        $(this).disabled = false;
        setTimeout(function () {
          $('#button-get-validate-code-modal2').disabled = true;
          $('.show').removeClass('hidden');
        }, 60000)
      });
    }

  });

}).call(this);

//# sourceMappingURL=login_modal.js.map

