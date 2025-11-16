// ==========================================
// CONTACT PAGE - Form Handler
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const contactForm = document.getElementById('contactForm');
    const userName = document.getElementById('userName');
    const userEmail = document.getElementById('userEmail');
    const userMessage = document.getElementById('userMessage');

    // ==========================================
    // FORM SUBMISSION
    // ==========================================
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Get form values
        const name = userName.value.trim();
        const email = userEmail.value.trim();
        const message = userMessage.value.trim();

        // Validate form
        if (!name || !email || !message) {
            showNotification('⚠️ Mohon lengkapi semua field', 'error');
            return;
        }

        // Validate email format
        if (!isValidEmail(email)) {
            showNotification('⚠️ Format email tidak valid', 'error');
            userEmail.focus();
            return;
        }

        // Create WhatsApp message
        const whatsappMessage = `
*PESAN BARU - CONTACT FORM* 📧

👤 *Nama:* ${name}
📧 *Email:* ${email}

💬 *Pesan:*
${message}

---
Dikirim melalui Contact Form DapoerHub
        `.trim();

        // WhatsApp number
        const whatsappNumber = '6285657133691';
        const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(whatsappMessage)}`;

        // Show success notification
        showNotification('✅ Mengarahkan ke WhatsApp...', 'success');

        // Open WhatsApp
        setTimeout(() => {
            window.open(whatsappUrl, '_blank');
            
            // Reset form after sending
            contactForm.reset();
        }, 1000);
    });

    // ==========================================
    // EMAIL VALIDATION
    // ==========================================
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // ==========================================
    // NOTIFICATION FUNCTION
    // ==========================================
    function showNotification(message, type = 'info') {
        let notification = document.getElementById('notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 25px;
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

        // Set color based on type
        if (type === 'success') {
            notification.style.background = '#4CAF50';
            notification.style.color = 'white';
        } else if (type === 'error') {
            notification.style.background = '#f44336';
            notification.style.color = 'white';
        } else {
            notification.style.background = '#C4551A';
            notification.style.color = 'white';
        }

        notification.textContent = message;
        
        // Show notification
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Hide notification
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(400px)';
        }, 4000);
    }

    // ==========================================
    // REAL-TIME EMAIL VALIDATION
    // ==========================================
    userEmail.addEventListener('blur', function() {
        if (this.value.trim() && !isValidEmail(this.value.trim())) {
            this.style.borderColor = '#f44336';
            showNotification('⚠️ Format email tidak valid', 'error');
        } else if (this.value.trim()) {
            this.style.borderColor = '#4CAF50';
        }
    });

    userEmail.addEventListener('focus', function() {
        this.style.borderColor = '';
    });

    // ==========================================
    // INPUT ANIMATIONS
    // ==========================================
    const inputs = document.querySelectorAll('.form-input, .form-textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // ==========================================
    // VOICE BUTTON PLACEHOLDER
    // ==========================================
    const voiceBtn = document.querySelector('.voice-btn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', function() {
            showNotification('🎤 Fitur pencarian suara akan segera hadir!', 'info');
        });
    }

    // ==========================================
    // INFO CARDS CLICK TO COPY
    // ==========================================
    const infoCards = document.querySelectorAll('.info-card');
    infoCards.forEach(card => {
        card.addEventListener('click', function() {
            const text = this.querySelector('.info-text').textContent;
            
            // Copy to clipboard
            navigator.clipboard.writeText(text).then(() => {
                showNotification('📋 Disalin ke clipboard!', 'success');
                
                // Visual feedback
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 200);
            }).catch(() => {
                showNotification('⚠️ Gagal menyalin', 'error');
            });
        });
        
        // Add cursor pointer hint
        card.style.cursor = 'pointer';
        card.title = 'Klik untuk menyalin';
    });
});