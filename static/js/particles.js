/**
 * Chalk Dust Particle System
 * Spawns tiny floating particles inside the chalkboard area to increase visual immersion.
 */
window.initChalkDust = function(containerId, count = 25) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.warn(`[Genius Particles] Container '${containerId}' not found.`);
        return;
    }
    
    // Clear previous particles
    container.innerHTML = '';
    container.style.position = 'absolute';
    container.style.inset = '0';
    container.style.overflow = 'hidden';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '1';
    
    for (let i = 0; i < count; i++) {
        const p = document.createElement('div');
        const size = 1 + Math.random() * 3;
        const x = Math.random() * 100; // percentage-based width positioning
        const y = Math.random() * 100; // percentage-based height positioning
        const duration = 5 + Math.random() * 7;
        const delay = Math.random() * -duration;
        const drift = (Math.random() - 0.5) * 60 + 'px';
        const opacity = 0.15 + Math.random() * 0.4;
        
        p.style.position = 'absolute';
        p.style.left = `${x}%`;
        p.style.top = `${y}%`;
        p.style.width = `${size}px`;
        p.style.height = `${size}px`;
        p.style.backgroundColor = 'rgba(245, 242, 232, 0.5)';
        p.style.borderRadius = '50%';
        p.style.pointerEvents = 'none';
        p.style.animation = `float-dust-up ${duration}s linear infinite`;
        p.style.animationDelay = `${delay}s`;
        
        // Inject custom CSS variables used in keyframes
        p.style.setProperty('--dust-opacity', opacity);
        p.style.setProperty('--dust-drift', drift);
        
        container.appendChild(p);
    }
};
