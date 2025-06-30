// Custom JavaScript for Supreme Cycle Store

$(document).ready(function() {
    // Initialize page
    initializePage();
    
    // Shopping cart functionality
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    updateCartCounter();
    
    // Add to cart functionality
    $(document).on('click', '.add-to-cart', function(e) {
        e.preventDefault();
        const productId = $(this).data('id');
        const productName = $(this).closest('.product-card, .card-hover').find('h3').text();
        const productPrice = $(this).closest('.product-card, .card-hover').find('.price, .font-bold').text();
        
        addToCart(productId, productName, productPrice);
        showNotification('Product added to cart!', 'success');
    });
    
    // Wishlist functionality
    let wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
    
    $(document).on('click', '.add-to-wishlist', function(e) {
        e.preventDefault();
        const productId = $(this).data('id');
        toggleWishlist(productId, $(this));
    });
    
    // Search functionality
    $('#search-btn').click(function() {
        const searchTerm = $('#search-input').val();
        if (searchTerm) {
            window.location.href = `/search?q=${encodeURIComponent(searchTerm)}`;
        }
    });
    
    $('#search-input').keypress(function(e) {
        if (e.which === 13) {
            $('#search-btn').click();
        }
    });
    
    // Lazy loading for images
    initializeLazyLoading();
    
    // Smooth scroll to top
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            showScrollToTop();
        } else {
            hideScrollToTop();
        }
    });
});

function initializePage() {
    // Add scroll to top button
    if (!$('#scroll-to-top').length) {
        $('body').append(`
            <button id="scroll-to-top" class="fixed bottom-4 right-4 bg-primary text-white p-3 rounded-full shadow-lg z-50 hidden hover:bg-blue-700 transition-colors">
                <i class="fas fa-arrow-up"></i>
            </button>
        `);
        
        $('#scroll-to-top').click(function() {
            $('html, body').animate({scrollTop: 0}, 600);
        });
    }
    
    // Initialize tooltips
    $('[data-tooltip]').each(function() {
        $(this).attr('title', $(this).data('tooltip'));
    });
}

function addToCart(productId, productName, productPrice) {
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: productName,
            price: productPrice,
            quantity: 1
        });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCounter();
}

function updateCartCounter() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    $('.cart-counter').text(totalItems);
}

function toggleWishlist(productId, button) {
    const index = wishlist.indexOf(productId);
    
    if (index > -1) {
        wishlist.splice(index, 1);
        button.find('i').removeClass('fas').addClass('far');
        button.removeClass('text-red-500').addClass('text-gray-500');
        showNotification('Removed from wishlist', 'info');
    } else {
        wishlist.push(productId);
        button.find('i').removeClass('far').addClass('fas');
        button.removeClass('text-gray-500').addClass('text-red-500');
        showNotification('Added to wishlist!', 'success');
    }
    
    localStorage.setItem('wishlist', JSON.stringify(wishlist));
}

function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const notification = $(`
        <div class="fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform">
            <div class="flex items-center">
                <i class="fas fa-check-circle mr-2"></i>
                <span>${message}</span>
            </div>
        </div>
    `);
    
    $('body').append(notification);
    
    setTimeout(() => {
        notification.removeClass('translate-x-full');
    }, 100);
    
    setTimeout(() => {
        notification.addClass('translate-x-full');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

function showScrollToTop() {
    $('#scroll-to-top').removeClass('hidden').addClass('animate-fade-in');
}

function hideScrollToTop() {
    $('#scroll-to-top').addClass('hidden').removeClass('animate-fade-in');
}

// Price formatting
function formatPrice(price) {
    return '₹' + new Intl.NumberFormat('en-IN').format(price);
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[+]?[\d\s\-\(\)]{10,}$/;
    return re.test(phone);
}

// Product filter functionality
function filterProducts(filters) {
    const products = $('.product-item');
    
    products.each(function() {
        const product = $(this);
        let show = true;
        
        // Apply filters
        if (filters.category && product.data('category') !== filters.category) {
            show = false;
        }
        
        if (filters.priceMin && parseFloat(product.data('price')) < filters.priceMin) {
            show = false;
        }
        
        if (filters.priceMax && parseFloat(product.data('price')) > filters.priceMax) {
            show = false;
        }
        
        if (show) {
            product.removeClass('hidden').addClass('animate-fade-in');
        } else {
            product.addClass('hidden').removeClass('animate-fade-in');
        }
    });
}

// Export functions for global use
window.CycleStore = {
    addToCart,
    toggleWishlist,
    showNotification,
    formatPrice,
    validateEmail,
    validatePhone,
    filterProducts
};
