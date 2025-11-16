// ==========================================
// CHECKOUT PAGE - Enhanced with Dynamic Pricing
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // State variables
    let quantity = 20;
    let pricePerPortion = 0; // ✅ Akan diambil dari data-price
    let selectedPriceOption = '10-50';
    let userLocation = null;
    
    // Get DOM elements
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

    // ==========================================
    // INITIALIZE PRICE FROM ACTIVE OPTION
    // ==========================================
    function initializePrice() {
        const activeOption = document.querySelector('.price-option.active');
        if (activeOption) {
            pricePerPortion = parseInt(activeOption.getAttribute('data-price'));
            selectedPriceOption = activeOption.getAttribute('data-portions') || '10-50';
            updateSummary();
        }
    }

    // ==========================================
    // GEOLOCATION - DETECT USER LOCATION
    // ==========================================
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

    // ==========================================
    // PRICE OPTION SELECTION
    // ==========================================
    priceOptions.forEach(option => {
        option.addEventListener('click', function() {
            priceOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            pricePerPortion = parseInt(this.getAttribute('data-price'));
            selectedPriceOption = this.getAttribute('data-portions');
            
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
    increaseBtn.addEventListener('click', function() {
        quantity++;
        quantityInput.value = quantity;
        updateSummary();
        validateQuantityRange();
    });

    decreaseBtn.addEventListener('click', function() {
        if (quantity > 1) {
            quantity--;
            quantityInput.value = quantity;
            updateSummary();
            validateQuantityRange();
        }
    });

    // Manual input
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

    // ==========================================
    // UPDATE FUNCTIONS
    // ==========================================
    function updateSummary() {
        pricePerPortionEl.textContent = formatRupiah(pricePerPortion);
        totalPortionsEl.textContent = `${quantity} porsi`;
        const total = quantity * pricePerPortion;
        totalPriceEl.textContent = formatRupiah(total);
    }

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
    // ORDER BUTTON - WHATSAPP INTEGRATION
    // ==========================================
    orderBtn.addEventListener('click', function() {
        // Validate form
        if (!deliveryDate.value) {
            showNotification('⚠️ Mohon isi tanggal pengantaran');
            deliveryDate.focus();
            return;
        }

        if (!deliveryLocation.value || deliveryLocation.value === 'Mendeteksi lokasi...') {
            showNotification('⚠️ Mohon isi atau deteksi lokasi pengantaran');
            deliveryLocation.focus();
            return;
        }

        if (!detailAddress.value.trim()) {
            showNotification('⚠️ Mohon isi alamat detail pengantaran');
            detailAddress.focus();
            return;
        }

        // Validate quantity range
        if (!validateQuantityRange()) {
            return;
        }

        // Format date
        const dateObj = new Date(deliveryDate.value);
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const formattedDate = dateObj.toLocaleDateString('id-ID', options);

        // Calculate total
        const total = quantity * pricePerPortion;

        // Create WhatsApp message
        const message = `
*PESANAN BARU - DAPOERHUB* 🍽️

📦 *Menu:* ${productTitle.textContent}
📊 *Jumlah:* ${quantity} porsi
💰 *Harga per porsi:* ${formatRupiah(pricePerPortion)}
💵 *TOTAL:* ${formatRupiah(total)}

📅 *Tanggal Pengantaran:* ${formattedDate}
📍 *Lokasi:* ${deliveryLocation.value}
🏠 *Alamat Detail:* ${detailAddress.value}

Mohon konfirmasi ketersediaan dan detail pembayaran. Terima kasih! 🙏
        `.trim();

        // WhatsApp number
        const whatsappNumber = '6285657133691';
        const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;

        // Open WhatsApp
        window.open(whatsappUrl, '_blank');
        
        showNotification('✅ Mengarahkan ke WhatsApp...');
    });

    // ==========================================
    // SET MINIMUM DATE (TOMORROW)
    // ==========================================
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const minDate = tomorrow.toISOString().split('T')[0];
    deliveryDate.setAttribute('min', minDate);

    // ==========================================
    // INITIALIZE
    // ==========================================
    initializePrice();
    updateSummary();
});

// ==========================================
// RATING STARS FUNCTIONALITY
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    const ratingStars = document.querySelector('.rating-stars');
    
    if (ratingStars) {
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