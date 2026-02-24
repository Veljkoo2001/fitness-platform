// DOM elementi
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const navMenu = document.getElementById('navMenu');
        const navLinks = document.querySelectorAll('.nav-link');
        const pages = document.querySelectorAll('.page');
        const fitnessForm = document.getElementById('fitnessForm');
        const resultMessage = document.getElementById('resultMessage');
        const joinBtn = document.getElementById('joinBtn');
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
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            const age = document.getElementById('age').value;
            const height = document.getElementById('height').value;
            const weight = document.getElementById('weight').value;
            
            const experience = document.querySelector('input[name="experience"]:checked');
            const activity = document.querySelector('input[name="activity"]:checked');
            const goals = document.querySelectorAll('input[name="goal"]:checked');
            
            // Validacija
            if (!experience || !activity || goals.length === 0) {
                resultMessage.textContent = "Molimo popunite sva obavezna polja.";
                resultMessage.style.backgroundColor = "#f8d7da";
                resultMessage.style.color = "#721c24";
                resultMessage.style.display = "block";
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
                    resultMessage.innerHTML = `
                        <h3>Hvala ${firstName} ${lastName}!</h3>
                        <p>Vaš BMI iznosi: <strong>${data.data.bmi}</strong> (${data.data.bmi_category})</p>
                        <p>${data.data.personal_message}</p>
                        <p>Kontaktiraćemo vas u roku od 24 sata sa personalizovanim planom.</p>
                    `;
                    resultMessage.style.backgroundColor = "#d4edda";
                    resultMessage.style.color = "#155724";
                    
                    // Resetuj formu
                    fitnessForm.reset();
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                resultMessage.innerHTML = `
                    <p>Došlo je do greške: ${error.message}</p>
                    <p>Molimo pokušajte ponovo ili nas kontaktirajte telefonom.</p>
                `;
                resultMessage.style.backgroundColor = "#f8d7da";
                resultMessage.style.color = "#721c24";
            }
            
            resultMessage.style.display = "block";
            resultMessage.scrollIntoView({ behavior: 'smooth' });            

            // Izračunavanje BMI
            const heightInMeters = height / 100;
            const bmi = (weight / (heightInMeters * heightInMeters)).toFixed(1);
            
            // Poruka sa rezultatima
            resultMessage.innerHTML = `
                <h3>Hvala ${firstName} ${lastName}!</h3>
                <p>Primili smo vaš upitnik. Na osnovu unetih podataka:</p>
                <ul style="text-align: left; margin: 10px 0;">
                    <li>Imate ${age} godina</li>
                    <li>Vaš BMI iznosi ${bmi}</li>
                    <li>Nivo iskustva: ${experience.value === 'beginner' ? 'Početnik' : experience.value === 'intermediate' ? 'Srednji nivo' : 'Napredni'}</li>
                    <li>Nivo aktivnosti: ${activity.value === 'sedentary' ? 'Sedentaran' : activity.value === 'moderate' ? 'Umereno aktivan' : 'Veoma aktivan'}</li>
                    <li>${goalText}</li>
                </ul>
                <p>Kontaktiraćemo vas u roku od 24 sata sa personalizovanim planom treninga i ishrane.</p>
            `;
            
            resultMessage.style.backgroundColor = "#d4edda";
            resultMessage.style.color = "#155724";
            resultMessage.style.display = "block";
            
            // Resetovanje forme
            fitnessForm.reset();
            
            // Scroll to result
            resultMessage.scrollIntoView({ behavior: 'smooth' });

        });
        
        // Inicijalizacija - pokaži početnu stranicu
        showPage('home');