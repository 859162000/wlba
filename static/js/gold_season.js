(function() {
  require.config({
    paths: {
        jquery: 'lib/jquery.min'
    }
  });

  require(['jquery'], function($) {
    //初始化数据
    $.ajax({
        url: '/api/gettopofearings/',
        type: "POST"
    }).done(function (json) {
        var rankingList_phone = [];
        var rankingList_amount = [];
        var json_one;
        for(var i=0; i<json.records.length; i++){
            json_one = json.records[i];
            if(json_one!=''){
                if(i<=2){
                    rankingList_phone.push(['<li class="front">'+json_one.phone+'</li>'].join(''));
                    rankingList_amount.push(['<li class="front">'+json_one.amount+'</li>'].join(''));
                }else{
                    rankingList_phone.push(['<li>'+json_one.phone+'</li>'].join(''));
                    rankingList_amount.push(['<li>'+json_one.amount+'</li>'].join(''));
                }
            }else{
                rankingList_phone.push(['<li>虚位以待</li>'].join(''));
                rankingList_amount.push(['<li>虚位以待</li>'].join(''));
            }

        }
        $('.rankingList ul.two').html(rankingList_phone.join(''));
        $('.rankingList ul.three').html(rankingList_amount.join(''));
       })
    })
}).call(this);



