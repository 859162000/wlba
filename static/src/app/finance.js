CanvasRenderingContext2D.prototype.clear = function() {
    this.save();
    this.globalCompositeOperation = 'destination-out';
    this.fillStyle = 'black';
    this.fill();
    this.restore();
};
CanvasRenderingContext2D.prototype.clearArc = function(x, y, radius, startAngle, endAngle, anticlockwise) {
    this.beginPath();
    this.arc(x, y, radius, startAngle, endAngle, anticlockwise);
    this.clear();
};

org.finance = (function (org) {
    var lib = {
        process_num: 0,
        model_canvac_opeartion: true,
        canvas_model4: null,
        init: function () {
            $('.refresh').on('click', function(){
                window.location = window.location.href
            })
            window.onload = function(){
                $('.client-loding-warp').animate({
                    opacity: 0
                },300, function(){
                    $(this).hide()
                })

            }
            var swiper = new Swiper('.swiper-container', {
                paginationClickable: true,
                direction: 'vertical',
                initialSlide: 0,
                onSlideChangeEnd: function(swiper){
                    if(swiper.activeIndex == 2){
                        lib.canvas_model3_doging()
                    }
                    if(swiper.activeIndex == 3){
                        if(!lib.canvas_model4){
                            lib.cavas_model4()
                        }

                    }

                }
            });
        },
        fetch_data: function(){
            org.ajaj({
                url: '/api/account2015/',

            })
        },
        canvas_model3_doging: function () {
            var _self = this,canvas_w = 140,canvas_r = 140,canvas_font = '34px';
            var isAndroid = navigator.userAgent.indexOf('Android') > -1 || navigator.userAgent.indexOf('Adr') > -1; //android终端
            if(isAndroid){
                canvas_w = canvas_w/2
                canvas_r = canvas_r/2
                canvas_font = '17px'
            }
            function infinite(){
                _self.canvas_model3(canvas_w/2, canvas_w/2, canvas_r/2, _self.process_num, canvas_w, canvas_font);
                t = setTimeout(infinite, 30);
                if (_self.process_num >= 60) {
                    clearTimeout(t);
                    _self.process_num = 0;
                    return;
                }
                _self.process_num += 1;
            }
            infinite()
        },
        canvas_model3: function (x, y, radius, process, canvas_w, canvas_font) {
            var _self = this;
            var canvas = document.getElementById('canvas-model3');

            if (canvas.getContext) {
                var cts = canvas.getContext('2d');

                if (_self.model_canvac_opeartion) {
                    canvas.getContext('2d').translate(0.5, 0.5)
                    canvas.width = canvas_w;
                    canvas.height = canvas_w;
                    _self.model_canvac_opeartion = false
                }
            } else {
                return;
            }

            cts.beginPath();
            cts.moveTo(x, y);
            cts.arc(x, y, radius, 0, Math.PI * 2, false);
            cts.closePath();
            cts.fillStyle = '#D8D8D8';
            cts.fill();

            cts.beginPath();
            cts.moveTo(x, y);
            endAgl = Math.PI * 2 * process / 100
            cts.arc(x, y, radius, 0, endAgl, false);
            cts.closePath();
            cts.fillStyle = '#FDF11C';
            cts.fill();
            cts.clearArc(x, y, radius - (radius * 0.26), 0, Math.PI * 2, true);
            //在中间写字
            cts.font = canvas_font + ' Arial'
            cts.fillStyle = '#FDF11C';
            cts.textAlign = 'center';
            cts.textBaseline = 'middle';
            cts.moveTo(x, y);
            cts.fillText(process + "%", x, y);
        },
        cavas_model4: function(){
            var doughnutData = [
				{
					value: 5,
					color:"#4877C8"
				},
				{
					value : 15,
					color : "#FFBA26"
				},
				{
					value : 80,
					color : "#F35B47"
				},

			];
            var canvas_target  = document.getElementById("model4-canvas");
            var _self = this,canvas_w = 300,canvas_h = 300
            var isAndroid = navigator.userAgent.indexOf('Android') > -1 || navigator.userAgent.indexOf('Adr') > -1; //android终端
            if(isAndroid){
                canvas_w = canvas_w/2;
                canvas_h = canvas_h/2;
            }
            canvas_target.width = canvas_w;
            canvas_target.height = canvas_h;
            lib.canvas_model4 = new Chart(canvas_target.getContext("2d")).Doughnut(doughnutData, {segmentShowStroke: false});
        }
    }

    return {
        init: lib.init
    }
})(org);

;
(function (org) {
    $.each($('script'), function () {
        var src = $(this).attr('src');
        if (src) {
            if ($(this).attr('data-init') && org[$(this).attr('data-init')]) {
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);