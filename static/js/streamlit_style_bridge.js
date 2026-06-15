/**
 * Streamlit Style Bridge for Genius
 * Periodically scan the DOM and apply design system CSS classes to standard Streamlit widgets.
 * This overrides Streamlit's default templates with our classroom chalk-and-wood theme.
 */
(function() {
    function applyClassroomStyling() {
        // 1. Target all Sidebar Buttons -> convert to wood-carved sidebar items
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            const sidebarButtons = sidebar.querySelectorAll('button');
            sidebarButtons.forEach(btn => {
                btn.classList.add('sidebar-item');
                
                // Style cleanup to override default streamlit border/bg transitions
                btn.style.setProperty('border', 'none', 'important');
                btn.style.setProperty('box-shadow', 'none', 'important');
            });
        }

        // 2. Target Chalk Text Inputs
        const inputs = document.querySelectorAll('[data-testid="stTextInput"] input');
        inputs.forEach(input => {
            input.classList.add('chalk-text-input');
        });

        // 3. Target Mic Button
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            const btnText = btn.innerText || btn.textContent || "";
            
            // Microphone Button
            if (btnText.includes('🎤') || btnText.includes('🛑')) {
                btn.classList.add('mic-circle-btn');
                if (btnText.includes('🛑')) {
                    btn.classList.add('recording');
                } else {
                    btn.classList.remove('recording');
                }
                
                // Remove default button border / layout boxes
                btn.style.setProperty('border', 'none', 'important');
                btn.style.setProperty('border-radius', '50%', 'important');
                btn.style.setProperty('padding', '0', 'important');
            }
            
            // Key Term Chips (e.g. "Explain photosynthesis" or buttons under key-terms)
            const parentKeyTerms = btn.closest('.key-terms-box') || btn.closest('.key-terms-list');
            if (parentKeyTerms || btn.key?.includes('chip_')) {
                btn.classList.add('key-term-chip');
            }
            
            // Remove old select styling checks and let options container style them directly
        });

        // 4. Target Quiz option buttons inside quiz options container
        const quizContainer = document.querySelector('.st-key-quiz_options_container');
        const quizMeta = document.getElementById('quiz_metadata');
        if (quizContainer && quizMeta) {
            const userResponse = quizMeta.getAttribute('data-user-response');
            const correctAnswer = quizMeta.getAttribute('data-correct-answer');
            
            const quizButtons = quizContainer.querySelectorAll('button');
            quizButtons.forEach(btn => {
                btn.classList.add('quiz-option-card');
                
                // Remove default button border / layouts
                btn.style.setProperty('border', 'none', 'important');
                
                const text = btn.innerText || btn.textContent || "";
                const match = text.trim().match(/^([A-D])\./);
                if (match) {
                    const label = match[1];
                    btn.setAttribute('data-label', label);
                    
                    // Clear old state classes
                    btn.classList.remove('correct', 'wrong', 'dimmed');
                    
                    if (userResponse) {
                        if (label === correctAnswer) {
                            btn.classList.add('correct');
                        } else if (label === userResponse) {
                            btn.classList.add('wrong');
                        } else {
                            btn.classList.add('dimmed');
                        }
                    }
                }
            });
        }

        // 5. Customise default Streamlit form containers
        const containers = document.querySelectorAll('[data-testid="stForm"]');
        containers.forEach(form => {
            form.style.setProperty('background', 'rgba(26, 48, 14, 0.6)', 'important');
            form.style.setProperty('border', 'var(--border-chalk-solid)', 'important');
            form.style.setProperty('border-radius', 'var(--border-radius-lg)', 'important');
        });
    }

    // Run immediately and setup interval to capture Streamlit dynamic updates
    applyClassroomStyling();
    setInterval(applyClassroomStyling, 250);
})();
