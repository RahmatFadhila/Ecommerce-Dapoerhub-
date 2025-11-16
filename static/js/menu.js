// ==========================================
// MENU PAGE - Enhanced Category Filter
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // Get all category buttons and menu cards
    const categoryButtons = document.querySelectorAll('.category-btn');
    const menuCards = document.querySelectorAll('.menu-card');
    const menuGrid = document.querySelector('.menu-grid');

    // ==========================================
    // CATEGORY FILTER WITH SMOOTH ANIMATION
    // ==========================================
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Prevent multiple clicks
            if (this.classList.contains('filtering')) return;
            
            // Remove active class from all buttons
            categoryButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.classList.remove('filtering');
            });
            
            // Add active and filtering class
            this.classList.add('active', 'filtering');
            
            // Get selected category
            const selectedCategory = this.getAttribute('data-category');
            
            // Add loading effect to grid
            menuGrid.style.opacity = '0.5';
            
            // Filter with delay for smooth transition
            setTimeout(() => {
                let visibleCount = 0;
                
                menuCards.forEach((card, index) => {
                    const cardCategory = card.getAttribute('data-category');
                    
                    if (selectedCategory === 'all' || cardCategory === selectedCategory) {
                        card.style.display = 'flex';
                        
                        // Stagger animation
                        setTimeout(() => {
                            card.style.opacity = '1';
                            card.style.animation = `fadeInUp 0.5s ease-out ${visibleCount * 0.05}s forwards`;
                        }, 50);
                        
                        visibleCount++;
                    } else {
                        card.style.opacity = '0';
                        setTimeout(() => {
                            card.style.display = 'none';
                        }, 300);
                    }
                });
                
                // Remove loading effect
                menuGrid.style.opacity = '1';
                this.classList.remove('filtering');
                
                // Show empty state if no results
                showEmptyState(visibleCount);
            }, 200);
        });
    });

    // ==========================================
    // EMPTY STATE HANDLER
    // ==========================================
    function showEmptyState(count) {
        let emptyState = document.querySelector('.empty-state-filter');
        
        if (count === 0 && menuCards.length > 0) {
            if (!emptyState) {
                emptyState = document.createElement('div');
                emptyState.className = 'empty-state empty-state-filter';
                emptyState.innerHTML = `
                    <div class="empty-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <h3>Kategori Tidak Ditemukan</h3>
                    <p>Tidak ada menu dalam kategori ini</p>
                `;
                menuGrid.appendChild(emptyState);
            }
            emptyState.style.display = 'block';
        } else if (emptyState) {
            emptyState.style.display = 'none';
        }
    }

    // ==========================================
    // LAZY LOADING IMAGES
    // ==========================================
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src || img.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    }, {
        rootMargin: '50px'
    });

    // Observe all menu images
    document.querySelectorAll('.menu-image img').forEach(img => {
        imageObserver.observe(img);
    });

    // ==========================================
    // SMOOTH SCROLL TO TOP ON CATEGORY CHANGE
    // ==========================================
    function smoothScrollToTop() {
        const menuSection = document.querySelector('.menu-section');
        if (menuSection) {
            window.scrollTo({
                top: menuSection.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    }

    // Add scroll to category buttons on mobile
    if (window.innerWidth <= 768) {
        categoryButtons.forEach(button => {
            button.addEventListener('click', smoothScrollToTop);
        });
    }

    // ==========================================
    // PERFORMANCE: DEBOUNCE FUNCTION
    // ==========================================
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // ==========================================
    // SEARCH FUNCTIONALITY (if exists)
    // ==========================================
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const handleSearch = debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            let visibleCount = 0;
            
            menuCards.forEach(card => {
                const menuTitle = card.querySelector('.menu-title').textContent.toLowerCase();
                const menuDesc = card.querySelector('.menu-desc').textContent.toLowerCase();
                const menuCategory = card.querySelector('.menu-category-tag').textContent.toLowerCase();
                
                if (menuTitle.includes(searchTerm) || 
                    menuDesc.includes(searchTerm) || 
                    menuCategory.includes(searchTerm)) {
                    card.style.display = 'flex';
                    card.style.opacity = '1';
                    visibleCount++;
                } else {
                    card.style.opacity = '0';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
            
            // Reset category filter if searching
            if (searchTerm) {
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                document.querySelector('[data-category="all"]')?.classList.add('active');
            }
            
            showEmptyState(visibleCount);
        }, 300);
        
        searchInput.addEventListener('input', handleSearch);
    }

    // ==========================================
    // CART BUTTON ANIMATION (optional enhancement)
    // ==========================================
    const detailButtons = document.querySelectorAll('.btn-detail');
    detailButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // ==========================================
    // TRACK SCROLL FOR ANIMATIONS
    // ==========================================
    let lastScroll = 0;
    const header = document.querySelector('.menu-header');
    
    window.addEventListener('scroll', debounce(function() {
        const currentScroll = window.pageYOffset;
        
        if (header && currentScroll > lastScroll && currentScroll > 100) {
            // Scrolling down
            header.style.transform = 'translateY(-20px)';
            header.style.opacity = '0.7';
        } else {
            // Scrolling up
            header.style.transform = 'translateY(0)';
            header.style.opacity = '1';
        }
        
        lastScroll = currentScroll;
    }, 100));

    // ==========================================
    // CATEGORY FILTER - HORIZONTAL SCROLL INDICATOR
    // ==========================================
    const categoryFilter = document.querySelector('.category-filter');
    if (categoryFilter && window.innerWidth <= 768) {
        // Add scroll shadow indicator
        categoryFilter.addEventListener('scroll', function() {
            if (this.scrollLeft > 10) {
                this.classList.add('scrolled');
            } else {
                this.classList.remove('scrolled');
            }
        });
        
        // Add scroll hint
        if (categoryButtons.length > 3) {
            setTimeout(() => {
                categoryFilter.classList.add('scroll-hint');
                setTimeout(() => {
                    categoryFilter.classList.remove('scroll-hint');
                }, 2000);
            }, 1000);
        }
    }

    // ==========================================
    // ERROR HANDLING FOR IMAGES
    // ==========================================
    document.querySelectorAll('.menu-image img').forEach(img => {
        img.addEventListener('error', function() {
            this.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=400&fit=crop';
            this.alt = 'Gambar tidak tersedia';
        });
    });

    // ==========================================
    // INITIALIZE: Set default state
    // ==========================================
    console.log('✅ Menu page initialized');
    console.log(`📦 Total products: ${menuCards.length}`);
    console.log(`🏷️ Total categories: ${categoryButtons.length - 1}`); // -1 for "all" button
});