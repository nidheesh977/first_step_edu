$(document).ready(function () {

    $(window).scroll(function () {
        if ($(window).scrollTop() > 10) {
            $('.section-header').addClass('navbar-fixed');
        }
        else {
            $('.section-header').addClass('navbar-fixeded');
            $('.section-header').removeClass('navbar-fixed');
        }
    });

    var selector = '.head-menu li  a';
    $(selector).on('click', function () {
        $(selector).removeClass('active');
        $(this).addClass('active');
    });

    $('.landing-links').on('click', function () {
        var target = this.hash,
            $target = $(target);
        $('html, body').stop().animate({
            'scrollTop': $target.offset().top - 120
        }, 1000, 'swing', function () {
            window.location.hash = target;
        });
    });

    //   header-menu-active-script-code started
    if (window.location.href.indexOf("index") > 1) {
        $('#id_home').addClass('active');
    }
    else if (window.location.href.indexOf("about") > 1) {
        $('#id_about').addClass('active');
    }
    else if (window.location.href.indexOf("class") > 1) {
        $('#id_exam').addClass('active');
    }
    else if (window.location.href.indexOf("blog") > 1) {
        $('#id_blog').addClass('active');
    }
    else if (window.location.href.indexOf("contact") > 1) {
        $('#id_contact').addClass('active');
    }

    $(".nav-pills .nav-item").click(function () {
        $(".nav-item").removeClass("active");
        $(this).addClass("active");
    });

    $('.banner-slider').owlCarousel({
        loop: true,
        margin: 0,
        nav: true,
        items: 1,
        dots: false,
        smartSpeed: 2000,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplaySpeed: 3000,
        autoplayHoverPause: true,
    });

    $('.review-slider').owlCarousel({
        loop: true,
        margin: 10,
        nav: false,
        smartSpeed: 2000,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplaySpeed: 3000,
        autoplayHoverPause: true,
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 2
            },
            1000: {
                items: 2
            }
        }
    });

    $('.syllabus-slider').owlCarousel({
        loop: false,
        margin: 10,
        nav: true,
        dots: false,
        smartSpeed: 2000,
        responsive: {
            0: {
                items: 1
            },
            768: {
                items: 2
            },
            1200: {
                items: 3
            }
        }
    });

    var counted = 0;
    $(window).scroll(function () {
        if ($('.counter_method').length) {
            var oTop = $(".counter_method").offset().top - window.innerHeight;
            if (counted == 0 && $(window).scrollTop() > oTop) {
                // alert();
                $(".counter_method .counter").each(function () {
                    var $this = $(this),
                        countTo = $this.attr("data-count");
                    $({
                        countNum: $this.text(),
                    }).animate({
                        countNum: countTo,
                    },

                        {
                            duration: 4000,
                            easing: "linear",
                            step: function () {
                                $this.text(Math.floor(this.countNum));
                            },
                            complete: function () {
                                $this.text(this.countNum);
                            },
                        }
                    );
                });
                counted = 1;
            }
        }
    });

    $(".side-box").hide();
    $(".hide-box").click(function () {
        $(".section-acc-sidebar").show();
        $(".hide-box").hide();
        $(".side-box").show();
        // $(".dashboard-content").css('background-color','#000');
        // $(".dashboard-content").css('opacity','0.2')
    });
    $(".side-box").click(function () {
        $(".section-acc-sidebar").hide();
        $(".side-box").hide();
        $(".hide-box").show();
        // $(".dashboard-content").css('background-color','#F1FAFD');
        // $(".dashboard-content").css('opacity','1')
    });

    $('.moreless-button').click(function () {
        $(this).closest('.jee_trainer_carrer').find('.moretext').toggle();
        if ($(this).closest('.jee_trainer_carrer').find('.moreless-button').text() == "VIEW MORE") {
            $(this).closest('.jee_trainer_carrer').find('.moreless-button').text("VIEW LESS")
        } else {
            $(this).closest('.jee_trainer_carrer').find('.moreless-button').text("VIEW MORE")
        }
    });

    $('.start-exam').hide();
    // $('.start-test').click(function () {
    //     $('.start-exam').show();
    //     $('.start-test').hide();
    //     // countdown script started code
    //     function countdown(elementName, minutes, seconds) {
    //         var element, endTime, hours, mins, msLeft, time;
    //         function twoDigits(n) {
    //             return (n <= 9 ? "0" + n : n);
    //         }
    //         function updateTimer() {
    //             msLeft = endTime - (+new Date);
    //             if (msLeft < 1000) {
    //                 element.innerHTML = "Time is up!";
    //             } else {
    //                 time = new Date(msLeft);
    //                 hours = time.getUTCHours();
    //                 mins = time.getUTCMinutes();
    //                 element.innerHTML = (hours ? hours + ':' + twoDigits(mins) : mins) + ':' + twoDigits(time.getUTCSeconds());
    //                 setTimeout(updateTimer, time.getUTCMilliseconds() + 500);
    //             }
    //         }
    //         element = document.getElementById(elementName);
    //         endTime = (+new Date) + 1000 * (60 * minutes + seconds) + 500;
    //         updateTimer();
    //     }
    //     // countdown( "ten-countdown", 30, 00 );

    //     function countsec(elementName, minutes, seconds) {
    //         var element, endTime, hours, mins, msLeft, time;
    //         function twoDigits(n) {
    //             return (n <= 9 ? "0" + n : n);
    //         }
    //         function updateTimer() {
    //             msLeft = endTime - (+new Date);
    //             if (msLeft < 1000) {
    //                 element.innerHTML = "Time is up!";
    //             } else {
    //                 time = new Date(msLeft);
    //                 hours = time.getUTCHours();
    //                 mins = time.getUTCMinutes();
    //                 element.innerHTML = (hours ? hours + ':' + twoDigits(mins) : mins) + ':' + twoDigits(time.getUTCSeconds());
    //                 setTimeout(updateTimer, time.getUTCMilliseconds() + 500);
    //             }
    //         }
    //         element = document.getElementById(elementName);
    //         endTime = (+new Date) + 1000 * (60 * minutes + seconds) + 500;
    //         updateTimer();
    //     }
    //     //countsec( "ten-countsec", 0, 30 );
    // });

    const date = new Date();
    let day = date.getDate();
    let month = date.getMonth() + 1;
    let year = date.getFullYear();
    let currentDate = `${day}-${month}-${year}`;
    document.getElementById("current-date").innerHTML = currentDate;
});
