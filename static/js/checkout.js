// ==========================================
// CHECKOUT PAGE - Enhanced with Dynamic Pricing & Cart Integration
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // ==========================================
    // STATE VARIABLES
    // ==========================================
    let quantity = 20;
    let pricePerPortion = 0;
    let selectedPriceOption = '10-50';
    let userLocation = null;
    
    // ==========================================
    // GET DOM ELEMENTS
    // ==========================================
    const quantityInput = document.getElementById('quantityInput');
    const increaseBtn = document.getElementById('increaseBtn');
    const decreaseBtn = document.getElementById('decreaseBtn');
    const pricePerPortionEl = document.getElementById('pricePerPortion');
    const totalPortionsEl = document.getElementById('totalPortions');
    const totalPriceEl = document.getElementById('totalPrice');
    const priceOptions = document.querySelectorAll('.price-option');
    const orderBtn = document.getElementById('orderBtn');
    const deliveryDate = document.getElementById('deliveryDate');
    const deliveryLocation = document.getElementById('deliveryLocation');
    const detailAddress = document.getElementById('detailAddress');
    const detectLocationBtn = document.getElementById('detectLocationBtn');
    const productTitle = document.querySelector('.product-title');
    const hiddenPrice = document.getElementById('hiddenPrice');
    const addToCartBtn = document.getElementById('addToCartBtn');
    const checkoutDirectBtn = document.getElementById('checkoutDirectBtn');

    // ==========================================
    // INITIALIZE PRICE FROM ACTIVE OPTION
    // ==========================================
    function initializePrice() {
        const activeOption = document.querySelector('.price-option.active');
        if (activeOption) {
            pricePerPortion = parseInt(activeOption.getAttribute('data-price'));
            selectedPriceOption = activeOption.getAttribute('data-portions') || '10-50';
            console.log('Initialized price:', pricePerPortion, 'Range:', selectedPriceOption);
            updateSummary();
        }
    }

    // ==========================================
    // GEOLOCATION - DETECT USER LOCATION
    // ==========================================
    if (detectLocationBtn) {
        detectLocationBtn.addEventListener('click', function() {
            if (!navigator.geolocation) {
                showNotification('⚠️ Browser Anda tidak mendukung deteksi lokasi');
                return;
            }

            // Show loading state
            deliveryLocation.value = 'Mendeteksi lokasi...';
            deliveryLocation.classList.add('loading');
            detectLocationBtn.classList.add('loading');
            detectLocationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            navigator.geolocation.getCurrentPosition(
                // Success callback
                function(position) {
                    userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };

                    console.log('User location:', userLocation);

                    // Use Nominatim (OpenStreetMap) for reverse geocoding
                    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${userLocation.lat}&lon=${userLocation.lng}&format=json`)
                        .then(response => response.json())
                        .then(data => {
                            let address = '';
                            
                            if (data.address) {
                                const parts = [];
                                if (data.address.road) parts.push(data.address.road);
                                if (data.address.suburb) parts.push(data.address.suburb);
                                if (data.address.city_district) parts.push(data.address.city_district);
                                if (data.address.city) parts.push(data.address.city);
                                if (data.address.state) parts.push(data.address.state);
                                
                                address = parts.join(', ');
                            }

                            if (!address) {
                                address = data.display_name || 'Lokasi terdeteksi';
                            }

                            deliveryLocation.value = address;
                            deliveryLocation.classList.remove('loading');
                            detectLocationBtn.classList.remove('loading');
                            detectLocationBtn.innerHTML = '<i class="fas fa-check"></i>';
                            
                            setTimeout(() => {
                                detectLocationBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                            }, 2000);

                            showNotification('✅ Lokasi berhasil terdeteksi!');
                        })
                        .catch(error => {
                            console.error('Geocoding error:', error);
                            deliveryLocation.value = `Koordinat: ${userLocation.lat.toFixed(6)}, ${userLocation.lng.toFixed(6)}`;
                            deliveryLocation.classList.remove('loading');
                            detectLocationBtn.classList.remove('loading');
                            detectLocationBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                            showNotification('⚠️ Lokasi terdeteksi, silakan isi alamat detail');
                        });
                },
                // Error callback
                function(error) {
                    deliveryLocation.value = '';
                    deliveryLocation.classList.remove('loading');
                    detectLocationBtn.classList.remove('loading');
                    detectLocationBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';

                    let errorMsg = '⚠️ ';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg += 'Akses lokasi ditolak. Mohon izinkan akses lokasi di browser Anda.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg += 'Informasi lokasi tidak tersedia.';
                            break;
                        case error.TIMEOUT:
                            errorMsg += 'Request timeout. Coba lagi.';
                            break;
                        default:
                            errorMsg += 'Terjadi kesalahan saat mendeteksi lokasi.';
                    }
                    showNotification(errorMsg);
                },
                // Options
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }

    // ==========================================
    // PRICE OPTION SELECTION
    // ==========================================
    priceOptions.forEach(option => {
        option.addEventListener('click', function() {
            priceOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            pricePerPortion = parseInt(this.getAttribute('data-price'));
            selectedPriceOption = this.getAttribute('data-portions');
            
            console.log('Price option changed:', pricePerPortion, 'Range:', selectedPriceOption);
            
            // Update hidden input
            if (hiddenPrice) {
                hiddenPrice.value = pricePerPortion;
            }
            
            updateSummary();
            validateQuantityRange();
        });
    });

    // ==========================================
    // QUANTITY CONTROLS
    // ==========================================
    if (increaseBtn) {
        increaseBtn.addEventListener('click', function() {
            quantity++;
            quantityInput.value = quantity;
            updateSummary();
            validateQuantityRange();
        });
    }

    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function() {
            if (quantity > 1) {
                quantity--;
                quantityInput.value = quantity;
                updateSummary();
                validateQuantityRange();
            }
        });
    }

    // Manual input
    if (quantityInput) {
        quantityInput.addEventListener('focus', function() {
            this.select();
        });

        quantityInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
            
            if (this.value !== '') {
                let value = parseInt(this.value);
                if (value > 0) {
                    quantity = value;
                    updateSummary();
                    validateQuantityRange();
                }
            }
        });

        quantityInput.addEventListener('blur', function() {
            if (!this.value || parseInt(this.value) < 1) {
                quantity = 1;
                this.value = 1;
                updateSummary();
            }
        });

        quantityInput.addEventListener('keypress', function(e) {
            const charCode = e.which ? e.which : e.keyCode;
            if (charCode > 31 && (charCode < 48 || charCode > 57)) {
                e.preventDefault();
                return false;
            }
        });
    }

    // ==========================================
    // UPDATE SUMMARY FUNCTION
    // ==========================================
    function updateSummary() {
        if (pricePerPortionEl) {
            pricePerPortionEl.textContent = formatRupiah(pricePerPortion);
        }
        if (totalPortionsEl) {
            totalPortionsEl.textContent = `${quantity} porsi`;
        }
        const total = quantity * pricePerPortion;
        if (totalPriceEl) {
            totalPriceEl.textContent = formatRupiah(total);
        }
    }

    // ==========================================
    // VALIDATE QUANTITY RANGE
    // ==========================================
    function validateQuantityRange() {
        let message = '';
        let isValid = true;
        
        if (selectedPriceOption === '10-50') {
            if (quantity < 10) {
                message = '💡 Minimal pemesanan 10 porsi untuk harga ini';
                isValid = false;
            } else if (quantity > 50) {
                message = '💡 Untuk pemesanan >50 porsi, pilih harga yang lebih murah!';
                isValid = false;
            }
        } else if (selectedPriceOption === '50-150') {
            if (quantity < 50) {
                message = '💡 Minimal 50 porsi untuk harga ini. Pilih harga untuk 10-50 porsi.';
                isValid = false;
            } else if (quantity > 150) {
                message = '💡 Untuk pemesanan >150 porsi, pilih harga yang lebih murah!';
                isValid = false;
            }
        } else if (selectedPriceOption === '>151') {
            if (quantity <= 150) {
                message = '💡 Minimal 151 porsi untuk harga ini. Pilih harga untuk 50-150 porsi.';
                isValid = false;
            }
        }
        
        if (!isValid && message) {
            showNotification(message);
        }
        
        return isValid;
    }

    // ==========================================
    // FORMAT RUPIAH
    // ==========================================
    function formatRupiah(number) {
        return 'Rp ' + number.toLocaleString('id-ID');
    }

    // ==========================================
    // NOTIFICATION FUNCTION
    // ==========================================
    function showNotification(message) {
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #C4551A;
                color: white;
                padding: 15px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                z-index: 9999;
                font-family: 'Poppins', sans-serif;
                font-size: 14px;
                font-weight: 500;
                max-width: 350px;
                opacity: 0;
                transform: translateX(400px);
                transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            `;
            document.body.appendChild(notification);
        }

        notification.textContent = message;
        
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(400px)';
        }, 4000);
    }

    // ==========================================
    // ADD TO CART BUTTON HANDLER
    // ==========================================
    if (addToCartBtn) {
        console.log('Add to Cart button found'); // ✅ Debug log
        
        addToCartBtn.addEventListener('click', function(e) {
            e.preventDefault(); // ✅ Prevent default behavior
            
            console.log('Add to Cart button clicked'); // ✅ Debug log
            console.log('Current quantity:', quantity);
            console.log('Current price:', pricePerPortion);
            console.log('Selected range:', selectedPriceOption);
            
            // Validate quantity
            if (quantity < 10) {
                showNotification('⚠️ Minimal pemesanan 10 porsi!');
                return;
            }
            
            // Validate quantity range
            if (!validateQuantityRange()) {
                return;
            }
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            if (!csrfToken) {
                showNotification('❌ Error: CSRF token tidak ditemukan');
                console.error('CSRF token not found');
                return;
            }
            
            console.log('CSRF token found:', csrfToken.value.substring(0, 10) + '...'); // ✅ Debug log
            
            // Buat FormData
            const formData = new FormData();
            formData.append('quantity', quantity);
            formData.append('price_per_portion', pricePerPortion);
            formData.append('notes', detailAddress ? detailAddress.value : '');
            formData.append('csrfmiddlewaretoken', csrfToken.value);
            
            // Show loading
            addToCartBtn.disabled = true;
            const originalHTML = addToCartBtn.innerHTML;
            addToCartBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Menambahkan...';
            
            // Ambil product_id dari URL
            const pathArray = window.location.pathname.split('/');
            const productIdIndex = pathArray.indexOf('checkout') + 1;
            const productId = pathArray[productIdIndex];
            
            console.log('URL path:', window.location.pathname); // ✅ Debug log
            console.log('Product ID:', productId); // ✅ Debug log
            
            if (!productId || productId === '') {
                showNotification('❌ Error: Product ID tidak ditemukan');
                console.error('Product ID not found in URL');
                addToCartBtn.disabled = false;
                addToCartBtn.innerHTML = originalHTML;
                return;
            }
            
            const url = `/cart/add/${productId}/`;
            console.log('Fetching URL:', url); // ✅ Debug log
            
            // Kirim ke server
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('Response status:', response.status); // ✅ Debug log
                console.log('Response OK:', response.ok); // ✅ Debug log
                
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Request failed with status ' + response.status);
                }
            })
            .then(data => {
                console.log('Response data:', data); // ✅ Debug log
                showNotification('✅ Produk berhasil ditambahkan ke keranjang!');
                
                // Update cart badge
                if (typeof updateCartBadge === 'function') {
                    console.log('Updating cart badge...');
                    setTimeout(updateCartBadge, 500);
                } else {
                    console.warn('updateCartBadge function not found');
                }
                
                // Reset button
                addToCartBtn.disabled = false;
                addToCartBtn.innerHTML = originalHTML;
                
                // Redirect ke cart setelah 1.5 detik
                setTimeout(() => {
                    console.log('Redirecting to cart...');
                    window.location.href = '/cart/';
                }, 1500);
            })
            .catch(error => {
                console.error('Error:', error); // ✅ Debug log
                showNotification('❌ Gagal menambahkan ke keranjang. Silakan coba lagi.');
                addToCartBtn.disabled = false;
                addToCartBtn.innerHTML = originalHTML;
            });
        });
    } else {
        console.error('Add to Cart button NOT found'); // ✅ Debug log
    }

    // ==========================================
    // WHATSAPP ORDER BUTTON
    // ==========================================
    if (orderBtn) {
        console.log('WhatsApp order button found'); // ✅ Debug log
        
        orderBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            console.log('WhatsApp button clicked');
            
            // Validate quantity range
            if (!validateQuantityRange()) {
                return;
            }

            // Format date
            let formattedDate = 'Belum ditentukan';
            if (deliveryDate && deliveryDate.value) {
                const dateObj = new Date(deliveryDate.value);
                const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                formattedDate = dateObj.toLocaleDateString('id-ID', options);
            }

            // Calculate total
            const total = quantity * pricePerPortion;

            // Create WhatsApp message
            const message = `
*PESANAN BARU - DAPOERHUB* 🍽️

📦 *Menu:* ${productTitle ? productTitle.textContent : 'Produk'}
📊 *Jumlah:* ${quantity} porsi
💰 *Harga per porsi:* ${formatRupiah(pricePerPortion)}
💵 *TOTAL:* ${formatRupiah(total)}

📅 *Tanggal Pengantaran:* ${formattedDate}
📍 *Lokasi:* ${deliveryLocation ? deliveryLocation.value : '-'}
🏠 *Alamat Detail:* ${detailAddress ? detailAddress.value : '-'}

Mohon konfirmasi ketersediaan dan detail pembayaran. Terima kasih! 🙏
            `.trim();

            // WhatsApp number
            const whatsappNumber = '6282188436343';
            const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;

            console.log('Opening WhatsApp:', whatsappUrl);

            // Open WhatsApp
            window.open(whatsappUrl, '_blank');
            
            showNotification('✅ Mengarahkan ke WhatsApp...');
        });
    }

    // ==========================================
    // CHECKOUT DIRECT BUTTON
    // ==========================================
    if (checkoutDirectBtn) {
        console.log('Checkout Direct button found'); // ✅ Debug log
        
        checkoutDirectBtn.addEventListener('click', function(e) {
            console.log('Checkout Direct button clicked');
            
            // Validate form
            if (!deliveryDate || !deliveryDate.value) {
                e.preventDefault();
                showNotification('⚠️ Mohon isi tanggal pengantaran');
                deliveryDate.focus();
                return false;
            }

            if (!deliveryLocation || !deliveryLocation.value || deliveryLocation.value === 'Mendeteksi lokasi...') {
                e.preventDefault();
                showNotification('⚠️ Mohon isi atau deteksi lokasi pengantaran');
                deliveryLocation.focus();
                return false;
            }

            if (!detailAddress || !detailAddress.value.trim()) {
                e.preventDefault();
                showNotification('⚠️ Mohon isi alamat detail pengantaran');
                detailAddress.focus();
                return false;
            }

            // Validate quantity
            if (quantity < 10) {
                e.preventDefault();
                showNotification('⚠️ Minimal pemesanan 10 porsi');
                return false;
            }

            // Validate quantity range
            if (!validateQuantityRange()) {
                e.preventDefault();
                return false;
            }

            // Form is valid, let it submit
            showNotification('⏳ Memproses pesanan...');
        });
    }

    // ==========================================
    // SET MINIMUM DATE (TOMORROW)
    // ==========================================
    if (deliveryDate) {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const minDate = tomorrow.toISOString().split('T')[0];
        deliveryDate.setAttribute('min', minDate);
        console.log('Min date set to:', minDate);
    }

    // ==========================================
    // INITIALIZE ON PAGE LOAD
    // ==========================================
    console.log('Checkout.js initialized');
    initializePrice();
    updateSummary();
});

