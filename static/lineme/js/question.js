/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/12/8
 * Time: 14:31
 */

$(function() {

    $('#save').click(function() {

        //$(this).attr('disabled', true);

        var qList = [];
        $.each($('#template').children('.row'), function(i, d) {
            var $d = $(d);
            var title = $d.find('.edit-item').find('input[name="title"]').val(),
                content,
                limit = 0;
            switch ($d.attr('class')) {
                case 'row normal-question':
                    content = $d.find('.edit-item').find('input[name="placeholder"]').val();
                    content = $.trim(content);
                    qList.push({"type":"n", "title":title, "placeholder":content});
                    break;
                case 'row single-question':
                    content = splitSelections($d.find('.edit-item').find('textarea').val());
                    qList.push({"type": "s", "title":title, "choices":content});
                    break;
                case 'row multiple-question':
                    content = splitSelections($d.find('.edit-item').find('textarea').val());
                    limit = $d.find('.edit-item').find('input[name="limit"]').val();
                    qList.push({"type":"m", "title":title, "choices":content, "limit":limit});
                    break;
                case 'row single-member-question':
                    qList.push({"type":"sm", "title":title});
                    break;
                case 'row multiple-member-question':
                    limit = $d.find('.edit-item').find('input[name="limit"]').val();
                    qList.push({"type":"mm", "title":title, "choices":content, "limit":limit});
                    break;
                default:
                    break;

            }
        });

        $.post(qHandleUrl, {questions: JSON.stringify(qList)}, function() {

        });
    });

    $('#type-normal').click(function() {
        $('#template').append(normalTemplate);
        itemCounter(this);
    });

    $('#type-single').click(function() {
        $('#template').append(singleTemplate);
        $('.select2').last().select2({minimumResultsForSearch: Infinity});
        itemCounter(this);
    });

    $('#type-multiple').click(function() {
        $('#template').append(multipleTemplate);
        $('.select2').last().select2({minimumResultsForSearch: Infinity});
        itemCounter(this);
    });

    $('#type-single-member').click(function() {
        $('#template').append(singleMemberTemplate);
        $('.select2').last().select2({minimumResultsForSearch: Infinity});
        itemCounter(this);
    });

    $('#type-multiple-member').click(function() {
        $('#template').append(multipleMemberTemplate);
        $('.select2').last().select2({minimumResultsForSearch: Infinity});
        itemCounter(this);
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
        var selections = splitSelections(text);
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

    // Todo: impl delete
    function itemCounter(d) {
        var $d = $(d).find('span');
        $d.text(parseInt($d.text()) + 1);
    }

    function splitSelections(text) {
        return text.split(/;|\s/).filter(function(t) {
            return t !== '';
        });
    }

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
