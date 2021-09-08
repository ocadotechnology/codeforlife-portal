// Level Solution page

$(function() {
    $('#episodes').accordion({ collapsible: true, heightStyle: "content", active: false });
    var normalEpisodes = $('#episodes').children('h5').not('.customLevelsEpisode');
    var minOpacity = 0.1;
    var maxOpacity = 0.7;
    var numEpisodes = normalEpisodes.length;
    var bg = {'r':236, 'g':234, 'b':238}; // base colour grey
    var baseColor = {'r': 110, 'g': 113, 'b': 113};
    for (var i=0; i < numEpisodes; i++) {
        var opacity = minOpacity + i*(maxOpacity - minOpacity)/numEpisodes;
        var color = {'r':baseColor.r, 'g':baseColor.g, 'b':baseColor.b, 'a':opacity};
        var combinedColor = combineColors(bg, color);
        var newRGB = 'rgb('+Math.floor(combinedColor.r).toString()+', '+Math.floor(combinedColor.g).toString()+', '+Math.floor(combinedColor.b).toString()+')';
        normalEpisodes[i].style.background = newRGB;
    }

});

function combineColors(bg, color)
{
    var a = color.a;

    return {'r': (1 - a) * bg.r + a * color.r,
        'g': (1 - a) * bg.g + a * color.g,
        'b': (1 - a) * bg.b + a * color.b};
}

