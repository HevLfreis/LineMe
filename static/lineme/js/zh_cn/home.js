/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/6/5
 * Time: 19:12
 */

$(function() {

    //var max_h = Math.max($('#table-my-group').height(),
    //    $('#table-in-group').height(),
    //    $('#table-rd-group').height());
    //
    //$('.content-wrapper').height($('.content-wrapper').height()+max_h+30);

    var $content = $('.content-wrapper');

    $('#btn-my-group').click(function() {
        $('#table-my-group').show();
        $('#table-in-group').hide();
        $('#table-rd-group').hide();
        $('#box-group').attr('class', 'box box-info').find('h3').text('我创建的群');
        keepHeight()
    });
    $('#btn-in-group').click(function() {
        $('#table-in-group').show();
        $('#table-my-group').hide();
        $('#table-rd-group').hide();
        $('#box-group').attr('class', 'box box-success').find('h3').text('我加入的群');
        keepHeight()
    });
    $('#btn-rd-group').click(function() {
        $('#table-rd-group').show();
        $('#table-my-group').hide();
        $('#table-in-group').hide();
        $('#box-group').attr('class', 'box box-warning').find('h3').text('我的群推荐');
        keepHeight()
    });

    $('.modal').on('show.bs.modal', function(e) {
        var $dialog = $(this).find('.modal-dialog');
        $dialog.css({
            'margin-top': function() {
                var modalHeight = $dialog.height();
                return ($(window).height() / 6 - (modalHeight / 2));
            }
        });
    });

    $('input[type="radio"].minimal').iCheck({
        radioClass: 'iradio_flat-green',
    });


    window.msgConfirmed = function(url, type, handleid, refresh) {
        $.get(url, function(data){
            if (data == -1) {
                alert("Server Internal Error");
            }

           // smu friend limit
            else if (data == -2) {
                alert("对方好友数达上限");
            }
            else {
                if (refresh)
                    updateMsgPanel(1);
                else if (type == 1)
                    $('#msg-'+handleid+' > small').attr('class', 'label label-success').text('已确认');
                else if (type == 0)
                    $('#msg-'+handleid+' > small').attr('class', 'label label-danger').text('已拒绝');
            }
        });
    };


    // Todo: impl dont show
    window.msgAggregateConfirmed = function(url, type, memberName, count) {

        count --;

        var $modal = $('#modal-msg');
        $modal.modal('show');
        if (type == 3) {
            $modal.find('.modal-body h4').html('另外 '+count+' 个人也邀请你连接 '+memberName+' , <span class="text-bold text-red">全部确认 ?</span>');
        }
        else {
            $modal.find('.modal-body h4').html('另外 '+count+' 个人也邀请你连接 '+memberName+' , <span class="text-bold text-red">全部拒绝 ?</span>');
        }

        $modal.find('.btn-primary').attr('onclick', "msgConfirmed('"+url+"', 0, 0, true)");
        var url_list = url.split("/");
        url_list[2] -= 2;
        url = url_list.join('/');
        $modal.find('.btn-warning').attr('onclick', "msgConfirmed('"+url+"', 0, 0, true)");

    };

    window.updateMsgPanel = function(page) {
        $.get(msgPanelUrl+'?page='+page, function(data){
            var msg = $('#box-msg');
            msg.find('.box-body').remove();
            msg.find('.box-footer').remove();
            msg.append(data);
            //msg.find('.box-body').hide().fadeIn();
            initCheckbox();

            $('#confirm').click(confirmChoosed);
            keepHeight();
        });
    };

    var timeout;
    window.updateInvPanel = function(page, groupname) {
        if (groupname)
            $.get(invPanelUrl+'?page='+page+'&groupname='+groupname, function(data) {
                onUpdateInvSucceess(data);
            });
        else
            $.get(invPanelUrl+'?page='+page, function(data){
                onUpdateInvSucceess(data);
            });
        keepHeight();
    };

    function onUpdateInvSucceess(data) {
        var inv = $('#box-inv');
        inv.find('.box-body').remove();
        inv.find('.box-footer').remove();
        inv.append(data);

        $('#search-group').bind('input', function() {

            clearTimeout(timeout);
            var text = $(this).val();
            if (text)
                timeout = setTimeout(function() {
                    updateInvPanel(1, text);
                }, 1000);
            else
                timeout = setTimeout(function() {
                    updateInvPanel(1, null);
                }, 1500);
        });
    }


    function confirmChoosed() {
        var selected = [];
        $('input[type="checkbox"][name="msg"]').each(function() {
            if($(this).parent('[class*="icheckbox"]').hasClass("checked")) {
                selected.push($(this).val());
            }
        });

        if (selected.length == 0) return;

        $.post(msgPostUrl, {linkids: JSON.stringify(selected)}, function(result) {
            if(selected.length != parseInt(result)) {
                alert(selected.length - parseInt(result)+' 条请求确认失败');
            }
            else {
                alert(result+' 条请求确认成功')
            }

            updateMsgPanel(1);
            keepHeight();
        });
    }

    $('.select2[name="identifier"]').select2({
        minimumResultsForSearch: Infinity
    }).on("change", function(e) {
        if (this.value == 2) {
            $('input[type="radio"][value="1"].minimal').iCheck('disable').iCheck('uncheck');
            $('input[type="radio"][value="0"].minimal').iCheck('check');
        }
        else
            $('input[type="radio"][value="1"].minimal').iCheck('enable');
    });

    var height = 0;
    function keepHeight() {
        var new_height = $content.height();

        if (new_height < height)
            $content.height(height);
        else
            height = new_height;
    }

    function initCheckbox() {
        $('input[type="checkbox"]').iCheck({
            checkboxClass: 'icheckbox_square-blue',
        });
    }

    updateMsgPanel(1);
    updateInvPanel(1, null);
    initCheckbox()

});



