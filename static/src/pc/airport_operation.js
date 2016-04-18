(function(){
    require.config({
        paths: {
            jquery : 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            tools: 'lib/modal.tools'
        },
        shim: {
            'jquery.model': ["jquery"]
        }
    })
    require(['jquery'],function($){
        $(".tz_btn").on("click",function(){
            $.ajax({
                type: "post",
                url: "/api/airport_reward/fetch/",
                dataType: 'json',
                success: function(data){
                    console.log(data)
                }
            })
        })

    })



}).call(this);