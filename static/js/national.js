require.config({
    paths: {
        jquery : "lib/jquery.min"
    }
});
require(["jquery"],function($){
    function toggles(obj){
        obj.slideToggle()
    }
    $("#dbtn").on("click",function(){
        toggles($("#dluo"));
    })
    $("#ashref").on("click",function(){
        toggles($("#dluo2"));
    })
    $("#rule").on("click",function(){
        toggles($("#relebox"));
    })
    $("#btns").on("click",function(){
        toggles($("#relebox3"));
    })

})


