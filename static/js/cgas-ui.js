// CGAS UI Enhancement Script
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Responsive table handling
    const tables = document.querySelectorAll('.table-responsive');
    if (tables.length) {
        tables.forEach(table => {
            // Add shadow indicators for scrollable tables
            table.addEventListener('scroll', function() {
                const maxScrollLeft = this.scrollWidth - this.clientWidth;
                
                if (this.scrollLeft > 0) {
                    this.classList.add('shadow-left');
                } else {
                    this.classList.remove('shadow-left');
                }
                
                if (this.scrollLeft < maxScrollLeft) {
                    this.classList.add('shadow-right');
                } else {
                    this.classList.remove('shadow-right');
                }
            });
            
            // Trigger scroll event once to set initial state
            table.dispatchEvent(new Event('scroll'));
        });
    }
    
    // Enhance form selects with Select2 if available
    if (typeof $.fn.select2 !== 'undefined') {
        $('.select2-enable').select2({
            theme: 'default',
            dropdownParent: $('body')
        });
    }
    
    // Add animation classes to cards
    const cards = document.querySelectorAll('.card');
    if (cards.length) {
        cards.forEach(card => {
            if (!card.classList.contains('no-hover')) {
                card.classList.add('hover-lift');
            }
        });
    }
    
    // Enhance mobile menu behavior
    const navbarToggler = document.querySelector('.navbar-toggler');
    const sidebar = document.querySelector('.sidebar');
    
    if (navbarToggler && sidebar) {
        navbarToggler.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-visible');
        });
    }
    
    // Enhance form validation feedback
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    }
    
    // Get CSRF token - useful for AJAX requests
    window.getCsrfToken = function() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
               document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || 
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    };
});