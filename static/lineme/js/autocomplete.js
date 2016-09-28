/**
 * Created by hevlhayt@foxmail.com
 * Date: 2016/6/27
 * Time: 18:39
 */

(function($) {
    $.fn.autocomplete = function(options) {

        var settings = {
            url: '/search/',
            opacity: 0.9,
            color: '#3b5998',
            zIndex: 3000,
            type: 'group',
            groupid: 0,
            onclick: function() {}
        };

        $.extend(settings, options);

        return this.each(function() {
            var $field = $(this);
            init($field);
        });

        function init($field) {

            var $input = $field.find('input'),
                timeout;
            $input.attr('autocomplete', 'off');

            var $ac = $field.siblings(".autocomplete");

            bindEvents();

            function prepareData(kw) {

                var url = (settings.type != 'member'? settings.url+'?kw='+kw : settings.url+'?kw='+kw+'&gid='+settings.groupid);

                $.get(url, function(data){
                    prepareField($.parseJSON(data));
                    showField();
                });
            }

            function prepareField(data) {
                $ac.remove();
                $field.after('<ul class="autocomplete nav nav-pills nav-stacked sidebar-open"></ul>');
                $ac = $field.siblings(".autocomplete");
                $ac.css({
                    margin: '5px 5px',
                    position: 'absolute',
                    border: '#fff 1px solid',
                    borderRadius: '3px',
                    backgroundColor: settings.color,
                    zIndex: settings.zIndex,
                    opacity: settings.opacity,

                });
                $ac.width($field.width() - 2);
                if (data.length == 0) {
                    $ac.append('<li><a>No Results</a></li>');
                    return;
                }
                $.each(data, function(i, d) {
                    if (settings.type == 'group')
                        $ac.append('<li><a href="/group/'+ d.gid+'"><img class="img-circle user-image" src="/media/images/avatars/'+d.cid+'.png" alt="user image"> '+ d.name+'</a></li>');
                    else if (settings.type == 'global')
                        $ac.append('<li><a href="/global/'+ d.gid+'"><img class="img-circle user-image" src="/media/images/avatars/'+d.cid+'.png" alt="user image"> '+ d.name+'</a></li>');
                    else if (settings.type == 'ego')
                        $ac.append('<li><a href="/ego/'+ d.gid+'"><img class="img-circle user-image" src="/media/images/avatars/'+d.cid+'.png" alt="user image"> '+ d.name+'</a></li>');
                    else if (settings.type == 'member') {
                        var uid = d.uid == 0 ? '' : d.uid,
                            pic = d.uid == 0 ? 'default' : d.uid,
                            id = 'srh-' + d.mid + '-' + uid + '-' + d.mname;
                        $ac.append('<li><a id="'+id+'"><img class="img-circle user-image" src="/media/images/avatars/'+pic+'.png" alt="user image"> '+ d.mname+'</a></li>');
                    }
                });

                $ac.find('img').css({
                    width: '30px',
                    marginRight: '15px'
                });

                $ac.find('a').click(function(){
                    settings.onclick(this);
                    $input.val('');
                    hideField();
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

            function showField() {
                if ($ac.is(":hidden"))
                    $ac.fadeIn("slow").show();
            }

            function hideField() {
                $ac.fadeOut().hide();
            }

        }
    };
}(jQuery));
