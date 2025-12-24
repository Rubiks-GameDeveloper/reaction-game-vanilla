<template>
  <div v-if="show" class="auth-modal-overlay" @click.self="close">
    <div class="auth-modal">
      <button class="close-button" @click="close">×</button>
      <h2>{{ isLogin ? 'Вход' : 'Регистрация' }}</h2>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div v-if="!isLogin" class="form-group">
          <label>Email:</label>
          <input
            v-model="formData.email"
            type="email"
            required
            placeholder="email@example.com"
          />
        </div>

        <div class="form-group">
          <label>Имя пользователя:</label>
          <input
            v-model="formData.username"
            type="text"
            required
            placeholder="username"
          />
        </div>

        <div class="form-group">
          <label>Пароль:</label>
          <input
            v-model="formData.password"
            type="password"
            required
            placeholder="••••••••"
          />
        </div>

        <div v-if="!isLogin" class="form-group">
          <label>Подтвердите пароль:</label>
          <input
            v-model="formData.password2"
            type="password"
            required
            placeholder="••••••••"
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>

        <button type="submit" class="button" :disabled="loading">
          {{ loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться') }}
        </button>
      </form>

      <div class="auth-switch">
        <button @click="toggleMode" class="link-button">
          {{ isLogin ? 'Нет аккаунта? Зарегистрироваться' : 'Уже есть аккаунт? Войти' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useAuth } from '../composables/useApi'

export default {
  name: 'AuthModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    initialMode: {
      type: String,
      default: 'login' // 'login' or 'register'
    }
  },
  emits: ['close', 'success'],
  setup(props, { emit }) {
    const { register, login, isAuthenticated } = useAuth()
    const isLogin = ref(props.initialMode === 'login')
    const loading = ref(false)
    const error = ref('')
    const success = ref('')

    const formData = ref({
      username: '',
      email: '',
      password: '',
      password2: ''
    })

    const toggleMode = () => {
      isLogin.value = !isLogin.value
      error.value = ''
      success.value = ''
    }

    const handleSubmit = async () => {
      loading.value = true
      error.value = ''
      success.value = ''

      try {
        if (isLogin.value) {
          await login(formData.value.username, formData.value.password)
          success.value = 'Успешный вход!'
          setTimeout(() => {
            emit('success')
            close()
          }, 1000)
        } else {
          await register(
            formData.value.username,
            formData.value.email,
            formData.value.password,
            formData.value.password2
          )
          success.value = 'Регистрация успешна!'
          setTimeout(() => {
            emit('success')
            close()
          }, 1000)
        }
      } catch (err) {
        // Show detailed error message
        const errorMessage = err.message || 'Произошла ошибка'
        error.value = errorMessage
        
        // Log full error for debugging
        console.error('Registration/Login error:', err)
      } finally {
        loading.value = false
      }
    }

    const close = () => {
      emit('close')
      formData.value = {
        username: '',
        email: '',
        password: '',
        password2: ''
      }
      error.value = ''
      success.value = ''
    }

    return {
      isLogin,
      formData,
      loading,
      error,
      success,
      toggleMode,
      handleSubmit,
      close
    }
  }
}
</script>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.auth-modal {
  background: #2a2a2a;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  position: relative;
}

.close-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 30px;
  height: 30px;
}

.close-button:hover {
  color: #00ff88;
}

.auth-modal h2 {
  margin-bottom: 1.5rem;
  color: #00ff88;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #00ff88;
}

.error-message {
  color: #ff4444;
  padding: 0.5rem;
  background: rgba(255, 68, 68, 0.1);
  border-radius: 4px;
  font-size: 0.9rem;
}

.success-message {
  color: #00ff88;
  padding: 0.5rem;
  background: rgba(0, 255, 136, 0.1);
  border-radius: 4px;
  font-size: 0.9rem;
}

.auth-switch {
  margin-top: 1rem;
  text-align: center;
}

.link-button {
  background: none;
  border: none;
  color: #00ff88;
  cursor: pointer;
  text-decoration: underline;
  font-size: 0.9rem;
}

.link-button:hover {
  color: #00cc6a;
}
</style>

