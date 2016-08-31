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
                $('.modal-body').find('h4').text('Reset password successfully, please re-login');
                setTimeout('window.location.href = loginUrl', 2000);
            }

            else {
                $('.modal-body').find('h4').text('Reset password failed');
                setTimeout("$('.modal').modal('hide');" +
                    "$('.modal-footer').find('.btn-primary').attr('disabled', false);" +
                    "$('.modal-body').find('h4').text('You are going to reset your password, continue ?');",
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
           if (result == 0) alert('Save Privacy Successfully');
        });
    });

    var width = $('.col-md-7').width();
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
        $(this).html('<i class="fa fa-upload pull-left"></i>Uploading...');
        var imageData = $('#image-cropper').cropit('export');

        $.post(imgHandleUrl, {imgBase64: imageData}, function (result) {
            if (result == '0') {
                alert('Upload Successfully');
                window.location.reload();
            }
            else alert('Upload Failed');

            $(this).attr('disabled', false);
            $(this).html('<i class="fa fa-upload pull-left"></i>Upload');
        });
    });

});
