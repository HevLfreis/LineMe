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
        $('#box-group').attr('class', 'box box-info').find('h3').text('Manage Groups --- My Created Groups');
        keepHeight()
    });
    $('#btn-in-group').click(function() {
        $('#table-in-group').show();
        $('#table-my-group').hide();
        $('#table-rd-group').hide();
        $('#box-group').attr('class', 'box box-success').find('h3').text('Manage Groups --- My Joined Groups');
        keepHeight()
    });
    $('#btn-rd-group').click(function() {
        $('#table-rd-group').show();
        $('#table-my-group').hide();
        $('#table-in-group').hide();
        $('#box-group').attr('class', 'box box-warning').find('h3').text('Manage Groups --- Group Recommendations');
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


    window.msgConfirmed = function(url, type, linkid) {
        $.get(url, function(data){
            if (data == -1) {
                alert("Server Internal Error");
            }
            else {
                if (type == 1)
                    $('#msg-'+linkid+' > small').attr('class', 'label label-success').text('Confirmed');
                else if (type == 0)
                    $('#msg-'+linkid+' > small').attr('class', 'label label-danger').text('Rejected');
            }
        });
    };

    window.updateMsgPanel = function(page) {
        $.get(msgPanelUrl+'?page='+page, function(data){
            var msg = $('#box-msg');
            msg.find('.box-body').remove();
            msg.find('.box-footer').remove();
            msg.append(data);
            //msg.height(msg.height());
            $('input[type="checkbox"]').iCheck({
                checkboxClass: 'icheckbox_square-blue',
            });

            $('#confirm').click(confirmChoosed);
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
        $('input[type="checkbox"]').each(function() {
            if($(this).parent('[class*="icheckbox"]').hasClass("checked")) {
                selected.push($(this).val());
            }
        });

        if (selected.length == 0) return;

        $.post(msgPostUrl, {linkids: JSON.stringify(selected)}, function(result) {
            if(selected.length != parseInt(result)) {
                alert(selected.length - parseInt(result)+' Messages Confirm Failed');
            }
            else {
                alert(result+' Messages Confirm Successfully')
            }

            updateMsgPanel(1);
            keepHeight();
        });
    }

    $('.select2[name="identifier"]').select2({
        minimumResultsForSearch: 4
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

    updateMsgPanel(1);
    updateInvPanel(1, null);

});



