/* jshint devel:true */

$(document).foundation('reflow', 'abide', 'accordion');

$('#slick-questions').slick({
  speed: 3000,
  autoplay: true,
  arrows: false,
  adaptiveHeight: true
});

//if (Foundation.utils.is_small_only()) {
$('#testimonials').slick({arrows: true, dots: true});
// } else {
//  $('#testimonials').unslick();
// }
