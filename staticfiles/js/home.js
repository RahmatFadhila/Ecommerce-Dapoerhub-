// ==========================================
// HOME PAGE - Product Filter
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    console.log('🔍 Filter Buttons:', filterButtons.length);
    console.log('🔍 Product Cards:', productCards.length);

    // ✅ Pastikan semua produk terlihat saat load
    productCards.forEach(card => {
        card.style.display = 'flex';
        card.style.opacity = '1';
    });

    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filterValue = this.getAttribute('data-filter');
            
            productCards.forEach(card => {
                const category = card.getAttribute('data-category');
                
                if (filterValue === 'all' || category === filterValue) {
                    card.style.display = 'flex';
                    card.style.opacity = '1';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
});
```

### **3. Hard Refresh Browser**
```
Ctrl + Shift + R