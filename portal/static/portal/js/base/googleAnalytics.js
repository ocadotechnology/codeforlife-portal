(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function() {
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');


ga('create', 'UA-49883146-1', 'auto');
ga('send', 'pageview');

function send_event(category_name, action, label_name) {
    ga('send', {
        hitType: 'event',
        eventCategory: category_name,
        eventAction: action,
        eventLabel: label_name
    });
}

riveted.init();

function send_event(name_of_file, action){
    ga('send', {
        hitType: 'event',
        eventCategory: 'PDFs',
        eventAction: action,
        eventLabel: name_of_file
    });
}
