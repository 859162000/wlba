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
        init: function () {

            var swiper = new Swiper('.swiper-container', {
                paginationClickable: true,
                direction: 'vertical',
                initialSlide: 0,
                onSlideChangeEnd: function(swiper){
                    if(swiper.activeIndex == 2){
                        lib.canvas_model3_doging()
                    }
                    if(swiper.activeIndex == 3){
                        lib.cavas_model4()
                    }

                }
            });


        },
        canvas_model3_doging: function () {
            var _self = this;

            function Start() {
                _self.canvas_model3(90, 90, 70, _self.process_num);
                t = setTimeout(Start, 30);
                if (_self.process_num >= 60) {
                    clearTimeout(t);
                    _self.process_num = 0;
                    return;
                }
                _self.process_num += 1;
            }

            Start()
        },
        canvas_model3: function (x, y, radius, process) {
            var _self = this;
            var canvas = document.getElementById('canvas-model3');

            if (canvas.getContext) {
                var cts = canvas.getContext('2d');

                if (_self.model_canvac_opeartion) {
                    canvas.getContext('2d').translate(0.5, 0.5)
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
            cts.font = '34px Arial'
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

            var myDoughnut = new Chart(document.getElementById("model4-canvas").getContext("2d"))
                .Doughnut(doughnutData, {segmentShowStroke: false, onAnimationComplete: function(e){
                }});
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