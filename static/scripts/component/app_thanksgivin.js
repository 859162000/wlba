

wlb.ready({
    app: function(mixins){

        document.getElementById('appjiang-button').onclick= function(){
            mixins.sendUserInfo(function(data){
                 document.getElementById('appjiang-button').innerHTML= JSON.stringify(data);
            })
        }
    },
    other: function(){
        console.log(2)
    }
})

