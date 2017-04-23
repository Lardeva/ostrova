$(document).ready(function() {
    $.fn.loadChildText = function(child) {
        var valuefield = child;
        var ajax_url = valuefield.attr('ajax_url');

        $.get(
            ajax_url,
            {
                field: valuefield.attr('name'),
                parent_field: $(this).attr('name'),
                parent_value: $(this).val()
            },
            function(j) {
                var txt = '';
                for (var i = 0; i < j.length; i++) {
                    txt += j[i][1] + ' ';
                }
                valuefield.val(txt);
                valuefield.trigger('change');
                valuefield.trigger("liszt:updated"); // support for chosen versions < 1.0.0
                valuefield.trigger("chosen:updated"); // support for chosen versions >= 1.0.0
            },
            "json"
        );
    };

    $.fn.loadAllChainedTexts = function() {
        var chained_ids = $(this).attr('chained_ids').split(",");

        for (var i = 0; i < chained_ids.length; i++) {
            var chained_id = chained_ids[i];

            $(this).loadChildText($('#' + chained_id));
        }
    };

    $('.chained-parent-field-txt').change(function() {
        $(this).loadAllChainedTexts();
    });
//    }).change();  // Use change only if really necessary. Be aware of using it in POST requests!
});