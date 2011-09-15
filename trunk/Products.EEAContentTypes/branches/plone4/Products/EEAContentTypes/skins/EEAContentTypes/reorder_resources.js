jQuery(document).ready(function($){
    var form = $("#reorder_form").get(0);
    $(form).prepend($("<ul class='reorder'>"));
    var textarea = $("textarea", form).get(0);

    var resources = $(textarea).val().split('\n');
    for (var i=0; i<resources.length; i++){
        var val = resources[i];
        var el = $("<li class='list-item'>").html(
            '<span title="Drag & drop to set order" ' +
            'class="handler ui-icon ui-icon-arrowthick-2-n-s"></span>' +
            val
            );
        $(".reorder", form).append(el);
    }

    $('.reorder').sortable({
        'handle':'.handler',
        'items':'.list-item',
        placeholder: 'ui-state-highlight',
        update:function(event, ui){
            var sortable = event.target;
            var ids = [];
            $('li', sortable).each(function(){
                ids.push($(this).text());
            });
            $(textarea).html(ids.join("\n"));
        }
    });

});

