var org = (function(){
    var lib = {
        test :function(){
            console.log('test')
        }
    }
    return {
        test : lib.test()
    }
})()



var list = (function($, org){
    var list = {
        init :function(){

        }
    };
    return {
        init : list.init()
    }
})(org)
