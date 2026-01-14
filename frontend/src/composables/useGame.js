import { ref, computed, nextTick } from 'vue'

export function useGame(soundManager) {
  const gameStarted = ref(false)
  const score = ref(0)
  const timeLeft = ref(60)
  const targets = ref([])
  const reactionTimes = ref([])
  const gameTimer = ref(null)
  const spawnTimer = ref(null)
  const highScores = ref([])

  const settings = ref({
    difficulty: 'easy',
    soundEnabled: true,
    particleEffects: true,
    screenShake: true
  })

  const difficultyLevels = {
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
  }

  const targetColors = [
    { start: '#ff4444', end: '#ff0000' },
    { start: '#44ff44', end: '#00ff00' },
    { start: '#4444ff', end: '#0000ff' },
    { start: '#ffff44', end: '#ffff00' },
    { start: '#ff44ff', end: '#ff00ff' }
  ]

  const currentDifficulty = computed(() => {
    return difficultyLevels[settings.value.difficulty]
  })

  const startGame = () => {
    if (!settings.value.difficulty) {
      console.error('Difficulty not selected')
      return
    }

    gameStarted.value = true
    score.value = 0
    reactionTimes.value = []
    targets.value = []

    const difficulty = currentDifficulty.value
    timeLeft.value = difficulty.gameTime

    soundManager.setMuted(!settings.value.soundEnabled)
    soundManager.startBackgroundMusic()

    startTimer()
    spawnTarget()
  }

  const spawnTarget = () => {
    if (!gameStarted.value) return

    const difficulty = currentDifficulty.value
    
    if (targets.value.length >= difficulty.maxTargets) {
      spawnTimer.value = setTimeout(() => spawnTarget(), difficulty.spawnRate)
      return
    }

    const size = Math.floor(Math.random() * (difficulty.maxSize - difficulty.minSize + 1)) + difficulty.minSize
    const colorIndex = Math.floor(Math.random() * targetColors.length)
    const colors = targetColors[colorIndex]

    // Use setTimeout to ensure DOM is ready
    setTimeout(() => {
      const gameArea = document.querySelector('.game-area')
      if (!gameArea) {
        spawnTimer.value = setTimeout(() => spawnTarget(), difficulty.spawnRate)
        return
      }

      const gameAreaRect = gameArea.getBoundingClientRect()
      const left = Math.random() * (gameAreaRect.width - size)
      const top = Math.random() * (gameAreaRect.height - size)

      const target = {
        id: Date.now() + Math.random(),
        size: size,
        left: left + 'px',
        top: top + 'px',
        colors: colors,
        spawnTime: null, // Will be set when element is rendered
        hit: false
      }

      targets.value.push(target)

      // Set spawnTime when element is actually rendered in DOM
      nextTick(() => {
        const targetElement = document.querySelector(`[data-target-id="${target.id}"]`)
        if (targetElement) {
          // Set spawn time when element is visible
          target.spawnTime = Date.now()
          
          // Animate target fade out
          if (window.gsap) {
            gsap.to(targetElement, {
              opacity: 0,
              scale: 0.8,
              duration: difficulty.targetLifetime / 1000,
              ease: "power2.in"
            })
          }
        }
      })

      // Remove target after lifetime
      setTimeout(() => {
        removeTarget(target.id)
      }, difficulty.targetLifetime)

      spawnTimer.value = setTimeout(() => spawnTarget(), difficulty.spawnRate)
    }, 10)
  }

  const removeTarget = (targetId) => {
    targets.value = targets.value.filter(t => t.id !== targetId)
  }

  const hitTarget = (target) => {
    if (!gameStarted.value || target.hit) return null
    
    // Don't calculate reaction time if spawnTime is not set yet
    if (!target.spawnTime) return null

    target.hit = true
    const difficulty = currentDifficulty.value
    const reactionTime = Date.now() - target.spawnTime

    reactionTimes.value.push(reactionTime)

    const timeBonus = Math.max(0, 1 - (reactionTime / 1000))
    const points = Math.floor(difficulty.pointsPerHit * (1 + timeBonus))
    score.value += points

    soundManager.play('hit')

    if (settings.value.particleEffects) {
      createParticles(target)
    }

    if (settings.value.screenShake) {
      screenShake()
    }

    if (score.value % 100 === 0) {
      soundManager.play('achievement')
      showAchievement()
    }

    setTimeout(() => {
      removeTarget(target.id)
    }, 300)

    return reactionTime
  }

  const createParticles = (target) => {
    setTimeout(() => {
      const targetElement = document.querySelector(`[data-target-id="${target.id}"]`)
      if (!targetElement) return

      const rect = targetElement.getBoundingClientRect()
      const scrollX = window.scrollX || window.pageXOffset
      const scrollY = window.scrollY || window.pageYOffset
      
      const centerX = rect.left + rect.width / 2 + scrollX
      const centerY = rect.top + rect.height / 2 + scrollY

      for (let i = 0; i < 10; i++) {
        const particle = document.createElement('div')
        particle.className = 'particle'
        particle.style.position = 'fixed'
        particle.style.left = `${centerX}px`
        particle.style.top = `${centerY}px`
        particle.style.width = '10px'
        particle.style.height = '10px'
        particle.style.background = `radial-gradient(circle, ${target.colors.start} 0%, ${target.colors.end} 100%)`
        particle.style.pointerEvents = 'none'
        particle.style.zIndex = '9999'

        const angle = (Math.random() * Math.PI * 2)
        const velocity = 2 + Math.random() * 2
        const vx = Math.cos(angle) * velocity
        const vy = Math.sin(angle) * velocity

        document.body.appendChild(particle)

        let posX = centerX
        let posY = centerY
        let opacity = 1

        const animate = () => {
          if (opacity <= 0) {
            if (particle.parentNode) {
              document.body.removeChild(particle)
            }
            return
          }

          posX += vx
          posY += vy
          opacity -= 0.02

          particle.style.left = `${posX}px`
          particle.style.top = `${posY}px`
          particle.style.opacity = opacity

          requestAnimationFrame(animate)
        }

        requestAnimationFrame(animate)
      }
    }, 10)
  }

  const screenShake = () => {
    if (!settings.value.screenShake) return

    const gameArea = document.querySelector('.game-area')
    if (!gameArea) return

    const intensity = 5
    const duration = 200

    gameArea.style.transform = ''

    const keyframes = [
      { transform: 'translate(0, 0)' },
      { transform: `translate(${intensity}px, ${intensity}px)` },
      { transform: `translate(-${intensity}px, -${intensity}px)` },
      { transform: `translate(${intensity}px, -${intensity}px)` },
      { transform: `translate(-${intensity}px, ${intensity}px)` },
      { transform: 'translate(0, 0)' }
    ]

    const options = {
      duration: duration,
      easing: 'ease-in-out'
    }

    gameArea.animate(keyframes, options)
  }

  const showAchievement = () => {
    const achievement = document.createElement('div')
    achievement.className = 'achievement'
    achievement.textContent = '🎉 Достижение: 100 очков! 🎉'
    document.body.appendChild(achievement)

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
                    document.body.removeChild(achievement)
                  }
                }
              })
            }, 2000)
          }
        }
      )
    }
  }

  const startTimer = () => {
    gameTimer.value = setInterval(() => {
      timeLeft.value--
      if (timeLeft.value <= 0) {
        endGame()
      }
    }, 1000)
  }

  const endGame = () => {
    gameStarted.value = false
    targets.value = []
    clearInterval(gameTimer.value)
    if (spawnTimer.value) {
      clearTimeout(spawnTimer.value)
    }
    soundManager.pauseBackgroundMusic()

    const avgReactionTime = reactionTimes.value.length > 0
      ? Math.round(reactionTimes.value.reduce((a, b) => a + b, 0) / reactionTimes.value.length)
      : 0

    const newScore = {
      name: settings.value.difficulty,
      score: score.value,
      avgReactionTime: avgReactionTime
    }

    addHighScore(newScore)
  }

  const addHighScore = (score) => {
    highScores.value.push(score)
    highScores.value.sort((a, b) => b.score - a.score)
    if (highScores.value.length > 10) {
      highScores.value = highScores.value.slice(0, 10)
    }
    saveHighScores()
  }

  const loadHighScores = () => {
    const scores = JSON.parse(localStorage.getItem('highScores') || '[]')
    highScores.value = scores
  }

  const saveHighScores = () => {
    localStorage.setItem('highScores', JSON.stringify(highScores.value))
  }

  const loadSettings = () => {
    const savedSettings = localStorage.getItem('gameSettings')
    if (savedSettings) {
      const parsed = JSON.parse(savedSettings)
      settings.value = { ...settings.value, ...parsed }
    }
  }

  const saveSettings = () => {
    localStorage.setItem('gameSettings', JSON.stringify(settings.value))
  }

  const cleanup = () => {
    clearInterval(gameTimer.value)
    if (spawnTimer.value) {
      clearTimeout(spawnTimer.value)
    }
  }

  return {
    gameStarted,
    score,
    timeLeft,
    targets,
    reactionTimes,
    highScores,
    settings,
    difficultyLevels,
    startGame,
    hitTarget,
    endGame,
    cleanup,
    loadHighScores,
    loadSettings,
    saveSettings,
    addHighScore
  }
}

