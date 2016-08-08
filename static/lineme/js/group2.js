/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/7/15
 * Time: 17:40
 */

$(function() {

    $('.modal').on('show.bs.modal', function (e) {
        var $dialog = $(this).find('.modal-dialog');
        $dialog.css({
            'margin-top': function () {
                var modalHeight = $dialog.height();
                return ($(window).height() / 6 - (modalHeight / 2));
            }
        });
    });

    $('input[type="radio"].minimal').iCheck({
        radioClass: 'iradio_flat-green'
    });

    function joinGroup() {

        $.get(joinUrl, function(result) {

            switch (result) {
                case '0':
                    window.location.replace(egoUrl);
                    break;
                case '-1':
                    if (identifier == 0) {
                        var $modal = $('#modal-join');
                        $modal.find('.modal-title').text('Identifier');
                        $modal.find('.modal-footer button').val('Follow');
                        $modal.find('input').attr('placeholder', '');
                        $modal.modal('show');
                    }
                    else {
                        $('#modal-join').modal('show');
                    }
                    break;
                case '-2':
                    $('#modal-notin').modal('show');
                    break;
                case '-4':
                    alert('Server Internal Error');
                    break;
                default :
                    break;
            }
        });
    }

    $('#follow').click(function() {
        joinGroup();
    });

});


