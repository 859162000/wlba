$(function(){

    var mp3 = document.getElementById("music");
    mp3.play();
	var mp3_open = true;
	$('#play').click(function(){
		if(mp3_open){
			mp3.pause();
			mp3_open = false;
			$('#play').addClass('close_music').removeClass('play_music');
		}else{
			mp3.play();
			mp3_open = true;
			$('#play').addClass('play_music').removeClass('close_music');
		}
	});

    $('.section3 .line').load(function(){
        var s3line_height = $('.section3 .line').height();
        $('.section3 .line_img').css('height',s3line_height);
    });
    $('.section4 .line').load(function(){
        var s4line_height = $('.section4 .line').height();
        $('.section4 .line_img').css('height',s4line_height);
    });
    $('.section5 .line').load(function(){
        var s5line_height = $('.section5 .line').height();
        $('.section5 .line_img').css('height',s5line_height);
    });

    var say;
    var say_num
    $('.button').click(function(){
        say = $('input').val();
        $('#name').text(say);
        $('body').unbind('touchmove');
        say_num = parseInt(18*Math.random());
        switch(say_num){
            case 1:
                $('#say').text('去旅游');
                break;
            case 2:
                $('#say').text('去邂逅');
                break;
            case 3:
                $('#say').text('少睡觉');
                break;
            case 4:
                $('#say').text('多看书');
                break;
            case 5:
                $('#say').text('少玩游戏');
                break;
            case 6:
                $('#say').text('多赚钱');
                break;
            case 7:
                $('#say').text('养只宠物');
                break;
            case 8:
                $('#say').text('解解闷');
                break;
            case 9:
                $('#say').text('多锻炼');
                break;
            case 10:
                $('#say').text('保持好身材');
                break;
            case 11:
                $('#say').text('一切都会过去');
                break;
            case 12:
                $('#say').text('好好爱自己');
                break;
            case 13:
                $('#say').text('别做梦');
                break;
            case 14:
                $('#say').text('学一项技能');
                break;
            case 15:
                $('#say').text('好好听课');
                break;
            case 16:
                $('#say').text('不要留遗憾');
                break;
            case 17:
                $('#say').text('对自己好一点');
                break;
            case 18:
                $('#say').text('买买买');
                break;
        }
    });

    $('#wrap').fullpage({
        anchors: ['page1','page2','page3','page4','page5','page6','page7','page8'],
        afterLoad: function(anchorLink, index) {
            if(index == 1){
                $('.section1 .theme,.section1 .text1,.section1 .text2').css('opacity','1').addClass('animate');
                $('.section2 .young,.section2 .text').css('opacity','0');
            }
            if(index == 2){
                $('.theme,.section1 .text1,.section1 .text2,.section3 .boy_before,.section3 .line_img,.section3 .talk').css('opacity','0');
                $('.section2 .young,.section2 .text,.section2 .old').css('opacity','1').addClass('animate');
            }
            if(index == 3){
                $('.section2 .young,.section2 .text,.section4 .line_img,.section4 .talk,.section4 .man1_before,.math').css('opacity','0');
                $('.section3 .boy_before,.section3 .line_img,.section3 .talk').css('opacity','1').addClass('animate');
            }
            if(index == 4){
                $('.section3 .boy_before,.section3 .line_img,.section3 .talk,.section5 .line_img,.section5 .talk,.woman1_before,.bamboo').css('opacity','0');
                $('.section4 .line_img,.section4 .talk,.section4 .man1_before,.math').css('opacity','1').addClass('animate');
            }
            if(index == 5){
                $('.section4 .line_img,.section4 .talk,.section4 .man1_before,.math').css('opacity','0');
                $('.section5 .line_img,.section5 .talk,.woman1_before,.bamboo').css('opacity','1').addClass('animate');
            }
            if(index == 6){
                $('.section5 .line_img,.section5 .talk,.woman1_before,.bamboo').css('opacity','0')
                $('.section6 .fly').addClass('animate');
                say = $('input').val();
                if(say==''||say==undefined){
                    $('body').bind("touchmove", function(e) {e.preventDefault();}, false);
                }else{
                    $('body').unbind('touchmove');
                }
            }
            if(index == 7){
                $('.section7 .fly').addClass('animate');
            }
            if(index == 8){
                $('.section8 .fly').addClass('animate');
            }
        },
        onLeave: function(index, direction) {
            if(index == 1){
                $('.section1 .theme,.section1 .text1,.section1 .text2').removeClass('animate');

            }
            if(index == 2){
                $('.section2 .young,.section2 .text,.section2 .old').removeClass('animate');
            }
            if(index == 3){
                $('.section3 .boy_before,.section3 .line_img,.section3 .talk').removeClass('animate');
            }
            if(index == 4){
                $('.section4 .line_img,.section4 .talk,.section4 .man1_before,.math').removeClass('animate');
            }
            if(index == 5){
                $('.section5 .line_img,.section5 .talk,.woman1_before,.bamboo').removeClass('animate');
            }
            if(index == 6){
                $('.section6 .fly').removeClass('animate');
            }
            if(index == 7){
                $('.section7 .fly').removeClass('animate');
            }
            if(index == 8){
                $('.section8 .fly').removeClass('animate');
            }
        }
    })
});
