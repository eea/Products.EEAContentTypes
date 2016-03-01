var GISMapEmbedSelection = function (btnel) {
        var btn            = jQuery(btnel);
        var embed_titles   = btn.parent().parent();
        var divparent      = embed_titles.parent();
        var metadata       = divparent.find('.metadata');
        var uid            = metadata.find('.metadata-gismap-uid').text();
        var url            = metadata.find('.metadata-url').text();
        var embed_type     = metadata.find('.metadata-embed-type').text();
        var is_static      = (embed_type=='static');
        var is_interactive = ((embed_type=='interactive') || (embed_type===''));

        var popup = jQuery("<div />");

        // build the radios
        var p = jQuery("<p />");
        p.append(jQuery("<input />").attr({
            'type': 'radio',
            'name': 'embed-' + uid, 'id': 'embed-interactive-' + uid,
            'value': 'interactive',
            'checked': is_interactive}));
        p.append(jQuery("<label />").attr({
            'for': 'embed-interactive-' + uid}).text('Interactive (default)'));
        p.append('<br /><em style="padding-left:15px;">Show the emebed code like in the view</em>');
        popup.append(p);

        p = jQuery("<p />");
        p.append(jQuery("<input />").attr({
            'type': 'radio',
            'name': 'embed-' + uid, 'id': 'embed-static-' + uid,
            'value': 'static',
            'checked': is_static}));
        p.append(jQuery("<label />").attr({
            'for': 'embed-static-' + uid}).text('Static'));
        p.append('<br /><em style="padding-left:15px;">Show the standard screenshot preview</em>');
        popup.append(p);

        var width = 300;
        var height = 200;

        popup.dialog({
            'title':'Select embed type',
            modal: true,
            minWidth:width,
            'width':width,
            minHeight:height,
            'height':height,
            buttons: {
                'OK': function () {
                    //process selection
                    var embed = $('input[name=\'' + 'embed-' + uid + '\']:checked').val();
                    if (typeof(embed)==='undefined') {embed = 'interactive';}
                    //save data
                    var dialog = this;
                    jQuery.ajax({
                        type: 'POST',
                        url: url,
                        data: {
                            'gismap_uid': uid,
                            'embed': embed
                        },
                        error: function () {
                            alert("Could not save data on server");
                        },
                        success: function () {
                            //update label and metadata
                            embed_titles.find('.embed-title').removeAttr('style');
                            embed_titles.find('.embed-title').text(embed);
                            metadata.find('.metadata-embed-type').text(embed);
                            jQuery(dialog).dialog('destroy').remove();
                        }
                    });
                },
                'Cancel': function () {
                    jQuery(this).dialog('destroy').remove();
                }
            }
        });

    };
