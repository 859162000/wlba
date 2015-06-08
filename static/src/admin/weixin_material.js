/**
 * Created by jeff on 15/6/1.
 */
var app = angular.module('app', ['wu.masonry']);

//app.config(['$interpolateProvider', function ($interpolateProvider) {
//    $interpolateProvider.startSymbol('<{');
//    $interpolateProvider.endSymbol('}>');
//}]);
//
//
//app.directive('newsItemRepeat', function () {
//    return {
//        restrict: 'A',
//        template:
//        '<div style="display: table-cell; width: 50px;">' +
//        '<img class="ui image" src="/weixin/manage/images/thumb/<{ item.thumb_media_id }>" style="width: 40px;">' +
//        '</div>' +
//        '<div class="content " style="display: table-cell; vertical-align: middle;">' +
//        '<span ng-bind="item.title"></span>' +
//        '</div>',
//        scope: {item: '='}
//    };
//});


app.controller('MaterialCtl', function($scope, $http) {
    $scope.data = {};
    $scope.data.materials_data = {};
    $scope.data.materials_data.count = null;

    $scope.data.news = [
        {id: 'p1', 'title': 'A nice day!', src: "http://lorempixel.com/300/400/"},
        {id: 'p2', 'title': 'Puh!', src: "http://lorempixel.com/300/400/sports"},
        {id: 'p3', 'title': 'What a club!', src: "http://lorempixel.com/300/400/nightlife"}
    ];

    function genBrick() {
        var height = ~~(Math.random() * 500) + 100;
        var id = ~~(Math.random() * 10000);
        return {
            src: 'http://lorempixel.com/g/280/' + height + '/?' + id
        };
    }

    $scope.bricks = [
        genBrick(),
        genBrick(),
        genBrick(),
        genBrick(),
        genBrick()
    ];


    //$http.get('/weixin/manage/api/materials/count/').success(function(res) {
    //    $scope.data.materials_data.count = res;
    //}).error(function(res) {
    //    weixin.error_messages.echo(res['errcode']);
    //});

    //$http.get('/weixin/manage/api/materials/?media_type=news').success(function(res) {
    //    $scope.data.news = res['item'];
    //});

});


$(function() {
    $('.menu .item').tab();
});
