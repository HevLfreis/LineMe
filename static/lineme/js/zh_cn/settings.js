/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/7/20
 * Time: 22:42
 */

$(function() {

    $('.js-switch').each(function () {
        var init = new Switchery(this);
    });


    $('.modal').on('show.bs.modal', function (e) {
        var $dialog = $(this).find('.modal-dialog');
        $dialog.css({
            'margin-top': function () {
                var modalHeight = $dialog.height();
                return ($(window).height() / 4 - (modalHeight / 2));
            }
        });
    });


    $('#reset-passwd').click(function () {
        $('.modal-footer').find('.btn-primary').attr('disabled', true);
        $.post(pwResetUrl, $('#form-passwd').serialize(), function (result) {

            if (result == 0) {
                $('.modal-body').find('h4').text('重置密码成功，请重新登录');
                setTimeout('window.location.href = loginUrl', 2000);
            }

            else {
                $('.modal-body').find('h4').text('重置密码失败');
                setTimeout("$('.modal').modal('hide');" +
                    "$('.modal-footer').find('.btn-primary').attr('disabled', false);" +
                    "$('.modal-body').find('h4').text('你将重置密码，继续 ?');",
                    1500);
            }
        });

    });

    $('#save-pri').click(function () {
        var priDict = {};
        $('.js-switch').each(function (){
            priDict[$(this).attr('name')] = this.checked;
        });

        $.post(priSaveUrl, {privacies: JSON.stringify(priDict)}, function (result) {
           if (result == 0) alert('隐私设置保存成功');
        });
    });

    var width = $('.col-md-7').width() - 8;
    $('.cropit-preview').height(width);
    $('.cropit-preview').width(width);
    $('#image-cropper').cropit({
        imageState: {
            src: '/media/images/avatars/hdpi/'+userid+'.png'
        },
        smallImage: 'stretch',
        onFileChange: function () {
            $('#upload').attr('disabled', false);
        },
        exportZoom: 400.0 / width
    });

    $('#select').click(function () {
        $('.cropit-image-input').click();
    });

    // Handle rotation
    $('.rotate-cw').click(function () {
        $('#image-cropper').cropit('rotateCW');
    });
    $('.rotate-ccw').click(function () {
        $('#image-cropper').cropit('rotateCCW');
    });

    $('#upload').click(function () {

        $(this).attr('disabled', true);
        $(this).html('<i class="fa fa-upload pull-left"></i>上传中...');
        var imageData = $('#image-cropper').cropit('export');

        $.post(imgHandleUrl, {imgBase64: imageData}, function (result) {
            if (result == '0') {
                alert('上传成功');
                window.location.reload();
            }
            else alert('上传失败');

            $(this).attr('disabled', false);
            $(this).html('<i class="fa fa-upload pull-left"></i>上传');
        });
    });

});
