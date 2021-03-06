// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.validate': 'lib/jquery.validate.min',
      'jquery.complexify': 'lib/jquery.complexify.min',
      'jquery.placeholder': 'lib/jquery.placeholder',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.validate': ['jquery'],
      'jquery.complexify': ['jquery'],
      'jquery.placeholder': ['jquery']
    }
  });

  require(['jquery', 'jquery.validate', 'tools', 'jquery.complexify', 'lib/backend', 'jquery.placeholder'], function($, validate, tool, complexify, backend, placeholder) {

    /*$form = $('#register-form') */
    var checkMobile, container, url;
    url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
    $.getJSON(url, {}, function(json) {
      $('#register-form').find('input[name="captcha_0"]').val(json.key);
      return $('#register-form').find('img.captcha').attr('src', json.image_url);
    });
    $('input, textarea').placeholder();
    checkMobile = function(identifier) {
      var re;
      re = void 0;
      re = /^1\d{10}$/;
      return re.test(identifier);
    };
    $("#id_identifier").change(function() {
      return $(this).parent().parent().find('.error-label').remove();
    });
    $("#id_identifier").keyup(function() {
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
    $("#id_identifier").keyup();
    $('#button-get-validate-code').click(function() {
      var phoneNumber;
      url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
      $.getJSON(url, {}, function(json) {
        $('input[name="captcha_0"]').val(json.key);
        return $('img.captcha').attr('src', json.image_url);
      });
      phoneNumber = $.trim($("#id_identifier").val());
      if (checkMobile(phoneNumber)) {
        if (typeof console !== "undefined" && console !== null) {
          console.log("Phone number checked, now send the valdiation code");
        }
        $('#img-code-div1').modal();
        return $('#img-code-div1').find('#id_captcha_1').val('');
      }
    });
    $("#submit-code-img").click(function(e) {
      var captcha_0, captcha_1, count, element, intervalId, phoneNumber, timerFunction;
      element = $('#button-get-validate-code');
      phoneNumber = $.trim($("#id_identifier").val());
      captcha_0 = $(this).parents('form').find('#id_captcha_0').val();
      captcha_1 = $(this).parents('form').find('#id_captcha_1').val();
      $.ajax({
        url: "/api/phone_validation_code/register/" + phoneNumber + "/",
        type: "POST",
        data: {
          captcha_0: captcha_0,
          captcha_1: captcha_1
        }
      }).success(function(xhr) {
        element.attr('disabled', 'disabled');
        element.removeClass('button-red');
        element.addClass('button-gray');
        $('.voice-validate').attr('disabled', 'disabled');
        return $.modal.close();
      }).fail(function(xhr) {
        var result;
        clearInterval(intervalId);
        $(element).text('重新获取');
        $(element).removeAttr('disabled');
        $(element).addClass('button-red');
        $(element).removeClass('button-gray');
        result = JSON.parse(xhr.responseText);
        if (result.type === 'captcha') {
          return $("#submit-code-img").parent().parent().find('.code-img-error').html(result.message);
        } else {
          if (xhr.status >= 400) {
            return tool.modalAlert({
              title: '温馨提示',
              msg: result.message
            });
          }
        }
      });
      intervalId;
      count = 180;
      $(element).attr('disabled', 'disabled');
      $(element).removeClass('button-red');
      $(element).addClass('button-gray');
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
          $(element).removeClass('button-gray');
          $('.voice').removeClass('hidden');
          $('.voice-validate').removeAttr('disabled');
          return $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voice-validate">语音验证</a>');
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    });
    $.validator.addMethod("isMobile", function(value, element) {
      return checkMobile(value);
    });
    $('#register-form').validate({
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
          equalTo: "#id_password"
        },
        'validate_code': {
          required: true,
          depends: function(e) {}
        },
        captcha_1: {
          required: true,
          minlength: 1
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
        'validate_code': {
          required: '不能为空'
        },
        password2: {
          equalTo: '密码不一致'
        },
        captcha_1: {
          required: '不能为空',
          minlength: $.format("验证码至少输入1位")
        }
      },
      errorPlacement: function(error, element) {
        return error.appendTo($(element).parents('.form-row').children('.form-row-error'));
      }
    });
    this.COMPLEXIFY_BANLIST = '123456|password|12345678|1234|pussy|12345|dragon|qwerty|696969|mustang|letmein|baseball|master|michael|football|shadow|monkey|abc123|pass|fuckme|6969|jordan|harley|ranger|iwantu|jennifer|hunter|fuck|2000|test|batman|trustno1|thomas|tigger|robert|access|love|buster|1234567|soccer|hockey|killer|george|sexy|andrew|charlie|superman|asshole|fuckyou|dallas|jessica|panties|pepper|1111|austin|william|daniel|golfer|summer|heather|hammer|yankees|joshua|maggie|biteme|enter|ashley|thunder|cowboy|silver|richard|fucker|orange|merlin|michelle|corvette|bigdog|cheese|matthew|121212|patrick|martin|freedom|ginger|blowjob|nicole|sparky|yellow|camaro|secret|dick|falcon|taylor|111111|131313|123123|bitch|hello|scooter|please|porsche|guitar|chelsea|black|diamond|nascar|jackson|cameron|654321|computer|amanda|wizard|xxxxxxxx|money|phoenix|mickey|bailey|knight|iceman|tigers|purple|andrea|horny|dakota|aaaaaa|player|sunshine|morgan|starwars|boomer|cowboys|edward|charles|girls|booboo|coffee|xxxxxx|bulldog|ncc1701|rabbit|peanut|john|johnny|gandalf|spanky|winter|brandy|compaq|carlos|tennis|james|mike|brandon|fender|anthony|blowme|ferrari|cookie|chicken|maverick|chicago|joseph|diablo|sexsex|hardcore|666666|willie|welcome|chris|panther|yamaha|justin|banana|driver|marine|angels|fishing|david|maddog|hooters|wilson|butthead|dennis|fucking|captain|bigdick|chester|smokey|xavier|steven|viking|snoopy|blue|eagles|winner|samantha|house|miller|flower|jack|firebird|butter|united|turtle|steelers|tiffany|zxcvbn|tomcat|golf|bond007|bear|tiger|doctor|gateway|gators|angel|junior|thx1138|porno|badboy|debbie|spider|melissa|booger|1212|flyers|fish|porn|matrix|teens|scooby|jason|walter|cumshot|boston|braves|yankee|lover|barney|victor|tucker|princess|mercedes|5150|doggie|zzzzzz|gunner|horney|bubba|2112|fred|johnson|xxxxx|tits|member|boobs|donald|bigdaddy|bronco|penis|voyager|rangers|birdie|trouble|white|topgun|bigtits|bitches|green|super|qazwsx|magic|lakers|rachel|slayer|scott|2222|asdf|video|london|7777|marlboro|srinivas|internet|action|carter|jasper|monster|teresa|jeremy|11111111|bill|crystal|peter|pussies|cock|beer|rocket|theman|oliver|prince|beach|amateur|7777777|muffin|redsox|star|testing|shannon|murphy|frank|hannah|dave|eagle1|11111|mother|nathan|raiders|steve|forever|angela|viper|ou812|jake|lovers|suckit|gregory|buddy|whatever|young|nicholas|lucky|helpme|jackie|monica|midnight|college|baby|cunt|brian|mark|startrek|sierra|leather|232323|4444|beavis|bigcock|happy|sophie|ladies|naughty|giants|booty|blonde|fucked|golden|0|fire|sandra|pookie|packers|einstein|dolphins|chevy|winston|warrior|sammy|slut|8675309|zxcvbnm|nipples|power|victoria|asdfgh|vagina|toyota|travis|hotdog|paris|rock|xxxx|extreme|redskins|erotic|dirty|ford|freddy|arsenal|access14|wolf|nipple|iloveyou|alex|florida|eric|legend|movie|success|rosebud|jaguar|great|cool|cooper|1313|scorpio|mountain|madison|987654|brazil|lauren|japan|naked|squirt|stars|apple|alexis|aaaa|bonnie|peaches|jasmine|kevin|matt|qwertyui|danielle|beaver|4321|4128|runner|swimming|dolphin|gordon|casper|stupid|shit|saturn|gemini|apples|august|3333|canada|blazer|cumming|hunting|kitty|rainbow|112233|arthur|cream|calvin|shaved|surfer|samson|kelly|paul|mine|king|racing|5555|eagle|hentai|newyork|little|redwings|smith|sticky|cocacola|animal|broncos|private|skippy|marvin|blondes|enjoy|girl|apollo|parker|qwert|time|sydney|women|voodoo|magnum|juice|abgrtyu|777777|dreams|maxwell|music|rush2112|russia|scorpion|rebecca|tester|mistress|phantom|billy|6666|albert|111111|11111111|112233|121212|123123|123456|1234567|12345678|131313|232323|654321|666666|696969|777777|7777777|8675309|987654|abcdef|password1|password12|password123|twitter'.split('|');
    container = $('.password-strength-container');
    $('#id_password').complexify({
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
    $("#agreement").change(function(value) {
      if ($(this).attr("data-value") === "agree") {
        $("#register_submit").addClass("disabled");
        return $(this).attr("data-value", "disagree");
      } else {
        $(this).attr("data-value", "agree");
        return $("#register_submit").removeClass("disabled");
      }
    });
    $("#register_submit").click(function(e) {
      if ($(this).hasClass("disabled")) {
        e.preventDefault();
      }
    });
    return $(".voice").on('click', '.voice-validate', function(e) {
      var element, isMobile;
      e.preventDefault();
      isMobile = checkMobile($.trim($("#id_identifier").val()));
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
          phone: $.trim($("#id_identifier").val())
        }
      }).success(function(json) {
        var button, count, intervalId, timerFunction;
        if (json.ret_code === 0) {
          intervalId;
          count = 180;
          button = $("#button-get-validate-code");
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
      }).fail(function(xhr) {
        element = $('#sendValidateCodeButton');
        if (xhr.status >= 400) {
          tool.modalAlert({
            title: '温馨提示',
            msg: xhr.message
          });
          $(element).html('重新获取');
          $(element).prop('disabled', false);
          return $(element).removeClass("disabled");
        }
      });
    });
  });

}).call(this);

//# sourceMappingURL=register.js.map
