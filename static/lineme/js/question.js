/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/12/8
 * Time: 14:31
 */

$(function() {
    $('#type-normal').click(function() {
        $('#template').append(normalTemplate);
    });

    $('#type-single').click(function() {
        $('#template').append(singleTemplate);
        $('.select2').last().select2({minimumResultsForSearch: Infinity});
    });

    $('#type-multiple').click(function() {
        $('#template').append(multipleTemplate);
        $('.select2').last().select2({minimumResultsForSearch: Infinity});
    });

    $('#type-single-member').click(function() {
        $('#template').append(singleMemberTemplate);
        $('.select2').last().select2({minimumResultsForSearch: Infinity});
    });

    $('#type-multiple-member').click(function() {
        $('#template').append(multipleMemberTemplate);
        $('.select2').last().select2({minimumResultsForSearch: Infinity});
    });

    window.titleInputListener = function(d) {
        var text = $(d).val();
        if (text.length > 20) return;
        $(d).parents(".row").first().find('label').first().text(text===''?'标题':text);
    };

    window.hintInputListener = function(d) {
        var text = $(d).val();
        if (text.length > 30) return;
        $(d).parents(".row").first().find('input').first().attr('placeholder', text);
    };

    window.selectionInputListener = function(d) {
        var text = $(d).val();
        var selections = text.split(/;|\s/);
        if (selections.length > 20) return;
        var $select = $(d).parents(".row").first().find('select');
        $select.children().remove();
        $.each(selections, function (i, item) {
            $select.append($('<option>', {
                //value: item.value,
                text : item
            }));
        });
    };

    window.removeItemClickListener = function(d) {
        $(d).parents(".row").first().remove();
        keepHeight();
    };

    var height = 0;
    var $content = $('.content-wrapper');
    function keepHeight() {
        var new_height = $content.height();

        if (new_height < height)
            $content.height(height);
        else
            height = new_height;
    }

    keepHeight();

    var normalTemplate = $('#normal-template').html();
    var singleTemplate = $('#single-template').html();
    var multipleTemplate = $('#multiple-template').html();
    var singleMemberTemplate = $('#single-member-template').html();
    var multipleMemberTemplate = $('#multiple-member-template').html();
});
