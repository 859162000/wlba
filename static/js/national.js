/*function heightshow(ele,box){
    box.setAttribute("data",1)
    ele.onclick=function(){
        var data=box.getAttribute("data"),
            h=box.offsetHeight,
            w=box.offsetWidth;
        console.log(w+"  "+h);
        if(h>0){
            box.style.display="block"
            box.setAttribute("data",2)
        }else{
            box.style.display="none";
            box.setAttribute("data",1)
        }
    }
}*/



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


