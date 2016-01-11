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


		$("#file_1").fileinput({
	        uploadUrl: '/api/manual_modify/phone/', // you must set a valid URL here else you will get an error
	        allowedFileExtensions : ['jpg', 'png','gif'],
	        overwriteInitial: false,
	        maxFileSize: 1000,
	        maxFilesNum: 1,
	        //allowedFileTypes: ['image', 'video', 'flash'],
	        slugCallback: function(filename) {
	            return filename.replace('(', '_').replace(']', '_');
	        }
		});
		$("#file_2").fileinput({
	        uploadUrl: '/api/manual_modify/phone/', // you must set a valid URL here else you will get an error
	        allowedFileExtensions : ['jpg', 'png','gif'],
	        overwriteInitial: false,
	        maxFileSize: 1000,
	        maxFilesNum: 10,
	        //allowedFileTypes: ['image', 'video', 'flash'],
	        slugCallback: function(filename) {
	            return filename.replace('(', '_').replace(']', '_');
	        }
		});
		$("#file_3").fileinput({
	        uploadUrl: '/api/manual_modify/phone/', // you must set a valid URL here else you will get an error
	        allowedFileExtensions : ['jpg', 'png','gif'],
	        overwriteInitial: false,
	        maxFileSize: 1000,
	        maxFilesNum: 10,
	        //allowedFileTypes: ['image', 'video', 'flash'],
	        slugCallback: function(filename) {
	            return filename.replace('(', '_').replace(']', '_');
	        }
		});


        $('.main_title_top').click(function(){
            alert($('#id_id_back_image').val());
            var img_url = $('#id_id_back_image').val();
            $('#img').attr('src',img_url);
        });

        window.onload=function(){
            var result = document.getElementById("img_1");
            var input = document.getElementById("id_id_front_image");

            if(typeof FileReader==='undefined'){
                result.innerHTML = "抱歉，你的浏览器不支持 FileReader";
                input.setAttribute('disabled','disabled');
            }else{
                input.addEventListener('change',readFile,false);
            }


            function readFile(){
                var file = this.files[0];
                if(!/image\/\w+/.test(file.type)){
                    alert("文件必须为图片！");
                    return false;
                }
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function(e){
                    result.innerHTML = '<img src="'+this.result+'" alt=""/>'
                }
            }

            var result_2 = document.getElementById("img_2");
            var input_2 = document.getElementById("id_id_back_image");

            if(typeof FileReader==='undefined'){
                result_2.innerHTML = "抱歉，你的浏览器不支持 FileReader";
                input_2.setAttribute('disabled','disabled');
            }else{
                input_2.addEventListener('change',readFile_2,false);
            }


            function readFile_2(){
                var file = this.files[0];
                if(!/image\/\w+/.test(file.type)){
                    alert("文件必须为图片！");
                    return false;
                }
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function(e){
                    result_2.innerHTML = '<img src="'+this.result+'" alt=""/>'
                }
            }

            var result_3 = document.getElementById("img_3");
            var input_3 = document.getElementById("id_id_user_image");

            if(typeof FileReader==='undefined'){
                result_3.innerHTML = "抱歉，你的浏览器不支持 FileReader";
                input_3.setAttribute('disabled','disabled');
            }else{
                input_3.addEventListener('change',readFile_3,false);
            }


            function readFile_3(){
                var file = this.files[0];
                if(!/image\/\w+/.test(file.type)){
                    alert("文件必须为图片！");
                    return false;
                }
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function(e){
                    result_3.innerHTML = '<img src="'+this.result+'" alt=""/>'
                }
            }
        }

    })

}).call(this);