/*jslint browser: true, onevar: true, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, newcap: true, immed: true, regexp: false, white:true */
/*global jQuery, ajax_noresponse_message, window */

jQuery(document).ready(function () {
    jQuery('.selImageToCropBtn').prepOverlay({
        subtype: 'ajax',
        filter: '#cropImage',
        config: {
            onLoad: function () {
                var cropImage = jQuery("#croppableImage"),
                    imageRecrop = jQuery('#image-recrop'),
                    Math = window.Math,
                    field, yratio, xratio, crop_size, jcrop, cropbox, minX, minY;
                if (cropImage.length) {
                    field = cropImage.attr('data-field');
                    yratio = window.parseFloat(cropImage.attr('data-previewratioy'));
                    xratio = window.parseFloat(cropImage.attr('data-previewratiox'));
                    minX = Math.round(1024 / xratio);
                    minY = Math.round(576 / yratio);
                    crop_size = jQuery("#crop_size");
                    jcrop = jQuery.Jcrop(cropImage);
                    cropbox = null;
                    jcrop.setOptions({                                      
                        aspectRatio: 16 / 9,
                        allowSelect: true,
                        allowResize: true,
                        allowMove: true,
                        minSize: [minX, minY],
                        onSelect: function (coords) {
                                cropbox = coords;
                                var cropbox_x = window.parseInt(cropbox.w * xratio),
                                    cropbox_y = window.parseInt(cropbox.h * yratio),
                                    crop_text = cropbox_x + "x" + cropbox_y + "px";
                                crop_size.html(crop_text);
                                if (crop_size.text() !== '0x0px') {
                                    imageRecrop.removeClass('hidden');
                                }
                            }
                    });
                    jcrop.focus();

                    imageRecrop.click(function (e) {
                            e.preventDefault();
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
                                       y2: cropbox.y2
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
