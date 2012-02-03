/*jslint browser: true, onevar: true, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, newcap: true, immed: true, regexp: false, white:true */
/*global jQuery, ajax_noresponse_message, window */

jQuery(document).ready(function () {
    jQuery('.selImageToCropBtn').prepOverlay({
        subtype: 'ajax',
        filter: 'form#cropImage',
        config: {
            onLoad: function () {
                var cropimage = jQuery("#croppableImage"),
                    size_selector = jQuery("#imagesize-selector"),
                    sel_size, field, yratio, xratio, crop_size, jcrop, cropbox;
                if (cropimage.length) {
                    field = cropimage.attr('data-field');
                    yratio = window.parseFloat(cropimage.attr('data-previewratioy'));
                    xratio = window.parseFloat(cropimage.attr('data-previewratiox'));
                    crop_size = jQuery("#crop_size");
                    jcrop = jQuery.Jcrop(cropimage);
                    cropbox = null;
                    jcrop.setOptions({                                      
                        aspectRatio: 16 / 9,
                        allowSelect: true,
                        allowResize: true,
                        allowMove: true,
                        onSelect: function (coords) {
                                cropbox = coords;
                                var cropbox_x = window.parseInt(cropbox.w * xratio),
                                    cropbox_y = window.parseInt(cropbox.h * yratio),
                                    crop_text = cropbox_x + "x" + cropbox_y + "px";
                                crop_size.html(crop_text);
                                jQuery('input#image-recrop').removeAttr('disabled');
                            }
                    });
                    jcrop.focus();

                    jQuery('input#image-recrop').click(function (e) {
                            e.preventDefault();
                            sel_size = size_selector.find(":selected").attr('value') || "";
                            var context_url = jQuery('base').attr('href');
                            if (context_url.substr(-1) !== '/') {
                                context_url = context_url + '/';
                            }
                            jQuery.ajax({
                                type: 'GET',
                                url: context_url + '@@cropimage/cropImage',
                                data: {field: field,
                                       x1: cropbox.x,
                                       y1: cropbox.y,
                                       x2: cropbox.x2,
                                       y2: cropbox.y2,
                                       resize_size: sel_size
                                      },
                                success: function () {
                                    window.location.replace(context_url);
                                }
                            });
                        });
                }
            }
        }
    });
});
