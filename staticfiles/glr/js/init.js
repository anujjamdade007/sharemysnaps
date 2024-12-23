/*
 * Author: matchthemes.com
 *
 */
 
(function($) {
    "use strict";
	
	// home slider
	$('.home-slider').owlCarousel({
    items:1,
    loop:true,
	autoplay:true,
	autoplayTimeout:7000,
	autoplayHoverPause:true,
	animateOut: 'fadeOut',
	dots:false,
	nav:true,
	navText:''
});

	   $('.portfolio-slider-4items').owlCarousel({
   	loop:true,
	autoplay:true,
	autoplayTimeout:6000,
	margin: 30,
	dots:false,
	nav:true,
	navText:'',
	responsive:{	0:		{ items: 1 },
					568:	{ items: 2 },
					1024:	{ items: 3 },

				}
});

	$('.testimonial-slider').owlCarousel({
    items:1,
    loop:true,
	autoHeight: true,
	autoplay: true,
	autoplayTimeout:8000,
	animateOut: 'fadeOut'
});	

//mobile menu
$('.nav-button').on('click', function(e){
	
	e.preventDefault();
	
    $('.mobile-menu-holder, .menu-mask').addClass('is-active');
	$('body').addClass('has-active-menu');

});

$('.exit-mobile, .menu-mask').on('click', function(e){
	
	e.preventDefault();

    $('.mobile-menu-holder, .menu-mask').removeClass('is-active');
	$('body').removeClass('has-active-menu');

});

$('.menu-mobile > li.menu-item-has-children > a').on('click', function(e){
			
			e.preventDefault();
			e.stopPropagation();
			
			if ( $(this).parent().hasClass('menu-open') )
			
			$(this).parent().removeClass('menu-open');
			
			else {
			
			$(this).parent().addClass('menu-open');
			
			}
																  
			});
	
	// end mobile menu
	
// menu edge screen turn left

$(".menu-nav li").on('mouseenter mouseleave', function (e) {
        if ($('ul', this).length) {
            var elm = $('.sub-menu', this);
            var off = elm.offset();
            var l = off.left;
            var w = elm.width();
            var docW = $(window).width();

            var isEntirelyVisible = (l + w <= docW);

            if (!isEntirelyVisible) {
                $(this).addClass('edge');
            } else {
                $(this).removeClass('edge');
            }
        }
    });	
		
	
$(window).on('load', function() {
	
	//masonry
	var blogItems = $('.layout-masonry');
   var portfolioItems = $('.portfolio-layout-masonry');
   var portfolioItems2 = $('.portfolio-layout-masonry2');
   var portfolioItems4 = $('.grid-v4-masonry');
   
   blogItems.isotope({
  itemSelector : '.blog-item-masonry',
  layoutMode : 'masonry',
 
	});
	
	portfolioItems.isotope({
  itemSelector : '.item-portfolio',
  layoutMode : 'masonry',
 
	});
	
	portfolioItems2.isotope({
  itemSelector : '.grid-item-style',
  layoutMode : 'fitRows',
	});
	
	
	portfolioItems4.isotope({
	itemSelector : '.grid-item-v4',
	percentPosition: true,
	layoutMode: 'masonry',	
	masonry: {
	  columnWidth: '.grid-item-v4-init'
	}
	});
	
	
	// filter items when filter link is clicked
if ($('.portfolio-filter a').length){	
 $('.portfolio-filter a').on('click', function(){
 $('.portfolio-filter .current').removeClass('current');
 $(this).addClass('current');
		
  var selector = $(this).attr('data-filter');
  portfolioItems.isotope({ filter: selector });
  portfolioItems2.isotope({ filter: selector });
  return false;
});
}

});	//window.load

$(window).on('scroll', function() {
  if ($(document).scrollTop() > 1 ) {
    $('.main-header').addClass('nav-fixed-top');
	} else {
    $('.main-header').removeClass('nav-fixed-top');
  }
  
  });


//gallery

$('.gallery-post a').simpleLightbox({
	heightRatio: 1,
	widthRatio: 0.8
   
});

	
// faq
$('.faq-section').hide();
$('.faq-title').on('click',function(){

  if( $(this).next().is(':hidden') ) {

$(this).toggleClass('active').next().slideDown();
  } else {
   $(this).removeClass('active').next().slideUp();
 }
  return false; 
 });	
	

//fluid width videos

  $(".single-post-content, .custom-page-template, .post-video").fitVids({customSelector: "iframe[src^='https://w.soundcloud.com']"});
 
 
 //scroll up button
 
  $(".scrollup").hide();
     $(window).on('scroll', function() {
         if ($(this).scrollTop() > 400) {
             $('.scrollup').fadeIn();
         } else {
             $('.scrollup').fadeOut();
         }
     });

$("a.scrolltop[href^='#']").on('click', function(e) {
   e.preventDefault();
   var hash = this.hash;
   $('html, body').stop().animate({scrollTop:0}, 1000, 'easeOutExpo');

});
 
})(jQuery);