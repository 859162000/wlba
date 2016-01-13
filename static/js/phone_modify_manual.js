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
                return true;
            }




        window.onload=function(){



            //$('.button').click(function(){
//            $.ajax({
//                url: '/api/manual_modify/phone/',
//                type: 'post',
//                success: function (data1) {
//
//                }
//            })
//		})

            /*
            html5方法
            var result_1 = document.getElementById("user_img_1");
			var result_2 = document.getElementById("user_img_2");
			var result_3 = document.getElementById("user_img_3");
			var result_4 = document.getElementById("user_img_4");
            var input_1 = document.getElementById("id_front_image");
			var input_2 = document.getElementById("id_back_image");
			var input_3 = document.getElementById("id_user_image");
			var input_4 = document.getElementById("id_bank_image");

            if(typeof FileReader==='undefined'){
                $('.upload_img').html('抱歉，你的浏览器不支持 FileReader');
                input_1.setAttribute('disabled','disabled');
				input_2.setAttribute('disabled','disabled');
				input_3.setAttribute('disabled','disabled');
				input_4.setAttribute('disabled','disabled');
            }else{
                input_1.addEventListener('change',readFile,false);
				input_2.addEventListener('change',readFile,false);
				input_3.addEventListener('change',readFile,false);
				input_4.addEventListener('change',readFile,false);
            }

            function readFile(){
				var this_name=this.name;
				//alert(this_name);
                var file = this.files[0];
                if(!/image\/\w+/.test(file.type)){
                    alert("文件必须为图片！");
                    return false;
                }
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function(e){
					if(this_name=='id_front_image'){
						$('#user_img_1').show();
                    	result_1.innerHTML = '<img src="'+this.result+'" alt=""/>';
					}else if(this_name=='id_back_image'){
						$('#user_img_2').show();
                    	result_2.innerHTML = '<img src="'+this.result+'" alt=""/>';
					}else if(this_name=='id_user_image'){
						$('#user_img_3').show();
                    	result_3.innerHTML = '<img src="'+this.result+'" alt=""/>';
					}else if(this_name=='id_bank_image'){
						$('#user_img_4').show();
                    	result_4.innerHTML = '<img src="'+this.result+'" alt=""/>';
					}
                }
            }
            html5方法结束
            */

        }

    })

}).call(this);