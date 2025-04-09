document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const logoutBtn = document.getElementById('logoutBtn');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value
            };

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                
                if (response.ok) {
                    if (data.require_2fa) {
                        // Show 2FA verification input
                        document.getElementById('loginForm').style.display = 'none';
                        document.getElementById('twoFactorForm').style.display = 'block';
                    } else {
                        window.location.href = data.redirect || '/';
                    }
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                const errorDiv = document.getElementById('loginError');
                errorDiv.textContent = error.message;
                errorDiv.style.display = 'block';
            }
        });

        // 2FA Verification Handler
        const verifyLoginBtn = document.getElementById('verifyLoginCode');
        if (verifyLoginBtn) {
            verifyLoginBtn.addEventListener('click', async () => {
                const code = document.getElementById('verificationCode').value;
                try {
                    const response = await fetch('/api/auth/verify-login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                        },
                        body: JSON.stringify({ code })
                    });
                    const data = await response.json();
                    if (response.ok) {
                        window.location.href = data.redirect;
                    } else {
                        throw new Error(data.error);
                    }
                } catch (error) {
                    const errorDiv = document.getElementById('loginError');
                    errorDiv.textContent = error.message;
                    errorDiv.style.display = 'block';
                }
            });
        }
    }

    if (signupForm) {
        function validatePassword(password) {
            const requirements = {
                length: password.length >= 7,
                uppercase: /[A-Z]/.test(password),
                specialOrNumber: /[0-9!@#$%^&*]/.test(password)
            };
            
            if (!requirements.length) {
                throw new Error('Password must be at least 7 characters long');
            }
            if (!requirements.uppercase) {
                throw new Error('Password must contain at least one uppercase letter');
            }
            if (!requirements.specialOrNumber) {
                throw new Error('Password must contain at least one number or special character');
            }
            return true;
        }

        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Signup form submitted');
            
            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                developer_tag: document.getElementById('developer_tag').value
            };
            console.log('Form data prepared:', formData);

            try {
                validatePassword(formData.password);
                console.log('Sending signup request...');
                const response = await fetch('/api/auth/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(formData)
                });
                console.log('Response received:', response);

                const data = await response.json();
                console.log('Response data:', data);
                
                if (response.ok) {
                    window.location.href = data.redirect;
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                console.error('Signup error:', error);
                const errorDiv = document.getElementById('signupError');
                if (errorDiv) {
                    errorDiv.textContent = error.message;
                    errorDiv.style.display = 'block';
                }
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    window.location.href = data.redirect;
                }
            } catch (error) {
                console.error('Logout failed:', error);
            }
        });
    }
});
