(function ($, window, document) {

    var pluginName = "jqueryVideoLightning",
        defaults = {
            id: "y-dQw4w9WgXcQ",
            width: "640px",
            height: "390px",
            autoplay: 0,
            autohide: 2,
            controls: 1,
            iv_load_policy: 1,
            loop: 0,
            modestbranding: 0,
            playlist: "",
            related: 0,
            showinfo: 1,
            start_time: 0,
            theme: "dark",
            color: "",
            byline: 1,
            portrait: 1,
            effect_in: "fadeIn",
            ease_in: 300,
            ease_out: 0,
            z_index: 21000,
            backdrop_color: "#000",
            backdrop_opacity: 1,
            glow: 0,
            glow_color: "#fff",
            rick_roll: 0,
            cover: 0,
            popover: 0,
            popover_x: "auto",
            popover_y: "auto"
        };

    function JQVideoLightning(element, options) {
        this.element = element;
        this.base_settings = $.extend({}, defaults, options);
        this.init();
    }

    JQVideoLightning.prototype = {
        init: function () {
            var target, target_wrapper, settings, video_id, vendor, popover;
            target = $(this.element);
            target_wrapper = target.wrap("<span class='video-target'></span>").parent(".video-target");
            target_wrapper.css("cursor", "pointer");
            settings = this.settings();
            video_id = settings.videoId.substring(2);
            vendor = (settings.videoId.charAt(0).toLowerCase() === "v") ? "vimeo" : "youtube";
            popover = settings.videoPopover;
            if ($("style:contains('.video-wrapper')").length < 1) {
                $("<style type='text/css'>" +
                    ".video-wrapper{ " +
                    "display: none; " +
                    "position: fixed; " +
                    "min-width: 100%; " +
                    "min-height: 100%; " +
                    "top: 0; " +
                    "bottom: 0; " +
                    "left: 0; " +
                    "z-index: " + settings.videoZIndex + "; " +
                    "} " +
                    ".video-frame{ " +
                    "background: #000000;" +
                    "</style>").appendTo("head");
            }

            if (settings.videoCover === 1) {
                this.coverImage(vendor, video_id, target_wrapper);
            }

            function callPlayer() {
                $(this.player(target, target_wrapper, video_id, vendor, popover));
            }

            function resizeTail() {
                function tailPosition() {
                    var position_returns, sticky;
                    position_returns = this.popoverPosition(settings);
                    sticky = target_wrapper.find(".video-popover-tail").attr("points");
                    if (sticky !== undefined) {
                        sticky = sticky.substring(sticky.indexOf(' ') + 1);
                        return settings.videoTargetPositionsX[position_returns[0]] + "," +
                            settings.videoTargetPositionsY[position_returns[1]] + " " +
                            sticky;
                    }
                }

                target_wrapper.find(".video-popover-tail").attr({
                    points: $.proxy(tailPosition, this)
                });
            }

            target_wrapper.on("click", $.proxy(callPlayer, this));

            $(document).on("scroll mousewheel DOMMouseScroll MozMousePixelScroll", $.proxy(resizeTail, this));


        },

        player: function (target, target_wrapper, video_id, vendor, popover) {
            var settings;
            settings = (popover === 1) ? this.popover() : this.settings();

            if (target_wrapper.find(".video-wrapper").is(':visible')) {
                if (settings.videoRickRoll !== 1) {
                    return this.destroy(target_wrapper);
                }
                return;
            }

            target_wrapper.append('<div class="video-wrapper"><div class="video-frame"><div class="video"></div></div></div>');
            target_wrapper.find(".video-wrapper").css({
                backgroundColor: "rgba(" + this.colorConverter(settings.videoBackdropColor).red + "," + this.colorConverter(settings.videoBackdropColor).blue + "," + this.colorConverter(settings.videoBackdropColor).green + "," + settings.videoBackdropOpacity + ")"
            });
            target_wrapper.find(".video-frame").css({
                position: 'absolute',
                top: settings.videoFrameTop,
                left: settings.videoFrameLeft,
                width:  settings.videoWidth + 'px',
                height: settings.videoHeight + 'px',
                marginTop: settings.videoFrameMarginTop,
                marginLeft: settings.videoFrameMarginLeft,
                boxShadow: '0px 0px ' + settings.videoGlow + 'px ' + (settings.videoGlow / 5) + 'px ' + this.fullHex(settings.videoGlowColor)
            });
            target_wrapper.find(".video-wrapper")[settings.videoEffectIn](settings.videoEaseIn);

            return target_wrapper.find(".video").append(this[vendor + "Player"](settings, video_id));
        },

        settings: function () {
            var target, settings, setting_key, display_ratio;
            target = $(this.element);
            settings = this.base_settings;

            function remapSettings(settings) {
                $.each(settings,
                    $.proxy(function (key, value) {
                        setting_key = "video" +
                            key.toLowerCase().charAt(0).toUpperCase() +
                            key.slice(1).replace(/_([a-z])/g, function (m, w) {
                                return w.toUpperCase();
                            });
                        $(this).data(setting_key, value);
                    }, this)
                    );
                return $(this).data();
            }

            settings = target.extend({}, remapSettings(settings), target.data());

            settings.videoWidth = parseInt(settings.videoWidth, 10);
            settings.videoHeight = parseInt(settings.videoHeight, 10);
            display_ratio = settings.videoHeight / settings.videoWidth;

            if (settings.videoWidth > $(window).width() - 30) {
                settings.videoWidth = $(window).width() - 30;
                settings.videoHeight = Math.round(display_ratio * settings.videoWidth);
            }

            settings.videoFrameTop = '50%';
            settings.videoFrameLeft = '50%';
            settings.videoFrameMarginTop = '-' + settings.videoHeight / 2 + 'px';
            settings.videoFrameMarginLeft = '-' + settings.videoWidth / 2 + 'px';

            return settings;
        },

        popover: function () {
            var target,
                target_wrapper,
                settings;

            target = $(this.element);
            target_wrapper = target.parent(".video-target");
            settings = this.settings();

            target_wrapper.append('<div class="video-popover-tail-wrapper">' +
                '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">' +
                '<polygon class="video-popover-tail" points="" fill="" stroke="" stroke-width="" />' +
                '</svg></div>');

            target_wrapper.find(".video-popover-tail-wrapper").css({
                position: "fixed",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                "z-index": 0
            });

            this.popoverTail(settings);

            settings.videoFrameMarginTop = '0';
            settings.videoFrameMarginLeft = '0';
            settings.videoBackdropOpacity = 0;
            settings.videoEaseIn = 0;

            return settings;
        },

        popoverPosition: function (settings) {
            var target,
                target_wrapper,
                target_position_x,
                target_position_y,
                position_x,
                position_y,
                window_center_x,
                window_center_y,
                video_center_x,
                video_center_y,
                tempValues;

            target = $(this.element);
            target_wrapper = target.parent(".video-target");
            target_position_x = target_wrapper.offset().left - $(window).scrollLeft();
            target_position_y = target_wrapper.offset().top - $(window).scrollTop();
            window_center_x = $(window).width() / 2;
            window_center_y = $(window).height() / 2;
            video_center_x = settings.videoWidth / 2;
            video_center_y = settings.videoHeight / 2;

            settings.videoTargetPositionsX = {
                left: Math.round(target_position_x),
                center: Math.round(target_position_x + (target_wrapper.outerWidth() / 2)),
                right: Math.round(target_position_x + target_wrapper.outerWidth())
            };
            settings.videoTargetPositionsY = {
                top: Math.round(target_position_y),
                center: Math.round(target_position_y + (target_wrapper.outerHeight() / 2)),
                bottom: Math.round(target_position_y + target_wrapper.outerHeight())
            };
            settings.videoPositionsX = {
                left: settings.videoTargetPositionsX.left - settings.videoWidth - 15,
                center: settings.videoTargetPositionsX.center - video_center_x,
                right: settings.videoTargetPositionsX.right + 15
            };
            settings.videoPositionsY = {
                top: settings.videoTargetPositionsY.top - settings.videoHeight - 15,
                center: settings.videoTargetPositionsY.center - video_center_y,
                bottom: settings.videoTargetPositionsY.bottom + 15
            };

            function positionValues(positions) {
                return $.map(positions, function (value) {
                    return value;
                });
            }

            function optimalPosition(positions, video_center, window_center) {
                var tempPositions = [];
                tempValues = positionValues(positions).sort(function (a, b) {
                    return (Math.abs((a + video_center) - window_center)) - (Math.abs((b + video_center) - window_center));
                });

                $.each(tempValues, function (i, value) {
                    $.each(positions, function (list_key, list_value) {
                        if (list_value  === value) {
                            tempPositions.push(list_key);
                        }
                    });
                });
                return tempPositions;
            }

            settings.videoOptimalPositionsX = optimalPosition(settings.videoPositionsX, video_center_x, window_center_x);
            settings.videoOptimalPositionsY = optimalPosition(settings.videoPositionsY, video_center_y, window_center_y);

            position_x = (settings.videoPopoverX === "auto") ? settings.videoOptimalPositionsX[0] : settings.videoPopoverX;
            if (settings.videoOptimalPositionsX[0] === "center" && settings.videoOptimalPositionsY[0] === "center") {
                position_y = (settings.videoPopoverY === "auto") ? settings.videoOptimalPositionsY[1] : settings.videoPopoverY;
            } else {
                position_y = (settings.videoPopoverY === "auto") ? settings.videoOptimalPositionsY[0] : settings.videoPopoverY;
            }

            function popoverSizing(positions, optimal_position, target_position, video_center, primary_dimension, secondary_dimension, frame_dimension) {
                var position, old_dimension, display_ratio;
                position = positions[optimal_position];
                display_ratio = settings["video" + secondary_dimension] / settings["video" + primary_dimension];

                if (position < 0) {
                    old_dimension = settings["video" + primary_dimension];
                    settings["video" + primary_dimension] = settings["video" + primary_dimension] + position - 10;
                    settings["video" + secondary_dimension] = Math.round(display_ratio * settings["video" + primary_dimension]);
                    settings["videoFrame" + frame_dimension] = (position < target_position - video_center) ? (position + old_dimension) - settings["video" + primary_dimension] + 'px' : position + (old_dimension / 2) - (settings["video" + primary_dimension] / 2) + 'px';
                } else {
                    settings["videoFrame" + frame_dimension] = position + 'px';
                }
            }

            popoverSizing(settings.videoPositionsX, position_x, target_position_x, video_center_x, "Width", "Height", "Left");
            popoverSizing(settings.videoPositionsY, position_y, target_position_y, video_center_y, "Height", "Width", "Top");

            return [position_x, position_y, video_center_x, video_center_y];
        },

        popoverTail: function (settings) {
            var target,
                target_wrapper,
                position_x,
                position_y,
                video_center_x,
                video_center_y,
                position_return;

            target = $(this.element);
            target_wrapper = target.parent(".video-target");
            position_return = this.popoverPosition(settings);
            position_x = position_return[0];
            position_y = position_return[1];
            video_center_x = position_return[2];
            video_center_y = position_return[3];

            function tailPosition() {
                var x, x2, y, y2;
                if (position_x === "left") {
                    x = settings.videoPositionsX[position_x] + settings.videoWidth;
                    x2 = settings.videoPositionsX[position_x] + settings.videoWidth - 25;
                } else if (position_x === "right") {
                    x = settings.videoPositionsX[position_x];
                    x2 = settings.videoPositionsX[position_x] + 25;
                } else {
                    x = settings.videoPositionsX[position_x] + video_center_x - 30;
                    x2 = settings.videoPositionsX[position_x] + video_center_x + 15;
                }
                if (position_y === "top") {
                    y = settings.videoPositionsY[position_y] + settings.videoHeight;
                    y2 = settings.videoPositionsY[position_y] + settings.videoHeight - 25;
                } else if (position_y === "bottom") {
                    y = settings.videoPositionsY[position_y];
                    y2 = settings.videoPositionsY[position_y] + 25;
                } else {
                    y = settings.videoPositionsY[position_y] + video_center_y - 30;
                    y2 = settings.videoPositionsY[position_y] + video_center_y + 15;
                }
                return settings.videoTargetPositionsX[position_x] + "," +
                    settings.videoTargetPositionsY[position_y] + " " +
                    x + "," +
                    y2 + " " +
                    x2 + "," +
                    y;
            }

            target_wrapper.find(".video-popover-tail").attr({
                points: tailPosition(),
                fill: "black",
                stroke: "black",
                "stroke-width": 0
            });
        },

        colorConverter: function (hex) {
            var  red, green, blue;

            red = parseInt((this.prepHex(hex)).substring(0, 2), 16);
            blue = parseInt((this.prepHex(hex)).substring(2, 4), 16);
            green = parseInt((this.prepHex(hex)).substring(4, 6), 16);
            return {
                red: red,
                blue: blue,
                green: green
            };
        },

        prepHex: function (hex) {
            hex = (hex.charAt(0) === "#") ? hex.split("#")[1] : hex;
            if (hex.length === 3) {
                hex = hex + hex;
            }
            return hex;
        },

        fullHex: function (hex) {
            hex = "#" + this.prepHex(hex);
            return hex;
        },

        coverImage: function (vendor, video_id, target_wrapper) {
            var vimeo_api_url, youtube_img_url;
            vimeo_api_url = 'http://www.vimeo.com/api/v2/video/' + video_id + '.json?callback=?';
            youtube_img_url = 'http://img.youtube.com/vi/' + video_id + '/hqdefault.jpg';

            if (vendor === "youtube") {
                $("<img class='video-cover'>").attr("src", youtube_img_url).appendTo(target_wrapper);
            } else {
                $.getJSON(vimeo_api_url, {format: "jsonp"})
                    .done(function (data) {
                        $("<img class='video-cover'>").attr("src", data[0].thumbnail_large).appendTo(target_wrapper);
                    });
            }
        },

        youtubePlayer: function (settings, video_id) {
            return $("<iframe src=\"https://www.youtube.com/embed/" + video_id +
                "?autoplay=" + settings.videoAutoplay +
                "&autohide=" + settings.videoAutohide +
                "&controls=" + settings.videoControls +
                "&iv_load_policy=" + settings.videoIvLoadPolicy +
                "&loop=" + settings.videoLoop +
                "&modestbranding=" + settings.videoModestbranding +
                "&playlist=" + settings.videoPlaylist +
                "&rel=" + settings.videoRelated +
                "&showinfo=" + settings.videoShowinfo +
                "&start=" + settings.videoStartTime +
                "&theme=" + settings.videoTheme +
                "&color=" + settings.videoColor +
                "\" width=\"" + settings.videoWidth +
                "\"px height=\"" + settings.videoHeight +
                "\"px frameborder=\"0\" allowfullscreen></iframe>");
        },

        vimeoPlayer: function (settings, video_id) {
            return $("<iframe src=\"http://player.vimeo.com/video/" + video_id +
                "?autoplay=" + settings.videoAutoplay +
                "&loop=" + settings.videoLoop +
                "&title=" + settings.videoShowinfo +
                "&byline=" + settings.videoByline +
                "&portrait=" + settings.videoPortrait +
                "&color=" + this.prepHex(settings.videoColor) +
                "\" width=\"" + settings.videoWidth +
                "\"px height=\"" + settings.videoHeight +
                "\"px frameborder=\"0\" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>");
        },

        destroy: function (target_wrapper) {
            target_wrapper.find(".video-wrapper").hide((this.settings().videoEaseOut));
            setTimeout(function () {
                target_wrapper.find(".video").remove();
                target_wrapper.find(".video-popover-tail-wrapper").remove();
                target_wrapper.find(".video-wrapper").remove();
                $(this).off();
                $(this).removeData();
            }, this.settings().videoEaseOut);
        }
    };

    $.fn[pluginName] = function (options) {
        return this.each(function () {
            if (!$.data(this, "plugin_" + pluginName)) {
                $.data(this, "plugin_" + pluginName, new JQVideoLightning(this, options));
            }
        });
    };

    return this;

})(jQuery, window, document);