// DOM elementi
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navMenu = document.getElementById('navMenu');
const navLinks = document.querySelectorAll('.nav-link');
const pages = document.querySelectorAll('.page');
const fitnessForm = document.getElementById('fitnessForm');
const questionnaireResult = document.getElementById('questionnaireResult');
const joinBtn = document.getElementById('joinBtn');
const registerForm = document.getElementById('registerForm');
const API_URL = 'http://127.0.0.1:5000/api'
        
    // Funkcija za prebacivanje stranica
function showPage(pageId) {
    // Sakrij sve stranice
    pages.forEach(page => {
        page.classList.remove('active');
    });
    
    // Pokaži odabranu stranicu
    document.getElementById(pageId).classList.add('active');
    
    // Ažuriraj aktivni link u navigaciji
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === pageId) {
            link.classList.add('active');
        }
    });
    
    // Zatvori mobilni meni ako je otvoren
    navMenu.classList.remove('active');
}

// Dodaj event listener-e za navigacione linkove
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const pageId = link.getAttribute('data-page');
        showPage(pageId);
    });
});

// Mobilni meni
mobileMenuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('active');
});

// Dugme za pridruživanje
joinBtn.addEventListener('click', (e) => {
    e.preventDefault();
    showPage('pricing');
});

// Obrada forme upitnika
fitnessForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Prikupljanje podataka iz forme
    const firstName = fitnessForm.elements["firstName"].value;
    const lastName = fitnessForm.elements["lastName"].value;
    const age = fitnessForm.elements["age"].value;
    const height = fitnessForm.elements["height"].value;
    const weight = fitnessForm.elements["weight"].value;
    
    const experience = document.querySelector('input[name="experience"]:checked');
    const activity = document.querySelector('input[name="activity"]:checked');
    const goals = document.querySelectorAll('input[name="goal"]:checked');
    
    // Validacija
    if (!experience || !activity || goals.length === 0) {
        questionnaireResult.textContent = "Molimo popunite sva obavezna polja.";
        questionnaireResult.style.backgroundColor = "#f8d7da";
        questionnaireResult.style.color = "#721c24";
        questionnaireResult.style.display = "block";
        return;
    }
    
    // Priprema ciljeva kao string
    const goalValues = Array.from(goals).map(goal => goal.value);
    let goalText = "";
    if (goalValues.includes("lose_weight") && goalValues.includes("gain_muscle")) {
        goalText = "Želite da istovremeno smršate i dobijete mišićnu masu";
    } else if (goalValues.includes("lose_weight")) {
        goalText = "Vaš primarni cilj je mršavljenje";
    } else if (goalValues.includes("gain_muscle")) {
        goalText = "Vaš primarni cilj je dobijanje mišićne mase";
    } else {
        goalText = "Vaš cilj je " + goalValues.join(", ");
    }
    
    try {
        const response = await fetch(`${API_URL}/questionnaire`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                firstName: firstName,
                lastName: lastName,
                age: parseInt(age),
                height: parseFloat(height),
                weight: parseFloat(weight),
                experience: experience.value,
                activityLevel: activity.value,
                goals: goalValues,
                notes: document.getElementById('notes').value
            })
        });
        
        const data = await response.json();
        console.log('Odgovor od servera:', data)

        if (data.success) {
            // Prikaži poruku sa podacima iz backenda
            questionnaireResult.innerHTML = `
                <h3>Hvala ${firstName} ${lastName}!</h3>
                <p>Vaš BMI iznosi: <strong>${data.data.bmi}</strong> (${data.data.bmi_category})</p>
                <p>${data.data.personal_message}</p>
                <p>Kontaktiraćemo vas u roku od 24 sata sa personalizovanim planom.</p>
            `;
            questionnaireResult.style.backgroundColor = "#d4edda";
            questionnaireResult.style.color = "#155724";
            
            // Resetuj formu
            fitnessForm.reset();
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        questionnaireResult.innerHTML = `
            <p>Došlo je do greške: ${error.message}</p>
            <p>Molimo pokušajte ponovo ili nas kontaktirajte telefonom.</p>
        `;
        questionnaireResult.style.backgroundColor = "#f8d7da";
        questionnaireResult.style.color = "#721c24";
    }
    
    questionnaireResult.style.display = "block";
    questionnaireResult.scrollIntoView({ behavior: 'smooth' });         
    
    // Resetovanje forme
    fitnessForm.reset();

});


// ========== AUTHENTIFIKACIJA ==========

