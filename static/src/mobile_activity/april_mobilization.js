;(function(org){
    org.ajax({
        url: '/api/april_reward/fetch/',
        type: 'post',
        data: {
        },
        success: function (data) {
            var result = data.weekranks;
            var str = '';
            $.each(result,function(i,o){
                str+='<tr><td>'+o.phone.substring(0,3)+'****' +o.phone.substr(o.phone.length-4) +'</td><td>'+ fmoney(o.amount__sum) +' 元</td><td>'+ o.aa +'</td></tr>'
            })
            $('#list').append(str);
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
        return t.split("").reverse().join("");
    }
})(org);