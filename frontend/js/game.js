class Game {
    constructor() {
        this.gameStarted = false;
        this.score = 0;
        this.timeLeft = 60;
        this.targets = [];
        this.reactionTimes = [];
        this.gameTimer = null;
        this.spawnTimer = null;
        this.settings = {
            difficulty: 'easy',
            soundEnabled: true,
            particleEffects: true,
            screenShake: true
        };

        this.difficultyLevels = {
            easy: {
                minSize: 60,
                maxSize: 80,
                spawnRate: 2000,
                gameTime: 60,
                pointsPerHit: 10,
                targetLifetime: 3000, // 3 seconds
                maxTargets: 5
            },
            medium: {
                minSize: 40,
                maxSize: 60,
                spawnRate: 1500,
                gameTime: 45,
                pointsPerHit: 20,
                targetLifetime: 2000, // 2 seconds
                maxTargets: 7
            },
            hard: {
                minSize: 30,
                maxSize: 50,
                spawnRate: 1000,
                gameTime: 30,
                pointsPerHit: 30,
                targetLifetime: 1500, // 1.5 seconds
                maxTargets: 10
            }
        };

        this.targetColors = [
            { start: '#ff4444', end: '#ff0000' },
            { start: '#44ff44', end: '#00ff00' },
            { start: '#4444ff', end: '#0000ff' },
            { start: '#ffff44', end: '#ffff00' },
            { start: '#ff44ff', end: '#ff00ff' }
        ];

        this.initializeElements();
        this.loadHighScores();
        this.loadSettings();
        this.setupEventListeners();

        this.muteButton.classList.add('hidden');
    }

    initializeElements() {
        // Game elements
        this.gameArea = document.getElementById('gameArea');
        this.gameInfo = document.getElementById('gameInfo');
        this.scoreElement = document.getElementById('score');
        this.timerElement = document.getElementById('timer');
        this.reactionTimeElement = document.getElementById('reactionTime');
        this.highScoresList = document.getElementById('scoresList');

        // Buttons
        this.startButton = document.getElementById('startButton');
        this.settingsButton = document.getElementById('settingsButton');
        this.muteButton = document.getElementById('muteButton');
        this.closeSettingsButton = document.getElementById('closeSettings');
        this.resumeButton = document.getElementById('resumeButton');

        // Settings elements
        this.settingsOverlay = document.getElementById('settings');
        this.difficultySelect = document.getElementById('difficultySelect');
        this.particleEffectsCheckbox = document.getElementById('particleEffects');
        this.screenShakeCheckbox = document.getElementById('screenShake');

        // New elements
        this.difficultySelection = document.getElementById('difficultySelection');
        this.continueButton = document.getElementById('continueButton');
        this.difficultyButtons = document.querySelectorAll('.difficulty-button');

        // Game control elements
        this.gameButtons = document.getElementById('gameButtons');
        this.exitButton = document.getElementById('exitButton');
    }

    setupEventListeners() {
        // Game controls
        this.startButton.addEventListener('click', () => this.showDifficultySelection());
        this.settingsButton.addEventListener('click', () => this.toggleSettings());
        this.muteButton.addEventListener('click', () => this.toggleMute());
        this.closeSettingsButton.addEventListener('click', () => this.toggleSettings());

        // Settings controls
        this.particleEffectsCheckbox.addEventListener('change', (e) => this.updateSettings('particleEffects', e.target.checked));
        this.screenShakeCheckbox.addEventListener('change', (e) => this.updateSettings('screenShake', e.target.checked));

        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));

        // Game control listeners
        this.startButton.addEventListener('click', () => this.showDifficultySelection());
        this.exitButton.addEventListener('click', () => this.exitGame());

        // Difficulty selection listeners
        this.difficultyButtons.forEach(button => {
            button.addEventListener('click', () => {
                const difficulty = button.dataset.difficulty;
                if (difficulty) {
                    this.settings.difficulty = difficulty;
                    this.startGame();
                }
            });
        });
    }

    handleKeyPress(e) {
        switch (e.key.toLowerCase()) {
            case ' ':
                e.preventDefault();
                if (!this.gameStarted) {
                    this.showDifficultySelection();
                }
                break;
            case 'm':
                this.toggleMute();
                break;
            case 's':
                this.toggleSettings();
                break;
        }
    }

    showDifficultySelection() {
        this.difficultySelection.classList.remove('hidden');
        this.startButton.classList.add('hidden');
    }

    startGame() {
        if (!this.settings.difficulty) {
            console.error('Difficulty not selected');
            return;
        }

        this.gameStarted = true;
        this.score = 0;
        this.reactionTimes = [];
        this.targets = [];
        this.updateScore();
        this.updateTimer();

        const difficulty = this.difficultyLevels[this.settings.difficulty];
        this.timeLeft = difficulty.gameTime;

        this.startButton.classList.add('hidden');
        this.difficultySelection.classList.add('hidden');
        
        this.gameArea.classList.remove('hidden');
        this.gameInfo.classList.remove('hidden');
        this.gameButtons.classList.remove('hidden');
        this.muteButton.classList.remove('hidden');

        soundManager.isMuted = !this.settings.soundEnabled;
        soundManager.startBackgroundMusic();
        if (!this.settings.soundEnabled) {
            soundManager.pauseBackgroundMusic();
        }

        this.startTimer();
        this.spawnTarget();
    }

    spawnTarget() {
        if (!this.gameStarted) return;

        const difficulty = this.difficultyLevels[this.settings.difficulty];
        
        // Check maximum targets limit
        if (this.targets.length >= difficulty.maxTargets) {
            this.spawnTimer = setTimeout(() => this.spawnTarget(), difficulty.spawnRate);
            return;
        }

        const gameAreaRect = this.gameArea.getBoundingClientRect();

        // Random size within range
        const size = Math.floor(Math.random() * (difficulty.maxSize - difficulty.minSize + 1)) + difficulty.minSize;

        // Random color
        const colorIndex = Math.floor(Math.random() * this.targetColors.length);
        const colors = this.targetColors[colorIndex];

        const target = document.createElement('div');
        target.className = 'target';
        target.style.width = `${size}px`;
        target.style.height = `${size}px`;
        target.style.left = `${Math.random() * (gameAreaRect.width - size)}px`;
        target.style.top = `${Math.random() * (gameAreaRect.height - size)}px`;
        target.style.background = `radial-gradient(circle, ${colors.start} 0%, ${colors.end} 100%)`;
        target.dataset.spawnTime = Date.now();

        // Add target lifetime animation
        if (window.gsap) {
            gsap.to(target, {
                opacity: 0,
                scale: 0.8,
                duration: difficulty.targetLifetime / 1000,
                ease: "power2.in",
                onComplete: () => {
                    if (target.parentNode) {
                        this.gameArea.removeChild(target);
                        this.targets = this.targets.filter(t => t !== target);
                    }
                }
            });
        }

        target.addEventListener('click', () => this.hitTarget(target));
        this.gameArea.appendChild(target);
        this.targets.push(target);

        // Set timeout for target removal
        setTimeout(() => {
            if (target.parentNode) {
                this.gameArea.removeChild(target);
                this.targets = this.targets.filter(t => t !== target);
            }
        }, difficulty.targetLifetime);

        this.spawnTimer = setTimeout(() => this.spawnTarget(), difficulty.spawnRate);
    }

    hitTarget(target) {
        if (!this.gameStarted || target.classList.contains('hit')) return;

        target.classList.add('hit');
        const difficulty = this.difficultyLevels[this.settings.difficulty];
        const reactionTime = Date.now() - parseInt(target.dataset.spawnTime);

        this.reactionTimes.push(reactionTime);
        this.updateReactionTime(reactionTime);

        // Calculate score based on reaction time
        const timeBonus = Math.max(0, 1 - (reactionTime / 1000));
        const points = Math.floor(difficulty.pointsPerHit * (1 + timeBonus));
        this.score += points;
        this.updateScore();

        soundManager.play('hit');

        if (this.settings.particleEffects) {
            this.createParticles(target);
        }

        if (this.settings.screenShake) {
            this.screenShake();
        }

        if (this.score % 100 === 0) {
            soundManager.play('achievement');
            this.showAchievement();
        }

        // Remove target after animation
        setTimeout(() => {
            if (target.parentNode) {
                this.gameArea.removeChild(target);
                this.targets = this.targets.filter(t => t !== target);
            }
        }, 300);
    }

    createParticles(target) {
        const rect = target.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        for (let i = 0; i < 10; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = `${centerX}px`;
            particle.style.top = `${centerY}px`;
            particle.style.width = '10px';
            particle.style.height = '10px';
            particle.style.background = target.style.background;

            const angle = (Math.random() * Math.PI * 2);
            const velocity = 2 + Math.random() * 2;
            const vx = Math.cos(angle) * velocity;
            const vy = Math.sin(angle) * velocity;

            document.body.appendChild(particle);

            let posX = centerX;
            let posY = centerY;
            let opacity = 1;

            const animate = () => {
                if (opacity <= 0) {
                    document.body.removeChild(particle);
                    return;
                }

                posX += vx;
                posY += vy;
                opacity -= 0.02;

                particle.style.left = `${posX}px`;
                particle.style.top = `${posY}px`;
                particle.style.opacity = opacity;

                requestAnimationFrame(animate);
            };

            requestAnimationFrame(animate);
        }
    }

    screenShake() {
        if (!this.settings.screenShake) return;

        const gameArea = document.getElementById('gameArea');
        const intensity = 5;
        const duration = 200;

        // Reset any existing transform
        gameArea.style.transform = '';

        // Create shake animation
        const keyframes = [
            { transform: 'translate(0, 0)' },
            { transform: `translate(${intensity}px, ${intensity}px)` },
            { transform: `translate(-${intensity}px, -${intensity}px)` },
            { transform: `translate(${intensity}px, -${intensity}px)` },
            { transform: `translate(-${intensity}px, ${intensity}px)` },
            { transform: 'translate(0, 0)' }
        ];

        const options = {
            duration: duration,
            easing: 'ease-in-out'
        };

        gameArea.animate(keyframes, options);
    }

    showAchievement() {
        const achievement = document.createElement('div');
        achievement.className = 'achievement';
        achievement.textContent = '🎉 Достижение: 100 очков! 🎉';
        document.body.appendChild(achievement);

        gsap.fromTo(achievement,
            { y: -100, opacity: 0 },
            { 
                y: 20,
                opacity: 1,
                duration: 0.5,
                ease: "bounce.out",
                onComplete: () => {
                    setTimeout(() => {
                        gsap.to(achievement, {
                            y: -100,
                            opacity: 0,
                            duration: 0.5,
                            ease: "power2.in",
                            onComplete: () => document.body.removeChild(achievement)
                        });
                    }, 2000);
                }
            }
        );
    }

    startTimer() {
        this.gameTimer = setInterval(() => {
                this.timeLeft--;
                this.updateTimer();

                if (this.timeLeft <= 0) {
                    this.endGame();
                }
        }, 1000);
    }

    updateTimer() {
        this.timerElement.textContent = `Время: ${this.timeLeft}`;
    }

    updateScore() {
        this.scoreElement.textContent = `Счёт: ${this.score}`;
    }

    updateReactionTime(time) {
        this.reactionTimeElement.textContent = `Время реакции: ${time}мс`;
    }

    toggleSettings() {
        this.settingsOverlay.classList.toggle('hidden');
    }

    toggleMute() {
        this.settings.soundEnabled = !this.settings.soundEnabled;
        localStorage.setItem('gameSettings', JSON.stringify(this.settings));

        if (this.settings.soundEnabled) {
            soundManager.isMuted = false;
            if (this.gameStarted) {
                soundManager.startBackgroundMusic();
            }
            this.muteButton.textContent = '🔊';
        } else {
            soundManager.isMuted = true;
            soundManager.pauseBackgroundMusic();
            this.muteButton.textContent = '🔇';
        }
    }

    updateSettings(key, value) {
        this.settings[key] = value;
        localStorage.setItem('gameSettings', JSON.stringify(this.settings));
    }

    endGame() {
        this.gameStarted = false;
        this.targets.forEach(target => {
            if (target.parentNode) {
                this.gameArea.removeChild(target);
            }
        });
        this.targets = [];
        clearInterval(this.gameTimer);
        clearInterval(this.spawnTimer);
        soundManager.pauseBackgroundMusic();

        const avgReactionTime = this.reactionTimes.length > 0
            ? Math.round(this.reactionTimes.reduce((a, b) => a + b, 0) / this.reactionTimes.length)
            : 0;

        const newScore = {
            name: this.settings.difficulty,
            score: this.score,
            avgReactionTime: avgReactionTime
        };

        this.addHighScore(newScore);

        this.gameArea.classList.add('hidden');
        this.gameInfo.classList.add('hidden');
        this.gameButtons.classList.add('hidden');
        this.muteButton.classList.add('hidden');
        
        this.startButton.classList.remove('hidden');
    }

    loadHighScores() {
        const scores = JSON.parse(localStorage.getItem('highScores') || '[]');
        this.highScoresList.innerHTML = '';
        scores.forEach(score => this.addHighScore(score));
    }

    addHighScore(score) {
        const scoreItem = document.createElement('div');
        scoreItem.className = 'score-item';
        scoreItem.innerHTML = `
            <span class="rank">${this.highScoresList.children.length + 1}.</span>
            <span class="difficulty">${score.name}</span>
            <span class="points">${score.score} очков</span>
            <span class="reaction-time">${score.avgReactionTime}мс</span>
        `;
        this.highScoresList.appendChild(scoreItem);

        // Save to localStorage
        const scores = Array.from(this.highScoresList.children).map(item => ({
            name: item.querySelector('.difficulty').textContent,
            score: parseInt(item.querySelector('.points').textContent),
            avgReactionTime: parseInt(item.querySelector('.reaction-time').textContent)
        }));
        localStorage.setItem('highScores', JSON.stringify(scores));
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('gameSettings');
        if (savedSettings) {
            this.settings = JSON.parse(savedSettings);
        }

        this.particleEffectsCheckbox.checked = this.settings.particleEffects;
        this.screenShakeCheckbox.checked = this.settings.screenShake;
        
        if (this.settings.soundEnabled) {
            soundManager.isMuted = false;
            this.muteButton.textContent = '🔊';
        } else {
            soundManager.isMuted = true;
            this.muteButton.textContent = '🔇';
        }
    }

    initializeGSAP() {
        // Load GSAP from CDN
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js';
        script.onload = () => {
            console.log('GSAP loaded successfully');
        };
        document.head.appendChild(script);
    }

    showEasterEgg() {
        const easterEgg = document.createElement('div');
        easterEgg.className = 'easter-egg';
        easterEgg.textContent = '🎉 Пасхалка найдена! 🎉';
        document.body.appendChild(easterEgg);

        if (window.gsap) {
            gsap.fromTo(easterEgg, 
                { y: -100, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.5, ease: "bounce.out" }
            );
        }

        setTimeout(() => {
            if (window.gsap) {
                gsap.to(easterEgg, {
                    y: -100,
                    opacity: 0,
                    duration: 0.5,
                    onComplete: () => document.body.removeChild(easterEgg)
                });
            } else {
                document.body.removeChild(easterEgg);
            }
        }, 3000);
    }

    validateSettings(settings) {
        const validDifficulties = ['easy', 'medium', 'hard'];
        if (!validDifficulties.includes(settings.difficulty)) {
            settings.difficulty = 'easy';
        }
        return settings;
    }

    exitGame() {
        this.endGame();
        this.resetGameState();
        soundManager.pauseBackgroundMusic();
    }

    resetGameState() {
        this.gameStarted = false;
        this.score = 0;
        this.reactionTimes = [];
        this.targets = [];
        this.timeLeft = 0;

        this.gameArea.classList.add('hidden');
        this.gameInfo.classList.add('hidden');
        this.gameButtons.classList.add('hidden');
        this.muteButton.classList.add('hidden');
        
        this.startButton.classList.remove('hidden');

        this.updateScore();
        this.updateTimer();
    }

    saveHighScore() {
        // Implementation of saveHighScore method
    }
}

// Add responsive design styles
const addResponsiveStyles = () => {
    const style = document.createElement('style');
    style.textContent = `
        @media (max-width: 768px) {
            .game-container {
                padding: 1rem;
            }
            
            .game-header {
                flex-direction: column;
                gap: 1rem;
            }
            
            .controls {
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .game-area {
                height: 400px;
            }
            
            .game-info {
                flex-direction: column;
                gap: 0.5rem;
            }
        }

        @media (max-width: 480px) {
            .game-area {
                height: 300px;
            }
            
            .button {
                padding: 0.3rem 0.6rem;
                font-size: 0.9rem;
            }
            
            .settings-content {
                padding: 1rem;
            }
        }
    `;
    document.head.appendChild(style);
};

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    addResponsiveStyles();
    const game = new Game();
}); 