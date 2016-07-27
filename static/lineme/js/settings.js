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
        $('.modal-footer').find('.btn-primary').addClass('disabled');
        $.post(pwResetUrl, $('#form-passwd').serialize(), function (result) {

            if (result == 0) {
                $('.modal-body').find('h4').text('Reset password successfully, please re-login');
                setTimeout('window.location.href = loginUrl', 2000);
            }

            else {
                $('.modal-body').find('h4').text('Reset password failed');
                setTimeout("$('.modal').modal('hide');" +
                    "$('.modal-footer').find('.btn-primary').removeClass('disabled');",
                    1500);
            }
        });

    });

    $('#save-pri').click(function () {
        var priDict = {};
        $('.js-switch').each(function (){
            priDict[$(this).attr('name')] = this.checked;
        });

        //priDict['pri-9'] = false;
        $.post(priSaveUrl, {privacies: JSON.stringify(priDict)}, function (result) {
           if (result == 0) alert('Save Privacy Successfully');
        });
    });


    $('.cropit-preview').height($('.col-md-7').width());
    $('.cropit-preview').width($('.col-md-7').width());
    $('#image-cropper').cropit({
        imageState: {
            src: '/static/images/user_avatars/'+userid+'.png'
        },
        smallImage: 'stretch',
        onFileChange: function () {
            $('#upload').removeClass('disabled').removeAttr('disabled');
        }

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
        var imageData = $('#image-cropper').cropit('export');

        $.post(imgHandleUrl, {imgBase64: imageData}, function (result) {
            if (result == '0') {
                alert('Upload Successfully');
                window.location.reload();
            }
            else alert('Upload Failed');
        });
    });

});
