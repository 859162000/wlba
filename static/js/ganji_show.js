// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
      //固定回到顶部
     function backtop(box){
       var k=document.body.clientWidth,
         e=box.width();
         q=k-e;
         w=q/2;
         r= e+w;
         a=r+20+'px';
       return a;
     }

    var left2;
    left2=backtop($(".gjw-gold"));
    //浏览器大小改变触发的事件
    window.onresize = function(){
      left2 = backtop($(".gjw-gold"));
    };
    //赋值
    $('.xl-backtop').css({'left':left2});

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
    //模态口
    var body_h=$('body').height();
    $('#small-zc').height(body_h);
    //关闭模态窗
    $('.first-xl-off,.first-xl-off2,.look,.agin').on('click',function(){
      $('#small-zc').hide();
    });

    $('#small-zc').on('click',function(){
      $('#small-zc').hide();
    });
    //阻止冒泡
     $('.xl-box1,#seven-success,#activity-over,#gjw-success').on('click',function(event){
       if (event.stopPropagation){
         event.stopPropagation();
       }else{
         event.cancelBubble = true;
       }

     });
    //关闭提示
    $('.xl-off2').on('click',function(){
      $('#first-redpack-fail').hide()
    })
    //banner数字
//    $.ajax({
//      url: "/api/thousand/redpack/count/",
//      type: "GET"
//    }).done(function(data) {
//      var number=parseInt(data['redpack_total']);
//      if (number==0){
//        var str1='4543';
//        for(var j=0,len2=str1.length;j<len2;j++){
//          if(j>=$('#redpacknum li').length){
//              $('#redpacknum').append('<li>'+str1[j]+'<hr></li>');
//          }
//        }
//      }else{
//        var rednum=4543+number;
//        var str=rednum.toString();
//        for(var i=0,len=str.length;i<len;i++){
//          if(i>=$('#redpacknum li').length){
//              $('#redpacknum').append('<li>'+str[i]+'<hr></li>');
//          }else{
//            $.ajax({
//              url: "/api/thousand/redpack/",
//              type: "POST"
//            }).done(function(data) {
//
//              if(data['ret_code']==3002 || data['ret_code']==3003){
//                $('#small-zc').show();
//                $('#first-redpack-fail').show();
//                $('#first-redpack-fail p').html(data.message);
//              }
//              if(data['ret_code']==3001){
//                $('#small-zc').show();
//              }
//            })
//
//          }
//        }
//      }
//
//    });
    //显示模态窗口
//    $('#first-redpack-fail').hide();
//    $('#first-btn').on('click',function(){
//      if($(this).hasClass('selected')){
//        $('#small-zc').show();
//        $('#first-redpack-fail').show();
//        $('#seven-success').hide();
//        $('#box1').hide();
//        $('#first-redpack-fail p').html('您今天已经参加过该活动,不能重复参加');
//      }else{
//        if ($(this).attr('data-num') == 'false'){
//          $('#small-zc').show();
//        }else{
//          $.ajax({
//            url: "/api/thousand/redpack/",
//            type: "POST"
//          }).done(function(data) {
//            if(data['ret_code']==3002 || data['ret_code']==3003){
//              $('#small-zc').show();
//              $('#seven-success').hide();
//              $('#box1').hide();
//              $('#first-redpack-fail').show();
//              $('#first-redpack-fail p').html(data.message);
//            }
//            if(data['ret_code']==3001){
//              $('#small-zc').show();
//            }
//            if(data['ret_code']==0){
//              $('#small-zc').show();
//              $('#box1').hide();
//              $('#seven-success').show();
//            }
//          })
//        }
//      }
//
//    })
    //赶集网效果//滑动到相应区域
    $('#prize-two').on('click',function(){
      var re_top=$('#recharge').offset().top;
      $('body,html').animate({scrollTop:re_top}, 600);
      return false
    })
    $('#prize-four').on('click',function(){
      var re_top2=$('#tour').offset().top;
      $('body,html').animate({scrollTop:re_top2}, 600);
      return false
    })

    //点击领取
    $('.gjw-reg').on('click',function(){
      if ($(this).hasClass('reg1')){
        $('#small-zc').show();
      }else{
        $('#seven-success').hide();
        window.location.href="/accounts/home/";
      }
    })

    $('.gjw-reg3').on('click',function(){
      if ($(this).hasClass('reg2')){
        $('#small-zc').show();
      }else{
        $('#small-zc').show();
        $('#box1').hide();
        $('#gjw-success').children('p').text('请到投资页进行投资!')
        $('#gjw-success').children('ul').show();
        $('#gjw-success').children('a').hide();
        $('.fast').text('立即投资');
        $('#gjw-success').show();
      }

    })
    //领取奖品
    $('.gjw-recharge').on('click',function(){
      if ($(this).hasClass('gjw-star')){
        $('#box1').show();
        $('#gjw-success').hide();
        $('#small-zc').show();
      }else if ($(this).hasClass('notouch')){
        $('#small-zc').show();
        $('#box1').hide();
        $('#gjw-success').children('p').text('奖品发放完毕')
        $('#gjw-success').children('ul').hide();
        $('#gjw-success').children('a').show();
        $('#gjw-success').show();
      }else{
        $('#small-zc').show();
        $('#box1').hide();
        $('#gjw-success').children('p').text('您还没有充值哦!')
        $('#gjw-success').children('ul').show();
        $('#gjw-success').children('a').hide();
        $('.fast').text('立即充值')
        $('#gjw-success').show();
      }
    });

    //控制跳转
    $('.fast').on('click',function(){
      if($(this).text()=='立即充值'){
        window.location.href='/pay/banks/'
      }
      if($(this).text()=='立即投资'){
        window.location.href='/p2p/list/'
      }
    })

    //马上报名
    $('.gjw-small-com').on('click',function(){
      if ($(this).hasClass('go')){
        $('#box1').show();
        $('#gjw-success').hide();
        $('#small-zc').show();
      }else{
        window.location.href="/"
      }

    })
    //点击旅游路线
    $('#tour_line').on('click',function(){
      $('.gjw-tour').slideToggle(300)
    })

    //倒计时
    count_down = function(o) {
      var sec, timer;
      sec = (new Date(o.replace(/-/ig, '/')).getTime() - new Date().getTime()) / 1000;
      sec = parseInt(sec);
      timer = setTimeout((function() {
        count_down(o);
      }), 1000);
      if (sec <= 0) {
        console.log('时间到')
        $('#small-zc').show();
        $('#box1').hide();
        $('#activity-over').show();
        clearTimeout(timer)
      }
    };

    count_down('2015-09-20:00:00')


  });

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
          $('#seven-success').show();
          $('#first-redpack-fail').hide();
          $('#first-btn').addClass('selected');
          $.ajax({
            url: "/api/thousand/redpack/",
            type: "POST"
          }).done(function(data) {

            if(data['ret_code']==3002 || data['ret_code']==3003){
              $('#first-redpack-fail').hide();
              $('#box1').hide();
              $('#first-redpack-fail p').html(data.message);
            }
            if(data['ret_code']==3001){
              $('#small-zc').show();
            }
            if(data['ret_code']==0){
              $('#small-zc').show();
              $('#first-redpack-fail').hide();
              $('#seven-success').show();
            }

          })
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
        $("#register_submit2").css({'background':'#ccc'});
        return $(this).removeAttr("checked");
      } else {
        $("#register_submit2").css({'background':'#ff5252'});
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

