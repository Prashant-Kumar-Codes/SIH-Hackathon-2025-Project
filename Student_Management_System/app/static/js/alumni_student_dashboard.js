// ===================================================================
// MAIN APPLICATION ENTRY POINT (Runs after all HTML is loaded)
// ===================================================================

document.addEventListener('DOMContentLoaded', () => {
    
    // --- GLOBAL ELEMENTS & UTILITIES ---
    
    const navBtns = document.querySelectorAll('.nav-btn');
    const pages = document.querySelectorAll('.page');
    const sidebar = document.getElementById('sidebar');
    const hamburger = document.getElementById('hamburger');
    const modalBack = document.getElementById('modalBack');
    const profileForm = document.getElementById('profileForm');

    // CONFIGURATION: Set the maximum limits for chip lists
    const LIMITS = {
        educationList: 5,
        skillList: 10,
        traitsList: 10,
        interestList: 10
    };
    
    // FUNCTION: Toggles visibility of SPA pages and sets active state on nav buttons.
    function showPage(id){
        pages.forEach(p => {
            if (p.id === id) {
                // Use 'flex' for the profile page layout, 'block' for others
                p.style.display = (p.id === 'profile') ? 'flex' : 'block'; 
            } else {
                p.style.display = 'none';
            }
        });
        navBtns.forEach(b => {
            if (b.dataset.target === id) b.classList.add('active'); else b.classList.remove('active');
        });
        
        // Close mobile sidebar after navigation
        if (sidebar) sidebar.classList.remove('open');
        window.scrollTo(0, 0);
    }
    
    // FUNCTION: Creates and appends a removable chip element, respecting the limit.
    function createChip(listId, value) {
        const list = document.getElementById(listId);
        if (!list) return;

        // --- LIMIT CHECK ---
        if (list.children.length >= LIMITS[listId]) {
            alert(`You can only add a maximum of ${LIMITS[listId]} entries for this section.`);
            return; 
        }

        const li = document.createElement('li');
        li.className = 'chip';
        li.appendChild(document.createTextNode(value)); 

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.innerHTML = '×';
        removeBtn.addEventListener('click', () => li.remove());

        li.appendChild(removeBtn);
        list.appendChild(li);
    }

    // FUNCTION: Prompts user for a single text value and adds it as a chip 
    function addChipFromPrompt(listId, promptText) {
        const value = prompt(promptText);
        if (value && value.trim()) { 
            createChip(listId, value.trim());
        }
    }
    
    // --- EDUCATION LOGIC (NEW) ---
    /**
     * Prompts user for three pieces of education data and creates a structured chip.
     */
    function addEducationFromPrompt() {
        const listId = 'educationList';
        if (document.getElementById(listId).children.length >= LIMITS[listId]) {
            alert(`You can only add a maximum of ${LIMITS[listId]} education entries.`);
            return; 
        }

        const institute = prompt("Enter Institute Name:");
        if (!institute || !institute.trim()) return;

        const marks = prompt("Enter Marks (e.g., 90% or 8.5 CGPA):");
        if (!marks || !marks.trim()) return;
        
        const year = prompt("Enter Passing Year (e.g., 2025):");
        if (!year || !year.trim()) return;

        // Combine them into a single string for the chip display and later JSON extraction
        const combinedValue = `${institute.trim()} | ${marks.trim()} | ${year.trim()}`;
        createChip(listId, combinedValue);
    }

    /** * FUNCTION: Extracts chip text values and updates the hidden input field for Flask submission.
     * The server-side Flask route must read the hidden input field (e.g., 'interests_data')
     * and use Python's 'json.loads(request.form['interests_data'])' to convert the JSON string back into a Python list.
     */
    function gatherChipData(listId, hiddenInputId) {
        const list = document.getElementById(listId);
        const hiddenInput = document.getElementById(hiddenInputId);
        
        if (!list || !hiddenInput) return;

        const chipElements = list.querySelectorAll('.chip');
        const dataArray = Array.from(chipElements).map(chip => {
            // Get the text content, excluding the button's '×'
            let text = chip.firstChild ? chip.firstChild.textContent.trim() : chip.textContent.trim();
            if (chip.querySelector('button')) {
                text = chip.textContent.replace(chip.querySelector('button').textContent, '').trim();
            }
            return text;
        });
        
        // Set the hidden input value to a JSON string
        hiddenInput.value = JSON.stringify(dataArray);
    }

    
    // --- INITIALIZATION AND LISTENERS ---
    
    // Default page on load
    showPage('home'); 

    // SPA Navigation Listeners
    navBtns.forEach(b => {
        b.addEventListener('click', () => {
            const t = b.dataset.target;
            showPage(t);
        });
    });

    // HAMBURGER FIX: Toggles the mobile sidebar class 'open'
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            if (sidebar) sidebar.classList.toggle('open');
        });
    }
    
    // CHIP LOGIC: Listeners for adding new entries
    const addEducationBtn = document.getElementById('addEducationBtn');
    const addTraitBtn = document.getElementById('addTraitBtn'); // New button
    const addInterestBtn = document.getElementById('addInterestBtn');
    const addSkillBtn = document.getElementById('addSkillBtn');
    
    // Education Listener (NEW)
    if (addEducationBtn) {
        addEducationBtn.addEventListener('click', addEducationFromPrompt);
    }

    // Trait Listener (NEW)
    if (addTraitBtn) {
        addTraitBtn.addEventListener('click', () => addChipFromPrompt('traitsList', 'Enter a character trait (Limit 10):'));
    }

    // Interest Listener
    if (addInterestBtn) {
        addInterestBtn.addEventListener('click', () => addChipFromPrompt('interestList', 'Enter an interest (Limit 10):'));
    }

    // Skill Listener
    if (addSkillBtn) {
        addSkillBtn.addEventListener('click', () => addChipFromPrompt('skillList', 'Enter a skill (Limit 10):'));
    }

    // CHIP LOGIC: Make existing chips (from Jinja) removable
    document.querySelectorAll('.chip-list .chip button').forEach(button => {
        button.addEventListener('click', (event) => {
            event.target.closest('.chip').remove();
        });
    });

    // PROFILE FORM Submission Handler
    if (profileForm) {
        profileForm.addEventListener('submit', function(e){
            e.preventDefault(); 

            // 1. CRITICAL STEP: Gather the dynamic chip data before submitting
            gatherChipData('educationList', 'education_hidden_input'); // NEW
            gatherChipData('traitsList', 'traits_hidden_input'); // NEW
            gatherChipData('interestList', 'interests_hidden_input');
            gatherChipData('skillList', 'skills_hidden_input');
            
            // 2. DEMO: Live update the profile cards (Simplified)
            const name = document.getElementById('fullName').value;
            const role = document.getElementById('curr_role').value;

            // Update Home page profile card
            if (document.getElementById('profile-name')) document.getElementById('profile-name').textContent = name;
            if (document.getElementById('profile-role')) document.getElementById('profile-role').textContent = role;
            
            alert('Profile data (including Education, Traits, Interests, Skills) gathered and form submission simulated!');

            /** * FLASK CODE HERE: After gathering chip data, remove the e.preventDefault()
             * and let the form submit, OR use 'fetch' to submit the data via AJAX.
             */
        });
    }
    
    // --- Existing Dashboard Listeners (Keep as-is) ---
    
    // ... (All other existing listeners like contactBtn, consultBtn, exportCsv, etc. remain here)

    const consultBtn = document.getElementById('consultBtn');
    const cancelModal = document.getElementById('cancelModal');
    const sendConsult = document.getElementById('sendConsult');
    
    if (consultBtn && modalBack) consultBtn.addEventListener('click', () => modalBack.style.display='flex');
    if (cancelModal && modalBack) cancelModal.addEventListener('click', () => modalBack.style.display='none');
    
    if (sendConsult && modalBack) {
        sendConsult.addEventListener('click', () => {
            const name = document.getElementById('cname').value || 'Anonymous';
            const email = document.getElementById('cemail').value || 'not-provided';
            // const msg = document.getElementById('cmsg').value || ''; // msg not used in alert but kept for logic clarity
            
            alert('Consultation request sent!\nName: ' + name + '\nEmail: ' + email);
            modalBack.style.display = 'none';
            document.getElementById('cname').value = ''; 
            document.getElementById('cemail').value = ''; 
            document.getElementById('cmsg').value = '';
        });
    }


    // Logout confirm
    const confirmLogout = document.getElementById('confirmLogout');
    const cancelLogout = document.getElementById('cancelLogout');
    if (confirmLogout) {
        confirmLogout.addEventListener('click', () => {
            // Simulate logout
            document.body.innerHTML = '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#04101a,#071327);color:#eaf6fb"><div style="text-align:center"><h2>Logged out</h2><p class="muted-2">You have been logged out. Close window or <a href="#" id="backTo">return</a>.</p></div></div>';
        });
    }
    if (cancelLogout) cancelLogout.addEventListener('click', () => showPage('home'));


    // Avatar logic (must be run after elements are loaded)
    const avatarImg = document.getElementById('avatar-img');
    const avatarInitials = document.getElementById('avatar-initials');
    function setAvatar(imageUrl, name){
        if(avatarImg && avatarInitials){
            if(imageUrl){
                avatarImg.src = imageUrl;
                avatarImg.style.display = 'block';
                avatarInitials.style.display = 'none';
            } else {
                avatarImg.style.display = 'none';
                avatarInitials.textContent = (name ? name.split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase() : 'A');
                avatarInitials.style.display = 'flex'; // Use flex for centering initials
            }
        }
    }
    setAvatar('', 'Anjali Singh'); // Initial call


    // Skill bar animation (runs for visual flair)
    setTimeout(() => {
        document.querySelectorAll('.progress > i').forEach(el => {
            const w = el.style.width;
            el.style.width = '0';
            requestAnimationFrame(() => requestAnimationFrame(() => el.style.width = w));
        });
    }, 100); 
    
});