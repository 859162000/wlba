require(['jquery'], function( $ ) {
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
                   $('.finishEd').show()
                }else{
                   $('.finishingV').show()
                }
            })
        }
    }).fail(function(data){
        var result = JSON.parse(data.responseText);
        if(result.ret_code == 20001){

        }else{
           $('.finishing').show();
        }
    })
})