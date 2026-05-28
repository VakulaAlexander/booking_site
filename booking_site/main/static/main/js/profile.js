document.addEventListener('DOMContentLoaded', function() {
    const showBtn = document.getElementById('showOrganizerBtn');
    const container = document.getElementById('organizerFormContainer');
    const cancelBtn = document.getElementById('cancelOrganizerBtn');

    if (showBtn && container) {
        showBtn.addEventListener('click', function() {
            container.style.display = 'block';
            showBtn.style.display = 'none';
        });
    }

    if (cancelBtn && container) {
        cancelBtn.addEventListener('click', function() {
            container.style.display = 'none';
            if (showBtn) showBtn.style.display = 'inline-block';
            // очистить поля формы
            const phoneInput = document.getElementById('phone_num');
            const infoTextarea = document.getElementById('info');
            if (phoneInput) phoneInput.value = '';
            if (infoTextarea) infoTextarea.value = '';
        });
    }
});