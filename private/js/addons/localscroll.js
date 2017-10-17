import { isToolbarEnabled } from 'addons/utils';

const defaults = {
    offset: -20,
    scrollTime: 250,
};

export function scrollTo(position, scrollTime = defaults.scrollTime) {
    return new Promise(resolve => {
        $('html, body').animate(
            {
                scrollTop: position,
            },
            scrollTime,
            () => setTimeout(resolve)
        );
    });
}

export function initLocalScroll() {
    $(document).on('click', '.js-localscroll[href^="#"], .sub-menu a[href^="#"]', function(e) {
        e.preventDefault();

        const link = $(this);
        const href = link.attr('href');
        const data = link.data('localscroll');
        const options = $.extend(defaults, data);
        let target;

        try {
            target = $(href);
        } catch (e) {} // eslint-disable-line

        if (!target) {
            return;
        }

        const top = target.offset().top + parseInt(options.offset, 10) + (isToolbarEnabled() ? -46 : 0);

        scrollTo(top, options.scrollTime).then(function() {
            if (window.history.pushState) {
                window.history.pushState('', {}, href);
            } else {
                window.location.hash = href;
            }
        });
    });
}
