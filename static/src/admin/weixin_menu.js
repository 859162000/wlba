/**
 * Created by jeff on 15/5/16.
 */
var app = angular.module('app', []);

app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('<{');
    $interpolateProvider.endSymbol('}>');
}]);

app.controller('MenuCtl', function($scope, $http) {
    $scope.data = {};
    $scope.data.menu_api = '';
    $scope.data.menu_classify_all = [
        {'value': 'sub_button', 'text': '子菜单'},
        {'value': 'click', 'text': '点击推事件'},
        {'value': 'view', 'text': '跳转URL'},
        {'value': 'scancode_push', 'text': '扫码推事件'},
        {'value': 'scancode_waitmsg', 'text': '扫码推事件且弹出“消息接收中”提示框'},
        {'value': 'pic_sysphoto', 'text': '弹出系统拍照发图'},
        {'value': 'pic_photo_or_album', 'text': '弹出拍照或者相册发图'},
        {'value': 'pic_weixin', 'text': '弹出微信相册发图器'},
        {'value': 'location_select', 'text': '弹出地理位置选择器'}
    ];
    $scope.data.menu = {'button': []};
    $scope.data.menu_classify = null;
    $scope.data.current_menu_level = null;
    $scope.data.current_menu_index = null;
    $scope.data.current_menu_parent_index = null;
    $scope.data.new_menu = null;
    $scope.data.new_menu_action = null;

    $scope.$watch('data.menu_api', function(url) {
        $http.get(url).success(function(res) {
            $scope.data.menu = res;
        });
    });

    $scope.$watch('data.current_menu_level', function(level) {
        if (level == 1) {
            $scope.data.move_menu_left_btn = '左移';
            $scope.data.move_menu_right_btn = '右移';
        }
        else if (level == 2) {
            $scope.data.move_menu_left_btn = '上移';
            $scope.data.move_menu_right_btn = '下移';
        }
    });

    function set_name_max_length(level) {
        if (level == 1) {
            $scope.data.name_max_length = 4;
        }
        else if (level == 2) {
            $scope.data.name_max_length = 7;
        }
    }

    function init_current_menu(level, index, parent_index) {
        $scope.data.current_menu_level = level;
        $scope.data.current_menu_index = index;
        $scope.data.current_menu_parent_index = parent_index;
        set_name_max_length(level);
    }

    function reset_current_menu() {
        $scope.data.current_menu_level = null;
        $scope.data.current_menu_index = null;
        $scope.data.current_menu_parent_index = null;
    }

    $scope.add_menu = function(level, index) {
        $scope.data.new_menu_action = 'create';
        $scope.data.new_menu = {
            'type': 'click',
            'name': '',
            'key': ''
        };

        $scope.data.menu_classify = angular.copy($scope.data.menu_classify_all);
        if (level == 2) {
            $scope.data.menu_classify.shift();
        }
        $scope.data.new_menu_parent = index;
        reset_current_menu();
        set_name_max_length(level);
    };

    $scope.remove_menu = function() {
        var confirm = window.confirm('确定删除吗');
        if (! confirm) {
            return false;
        }

        if ($scope.data.current_menu_level == 1) {
            $scope.data.menu.button.splice($scope.data.current_menu_index, 1);
        }
        else if ($scope.data.current_menu_level == 2) {
            $scope.data.menu.button[$scope.data.current_menu_parent_index].sub_button.splice($scope.data.current_menu_index, 1);
        }

        reset_current_menu();
        $scope.data.new_menu = null;
    };

    $scope.add_menu_confirm = function() {
        var new_menu_data = angular.copy($scope.data.new_menu);
        var menu_data;

        if (new_menu_data.type == 'sub_button') {
            menu_data = {
                'name': new_menu_data.name,
                'sub_button': new_menu_data.sub_button || []
            }
        }
        else if (new_menu_data.type == 'view') {
            menu_data = {
                'type': new_menu_data.type,
                'name': new_menu_data.name,
                'url': new_menu_data.url
            }
        }
        else {
            menu_data = {
                'type': new_menu_data.type,
                'name': new_menu_data.name,
                'key': new_menu_data.key
            }
        }
        $scope.data.new_menu = null;
        if ($scope.data.new_menu_action == 'create') {
            if (typeof($scope.data.new_menu_parent) != 'undefined') {
                $scope.data.menu.button[$scope.data.new_menu_parent].sub_button.push(menu_data);
            }
            else {
                $scope.data.menu.button.push(menu_data);
            }
        }
        else if ($scope.data.new_menu_action == 'edit') {
            if ($scope.data.current_menu_level == 1) {
                $scope.data.menu.button.splice($scope.data.current_menu_index, 1, menu_data);
            }
            else if ($scope.data.current_menu_level == 2) {
                $scope.data.menu.button[$scope.data.current_menu_parent_index].sub_button.splice($scope.data.current_menu_index, 1, menu_data);
            }
        }
        reset_current_menu();
        return false;
    };

    $scope.choice_menu = function(level, index, parent_index) {
        var current_list;
        init_current_menu(level, index, parent_index);
        $scope.data.new_menu_action = 'edit';
        $scope.data.menu_classify = angular.copy($scope.data.menu_classify_all);

        if (level == 1) {
            current_list = $scope.data.menu.button;
            $scope.data.new_menu = angular.copy(current_list[index]);
            $scope.data.new_menu.type = $scope.data.new_menu.type || 'sub_button';
        }
        else if (level == 2) {
            current_list = $scope.data.menu.button[parent_index].sub_button;
            $scope.data.new_menu = angular.copy(current_list[index]);
            $scope.data.menu_classify.shift();
        }

        $scope.data.current_list_length = current_list.length;
    };

    $scope.move_menu = function(direction) {
        var menu, parent;

        if ($scope.data.current_menu_index <= 0 && direction == 'left') {
            return false;
        }

        if ($scope.data.current_menu_level == 1) {
            parent = $scope.data.menu.button;
        }
        else if ($scope.data.current_menu_level == 2) {
            parent = $scope.data.menu.button[$scope.data.current_menu_parent_index].sub_button;
        }

        if ($scope.data.current_menu_index >= parent.length - 1 && direction == 'right') {
            return false;
        }

        menu = angular.copy(parent[$scope.data.current_menu_index]);
        parent.splice($scope.data.current_menu_index, 1);

        if (direction == 'left') {
            $scope.data.current_menu_index -= 1;
        }
        else if (direction == 'right') {
            $scope.data.current_menu_index += 1;
        }

        parent.splice($scope.data.current_menu_index, 0, menu);
    };

    $scope.is_move_menu_left_hidden = function() {
        return $scope.data.current_menu_index <= 0;
    };

    $scope.is_move_menu_right_hidden = function() {
        return $scope.data.current_menu_index >= $scope.data.current_list_length -1;
    };

    $scope.create_menu = function() {
        $http.post($scope.data.menu_api, $scope.data.menu).success(function() {
            alert('生成成功');
        }).error(function(res) {
            weixin.error_messages.echo(res['errcode']);
        });
    };

    $scope.delete_menu = function() {
        $http.delete($scope.data.menu_api).success(function() {
            alert('删除成功');
        }).error(function(res) {
            weixin.error_messages.echo(res['errcode']);
        });
    };

});