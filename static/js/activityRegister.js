(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.placeholder': 'lib/jquery.placeholder',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.placeholder': ['jquery']
    }
  });

  define(['jquery', "tools", 'jquery.placeholder'], function($, tool, placeholder) {
    var container, csrfSafeMethod, getCookie, sameOrigin, _showModal;
    var activityRegister ={}
    jQuery.extend(activityRegister, {
        registerTitle :'',    //注册框标语
        isNOShow : '1',      //是否显示
        hasCallBack : false, //回调
        initFun : function(){
            $('.biaoyu').text(this.registerTitle);
            //cookie
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
        },
        //图片验证码
        imgCodeFun : function(){
            $('#img-code').click(function() {
                $('#aug-center').find('#id_captcha_1').val('');
                activityRegister.imgCodeRe();
                var phoneNumber;
                phoneNumber = $.trim($("#reg_identifier").val());
                if (activityRegister.checkMobile(phoneNumber)) {
                    if (typeof console !== "undefined" && console !== null) {
                        console.log("Phone number checked, now send the valdiation code");
                    }
                    $('#aug-code,#aug-center').show();
                    return $('#aug-center').find('#id_captcha_1').val('');
                }else{
                    $('#aug-form-row-eroor').text('* 请输入正确的手机号')
                }
            });
            $('#off-form').on('click',function(){   //关闭验证码弹框
              $('#aug-code,#aug-center').hide();
            })
        },
        //发送验证码
        imgCodePost : function(){
            $('#submit-code-img1').click(function() {
                var captcha_0, captcha_1, count, element, intervalId, phoneNumber, timerFunction;
                element = $('#img-code');
                phoneNumber = $.trim($("#reg_identifier").val());
                captcha_0 = $(this).parents('form').find('#id_captcha_0').val();
                captcha_1 = $(this).parents('form').find('.captcha').val();
                $.ajax({
                    url: "/api/phone_validation_code/register/" + phoneNumber + "/",
                    type: "POST",
                    data: {
                        captcha_0: captcha_0,
                        captcha_1: captcha_1
                    }
                }).success(function() {
                    element.attr('disabled', 'disabled');
                    $('.voice-validate').attr('disabled', 'disabled');
                    $('#aug-code,#aug-center').hide();
                }).fail(function(xhr) {
                    clearInterval(intervalId);
                    $(element).text('重新获取').removeAttr('disabled');
                    var result = JSON.parse(xhr.responseText);
                    if (result.type === 'captcha') {
                        return $("#submit-code-img1").parent().parent().find('.code-img-error').html(result.message);
                    } else {
                        if (xhr.status >= 400) {
                            $('#aug-code,#aug-center').hide();
                            return tool.modalAlert({
                                title: '温馨提示',
                                msg: result.message,
                                callback_ok: _showModal
                            });
                        }
                    }
                });
                count = 180;
                $(element).attr('disabled', 'disabled');
                $('.voice-validate').attr('disabled', 'disabled');
                timerFunction = function() {
                    if (count >= 1) {
                        count--;
                        return $(element).text('已经发送(' + count + ')');
                    } else {
                        clearInterval(intervalId);
                        $(element).text('重新获取').removeAttr('disabled');
                        $('.span12-omega').removeClass('hidden');
                        $('.voice-validate').removeAttr('disabled');
                        return $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/" class="voice-validate">语音验证</a>');
                    }
                };
                timerFunction();
                return intervalId = setInterval(timerFunction, 1000);
            });
        },
        //刷新验证码
        imgCodeRe : function(){
            url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
            $.getJSON(url, {}, function(json) {
              $('#img-code-form').find('input[name="captcha_0"]').val(json.key);
              $('#img-code-form').find('img.captcha').attr('src', json.image_url);
            });
        },
        //提交表单
        registerSubmitFun : function(){
            $('#register_submit').on('click',function(){
                if ($(this).hasClass("disabled")) {
                    return
                }else{
                    var errorLabel = $('#aug-form-row-eroor');
                    if ($('#reg_identifier').val()==''){
                        errorLabel.text('* 请输入手机号')
                    }else if (!activityRegister.checkMobile($('#reg_identifier').val())){
                        errorLabel.text('* 请输入正确的手机号')
                    }else if ($('#id_validate_code').val()==''){
                        errorLabel.text('* 请输入验证码')
                    }else if ($('#reg_password').val()==''){
                        errorLabel.text('* 请输入密码')
                    }else if ($('#reg_password').val().length<6){
                        errorLabel.text('* 密码需要最少6位')
                    }else if ($('#reg_password').val().length>20){
                        errorLabel.text('* 密码不能超过20位')
                    }else if ($('#reg_password2').val()==''){
                        errorLabel.text('* 请再次输入密码')
                    }else if ($('#reg_password').val()!=$('#reg_password2').val()){
                        errorLabel.text('* 密码不一致')
                    }else{
                        if($("#agreement").is(':checked')) {
                            var phoneNumber, pw, code;
                            phoneNumber = $('#reg_identifier').val();
                            code = $('#id_validate_code').val();
                            pw = $('#reg_password').val();
                            $.ajax({
                                url: '/accounts/register/ajax/',
                                type: "POST",
                                data: {identifier: phoneNumber, validate_code: code, password: pw}
                            }).done(function () {
                                if(activityRegister.hasCallBack == true){
                                    activityRegister.callBack();
                                }else{
                                    return location.reload();
                                }
                            }).fail(function (xhr) {
                                var result = JSON.parse(xhr.responseText);
                                $('#aug-form-row-eroor').text('* ' + result.message.validate_code)
                            });
                        }else{
                           return tool.modalAlert({
                                title: '温馨提示',
                                msg: '请查看网利宝注册协议'
                           });
                        }
                    }
                }

            })
        },
        //input验证
        inputValidateFun : function(){
            var errorLabel = $('#aug-form-row-eroor');
            $('#reg_identifier,#id_validate_code').on('keyup',function(){
              errorLabel.text('')
            })
            $('#reg_password').on('keyup',function(){
              if ($('#reg_password').val().length<6){
                errorLabel.text('* 密码需要最少6位')
              }else if ($('#reg_password').val().length>20){
                errorLabel.text('* 密码不能超过20位')
              }else{
                errorLabel.text('')
              }
            })
            $('#reg_password2').on('keyup',function(){
              if ($('#reg_password').val()!=$('#reg_password2').val()){
                errorLabel.text('* 密码不一致')
              }else{
                errorLabel.text('')
              }
            })
            $('input, textarea').placeholder();
             //文本框的得到和失去光标
            var zhi;
            $('.com-tu').on("focus", function () {
                var self = $(this)
                if (self.attr('placeholder')) {
                  zhi = self.attr('placeholder');
                }
                self.attr('placeholder', '');
            });

            $('.com-tu').on('blur', function () {
                $(this).attr('placeholder', zhi)
            })
        },
        checkMobile : function(identifier) {  //验证手机号
          var re = /^1\d{10}$/;
          return re.test(identifier);
        },
        captchaRefresh : function(){   //刷新图片验证码
            $('.captcha-refresh').click(function() {
              activityRegister.imgCodeRe();
            });
        },
        //语音验证码
        voiceValidateFun : function(){
            return $(".voice").on('click', '.voice-validate', function(e) {
                var element, isMobile, url;
                e.preventDefault();
                isMobile = activityRegister.checkMobile($("#reg_identifier").val().trim());
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
                        phone: $("#reg_identifier").val().trim()
                    }
                }).success(function(json) {
                    var button, count, intervalId, timerFunction;
                    if (json.ret_code === 0) {
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
        },
        setup : function(options){  //初始化
            this.registerTitle = options.registerTitle;
            this.isNOShow = options.isNOShow;
            this.hasCallBack = options.hasCallBack;
            this.callBack = options.callBack;    //回调函数

            if(this.isNOShow == '1'){
                activityRegister.initFun();
                activityRegister.imgCodeFun();
                activityRegister.imgCodePost();
                activityRegister.registerSubmitFun();
                activityRegister.captchaRefresh();
                activityRegister.voiceValidateFun();
                activityRegister.inputValidateFun()
            }else{
                $('#denglu').hide();
            }
        },
        activityRegisterInit : function(options) {
            activityRegister.setup(options);
        }
    })
      return {
        activityRegister : activityRegister
      }
    this.COMPLEXIFY_BANLIST = '123456|password|12345678|1234|pussy|12345|dragon|qwerty|696969|mustang|letmein|baseball|master|michael|football|shadow|monkey|abc123|pass|fuckme|6969|jordan|harley|ranger|iwantu|jennifer|hunter|fuck|2000|test|batman|trustno1|thomas|tigger|robert|access|love|buster|1234567|soccer|hockey|killer|george|sexy|andrew|charlie|superman|asshole|fuckyou|dallas|jessica|panties|pepper|1111|austin|william|daniel|golfer|summer|heather|hammer|yankees|joshua|maggie|biteme|enter|ashley|thunder|cowboy|silver|richard|fucker|orange|merlin|michelle|corvette|bigdog|cheese|matthew|121212|patrick|martin|freedom|ginger|blowjob|nicole|sparky|yellow|camaro|secret|dick|falcon|taylor|111111|131313|123123|bitch|hello|scooter|please|porsche|guitar|chelsea|black|diamond|nascar|jackson|cameron|654321|computer|amanda|wizard|xxxxxxxx|money|phoenix|mickey|bailey|knight|iceman|tigers|purple|andrea|horny|dakota|aaaaaa|player|sunshine|morgan|starwars|boomer|cowboys|edward|charles|girls|booboo|coffee|xxxxxx|bulldog|ncc1701|rabbit|peanut|john|johnny|gandalf|spanky|winter|brandy|compaq|carlos|tennis|james|mike|brandon|fender|anthony|blowme|ferrari|cookie|chicken|maverick|chicago|joseph|diablo|sexsex|hardcore|666666|willie|welcome|chris|panther|yamaha|justin|banana|driver|marine|angels|fishing|david|maddog|hooters|wilson|butthead|dennis|fucking|captain|bigdick|chester|smokey|xavier|steven|viking|snoopy|blue|eagles|winner|samantha|house|miller|flower|jack|firebird|butter|united|turtle|steelers|tiffany|zxcvbn|tomcat|golf|bond007|bear|tiger|doctor|gateway|gators|angel|junior|thx1138|porno|badboy|debbie|spider|melissa|booger|1212|flyers|fish|porn|matrix|teens|scooby|jason|walter|cumshot|boston|braves|yankee|lover|barney|victor|tucker|princess|mercedes|5150|doggie|zzzzzz|gunner|horney|bubba|2112|fred|johnson|xxxxx|tits|member|boobs|donald|bigdaddy|bronco|penis|voyager|rangers|birdie|trouble|white|topgun|bigtits|bitches|green|super|qazwsx|magic|lakers|rachel|slayer|scott|2222|asdf|video|london|7777|marlboro|srinivas|internet|action|carter|jasper|monster|teresa|jeremy|11111111|bill|crystal|peter|pussies|cock|beer|rocket|theman|oliver|prince|beach|amateur|7777777|muffin|redsox|star|testing|shannon|murphy|frank|hannah|dave|eagle1|11111|mother|nathan|raiders|steve|forever|angela|viper|ou812|jake|lovers|suckit|gregory|buddy|whatever|young|nicholas|lucky|helpme|jackie|monica|midnight|college|baby|cunt|brian|mark|startrek|sierra|leather|232323|4444|beavis|bigcock|happy|sophie|ladies|naughty|giants|booty|blonde|fucked|golden|0|fire|sandra|pookie|packers|einstein|dolphins|chevy|winston|warrior|sammy|slut|8675309|zxcvbnm|nipples|power|victoria|asdfgh|vagina|toyota|travis|hotdog|paris|rock|xxxx|extreme|redskins|erotic|dirty|ford|freddy|arsenal|access14|wolf|nipple|iloveyou|alex|florida|eric|legend|movie|success|rosebud|jaguar|great|cool|cooper|1313|scorpio|mountain|madison|987654|brazil|lauren|japan|naked|squirt|stars|apple|alexis|aaaa|bonnie|peaches|jasmine|kevin|matt|qwertyui|danielle|beaver|4321|4128|runner|swimming|dolphin|gordon|casper|stupid|shit|saturn|gemini|apples|august|3333|canada|blazer|cumming|hunting|kitty|rainbow|112233|arthur|cream|calvin|shaved|surfer|samson|kelly|paul|mine|king|racing|5555|eagle|hentai|newyork|little|redwings|smith|sticky|cocacola|animal|broncos|private|skippy|marvin|blondes|enjoy|girl|apollo|parker|qwert|time|sydney|women|voodoo|magnum|juice|abgrtyu|777777|dreams|maxwell|music|rush2112|russia|scorpion|rebecca|tester|mistress|phantom|billy|6666|albert|111111|11111111|112233|121212|123123|123456|1234567|12345678|131313|232323|654321|666666|696969|777777|7777777|8675309|987654|abcdef|password1|password12|password123|twitter'.split('|');
  });
}).call(this);

