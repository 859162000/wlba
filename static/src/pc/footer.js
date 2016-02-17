require(['jquery'], function( $ ) {
    var checkUserStatus = function(){
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
                        window.location.href = '/accounts/home/'
                    }else{
                        window.location.href = '/qiye/profile/edit/'
                    }
                })
            }
        }).fail(function(data){
            var result = JSON.parse(data.responseText)
            if(result.ret_code != 20001){
                window.location.href = '/qiye/info/'
            }else{
                window.location.href = '/accounts/home/'    
            }
        })
    }
    $('#investment,#checkUserType').on('click',function(){
        if($('.checkLoginStatus').length > 0){
            checkUserStatus();
        }else{
            if($(this).hasClass('samll-nav-guide')){
                window.location.href = '/qiye/register/'
            }else{
                window.location.href = '/accounts/home/'
            }
        }
    })

})