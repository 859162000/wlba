// Generated by CoffeeScript 1.8.0
(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'jquery.placeholder': 'lib/jquery.placeholder',
      'jquery.validate': 'lib/jquery.validate.min',
      tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery'],
      'jquery.placeholder': ['jquery'],
      'jquery.validate': ['jquery']
    }
  });

  require(['jquery', 'lib/modal', 'lib/backend', 'jquery.placeholder', 'jquery.validate', 'tools'], function($, modal, backend, placeholder, validate, tool) {
    var card_id, _delCard, _showModal;
    $('input, textarea').placeholder();
    $('#add-card-button').click(function(e) {
      if ($('#id-is-valid').val() === 'False') {
        $('#id-validate').modal();
        return;
      }
      e.preventDefault();
      return $(this).modal();
    });
    _showModal = function() {
      return $('#add-card-button').modal();
    };
    $('#add-card').click(function(e) {
      var bank_id, card_no, is_default;
      e.preventDefault();
      card_no = $('#card-no').val();
      if (!backend.checkCardNo(card_no)) {
        tool.modalAlert({
          title: '温馨提示',
          msg: '请输入有效的银行卡号',
          callback_ok: _showModal
        });
        return;
      }
      bank_id = $('#bank-select').val();
      if (!bank_id) {
        tool.modalAlert({
          title: '温馨提示',
          msg: '请选择银行',
          callback_ok: _showModal
        });
        return;
      }
      is_default = $('#default-checkbox').prop('checked');
      return $.ajax({
        url: '/api/card/',
        data: {
          no: card_no,
          bank: bank_id,
          is_default: is_default
        },
        type: 'post'
      }).done(function() {
        return location.reload();
      }).fail(function(xhr) {
        var result;
        $.modal.close();
        result = JSON.parse(xhr.responseText);
        if (result.error_number === 5) {
          tool.modalAlert({
            title: '温馨提示',
            msg: result.message
          });
          return;
        }
        return tool.modalAlert({
          title: '温馨提示',
          msg: '添加银行卡失败'
        });
      });
    });
    card_id = "";
    $('a#del-card').click(function(e) {
      card_id = $(this).attr("card_id");
      return tool.modalConfirm({
        title: '温馨提示',
        msg: '确定删除？',
        callback_ok: _delCard
      });
    });
    return _delCard = function() {
      return $.ajax({
        url: '/api/card/' + card_id + '/',
        data: {
          card_id: card_id
        },
        type: 'delete'
      }).done(function() {
        return location.reload();
      }).fail(function(xhr) {
        var result;
        $.modal.close();
        result = JSON.parse(xhr.responseText);
        if (result.error_number === 5) {
          tool.modalAlert({
            title: '温馨提示',
            msg: result.message
          });
          return;
        }
        return tool.modalAlert({
          title: '温馨提示',
          msg: '删除失败'
        });
      });
    };
  });

}).call(this);

//# sourceMappingURL=add_card.js.map
