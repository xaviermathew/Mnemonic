$(document).ready(function() {
    $('select').select2();

    $('#select_source_types').change(function() {
        var el = $(this);
        var value = el.val();
        if (value.indexOf('news') == -1) {
            $('#select_newspapers').val([]);
            $('#select_newspapers').change();
            $('#select_newspapers').prop('disabled', true);
        } else {
            $('#select_newspapers').prop('disabled', false);
        }
        if (value.indexOf('tweet') == -1) {
            $('#select_twitter_handles').val([]);
            $('#select_twitter_handles').change();
            $('#select_twitter_handles').prop('disabled', true);
            $('#select_twitter_mentions').val([]);
            $('#select_twitter_mentions').change();
            $('#select_twitter_mentions').prop('disabled', true);
        } else {
            $('#select_twitter_handles').prop('disabled', false);
            $('#select_twitter_mentions').prop('disabled', false);
        }
    });
    $('#select_source_types').val(['news', 'tweet']);
    $('#select_source_types').change();
});