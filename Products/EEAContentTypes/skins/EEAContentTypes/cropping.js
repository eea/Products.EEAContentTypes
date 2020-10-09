/*jslint browser: true, onevar: true, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, newcap: true, immed: true, regexp: false, white:true */
/*global jQuery, ajax_noresponse_message, window */

jQuery(document).ready(function() {
    jQuery('.selImageToCropBtn').prepOverlay({
        subtype: 'ajax',
        filter: '#cropImage',
        config: {
            onLoad: function() {
                var cropImage = jQuery("#croppableImage"),
                    imageRecrop = jQuery('#image-recrop'),
                    image_size = jQuery('#current_image_size'),
                    image_small_warning = jQuery("#current_image_too_small"),
                    crop_disclaimer = jQuery('#crop-disclaimer'),
                    Math = window.Math,
                    field, yratio, xratio, crop_size, jcrop, cropbox, minX,
                    minY,
                    aspect_ratio = 16 / 9;
                var image_too_small = window.parseInt(image_size.text().split('x')[0], 10) < 1920;
                if (image_too_small) {
                    image_small_warning.removeClass('hidden');
                }
                else {
                    crop_disclaimer.removeClass('hidden');
                }
                if (cropImage.length) {
                    field = cropImage.attr('data-field');
                    yratio = window.parseFloat(cropImage.attr('data-previewratioy'));
                    xratio = window.parseFloat(cropImage.attr('data-previewratiox'));
                    minX = Math.round(1920 / xratio);
                    minY = Math.round(1080 / yratio);

                    crop_size = jQuery("#crop_size");
                    jcrop = jQuery.Jcrop(cropImage);
                    cropbox = null;
                    jcrop.setOptions({
                        aspectRatio: aspect_ratio,
                        allowSelect: true,
                        allowResize: true,
                        allowMove: true,
                        minSize: [minX, minY],
                        onSelect: function(coords) {
                            if (image_too_small) {
                                return;
                            }
                            cropbox = coords;
                            var cropbox_x = Math.ceil(cropbox.w * xratio),
                                cropbox_y = Math.ceil(cropbox.h * yratio),
                                crop_text,
                                sixteen_nine_x = 1920 / xratio,
                                sixteen_nine_y = 1080 / yratio;

                            var sixteen_nine_proper_x =Math.round(cropbox_x / 16) * 16;
                            var sixteen_nine_proper_y = Math.round(cropbox_y / 9) * 9;

                            if (cropbox.w) {
                                if (sixteen_nine_proper_x !== cropbox_x) {
                                    cropbox_x = sixteen_nine_proper_x;
                                    cropbox.w = sixteen_nine_proper_x / xratio;
                                }
                            }

                            if (cropbox.h) {
                                if (sixteen_nine_proper_y !== cropbox_y) {
                                    cropbox_y = sixteen_nine_proper_y;
                                    cropbox.h = sixteen_nine_proper_y / yratio;
                                }
                            }
                            cropbox.full_width = cropbox_x;
                            cropbox.full_height = cropbox_y;
                            crop_text = cropbox_x + "x" + cropbox_y + "px";
                            crop_size.html(crop_text);
                            if (crop_size.text() !== '0x0px') {
                                imageRecrop.removeClass('hidden');
                            }
                        }
                    });
                    jcrop.focus();

                    imageRecrop.click(function(e) {
                        e.preventDefault();
                        var context_url = jQuery('body').data('base-url') || jQuery('base').attr('href') || '';
                        if (context_url.substr(-1) !== '/') {
                            context_url = context_url + '/';
                        }
                        jQuery.ajax({
                            type: 'GET',
                            url: context_url + '@@cropimage/cropImage',
                            data: {
                                field: field,
                                x1: cropbox.x,
                                y1: cropbox.y,
                                x2: cropbox.x2,
                                y2: cropbox.y2,
                                full_width: cropbox.full_width,
                                full_height: cropbox.full_height
                            },
                            success: function() {
                                window.location.replace(context_url);
                            }
                        });
                    });
                }
            }
        }
    });
});
