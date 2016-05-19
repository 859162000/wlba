
require(['jquery'], function ($) {
    $.ajax({
         url: "/api/php/unread_messages/",
         type: "GET"
     }).done(function (data) {
         var date = JSON.parse(data);
         var num = date.unread_num;
         if (num == 0){
             $('.letter').hide();
         }else{
             $('.letter').show().text(num);
         }
 
     });
});
