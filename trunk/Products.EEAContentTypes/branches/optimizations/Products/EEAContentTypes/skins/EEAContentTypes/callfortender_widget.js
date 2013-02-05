jQuery(function($){
    // #10204 disable award notice none entry when object is in portal_factory
    var disableAward = function() {
        var $award = $("#archetypes-fieldname-awardNotice"),
            $input = $award.find('input'),
            $label = $input.next();
        $input.attr('disabled', 'disabled');
        $label.css('opacity', 0.5);
    };

    if ( window.location.href.indexOf('portal_factory') !== -1 ) {
        disableAward();
    }
});
