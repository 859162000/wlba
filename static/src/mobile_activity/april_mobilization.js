;(function(org){
    org.ajax({
        url: '/api/april_reward/fetch/',
        type: 'post',
        data: {
        },
        success: function (data) {
            var result = data.weekranks;
            var str = '',sty = '',icon = '';
            substring(data.week_sum_amount);
            $.each(result,function(i,o){
                if(i <= 2){
                    sty ='red';
                    icon = 'icon'+ (i+1)
                }else{
                    sty ='';
                }
                str+='<tr class='+ sty +'><td><span class='+ icon +'>'+ (i+1) +'</span>'+o.phone.substring(0,3)+'****' +o.phone.substr(o.phone.length-4) +'</td><td class="tl">'+ fmoney(o.amount__sum) +' 元</td><td>'+ o.coupon +'</td></tr>'
            })
            $('#list').append(str);

            substring_2(data.week_sum_amount);
        }
    })
    function fmoney(s, n) {
        n = n > 0 && n <= 20 ? n : 2;
        s = parseFloat((s + "").replace(/[^\d\.-]/g, "")).toFixed(n) + "";
        var l = s.split(".")[0].split("").reverse(), r = s.split(".")[1];
        t = "";
        for (i = 0; i < l.length; i++) {
            t += l[i] + ((i + 1) % 3 == 0 && (i + 1) != l.length ? "," : "");
        }
        if(n == 0){
            return t.split("").reverse().join("");
        }else{
            return t.split("").reverse().join("") + "," + r;
        }
    }

    function substring(text){
        //alert(text);
        var box_num = $('.transaction-counts .num_1').length;
        for(var i=text.length; i>=0; i--) {
            if (text.length - 3 != i) {
                //num = text.charAt(i);
                if(text.length - 2 == i||text.length - 7 == i){
                    $('.transaction-counts').prepend('<span class="num_2"></span>');

                }else{

                    $('.transaction-counts').prepend('<span class="num_1"></span>');
                }

                //$('.num_wrap .num_1').eq(box_num).text(num);
                box_num--;
            }
        }
        $('.transaction-counts').prepend('<span class="num_1"></span>');

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

        //var width = 78*$('.transaction-counts .num_1').length+25*$('.transaction-counts .num_2').length;
        //$('.transaction-counts').css('margin-left','-'+width/2+'px')

    };
})(org);