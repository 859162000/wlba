(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
			'fileinput': 'lib/fileinput'
        },
        shim: {
            'jquery.modal': ['jquery'],
			'fileinput': ['jquery']
        }
    });
    require(['jquery','fileinput'],
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

//		$('.button').click(function(){
//            $.ajax({
//                url: '/api/manual_modify/phone/',
//                type: 'post',
//                success: function (data1) {
//
//                }
//            })
//		})



        $('.main_title_top').click(function(){
            alert($('#id_id_back_image').val());
            var img_url = $('#id_id_back_image').val();
            $('#img').attr('src',img_url);
        });

        window.onload=function(){

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

        }

    })

}).call(this);