if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const registerResult = document.getElementById('registerResult');
        
        // Prikupljanje podataka
        const data = {
            firstName: registerForm.elements["firstName"].value,
            lastName: registerForm.elements["lastName"].value,
            email: registerForm.elements["email"].value,
            password: registerForm.elements["password"].value,
            phone: registerForm.elements["phone"].value || ''
        };
        // Validacija lozinke
        if (data.password.length < 6) {
            registerResult.innerHTML = `
                <div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px;">
                    ❌ Lozinka mora imati najmanje 6 karaktera.
                </div>
            `;
            registerResult.style.display = 'block';
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Sačuvaj token u localStorage
                localStorage.setItem('token', result.data.token);
                localStorage.setItem('user', JSON.stringify(result.data.user));
                
                registerResult.innerHTML = `
                    <div style="background: #d4edda; color: #155724; padding: 20px; border-radius: 4px;">
                        <h3 style="margin-bottom: 10px;">✅ Uspešna registracija!</h3>
                        <p>Dobrodošli, ${result.data.user.first_name}!</p>
                        <p>Vaš token je sačuvan. Možete nastaviti sa popunjavanjem upitnika.</p>
                        <a href="index.html" class="btn" style="margin-top: 15px; display: inline-block;">Idi na početnu</a>
                        <a href="#" id="goToQuestionnaire" class="btn btn-secondary" style="margin-top: 15px; margin-left: 10px; display: inline-block;">Popuni upitnik</a>
                    </div>
                `;
                
                const goToQuestionnaireBtn = document.getElementById('goToQuestionnaire');

                goToQuestionnaireBtn.addEventListener('click', (e) => {
                    e.preventDefault(); // Sprečava reload stranice
                    showPage('questionnaire'); // Prikazuje sekciju sa upitnikom
                });

                // Resetuj formu
                registerForm.reset();
            } else {
                registerResult.innerHTML = `
                    <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px;">
                        ❌ Greška: ${result.message}
                    </div>
                `;
            }
        } catch (error) {
            registerResult.innerHTML = `
                <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px;">
                    ❌ Greška pri povezivanju sa serverom: ${error.message}<br>
                    Proverite da li je backend pokrenut na portu 5000.
                </div>
            `;
        }
        
        registerResult.style.display = 'block';
        registerResult.scrollIntoView({ behavior: 'smooth' });
    });
}

// Login forma (ako je napravimo kasnije)
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const loginResult = document.getElementById('loginResult');
        
        const data = {
            email: loginForm.elements["email"].value,
            password: loginForm.elements["password"].value
        };
        
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                localStorage.setItem('token', result.data.token);
                localStorage.setItem('user', JSON.stringify(result.data.user));
                
                loginResult.innerHTML = `
                    <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 4px;">
                        ✅ Uspešna prijava! Dobrodošli, ${result.data.user.first_name}!
                    </div>
                `;
                
                // Preusmeri na početnu posle 2 sekunde
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);
            } else {
                loginResult.innerHTML = `
                    <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px;">
                        ❌ Greška: ${result.message}
                    </div>
                `;
            }
        } catch (error) {
            loginResult.innerHTML = `
                <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px;">
                    ❌ Greška pri povezivanju: ${error.message}
                </div>
            `;
        }
        
        loginResult.style.display = 'block';
    });
}

// Funkcija za proveru da li je korisnik ulogovan
function isLoggedIn() {
    return localStorage.getItem('token') !== null;
}

// Funkcija za dobijanje tokena
function getToken() {
    return localStorage.getItem('token');
}

// Funkcija za odjavu
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

// Prikaz korisničkog menija u navigaciji (ako je ulogovan)
function updateNavForUser() {
    const navMenu = document.getElementById('navMenu');
    if (!navMenu) return;
    
    if (isLoggedIn()) {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        
        // Proveri da li već postoji dugme za odjavu
        if (!document.getElementById('logoutBtn')) {
            const li = document.createElement('li');
            li.innerHTML = `<a href="#" id="logoutBtn" class="nav-link">Odjava (${user.firstName || user.first_name})</a>`;
            navMenu.appendChild(li);
            
            document.getElementById('logoutBtn').addEventListener('click', (e) => {
                e.preventDefault();
                logout();
            });
        }
    }
}

// Pozovi funkciju kada se učita stranica
document.addEventListener('DOMContentLoaded', updateNavForUser);

// Inicijalizacija - pokaži početnu stranicu
showPage('home');