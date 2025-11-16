// ==========================================
// MENU PAGE - Category Filter Functionality
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // Get all category buttons and menu cards
    const categoryButtons = document.querySelectorAll('.category-btn');
    const menuCards = document.querySelectorAll('.menu-card');

    // Add click event to each category button
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get selected category
            const selectedCategory = this.getAttribute('data-category');
            
            // Filter menu cards
            menuCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');
                
                if (selectedCategory === 'all' || cardCategory === selectedCategory) {
                    card.style.display = 'flex';
                    // Add fade in animation
                    card.style.animation = 'fadeInUp 0.5s ease-out';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // ==========================================
    // DETAIL BUTTON - REDIRECT TO CHECKOUT
    // ==========================================
    const detailButtons = document.querySelectorAll('.btn-detail');
    detailButtons.forEach(button => {
        button.addEventListener('click', function() {
            const menuCard = this.closest('.menu-card');
            const menuTitle = menuCard.querySelector('.menu-title').textContent;
            const menuPrice = menuCard.querySelector('.menu-price').textContent;
            const menuImage = menuCard.querySelector('.menu-image img').getAttribute('src');
            const menuCategory = menuCard.getAttribute('data-category');
            
            // Create menu data object
            const menuData = {
                title: menuTitle,
                price: menuPrice,
                image: menuImage,
                category: menuCategory
            };
            
            // Save to sessionStorage
            sessionStorage.setItem('selectedMenu', JSON.stringify(menuData));
            
            // Redirect to checkout page
            window.location.href = 'product.html';
        });
    });

    // ==========================================
    // SEARCH FUNCTIONALITY
    // ==========================================
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            menuCards.forEach(card => {
                const menuTitle = card.querySelector('.menu-title').textContent.toLowerCase();
                
                if (menuTitle.includes(searchTerm)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Reset category filter if searching
            if (searchTerm) {
                categoryButtons.forEach(btn => btn.classList.remove('active'));
            }
        });
    }

    // ==========================================
    // VOICE BUTTON PLACEHOLDER
    // ==========================================
    const voiceBtn = document.querySelector('.voice-btn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', function() {
            alert('Fitur pencarian suara akan segera hadir!');
        });
    }
});