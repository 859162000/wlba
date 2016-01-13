(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',

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

        var h5_user_static;
		$.ajax({
			url: '/api/user_login/',
			type: 'post',
			success: function (data1) {
				h5_user_static = data1.login;
			}
		})

        var id_front_image,id_back_image,id_user_image,id_bank_image,new_phone;
        var docObj,imgObjPreview;
        $('#id_front_image').on('change',function(){
            docObj=document.getElementById("id_front_image");
            imgObjPreview=document.getElementById("file_img_1");
            setImagePreview(docObj,imgObjPreview);
            $('#user_img_1').show();
        });
        $('#id_back_image').on('change',function(){
            docObj=document.getElementById("id_back_image");
            imgObjPreview=document.getElementById("file_img_2");
            setImagePreview(docObj,imgObjPreview);
            $('#user_img_2').show();
        });
        $('#id_user_image').on('change',function(){
            docObj=document.getElementById("id_user_image");
            imgObjPreview=document.getElementById("file_img_3");
            setImagePreview(docObj,imgObjPreview);
            $('#user_img_3').show();
        });
        $('#id_bank_image').on('change',function(){
            docObj=document.getElementById("id_bank_image");
            imgObjPreview=document.getElementById("file_img_4");
            setImagePreview(docObj,imgObjPreview);
            $('#user_img_4').show();
        });
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
                }else if(docObj.id=='id_back_image'){
                    id_back_image = img_url;
                }else if(docObj.id=='id_user_image'){
                    id_user_image = img_url;
                }else if(docObj.id=='id_bank_image'){
                    id_bank_image = img_url;
                }
                return true;
            }

        $('.get_code').click(function(){
            var phone = $('.input_phone');
            alert(phone.val());
            $.ajax({
                url: '/api/phone_validation_code/' + phone.val() + '/',
                type: 'POST',
                success: function (xhr) {

            }});
        })

        $('.button').click(function(){
            var form =$("#form");
            //alert(form.action);
            $.ajax({
                url:'/api/manual_modify/phone/',
                type:'post',
                data: form.serialize(),
                dataType: 'json',
                success:function(data){
                    alert('1');
                },
                error:function(data){
                    alert('2');
                }
            })
        });

        //$('#form').submit(function(){
        //    alert($(this).serialize());
        //    return false;
        //});


        //$('.button').click(function(){
        //    //alert(id_front_image);
        //    //alert(id_back_image);
        //    //alert(id_user_image);
        //    //alert(id_bank_image);
        //    var new_phone = $('.input_phone').val();
        //    var new_code = $('.new_code').val();
        //    $.ajax({
        //        url: '/api/manual_modify/phone/',
        //        type: 'post',
        //        data: {
        //            'id_front_image': id_front_image,
        //            'id_back_image': id_back_image,
        //            'id_user_image': id_user_image,
        //            //'id_bank_image': id_bank_image,
        //            'new_phone': new_phone,
        //            'validate_code': new_code
        //        },
        //        success: function (data1) {
		//
        //        }
        //    });
        //})


        window.onload=function(){


        }

    })

}).call(this);