// ==========================================
// RATING STARS FUNCTIONALITY
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    const ratingStars = document.querySelector('.rating-stars');
    
    if (ratingStars) {
        console.log('Rating stars found');
        
        const labels = ratingStars.querySelectorAll('label');
        const inputs = ratingStars.querySelectorAll('input[type="radio"]');
        
        // Function untuk update warna bintang
        function updateStars(rating) {
            labels.forEach((label, index) => {
                const starValue = index + 1;
                
                if (starValue <= rating) {
                    label.style.color = '#FFD700'; // Kuning
                } else {
                    label.style.color = '#E0E0E0'; // Abu-abu
                }
            });
        }
        
        // Reset semua bintang jadi abu-abu dulu
        updateStars(0);
        
        // Cek apakah ada rating yang sudah dipilih (edit review)
        inputs.forEach((input) => {
            if (input.checked) {
                updateStars(parseInt(input.value));
            }
        });
        
        // Hover effect
        labels.forEach((label) => {
            label.addEventListener('mouseenter', function() {
                const starId = this.getAttribute('for');
                const rating = parseInt(starId.replace('star', ''));
                updateStars(rating);
            });
        });
        
        // Ketika mouse keluar dari area rating
        ratingStars.addEventListener('mouseleave', function() {
            let selectedRating = 0;
            inputs.forEach(input => {
                if (input.checked) {
                    selectedRating = parseInt(input.value);
                }
            });
            updateStars(selectedRating);
        });
        
        // Ketika bintang diklik
        inputs.forEach((input) => {
            input.addEventListener('change', function() {
                if (this.checked) {
                    const rating = parseInt(this.value);
                    updateStars(rating);
                }
            });
        });
    }
});