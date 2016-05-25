(function(a,h,c,b,f,g){a["UdeskApiObject"]=f;a[f]=a[f]||function(){(a[f].d=a[f].d||[]).push(arguments)};g=h.createElement(c);g.async=1;g.src=b;c=h.getElementsByTagName(c)[0];c.parentNode.insertBefore(g,c)})(window,document,"script","http://18612250386.udesk.cn/im_client/js/udeskApi.js?_t=1464059162377","ud"); ud({"panel":{css:{bottom:"43px",right:"30px"}},"code":"h3g84ai","link":"http://18612250386.udesk.cn/im_client","mobile":{"mode":"blank","color":"#307AE8","pos_flag":"crb","onlineText":"联系客服，在线咨询","offlineText":"客服下班，请留言","pop":{"direction":"top","arrow":{"top":0,"left":"70%"}}},"mode":"inner","color":"#307AE8","pos_flag":"srb","onlineText":"联系客服，在线咨询","offlineText":"客服下班，请留言","pop":{"direction":"top","arrow":{"top":0,"left":"80%"}}})

function kefu_new(){

    var openUrl = "https://18612250386.udesk.cn/im_client/";//弹出窗口的url
    var iWidth = 800; //弹出窗口的宽度;
    var iHeight = 600; //弹出窗口的高度;
    var iTop = (window.screen.availHeight - 30 - iHeight) / 2; //获得窗口的垂直位置;
    var iLeft = (window.screen.availWidth - 10 - iWidth) / 2; //获得窗口的水平位置;

    document.getElementById('kefu_link').onclick = function(){
      window.open(openUrl, "_blank", "height=" + iHeight + ", width=" + iWidth + ", top=" + iTop + ", left=" + iLeft);
    };

}
kefu_new();

