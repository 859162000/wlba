function heightshow(ele,box){
    box.setAttribute("data",1)
    ele.onclick=function(){
        var data=box.getAttribute("data");
        if(data==1){
            box.style.display="block"
            box.setAttribute("data",2)
        }else{
            box.style.display="none";
            box.setAttribute("data",1)
        }
    }
}



/*require.config({
    paths: {
        jquery : "lib/jquery.min"
    }
});
require(["jquery"],function($){
    function heightshow($ele,$box){
        $ele.on('click',function(){
            var dis=$box.attr("display");
            if(dis=="block"){
                $box.hide();
                $box.attr("display","none");
            }else{
                $box.show();
                $box.attr("display","block");
            }

        })
    }
    heightshow($("#dbtn"),$("#dluo"))

})*/


