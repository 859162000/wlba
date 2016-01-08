require(['jquery'], function( $ ) {
    _getQueryStringByName = function(name){
            var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
             if(result == null || result.length < 1){
                 return '';
             }
             return result[1];
    }
    $('#investment').on('click',function(){
        if($('.checkLoginStatus').length > 0){
            $.ajax({
              url: '/qiye/profile/exists/',
              type: "GET",
              data: {
              }
            }).done(function(data) {
                if(data.ret_code == 10000){
                    $.ajax({
                      url: '/qiye/profile/get/',
                      type: "GET",
                      data: {
                      }
                    }).done(function(data) {
                        if(data.data.status == '审核通过'){
                             window.location.href = '/accounts/home/';
                        }else{
                            window.location.href = '/qiye/profile/edit/';
                        }
                    })
                }
            }).fail(function(data){
                var result = JSON.parse(data.responseText);
                if(result.ret_code == 20001){
                    window.location.href = '/qiye/register/'
                }else{
                    window.location.href = '/qiye/info/';
                }
            })
        }else{
            window.location.href = '/qiye/register/'
        }
    })

    $.ajax({
      url: '/qiye/profile/exists/',
      type: "GET",
      data: {
      }
    }).done(function(data) {
        if(data.ret_code == 10000){
            $.ajax({
              url: '/qiye/profile/get/',
              type: "GET",
              data: {
              }
            }).done(function(data) {
                if(data.data.status == '审核通过'){
                     $('#checkUserType').attr('href','/accounts/home/')
                }else{
                    $('#checkUserType').attr('href','/qiye/profile/edit/')
                    $('#minNavs').hide()
                }
            })
        }
    }).fail(function(data){
        var result = JSON.parse(data.responseText);
        if(result.ret_code == 20001){
            $('#checkUserType').attr('href','/accounts/home')
        }else{
           $('#checkUserType').attr('href','/qiye/info/')
           $('#minNavs').hide()
        }
    })
})