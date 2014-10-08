// Generated by CoffeeScript 1.7.1
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

  require(['jquery', 'lib/modal', 'lib/backend', 'jquery.validate', "tools", 'jquery.complexify', 'jquery.placeholder', 'underscore'], function($, modal, backend, validate, tool, complexify, placeholder, _) {
    var checkMobile, container, csrfSafeMethod, getCookie, sameOrigin, _showModal;
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
    $('#login-modal-form').validate({
      rules: {
        identifier: {
          required: true,
          emailOrPhone: true
        },
        password: {
          required: true,
          minlength: 6
        },
        captcha_1: {
          required: true,
          minlength: 4
        }
      },
      messages: {
        identifier: {
          required: '不能为空',
          emailOrPhone: '请输入手机号'
        },
        password: {
          required: '不能为空',
          minlength: $.format("密码需要最少{0}位")
        },
        captcha_1: {
          required: '不能为空',
          minlength: $.format("验证码要输入4位")
        }
      },
      errorPlacement: function(error, element) {
        return error.appendTo($(element).parents('.form-row').children('.form-row-error'));
      },
      submitHandler: function(form) {
        return $.ajax({
          url: $('#login-modal-form').attr('action'),
          type: "POST",
          data: $("#login-modal-form").serialize()
        }).done(function(data, textStatus) {
          return location.reload();
        }).fail(function(xhr) {
          var error_message, message, result;
          result = JSON.parse(xhr.responseText);
          message = result.message;
          error_message = _.chain(message).pairs().map(function(e) {
            return e[1];
          }).flatten().value();
          $('.captcha-refresh', '#login-modal-form').trigger('click');
          return alert(error_message);
        });
      }
    });
    $('#register-modal-form').validate({
      rules: {
        identifier: {
          required: true,
          isMobile: true
        },
        validation_code: {
          required: true,
          depends: function(e) {
            return checkMobile($('#reg_identifier').val());
          }
        },
        password: {
          required: true,
          minlength: 6
        },
        password2: {
          equalTo: "#reg_password"
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
        validation_code: {
          required: '不能为空'
        },
        password: {
          required: '不能为空',
          minlength: $.format("密码需要最少{0}位")
        },
        password2: {
          equalTo: '密码不一致'
        },
        agreement: {
          required: '请勾选注册协议'
        }
      },
      errorPlacement: function(error, element) {
        return error.appendTo($(element).parents('.form-row').children('.form-row-error'));
      },
      submitHandler: function(form) {
        return $.ajax({
          url: $(form).attr('action'),
          type: "POST",
          data: $(form).serialize()
        }).done(function(data, textStatus) {
          return location.reload();
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
    $("#reg_identifier").keyup(function(e) {
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
    $("#reg_identifier").keyup();
    _showModal = function() {
      return $('#login-modal').modal();
    };
    $("#button-get-validate-code-modal").click(function(e) {
      var count, element, intervalId, phoneNumber, timerFunction;
      e.preventDefault();
      element = this;
      phoneNumber = $.trim($("#reg_identifier").val());
      if (checkMobile(phoneNumber)) {
        if (typeof console !== "undefined" && console !== null) {
          console.log("Phone number checked, now send the valdiation code");
        }
        $.ajax({
          url: "/api/phone_validation_code/register/" + phoneNumber + "/",
          type: "POST"
        }).fail(function(xhr) {
          var result;
          $.modal.close();
          clearInterval(intervalId);
          $(element).text('重新获取');
          $(element).removeAttr('disabled');
          $(element).addClass('button-red');
          $(element).removeClass('button-gray');
          result = JSON.parse(xhr.responseText);
          return tool.modalAlert({
            title: '温馨提示',
            msg: result.message,
            callback_ok: _showModal
          });
        });
        intervalId;
        count = 60;
        $(element).attr('disabled', 'disabled');
        $(element).removeClass('button-red');
        $(element).addClass('button-gray');
        timerFunction = function() {
          if (count >= 1) {
            count--;
            return $(element).text('已经发送(' + count + ')');
          } else {
            clearInterval(intervalId);
            $(element).text('重新获取');
            $(element).removeAttr('disabled');
            $(element).addClass('button-red');
            return $(element).removeClass('button-gray');
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
    $('#reg_password').complexify({
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
    $("#invite_top_bar").click(function() {
      return backend.userProfile({}).done(function() {
        return window.location.href = $("#invite_top_bar").attr("data-url");
      }).fail(function(xhr) {
        if (xhr.status === 403) {
          $('.login-modal').trigger('click');
        }
      });
    });
    $("#agreement").change(function(value) {
      if ($(this).attr("checked")) {
        $("#register_submit").addClass("disabled");
        return $(this).removeAttr("checked");
      } else {
        $("#register_submit").removeClass("disabled");
        return $(this).attr("checked", "checked");
      }
    });
    $("#register_submit").click(function(e) {
      if ($(this).hasClass("disabled")) {
        e.preventDefault();
      }
    });
    $('.nologin').click(function(e) {
      e.preventDefault();
      return $('.login-modal').trigger('click');
    });
    return $("input:password").bind("copy cut paste", function(e) {
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
  });

}).call(this);

//# sourceMappingURL=login_modal.map
