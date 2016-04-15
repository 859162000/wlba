;(function(org){
    org.ajax({
        url: '/api/april_reward/fetch/',
        type: 'post',
        data: {
        },
        success: function (data) {
            var result = data.weekranks;
            var str = '',sty = '',icon = '',coupon='';
            substring(data.week_sum_amount);
            $.each(result,function(i,o){
                if(i <= 2){
                    sty ='red';
                    icon = 'icon'+ (i+1)
                    if(i == 0){
                        coupon = '5张百元加油卡+2张星美电影票';
                    }else if(i == 1){
                        coupon = '3张百元加油卡+2张星美电影票';
                    }else{
                        coupon = '2张百元加油卡+2张星美电影票';
                    }
                }else{
                    sty ='';coupon='1张百元加油卡+2张星美电影票'
                }
                str+='<tr class='+ sty +'><td><span class='+ icon +'>'+ (i+1) +'</span>'+o.phone.substring(0,3)+'****' +o.phone.substr(o.phone.length-4) +'</td><td class="tl">'+ fmoney(o.amount__sum) +' 元</td><td>'+ coupon +'</td></tr>'
            })
            $('#list').append(str);

            substring_2(data.week_sum_amount);
        }
    })
    function fmoney(s, n) {
        n = n > 0 && n <= 20 ? n : 2;
        s = parseFloat((s + "").replace(/[^\d\.-]/g, "")).toFixed(n) + "";
        var l = s.split(".")[0].split("").reverse();
        t = "";
        for (i = 0; i < l.length; i++) {
            t += l[i] + ((i + 1) % 3 == 0 && (i + 1) != l.length ? "," : "");
        }
        if(n == 0){
            return t.split("").reverse().join("");
        }else{
            return t.split("").reverse().join("");
        }
    }

    /*逐个字符*/
    function substring(text){
        //alert(text.length);

        var num_length = text.length;
        if(num_length==13){
            num_length+=2;
        }
        if(num_length==14||num_length==10){
            num_length+=1;
        }

        for(var i=num_length; i>=0; i--) {
            if (num_length - 3 != i) {
                //num = text.charAt(i);
                if(num_length - 7 == i||num_length - 11 == i||num_length - 15 == i){
                    $('.transaction-counts').prepend('<span class="num_2"></span>');
                    //alert(i);
                }else{
                    if(num_length - 2 == i){
                        $('.transaction-counts').prepend('<span class="num_3"></span>');
                    }else{
                        $('.transaction-counts').prepend('<span class="num_1"></span>');
                    }

                }

            }
        }
        if(text.length>=7){
            $('.transaction-counts').prepend('<span class="num_1"></span>');
            if(text.length!=13&&text.length>10){
                $('.transaction-counts').prepend('<span class="num_1"></span>');
            }
        }
    };

    function substring_2(text){
        var num_2;
        var box_num_2 = $('.transaction-counts .num_1').length;
        var box_num_3 = $('.transaction-counts .num_2').length;
        for(var i=text.length;i>=0;i--) {
            if (text.length - 3 != i) {
                num_2 = text.charAt(i);
                $('.transaction-counts .num_1').eq(box_num_2).text(num_2);
                box_num_2--;
            }
        }

    };

    wlb.ready({
        app: function (mixins) {
            $('#investmentBtn').on('click',function(){
                mixins.jumpToManageMoney();
            })
        },
        other: function(){
            $('#investmentBtn').on('click',function() {
                window.location.href = '/p2p/list/';
            })
        }
    })
})(org);