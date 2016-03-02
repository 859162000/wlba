(function() {
    require.config({
        paths: {
            jquery: '/static/js/lib/jquery.min',
        },
        shim: {
            'jquery.modal': ['jquery'],
        }
    });
    require(['jquery'],
    function($, re) {

		var csrfSafeMethod, getCookie, sameOrigin,
          getCookie = function (name) {
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
      csrfSafeMethod = function (method) {
          return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
      };
      sameOrigin = function (url) {
          var host, origin, protocol, sr_origin;
          host = document.location.host;
          protocol = document.location.protocol;
          sr_origin = "//" + host;
          origin = protocol + sr_origin;
          return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
      };



      $.ajaxSetup({
          beforeSend: function (xhr, settings) {
              if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                  xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
              }
          }
      });

        var h5_user_status;
		$.ajax({
			url: '/api/user_login/',
			type: 'post',
			success: function (data1) {
				h5_user_status = data1.login;
			}
		})

        var id_front_image,id_back_image,id_user_image,id_bank_image,new_phone;
        var docObj,imgObjPreview;

        var file_1 = document.getElementById("id_front_image").value;
        var file_2 = document.getElementById("id_back_image").value;
        var file_3 = document.getElementById("id_user_image").value;
        var phone_true = false;
        var code_num = $('.input_code').val();

        var id_front_image_input = document.getElementById("id_front_image");
        var file_img_1 = document.getElementById("file_img_1");
        var input_parent_1 = $('.input_box_1');
        var id_back_image_input = document.getElementById("id_back_image");
        var file_img_2 = document.getElementById("file_img_2");
        var input_parent_2 = $('.input_box_2');
        var id_user_image_input = document.getElementById("id_user_image");
        var file_img_3 = document.getElementById("file_img_3");
        var input_parent_3 = $('.input_box_3');

        $('#id_front_image').bind('change',function(){
            select_img(id_front_image_input,file_img_1,input_parent_1);
        })

        $('#id_back_image').bind('change',function(){
            select_img(id_back_image_input,file_img_2,input_parent_2);
        })

        $('#id_user_image').bind('change',function(){
            select_img(id_user_image_input,file_img_3,input_parent_3);
        })

        var error_file_status;
        function select_img(docObj,file_img,input_parent){
            var filename = docObj.value;
            var mime = filename.toLowerCase().substr(filename.lastIndexOf("."));
            //alert(mime);
            var file_size = docObj.files[0].size;
            //alert(file_size);
            if((mime==".jpg"||mime==".png"||mime==".bmp")&&file_size<'2097152'){

                setImagePreview(docObj,file_img);
            }else{
                docObj.value ='';
                if(mime==".jpg"||mime==".png"||mime==".bmp"){
                    error_file_status = '上传文件太大';
                }else{
                    error_file_status = '上传文件格式错误';
                }
                if(input_parent.hasClass('input_box_1')){
                    $('#user_img_1').hide();
                    $('.error_right_file_1').text(error_file_status).show();
                }
                if(input_parent.hasClass('input_box_2')){
                    $('#user_img_2').hide();
                    $('.error_right_file_2').text(error_file_status).show();
                }
                if(input_parent.hasClass('input_box_3')){
                    $('#user_img_3').hide();
                    $('.error_right_file_3').text(error_file_status).show();
                }
                //return false;
            }
        }


        function setImagePreview(docObj,imgObjPreview) {
                if(docObj.files &&docObj.files[0])
                {
                //火狐下，直接设img属性
                imgObjPreview.style.display = 'block';
                imgObjPreview.style.width = '158px';
                //imgObjPreview.style.height = '100px';
                //imgObjPreview.src = docObj.files[0].getAsDataURL();

                //火狐7以上版本不能用上面的getAsDataURL()方式获取，需要一下方式
                imgObjPreview.src = window.URL.createObjectURL(docObj.files[0]);
                }
                else
                {
                //IE下，使用滤镜
                docObj.select();
                var imgSrc = document.selection.createRange().text;
                var localImagId = document.getElementById("localImag");
                //必须设置初始大小
                localImagId.style.width = "158px";
                //localImagId.style.height = "100px";
                //图片异常的捕捉，防止用户修改后缀来伪造图片



                try{
                localImagId.style.filter="progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale)";
                localImagId.filters.item("DXImageTransform.Microsoft.AlphaImageLoader").src = imgSrc;
                }
                catch(e)
                {
                alert("您上传的图片格式不正确，请重新选择!");
                return false;
                }
                imgObjPreview.style.display = 'none';
                document.selection.empty();
                }
                var img_url = imgObjPreview.src;
                if(docObj.id=='id_front_image'){
                    id_front_image = img_url;
                    $('#user_img_1').show();
                    $('.error_right_file_1').hide();
                }else if(docObj.id=='id_back_image'){
                    id_back_image = img_url;
                    $('#user_img_2').show();
                    $('.error_right_file_2').hide();
                }else if(docObj.id=='id_user_image'){
                    id_user_image = img_url;
                    $('#user_img_3').show();
                    $('.error_right_file_3').hide();
                }
                return true;
            }

        /*输入手机号，验证码*/
        var myreg = /^(((12[0-9]{1}|)|(13[0-9]{1})|(15[0-9]{1})|(18[0-9]{1})|(14[57]{1})|(17[0678]{1}))+\d{8})$/;
        $('.input_phone').on('focus',function(){
           $('.get_code').text('获取验证码').removeAttr('disabled').removeClass('wait');
        });


        $('.input_phone').blur(function(){
            if(!myreg.test($(".input_phone").val()))
            {
                $('.error_phone').show();
                phone_true = false;
            }else{
                $('.error_phone').hide();
                phone_true = true;
                $('.status_code').hide();
            }
        });

        var time_count = 60;
		var time_intervalId;
        var timerFunction = function () {
            if (time_count > 1) {
                time_count--;
                return $('.get_code').text(time_count + '秒后可重发');
            } else {
                clearInterval(time_intervalId);
                $('.get_code').text('重新获取').removeAttr('disabled').removeClass('wait');
                //return $(document.body).trigger('from:captcha');
            }
        };

        var result;
        $('.get_code').click(function(){
            if(phone_true){
                $('.status_code').hide();
                var phone = $('.input_phone');

                $('.get_code').attr('disabled', 'disabled').addClass('wait');
                time_count = 60;
                time_intervalId = setInterval(timerFunction, 1000);
                time_intervalId;

                $.ajax({
                    url: '/api/manual_modify/phone_validation_code/'+phone.val()+'/',
                    type: 'POST',
                    success: function (xhr) {
                        $('.error_form').hide();
                    },
                    error: function (xhr) {
                        result = JSON.parse(xhr.responseText);
                        $('.error_form').text(result.message).show();

                        clearInterval(time_intervalId);
                        time_count = 0;
                        $('.get_code').text('重新获取').removeAttr('disabled').removeClass('wait');

                    }
                });
            }else{
                $('.status_code .false').text('请先输入正确的手机号');
                $('.status_code').show().children('.true').hide();
            }

        });

        /*输入手机号，验证码结束*/


        $('.button').click(function(){
            $('.error_form').hide();
            file_1 = document.getElementById("id_front_image").value;
            file_2 = document.getElementById("id_back_image").value;
            file_3 = document.getElementById("id_user_image").value;
            code_num = $('.input_code').val();

            if(file_1&&file_2&&file_3&&phone_true&&code_num){
                var form =$("#form");
                var formData = new FormData($( "#form" )[0]);
                //alert(formData);
                $.ajax({
                    url: '/api/manual_modify/phone/' ,
                    type: 'POST',
                    data: formData,
                    async: false,
                    cache: false,
                    contentType: false,
                    processData: false,
                    success: function (xhr) {

                        $('.error_form').hide();

                        $('.status .false').hide();
                        $('.status .true').show();
                        $('.status').show();
                        window.location.href = '/accounts/security/';

                    },
                    error: function (xhr) {
                        result = JSON.parse(xhr.responseText);
                        $('.error_form').text(result.message).show();
                        $('.input_code').val('');
                    }
                });
            }else{
                $('.error_form').text('请将表单填写完整').show();

            }


        });



    })

}).call(this);