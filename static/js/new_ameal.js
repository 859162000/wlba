/**
 * Created by zzl on 16-1-25.
 */
(function(){
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });
    require(["jquery"],function($){
        $(".years_pot_minbox").on("click",function(){
            var data = $(this).attr("data");
            isdata(data)
        })
        isdata = function(data){
            if(data == 2){
                $("#boil").animate({"left" : 16+"%", "top" : 80+"px"},500);
            }else if(data == 3){
                $("#boil").animate({"left" : 84+"%", "top" : 80+"px"},500);
            }else if(data == 4){
                $("#boil").animate({"left" : 49.5+"%", "top" : 244+"px"},500);
            }else{
                $("#boil").animate({"left" : 50+"%", "top" : -85+"px"},500);
            }
        }
        dialog = function(){

        }

    })
})()