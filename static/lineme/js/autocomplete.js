/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/6/27
 * Time: 18:39
 */

(function($) {
    $.fn.autocomplete = function(options) {

        var settings = {
            url: '',
            opacity: 0.8,
            color: '#3b5998',
            zIndex: 2000,
        };

        $.extend(settings, options);

        return this.each(function() {

            var $field = $(this);

            init($field);

        });

        function init($field) {

            var $input = $field.find('input');
            $input.attr('autocomplete', 'off');

            var $ac = $field.siblings(".autocomplete");

            bindEvents();

            function prepareData(kw) {
                $.get(settings.url+'?kw='+kw, function(data){
                    prepareField($.parseJSON(data));
                    showField();
                });
            }

            function prepareField(data) {
                $ac.remove();
                $field.after('<ul class="autocomplete nav nav-pills nav-stacked sidebar-open" style="margin: 5px;position: absolute;background-color: #3b5998;z-index: 3000;opacity: 0.9;border: #fff 1px solid;"></ul>');
                $ac = $field.siblings(".autocomplete");
                $ac.width($field.width() - 2);
                $.each(data, function(i, d) {
                    $ac.append('<li><a href="/group/'+ d.id+'"><i class="fa fa-envelope-o"></i> '+ d.name+'</a></li>');
                });
            }

            function bindEvents() {

                $input.bind('input', function () {
                    clearTimeout(timeout);
                    var text = $(this).val();
                    if(text)
                        timeout = setTimeout(function () {
                            prepareData(text);
                        }, 1000);
                    else
                        hideField();
                });

                $(document).on("mouseup", function (e) {
                    var container = $ac;

                    if (!container.is(e.target) && container.has(e.target).length === 0) {

                        // Todo: unbind listener
                        container.hide();
                    }

                });
            }

            function showField() {console.log($ac.is(":hidden"));
                if ($ac.is(":hidden"))
                    $ac.fadeIn().show();
            }

            function hideField() {
                $ac.fadeOut().hidden();
            }

        }
    };
}(jQuery));
