document.addEventListener("DOMContentLoaded", function () {

    const showError = (input, message) => {
        const formGroup = input.parentElement;
        
        input.classList.add('is-invalid');
        
        let errorDiv = formGroup.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            formGroup.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
    };

    // po poprawieniu przez uzytkownika clear
    const clearError = (input) => {
        input.classList.remove('is-invalid');
        const formGroup = input.parentElement;
        const errorDiv = formGroup.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove(); // Lub errorDiv.textContent = '';
        }
    };

    // regex dla maila
    const isValidEmail = (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    };

    const isValidPassword = (password) => {
        const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
        return re.test(password);
    };

    // REJESTRACJA
    const passwordConfirmInput = document.querySelector('input[name="password2"]');
    
    if (passwordConfirmInput) {
        const signupForm = passwordConfirmInput.closest('form');
        const usernameInput = signupForm.querySelector('input[name="username"]');
        const emailInput = signupForm.querySelector('input[name="email"]');
        const passwordInput = signupForm.querySelector('input[name="password1"]');

        signupForm.addEventListener('submit', function (e) {
            let isValid = true;

            // walidacja login - min 3 znaki
            if (usernameInput.value.trim().length < 3) {
                showError(usernameInput, "Nazwa użytkownika musi mieć co najmniej 3 znaki.");
                isValid = false;
            } else {
                clearError(usernameInput);
            }

            // walidacja - email
            if (!isValidEmail(emailInput.value.trim())) {
                showError(emailInput, "Wpisz poprawny adres email.");
                isValid = false;
            } else {
                clearError(emailInput);
            }

            // walidacja hasła
            if (!isValidPassword(passwordInput.value)) {
                showError(passwordInput, "Hasło musi mieć min. 8 znaków, dużą literę, małą literę i cyfrę.");
                isValid = false;
            } else {
                clearError(passwordInput);
            }

            // czy hasła są takie same
            if (passwordInput.value !== passwordConfirmInput.value) {
                showError(passwordConfirmInput, "Hasła nie są identyczne.");
                isValid = false;
            } else {
                clearError(passwordConfirmInput);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // --- 4. ANIMACJE REVEAL ON SCROLL ---
    const reveals = document.querySelectorAll(".reveal");

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        const elementVisible = 100; // Jak daleko od dołu element ma się pojawić

        reveals.forEach((reveal) => {
            const elementTop = reveal.getBoundingClientRect().top;
            if (elementTop < windowHeight - elementVisible) {
                reveal.classList.add("active");
            }
        });
    };

    // Nasłuchiwanie scrolla
    window.addEventListener("scroll", revealOnScroll);
    // Wywołanie raz na start (żeby pokazać górne elementy)
    revealOnScroll();
});

