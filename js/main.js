const { createApp } = Vue;

createApp({
    data() {
        return {
            gameStarted: false,
            score: 0,
            timeLeft: 60,
            targets: [],
            reactionTimes: [],
            gameTimer: null,
            spawnTimer: null,
            showDifficultySelection: false,
            showSettings: false,
            showGameArea: false,
            showGameInfo: false,
            currentReactionTime: null,
            highScores: [],
            settings: {
                difficulty: 'easy',
                soundEnabled: true,
                particleEffects: true,
                screenShake: true
            },
            difficultyLevels: {
                easy: {
                    minSize: 60,
                    maxSize: 80,
                    spawnRate: 2000,
                    gameTime: 60,
                    pointsPerHit: 10,
                    targetLifetime: 3000,
                    maxTargets: 5
                },
                medium: {
                    minSize: 40,
                    maxSize: 60,
                    spawnRate: 1500,
                    gameTime: 45,
                    pointsPerHit: 20,
                    targetLifetime: 2000,
                    maxTargets: 7
                },
                hard: {
                    minSize: 30,
                    maxSize: 50,
                    spawnRate: 1000,
                    gameTime: 30,
                    pointsPerHit: 30,
                    targetLifetime: 1500,
                    maxTargets: 10
                }
            },
            targetColors: [
                { start: '#ff4444', end: '#ff0000' },
                { start: '#44ff44', end: '#00ff00' },
                { start: '#4444ff', end: '#0000ff' },
                { start: '#ffff44', end: '#ffff00' },
                { start: '#ff44ff', end: '#ff00ff' }
            ]
        };
    },
    computed: {
        muteButtonIcon() {
            return this.settings.soundEnabled ? '🔊' : '🔇';
        },
        currentDifficulty() {
            return this.difficultyLevels[this.settings.difficulty];
        }
    },
    mounted() {
        this.loadHighScores();
        this.loadSettings();
        this.setupKeyboardListeners();
    },
    beforeUnmount() {
        this.cleanup();
    },
    methods: {
        setupKeyboardListeners() {
            document.addEventListener('keydown', this.handleKeyPress);
        },
        handleKeyPress(e) {
            switch (e.key.toLowerCase()) {
                case ' ':
                    e.preventDefault();
                    if (!this.gameStarted && !this.showDifficultySelection) {
                        this.openDifficultySelection();
                    }
                    break;
                case 'm':
                    this.toggleMute();
                    break;
                case 's':
                    this.toggleSettings();
                    break;
            }
        },
        openDifficultySelection() {
            this.showDifficultySelection = true;
        },
        selectDifficulty(difficulty) {
            this.settings.difficulty = difficulty;
            this.startGame();
        },
        startGame() {
            if (!this.settings.difficulty) {
                console.error('Difficulty not selected');
                return;
            }

            this.gameStarted = true;
            this.score = 0;
            this.reactionTimes = [];
            this.targets = [];
            this.showDifficultySelection = false;
            this.showGameArea = true;
            this.showGameInfo = true;

            const difficulty = this.currentDifficulty;
            this.timeLeft = difficulty.gameTime;

            soundManager.isMuted = !this.settings.soundEnabled;
            soundManager.startBackgroundMusic();
            if (!this.settings.soundEnabled) {
                soundManager.pauseBackgroundMusic();
            }

            this.startTimer();
            this.spawnTarget();
        },
        spawnTarget() {
            if (!this.gameStarted) return;

            const difficulty = this.currentDifficulty;
            
            if (this.targets.length >= difficulty.maxTargets) {
                this.spawnTimer = setTimeout(() => this.spawnTarget(), difficulty.spawnRate);
                return;
            }

            const size = Math.floor(Math.random() * (difficulty.maxSize - difficulty.minSize + 1)) + difficulty.minSize;
            const colorIndex = Math.floor(Math.random() * this.targetColors.length);
            const colors = this.targetColors[colorIndex];

            // Get game area dimensions
            this.$nextTick(() => {
                const gameArea = document.querySelector('.game-area');
                if (!gameArea) {
                    this.spawnTimer = setTimeout(() => this.spawnTarget(), difficulty.spawnRate);
                    return;
                }

                const gameAreaRect = gameArea.getBoundingClientRect();
                const left = Math.random() * (gameAreaRect.width - size);
                const top = Math.random() * (gameAreaRect.height - size);

                const target = {
                    id: Date.now() + Math.random(),
                    size: size,
                    left: left + 'px',
                    top: top + 'px',
                    colors: colors,
                    spawnTime: Date.now(),
                    hit: false
                };

                this.targets.push(target);

                // Remove target after lifetime
                setTimeout(() => {
                    this.removeTarget(target.id);
                }, difficulty.targetLifetime);

                // Animate target fade out
                this.$nextTick(() => {
                    const targetElement = document.querySelector(`[data-target-id="${target.id}"]`);
                    if (targetElement && window.gsap) {
                        gsap.to(targetElement, {
                            opacity: 0,
                            scale: 0.8,
                            duration: difficulty.targetLifetime / 1000,
                            ease: "power2.in"
                        });
                    }
                });

                this.spawnTimer = setTimeout(() => this.spawnTarget(), difficulty.spawnRate);
            });
        },
        hitTarget(target) {
            if (!this.gameStarted || target.hit) return;

            target.hit = true;
            const difficulty = this.currentDifficulty;
            const reactionTime = Date.now() - target.spawnTime;

            this.reactionTimes.push(reactionTime);
            this.currentReactionTime = reactionTime;

            const timeBonus = Math.max(0, 1 - (reactionTime / 1000));
            const points = Math.floor(difficulty.pointsPerHit * (1 + timeBonus));
            this.score += points;

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

            setTimeout(() => {
                this.removeTarget(target.id);
            }, 300);
        },
        removeTarget(targetId) {
            this.targets = this.targets.filter(t => t.id !== targetId);
        },
        createParticles(target) {
            // Get target element position
            this.$nextTick(() => {
                const targetElement = document.querySelector(`[data-target-id="${target.id}"]`);
                if (!targetElement) return;

                const rect = targetElement.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;

                for (let i = 0; i < 10; i++) {
                    const particle = document.createElement('div');
                    particle.className = 'particle';
                    particle.style.left = `${centerX}px`;
                    particle.style.top = `${centerY}px`;
                    particle.style.width = '10px';
                    particle.style.height = '10px';
                    particle.style.background = `radial-gradient(circle, ${target.colors.start} 0%, ${target.colors.end} 100%)`;

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
                            if (particle.parentNode) {
                                document.body.removeChild(particle);
                            }
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
            });
        },
        screenShake() {
            if (!this.settings.screenShake) return;

            const gameArea = document.querySelector('.game-area');
            if (!gameArea) return;

            const intensity = 5;
            const duration = 200;

            gameArea.style.transform = '';

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
        },
        showAchievement() {
            const achievement = document.createElement('div');
            achievement.className = 'achievement';
            achievement.textContent = '🎉 Достижение: 100 очков! 🎉';
            document.body.appendChild(achievement);

            if (window.gsap) {
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
                                    onComplete: () => {
                                        if (achievement.parentNode) {
                                            document.body.removeChild(achievement);
                                        }
                                    }
                                });
                            }, 2000);
                        }
                    }
                );
            }
        },
        startTimer() {
            this.gameTimer = setInterval(() => {
                this.timeLeft--;
                if (this.timeLeft <= 0) {
                    this.endGame();
                }
            }, 1000);
        },
        toggleSettings() {
            this.showSettings = !this.showSettings;
        },
        toggleMute() {
            this.settings.soundEnabled = !this.settings.soundEnabled;
            this.saveSettings();

            if (this.settings.soundEnabled) {
                soundManager.isMuted = false;
                if (this.gameStarted) {
                    soundManager.startBackgroundMusic();
                }
            } else {
                soundManager.isMuted = true;
                soundManager.pauseBackgroundMusic();
            }
        },
        updateSettings(key, value) {
            this.settings[key] = value;
            this.saveSettings();
        },
        endGame() {
            this.gameStarted = false;
            this.targets = [];
            clearInterval(this.gameTimer);
            if (this.spawnTimer) {
                clearTimeout(this.spawnTimer);
            }
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

            this.showGameArea = false;
            this.showGameInfo = false;
        },
        exitGame() {
            this.endGame();
        },
        addHighScore(score) {
            this.highScores.push(score);
            this.highScores.sort((a, b) => b.score - a.score);
            if (this.highScores.length > 10) {
                this.highScores = this.highScores.slice(0, 10);
            }
            this.saveHighScores();
        },
        loadHighScores() {
            const scores = JSON.parse(localStorage.getItem('highScores') || '[]');
            this.highScores = scores;
        },
        saveHighScores() {
            localStorage.setItem('highScores', JSON.stringify(this.highScores));
        },
        loadSettings() {
            const savedSettings = localStorage.getItem('gameSettings');
            if (savedSettings) {
                const parsed = JSON.parse(savedSettings);
                this.settings = { ...this.settings, ...parsed };
            }

            if (this.settings.soundEnabled) {
                soundManager.isMuted = false;
            } else {
                soundManager.isMuted = true;
            }
        },
        saveSettings() {
            localStorage.setItem('gameSettings', JSON.stringify(this.settings));
        },
        cleanup() {
            clearInterval(this.gameTimer);
            if (this.spawnTimer) {
                clearTimeout(this.spawnTimer);
            }
            document.removeEventListener('keydown', this.handleKeyPress);
        },
        getDifficultyLabel(difficulty) {
            const labels = {
                easy: 'Легкий',
                medium: 'Средний',
                hard: 'Сложный'
            };
            return labels[difficulty] || difficulty;
        }
    },
    template: `
        <div class="game-container">
            <div class="game-header">
                <h1>Игра на реакцию</h1>
                <div class="controls">
                    <button 
                        v-if="!gameStarted && !showDifficultySelection" 
                        @click="openDifficultySelection" 
                        class="button"
                    >
                        Начать игру
                    </button>
                    <button @click="toggleSettings" class="button">Настройки</button>
                    <button 
                        v-if="gameStarted || showDifficultySelection"
                        @click="toggleMute" 
                        class="button"
                    >
                        {{ muteButtonIcon }}
                    </button>
                </div>
            </div>

            <div class="game-content">
                <!-- Difficulty selection -->
                <div v-if="showDifficultySelection" class="difficulty-selection">
                    <h2>Выберите уровень сложности</h2>
                    <div class="difficulty-options">
                        <button 
                            class="difficulty-button" 
                            @click="selectDifficulty('easy')"
                        >
                            <h3>Легкий</h3>
                            <p>Большие цели (60-80px)</p>
                            <p>3 секунды на реакцию</p>
                            <p>60 секунд игры</p>
                        </button>
                        <button 
                            class="difficulty-button" 
                            @click="selectDifficulty('medium')"
                        >
                            <h3>Средний</h3>
                            <p>Средние цели (40-60px)</p>
                            <p>2 секунды на реакцию</p>
                            <p>45 секунд игры</p>
                        </button>
                        <button 
                            class="difficulty-button" 
                            @click="selectDifficulty('hard')"
                        >
                            <h3>Сложный</h3>
                            <p>Маленькие цели (30-50px)</p>
                            <p>1.5 секунды на реакцию</p>
                            <p>30 секунд игры</p>
                        </button>
                    </div>
                </div>

                <!-- Game area -->
                <div v-if="showGameArea" class="game-area">
                    <div
                        v-for="target in targets"
                        :key="target.id"
                        :data-target-id="target.id"
                        class="target"
                        :class="{ 'hit': target.hit }"
                        :style="{
                            width: target.size + 'px',
                            height: target.size + 'px',
                            left: target.left,
                            top: target.top,
                            background: 'radial-gradient(circle, ' + target.colors.start + ' 0%, ' + target.colors.end + ' 100%)'
                        }"
                        @click="hitTarget(target)"
                    ></div>
                </div>

                <!-- Game info -->
                <div v-if="showGameInfo" class="game-info">
                    <div class="game-controls">
                        <div class="game-buttons">
                            <button @click="exitGame" class="control-button">Выйти</button>
                        </div>
                    </div>
                    <div class="score">Счёт: {{ score }}</div>
                    <div class="timer">Время: {{ timeLeft }}</div>
                    <div v-if="currentReactionTime" class="reaction-time">
                        Время реакции: {{ currentReactionTime }}мс
                    </div>
                </div>

                <!-- High scores -->
                <div class="high-scores">
                    <h2>Рекорды:</h2>
                    <div class="scores-list">
                        <div 
                            v-for="(score, index) in highScores" 
                            :key="index"
                            class="score-item"
                        >
                            <span class="rank">{{ index + 1 }}.</span>
                            <span class="difficulty">{{ getDifficultyLabel(score.name) }}</span>
                            <span class="points">{{ score.score }} очков</span>
                            <span class="reaction-time">{{ score.avgReactionTime }}мс</span>
                        </div>
                        <div v-if="highScores.length === 0" class="score-item">
                            <span>Пока нет рекордов</span>
                        </div>
                    </div>
                </div>

                <!-- Keyboard controls -->
                <div class="keyboard-controls">
                    <h3>Управление с клавиатуры:</h3>
                    <div class="keyboard-grid">
                        <div class="key-item">
                            <span class="key">Пробел</span>
                            <span class="description">Начать игру</span>
                        </div>
                        <div class="key-item">
                            <span class="key">M</span>
                            <span class="description">Включить/выключить звук</span>
                        </div>
                        <div class="key-item">
                            <span class="key">S</span>
                            <span class="description">Настройки</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Settings overlay -->
            <div v-if="showSettings" class="settings-overlay" @click.self="toggleSettings">
                <div class="settings-content">
                    <h2>Настройки</h2>
                    <div class="settings-group">
                        <h3>Эффекты</h3>
                        <label>
                            <input 
                                type="checkbox" 
                                v-model="settings.particleEffects"
                                @change="updateSettings('particleEffects', settings.particleEffects)"
                            >
                            Частицы при попадании
                        </label>
                        <label>
                            <input 
                                type="checkbox" 
                                v-model="settings.screenShake"
                                @change="updateSettings('screenShake', settings.screenShake)"
                            >
                            Тряска экрана
                        </label>
                    </div>
                    <button @click="toggleSettings" class="button">Закрыть</button>
                </div>
            </div>
        </div>
    `
}).mount('#app');

