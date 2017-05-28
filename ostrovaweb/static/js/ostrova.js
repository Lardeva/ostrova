
$.fn.article_on_change_raw_id_helper = function() {
  field_obj = $(this)
   $.get(
       '/article_name_lookup',
       {
           field: $(this).attr('name'),
           value: $(this).val(),
       },
       function(txt) {
           if ( field_obj.next().next().is("strong")) {
                   field_obj.next().next().replaceWith( "<strong>"+txt+"</strong>" );
           } else {
                   $ ("<strong>"+txt+"</strong>").insertAfter( field_obj.next() );
           }
      },
       "text"
   );

};

$(document).ready(function() {
        $('.vForeignKeyRawIdAdminField').change(function() {
              $(this).article_on_change_raw_id_helper();
        });

        Suit.after_inline.register('row-id-lookup-dynamic', function(inline_prefix, row){
                $('.vForeignKeyRawIdAdminField').change(function() {
                      $(this).article_on_change_raw_id_helper();
                });
        });
});


/*
 * Trigger change events when Django admin's popup window is dismissed
 */
(function($) {
    $(document).ready(function() {

        // HACK to override `dismissRelatedLookupPopup()` and
        // `dismissAddAnotherPopup()` in Django's RelatedObjectLookups.js to
        // trigger change event when an ID is selected or added via popup.
        function triggerChangeOnField(win_name, chosenId) {
            var name = windowname_to_id(win_name);
            var elem = document.getElementById(name);
            $(elem).change();
        }

        window.ORIGINAL_dismissRelatedLookupPopup = window.dismissRelatedLookupPopup
        window.dismissRelatedLookupPopup = function(win, chosenId) {
            win_name = win.name;
            ORIGINAL_dismissRelatedLookupPopup(win, chosenId);
            triggerChangeOnField(win_name, chosenId);
        }

        window.ORIGINAL_dismissAddRelatedObjectPopup = window.dismissAddRelatedObjectPopup
        window.dismissAddRelatedObjectPopup = function(win, newId, newRepr) {
            win_name = win.name;
            ORIGINAL_dismissAddRelatedObjectPopup(win, newId, newRepr);
            triggerChangeOnField(win_name, newId);
        }

    });
})(jQuery);