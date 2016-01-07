require.config({
    paths: {
        'jquery.placeholder': 'lib/jquery.placeholder',
        'jquery.form': 'lib/jquery.form',
        'jquery.validate': 'lib/jquery.validate',
        'jquery.modal': 'lib/jquery.modal.min',
        'csrf' : 'model/csrf',
        'jquery.webuploader': 'lib/webuploader.min',
        tools: 'lib/modal.tools',
        upload: 'upload'
    },
    shim: {
        'jquery.placeholder': ['jquery'],
        'jquery.form': ['jquery'],
        'jquery.validate': ['jquery'],
        'jquery.modal': ['jquery'],
        'jquery.webuploader': ['jquery']
    }
});

require(['jquery','jquery.form', 'jquery.validate', 'jquery.placeholder', 'lib/modal', 'tools', 'jquery.webuploader', 'upload', 'csrf'], function ($, form ,validate, placeholder, modal, tool, webuploader) {
    //提交表单
    var qiyeFormValidate = $('#qiyeForm').validate({});
    $('.save-btn').on('click',function(){
        if(qiyeFormValidate.form()){
            if($('input[name="business_license"]').val() == ''){
                $('.yezzImg').show()
                return
            }else{
                $('.yezzImg').hide()
            }
            if($('input[name="registration_cert"]').val() == ''){
                $('.swdjzImg').show()
                return
            }else{
                $('.swdjzImg').hide()
            }
            $('#qiyeForm').ajaxSubmit({
                success: function (data) {
                    if (data.ret_code == 10000) {
                        window.location.href = '/accounts/home/';
                    } else {
                        result = JSON.parse(data.responseText);
                        return tool.modalAlert({
                            title: '温馨提示',
                            msg: result.message
                        });
                    }
                },
                error :function(data){
                    result = JSON.parse(data.responseText);
                    return tool.modalAlert({
                        title: '温馨提示',
                        msg: result.message
                    });
                }
            })
        }
    })
    //营业执照
   $('#yezz').diyUpload({
        url:'/qiye/profile/extra/',
        success:function( data ) {
            $('input[name="business_license"]').val(data.filename);
            $('#yezz').find('input[type="file"]').remove()
            $('#yezz').find('.diyButton').hide()
            $('#yezz').parent().find('img').remove();
        },
        error:function( data ) {
            result = JSON.parse(data.responseText);
            return tool.modalAlert({
              title: '温馨提示',
              msg: result.message
            });
        },
        buttonText : '营业执照',
        chunked:true,
        // 分片大小
        chunkSize:512 * 1024,
        //最大上传的文件数量, 总文件大小,单个文件大小(单位字节);
        fileNumLimit:1,
        fileSizeLimit:500000 * 1024,
        fileSingleSizeLimit:50000 * 1024,
        accept: {},
        fileVal: 'business_license'
        //sendAsBinary : true
    });
    //登记证
    $('#swdjz').diyUpload({
        url: '/qiye/profile/extra/',
        success:function( data ) {
            $('input[name="registration_cert"]').val(data.filename);
            $('#swdjz').find('input[type="file"]').remove()
            $('#swdjz').find('.diyButton').hide()
            $('#swdjz').parent().find('img').remove();
        },
        error:function( data ) {
            return tool.modalAlert({
              title: '温馨提示',
              msg: data.message
            });
        },
        buttonText : '登记证',
        chunked:true,
        // 分片大小
        chunkSize:512 * 1024,
        //最大上传的文件数量, 总文件大小,单个文件大小(单位字节);
        fileNumLimit:1,
        fileSizeLimit:500000 * 1024,
        fileSingleSizeLimit:50000 * 1024,
        accept: {
            title:"Images",
            extensions:"gif,jpg,jpeg,bmp,png",
            mimeTypes:"image/*"
        },
        fileVal:'registration_cert'
        //sendAsBinary : true
    });
    //输入框
    $('input, textarea').placeholder();

    if($('input[name="pageType"]').val() != 'edit'){
        new PCAS("deposit_bank_province","deposit_bank_city");
    }else{
        $.ajax({
          url: '/qiye/profile/exists/',
          type: "GET",
          data: {
          }
        }).done(function(data) {

        }).fail(function(data){
            $('.notThrough').text('请完善信息')
        })
    }


    /*----------------------验证码-----------------*/
    //图片验证码
    $('#button-get-code-btn').click(function() {
      var re = /^1\d{10}$/;
      if(re.test($('input[name="certigier_phone"]').val())){
        $('#img-code-div2').modal();
        $('#img-code-div2').find('#id_captcha_1').val('');
        var url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
        return $.getJSON(url, {}, function(json) {
            $('input[name="captcha_0"]').val(json.key);
            return $('img.captcha').attr('src', json.image_url);
        });
      }else{
        tool.modalAlert({title: '温馨提示',msg: '手机号格式不正确'});
      }
    });
    //刷新验证码
    $('.captcha-refresh').on('click',function(){
        url = location.protocol + "//" + window.location.hostname + ":" + location.port + "/captcha/refresh/?v=" + (+new Date());
      return $.getJSON(url, {}, function(json) {
        $('input[name="captcha_0"]').val(json.key);
        return $('img.captcha').attr('src', json.image_url);
      });
    })
    //短信验证码
    $("#submit-code-img4").click(function(e) {
      var captcha_0, captcha_1, count, element, intervalId, phoneNumber, timerFunction;
      element = $('#button-get-code-btn');
      if ($(element).attr('disabled')) {
        return;
      }
      phoneNumber = $('input[name="certigier_phone"]').val();
      captcha_0 = $(this).parents('form').find('#id_captcha_0').val();
      captcha_1 = $(this).parents('form').find('.captcha').val();
      $.ajax({
        url: "/api/phone_validation_code/" + phoneNumber + "/",
        type: "POST",
        data: {
          captcha_0: captcha_0,
          captcha_1: captcha_1
        }
      }).fail(function(xhr) {
        var result;
        clearInterval(intervalId);
        $(element).text('重新获取').removeAttr('disabled').addClass('button-red').removeClass('button-gray');
        result = JSON.parse(xhr.responseText);
        if (result.type === 'captcha') {
          return $("#submit-code-img4").parent().parent().find('.code-img-error').html(result.message);
        } else {
          if (xhr.status >= 400) {
            return tool.modalAlert({
              title: '温馨提示',
              msg: result.message
            });
          }
        }
      }).success(function() {
        element.attr('disabled', 'disabled').removeClass('button-red').addClass('button-gray');
        $('.voice-validate').attr('disabled', 'disabled');
        return $.modal.close();
      });
      intervalId;
      count = 60;
      $(element).attr('disabled', 'disabled').addClass('disabled');
      $('.voice-validate').attr('disabled', 'disabled');
      timerFunction = function() {
        if (count >= 1) {
          count--;
          return $(element).text('重新获取(' + count + ')');
        } else {
          clearInterval(intervalId);
          $(element).text('重新获取').removeAttr('disabled').removeClass('disabled').removeClass('button-gray');
          $('.voice').removeClass('hidden');
          $('.voice-validate').removeAttr('disabled');
          return $('.voice  .span12-omega').html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>');
        }
      };
      timerFunction();
      return intervalId = setInterval(timerFunction, 1000);
    });
    $(".voice").on('click', '.voice-validate', function(e) {
      var element, url;
      e.preventDefault();
      if ($(this).attr('disabled') && $(this).attr('disabled') === 'disabled') {
        return;
      }
      element = $('.voice .span12-omega');
      url = $(this).attr('href');
      return $.ajax({
        url: url,
        type: "POST",
        data: {
          phone: $("#button-get-code-btn").attr('data-phone').trim()
        }
      }).success(function(json) {
        var button, count, intervalId, timerFunction;
        if (json.ret_code === 0) {
          intervalId;
          count = 60;
          button = $("#button-get-code-btn");
          button.attr('disabled', 'disabled').addClass('button-gray');
          $('.voice').addClass('tip');
          timerFunction = function() {
            if (count >= 1) {
              count--;
              return element.text('语音验证码已经发送，请注意接听（' + count + '）');
            } else {
              clearInterval(intervalId);
              element.html('没有收到验证码？请尝试<a href="/api/ytx/send_voice_code/2/" class="voice-validate">语音验证</a>');
              element.removeAttr('disabled');
              button.removeAttr('disabled').addClass('button-red').removeClass('button-gray');
              return $('.voice').removeClass('tip');
            }
          };
          timerFunction();
          return intervalId = setInterval(timerFunction, 1000);
        } else {
          return element.html('系统繁忙请尝试短信验证码');
        }
      }).fail(function(xhr) {
        if (xhr.status > 400) {
          return tool.modalAlert({
            title: '温馨提示',
            msg: result.message
          });
        }
      });
    });
     /*----------------------验证码-----------------*/
});
