    // Basic SPA navigation + actions
    const navBtns = document.querySelectorAll('.nav-btn');
    const pages = document.querySelectorAll('.page');
    function showPage(id){
      pages.forEach(p=>{
        p.style.display = (p.id===id)?'block':'none';
      });
      navBtns.forEach(b=>{
        if(b.dataset.target===id) b.classList.add('active'); else b.classList.remove('active');
      });
      // close mobile sidebar
      document.getElementById('sidebar').classList.remove('open');
      window.scrollTo(0,0);
    }
    navBtns.forEach(b=>{
      b.addEventListener('click', e=>{
        const t=b.dataset.target;
        if(t==='logout'){
          showPage('logout');
          return;
        }
        showPage(t);
      });
    });

    // Hamburger toggle for mobile
    document.getElementById('hamburger').addEventListener('click', ()=>{
      document.getElementById('sidebar').classList.toggle('open');
    });

    // Contact button -> mailto
    document.getElementById('contactBtn').addEventListener('click', ()=>{
      window.location.href = 'mailto:support@alumniconnect.org?subject=Contact%20request&body=Hi%20team%2C%0A%0AI%20would%20like%20to%20get%20in%20touch.';
    });

    // Consultation modal
    const modalBack = document.getElementById('modalBack');
    document.getElementById('consultBtn').addEventListener('click', ()=> modalBack.style.display='flex');
    document.getElementById('cancelModal').addEventListener('click', ()=> modalBack.style.display='none');
    document.getElementById('sendConsult').addEventListener('click', ()=>{
      const name = document.getElementById('cname').value || 'Anonymous';
      const email = document.getElementById('cemail').value || 'not-provided';
      const msg = document.getElementById('cmsg').value || '';
      // simple simulated send
      alert('Consultation request sent!\\nName: '+name+'\\nEmail: '+email);
      modalBack.style.display='none';
      document.getElementById('cname').value='';document.getElementById('cemail').value='';document.getElementById('cmsg').value='';
    });

    // Quick action examples
    document.getElementById('create-event').addEventListener('click', ()=>{
      showPage('events');
      alert('Open Events → Click "Create new" to add an event (placeholder).');
    });
    document.getElementById('broadcast').addEventListener('click', ()=> alert('Broadcast feature placeholder'));

    // Logout confirm
    document.getElementById('confirmLogout').addEventListener('click', ()=>{
      // Simulate logout
      document.body.innerHTML = '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#04101a,#071327);color:#eaf6fb"><div style="text-align:center"><h2>Logged out</h2><p class="muted-2">You have been logged out. Close window or <a href="#" id="backTo">return</a>.</p></div></div>';
      // back to dashboard reload on click would be handled by real app
    });
    document.getElementById('cancelLogout').addEventListener('click', ()=> showPage('home'));

    // Export CSV (example: export recent registrations)
    document.getElementById('exportCsv').addEventListener('click', ()=>{
      const rows = [['Name','Batch','Email','Joined'],
        ['Rohit Sharma','2020','rohit@mail.com','2025-08-12'],
        ['Priya Verma','2019','priya@mail.com','2025-08-10'],
        ['Nisha Sandilya','2021','nisha@mail.com','2025-08-03']];
      const csv = rows.map(r=>r.map(cell=>'\"'+String(cell).replace(/\"/g,'\"\"')+'\"').join(',')).join('\\n');
      const blob = new Blob([csv],{type:'text/csv'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href=url; a.download='recent_registrations.csv'; a.click(); URL.revokeObjectURL(url);
    });

    // Directory search filter
    document.getElementById('dirSearch').addEventListener('input', (e)=>{
      const q = e.target.value.toLowerCase();
      const rows = document.querySelectorAll('#dirList tr');
      rows.forEach(r=>{
        const text = r.textContent.toLowerCase();
        r.style.display = text.includes(q)?'table-row':'none';
      });
    });
    document.getElementById('dirClear').addEventListener('click', ()=>{
      document.getElementById('dirSearch').value=''; document.getElementById('dirSearch').dispatchEvent(new Event('input'));
    });

    // Export Btn (quick)
    document.getElementById('exportBtn').addEventListener('click', ()=> alert('Exporting (placeholder)'));

    // Quick register (placeholder)
    document.getElementById('quickReg').addEventListener('click', ()=> alert('Open register modal (placeholder)'));

    // Simulate Save Settings
    document.getElementById('saveSettings').addEventListener('click', ()=>{
      const name = document.getElementById('displayName').value || 'ANJALI SINGH';
      const status = document.getElementById('statusText').value || 'Active';
      document.getElementById('profile-name').textContent = name;
      document.getElementById('profile-status').textContent = status;
      alert('Settings saved (locally).');
      showPage('home');
    });

    // Search input (global) basic highlight - focuses directory search
    document.getElementById('globalSearch').addEventListener('keydown', (e)=>{
      if(e.key === 'Enter'){
        const q = e.target.value.trim();
        if(!q) return;
        showPage('directory');
        document.getElementById('dirSearch').value = q;
        document.getElementById('dirSearch').dispatchEvent(new Event('input'));
      }
    });

    // Export CSV download from quick export button as well
    document.getElementById('exportBtn').addEventListener('click', ()=> document.getElementById('exportCsv').click());

    // Avatar initials or image loading (you can set avatar image by setting src)
    const avatarImg = document.getElementById('avatar-img');
    const avatarInitials = document.getElementById('avatar-initials');
    function setAvatar(imageUrl, name){
      if(imageUrl){
        avatarImg.src = imageUrl;
        avatarImg.style.display = 'block';
        avatarInitials.style.display = 'none';
      } else {
        avatarImg.style.display = 'none';
        avatarInitials.style.display = (name? name.split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase() : 'A');
      }
    }
    setAvatar('', 'Anjali Singh');

    // When page loads, animate skill bar fills (they already have width inline, but this ensures transition)
    window.addEventListener('load', ()=>{
      document.querySelectorAll('.progress > i').forEach(el=>{
        const w = el.style.width;
        el.style.width = '0';
        requestAnimationFrame(()=> requestAnimationFrame(()=> el.style.width = w));
      });
    });

    // Accessibility: close modal on ESC
    window.addEventListener('keydown', (e)=>{
      if(e.key === 'Escape'){
        modalBack.style.display='none';
        document.getElementById('sidebar').classList.remove('open');
      }
    });



    
    // Add Profile navigation
document.querySelectorAll('.nav-btn').forEach(b => {
  if(b.dataset.target === 'profile'){
    b.addEventListener('click', () => showPage('profile'));
  }
});

// Optional: auto-update profile card after form submit (without reload)
document.getElementById('profileForm').addEventListener('submit', function(e){
  e.preventDefault(); // prevent actual POST for demo
  const name = document.getElementById('fullName').value;
  const email = document.getElementById('email_id').value;
  const batch = document.getElementById('passingyear').value;
  const role = document.getElementById('curr_role').value;

  document.getElementById('profile-name').textContent = name;
  document.getElementById('profile-email').textContent = email;
  document.getElementById('profile-batch').textContent = batch;
  document.getElementById('profile-role').textContent = role;

  alert('Profile updated (demo)');
});
