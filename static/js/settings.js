(function($) {
  'use strict';
  $(function() {
    $(".nav-settings").on("click", function() {
      $("#right-sidebar").toggleClass("open");
    });
    $(".settings-close").on("click", function() {
      $("#right-sidebar,#theme-settings").removeClass("open");
    });

    $("#settings-trigger").on("click" , function(){
      $("#theme-settings").toggleClass("open");
    });


    //background constants
    var navbar_classes = "navbar-danger navbar-success navbar-warning navbar-dark navbar-light navbar-primary navbar-info navbar-pink";
    var sidebar_classes = "sidebar-light sidebar-dark";
    var $body = $("body");

    //sidebar backgrounds
    $("#sidebar-light-theme").on("click" , function(){
      $body.removeClass(sidebar_classes);
      $body.addClass("sidebar-light");
      $(".sidebar-bg-options").removeClass("selected");
      $(this).addClass("selected");
    });
    $("#sidebar-dark-theme").on("click" , function(){
      $body.removeClass(sidebar_classes);
      $body.addClass("sidebar-dark");
      $(".sidebar-bg-options").removeClass("selected");
      $(this).addClass("selected");
    });


    //Navbar Backgrounds
    $(".tiles.primary").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-primary");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
    });
    $(".tiles.success").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-success");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
    });
    $(".tiles.warning").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-warning");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
    });
    $(".tiles.danger").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-danger");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
    });
    $(".tiles.light").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-light");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
    });
    $(".tiles.info").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-info");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
    });
    $(".tiles.dark").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".navbar").addClass("navbar-dark");
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
    });
    $(".tiles.default").on("click" , function(){
      $(".navbar").removeClass(navbar_classes);
      $(".tiles").removeClass("selected");
      $(this).addClass("selected");
    });
  });
})(jQuery);

// document.getElementById('submitForm').addEventListener('submit', function(event) {
//   event.preventDefault();  // Prevent the default form submission

//   let formData = new FormData(this);

//   fetch('/add', {
//       method: 'POST',
//       body: formData
//   })
//   .then(response => response.json())
//   .then(data => {
//       if (data.status === 'error') {
//           let errorsContainer = document.getElementById('errors');
//           errorsContainer.innerHTML = '';  // Clear previous errors

//           data.errors.forEach(error => {
//               let errorElement = document.createElement('li');
//               errorElement.textContent = error;
//               errorsContainer.appendChild(errorElement);
//           });

//           // Ensure the modal stays open (if using Bootstrap modal)
//           $('#myModal').modal('show');
//       } else {
//           // Close the modal and maybe display a success message or redirect
//           $('#myModal').modal('hide');
//           // Redirect or show success message
//           window.location.href = '/client';
//       }
//   })
//   .catch(error => console.error('Error:', error));
// });

