;(function(org){
    org.ajax({
        url: '/api/april_reward/fetch/',
        type: 'post',
        data: {
        },
        success: function (data) {
            var result = data.weekranks;
            var str = '',sty = '',icon = '';
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
            $('.transaction-counts').html(fmoney1(data.week_sum_amount,2))
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
    function fmoney1(s, n) {
        n = n > 0 && n <= 20 ? n : 2;
        s = parseFloat((s + "").replace(/[^\d\.-]/g, "")).toFixed(n) + "";
        var l = s.split(".")[0].split("").reverse(), r = s.split(".")[1];
        t = "";
        for (i = 0; i < l.length; i++) {
            t += l[i] + ((i + 1) % 3 == 0 && (i + 1) != l.length ? "," : "");
        }
        return t.split("").reverse().join("") + "," + r;
    }
})(org);