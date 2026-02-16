// ===================================
// 股票分析系统 - 公共 JavaScript 工具
// ===================================

// Toast 通知
class Toast {
  static show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const iconMap = {
      success: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>',
      error: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>',
      warning: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>',
      info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>'
    };
    
    const colorMap = {
      success: '#10B981',
      error: '#DC2626',
      warning: '#F59E0B',
      info: '#3B82F6'
    };
    
    toast.innerHTML = `
      <div style="color: ${colorMap[type]}; flex-shrink: 0;">
        ${iconMap[type]}
      </div>
      <div style="flex: 1;">
        <p style="font-weight: 500; color: var(--gray-900);">${message}</p>
      </div>
      <button onclick="this.parentElement.remove()" style="color: var(--gray-400); background: none; border: none; cursor: pointer; padding: 0; flex-shrink: 0;">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideInRight 0.3s ease-out reverse';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
  
  static success(message, duration) {
    this.show(message, 'success', duration);
  }
  
  static error(message, duration) {
    this.show(message, 'error', duration);
  }
  
  static warning(message, duration) {
    this.show(message, 'warning', duration);
  }
  
  static info(message, duration) {
    this.show(message, 'info', duration);
  }
}

// Modal 对话框
class Modal {
  static show(options) {
    const {
      title = '提示',
      content = '',
      confirmText = '确定',
      cancelText = '取消',
      showCancel = true,
      onConfirm = () => {},
      onCancel = () => {}
    } = options;
    
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal" style="width: 500px;">
        <div class="modal-header">
          <h3 class="modal-title">${title}</h3>
          <button class="modal-close" style="background: none; border: none; color: var(--gray-400); cursor: pointer; padding: 0;">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          ${content}
        </div>
        <div class="modal-footer">
          ${showCancel ? `<button class="btn btn-secondary modal-cancel">${cancelText}</button>` : ''}
          <button class="btn btn-primary modal-confirm">${confirmText}</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(overlay);
    
    const close = () => {
      overlay.style.animation = 'fadeIn 0.2s ease-out reverse';
      setTimeout(() => overlay.remove(), 200);
    };
    
    overlay.querySelector('.modal-close').addEventListener('click', () => {
      onCancel();
      close();
    });
    
    if (showCancel) {
      overlay.querySelector('.modal-cancel').addEventListener('click', () => {
        onCancel();
        close();
      });
    }
    
    overlay.querySelector('.modal-confirm').addEventListener('click', () => {
      onConfirm();
      close();
    });
    
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        onCancel();
        close();
      }
    });
  }
  
  static confirm(options) {
    return new Promise((resolve) => {
      this.show({
        ...options,
        onConfirm: () => resolve(true),
        onCancel: () => resolve(false)
      });
    });
  }
  
  static alert(content, title = '提示') {
    return this.show({
      title,
      content,
      showCancel: false
    });
  }
}

// 表单验证
class Validator {
  static email(value) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(value);
  }
  
  static phone(value) {
    const regex = /^1[3-9]\d{9}$/;
    return regex.test(value);
  }
  
  static password(value) {
    // 至少8位，包含字母和数字
    return value.length >= 8 && /[a-zA-Z]/.test(value) && /\d/.test(value);
  }
  
  static required(value) {
    return value !== null && value !== undefined && value.toString().trim() !== '';
  }
  
  static minLength(value, length) {
    return value.toString().length >= length;
  }
  
  static maxLength(value, length) {
    return value.toString().length <= length;
  }
  
  static range(value, min, max) {
    const num = parseFloat(value);
    return !isNaN(num) && num >= min && num <= max;
  }
}

// 本地存储管理
class Storage {
  static set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      console.error('Storage.set error:', e);
      return false;
    }
  }
  
  static get(key, defaultValue = null) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : defaultValue;
    } catch (e) {
      console.error('Storage.get error:', e);
      return defaultValue;
    }
  }
  
  static remove(key) {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (e) {
      console.error('Storage.remove error:', e);
      return false;
    }
  }
  
  static clear() {
    try {
      localStorage.clear();
      return true;
    } catch (e) {
      console.error('Storage.clear error:', e);
      return false;
    }
  }
}

// 用户认证管理
class Auth {
  static TOKEN_KEY = 'auth_token';
  static USER_KEY = 'auth_user';
  
  static setToken(token) {
    Storage.set(this.TOKEN_KEY, token);
  }
  
  static getToken() {
    return Storage.get(this.TOKEN_KEY);
  }
  
  static setUser(user) {
    Storage.set(this.USER_KEY, user);
  }
  
  static getUser() {
    return Storage.get(this.USER_KEY);
  }
  
  static isLoggedIn() {
    return !!this.getToken();
  }
  
  static isAdmin() {
    const user = this.getUser();
    return user && user.role === 'admin';
  }
  
  static logout() {
    Storage.remove(this.TOKEN_KEY);
    Storage.remove(this.USER_KEY);
    window.location.href = 'login.html';
  }
  
  static checkAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  }
  
  static checkAdminAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = 'login.html';
      return false;
    }
    if (!this.isAdmin()) {
      Toast.error('您没有权限访问此页面');
      setTimeout(() => {
        window.location.href = 'filter.html';
      }, 1500);
      return false;
    }
    return true;
  }
}

// API 请求封装
class API {
  static BASE_URL = '/api/v1';
  
  static async request(url, options = {}) {
    const token = Auth.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
      const response = await fetch(this.BASE_URL + url, {
        ...options,
        headers
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        // Token 过期处理
        if (response.status === 401) {
          Auth.logout();
          throw new Error('登录已过期，请重新登录');
        }
        throw new Error(data.message || '请求失败');
      }
      
      return data;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }
  
  static get(url, params) {
    if (params) {
      const query = new URLSearchParams(params).toString();
      url += '?' + query;
    }
    return this.request(url, { method: 'GET' });
  }
  
  static post(url, data) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  static put(url, data) {
    return this.request(url, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  static delete(url) {
    return this.request(url, { method: 'DELETE' });
  }
}

// 数字格式化工具
class NumberFormatter {
  // 格式化金额（万元）
  static formatAmount(value) {
    if (!value && value !== 0) return '-';
    const num = parseFloat(value);
    if (isNaN(num)) return '-';
    
    if (Math.abs(num) >= 10000) {
      return (num / 10000).toFixed(2) + '亿';
    }
    return num.toFixed(2) + '万';
  }
  
  // 格式化百分比
  static formatPercent(value, decimals = 2) {
    if (!value && value !== 0) return '-';
    const num = parseFloat(value);
    if (isNaN(num)) return '-';
    return num.toFixed(decimals) + '%';
  }
  
  // 格式化价格
  static formatPrice(value, decimals = 2) {
    if (!value && value !== 0) return '-';
    const num = parseFloat(value);
    if (isNaN(num)) return '-';
    return num.toFixed(decimals);
  }
  
  // 格式化涨跌幅（带颜色）
  static formatChange(value) {
    if (!value && value !== 0) return '<span>0.00%</span>';
    const num = parseFloat(value);
    if (isNaN(num)) return '<span>-</span>';
    
    const formatted = num.toFixed(2) + '%';
    if (num > 0) {
      return `<span style="color: var(--primary);">+${formatted}</span>`;
    } else if (num < 0) {
      return `<span style="color: var(--success);">${formatted}</span>`;
    }
    return `<span>${formatted}</span>`;
  }
}

// 日期格式化工具
class DateFormatter {
  static format(date, format = 'YYYY-MM-DD HH:mm:ss') {
    if (!date) return '-';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '-';
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');
    
    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hours)
      .replace('mm', minutes)
      .replace('ss', seconds);
  }
  
  static formatDate(date) {
    return this.format(date, 'YYYY-MM-DD');
  }
  
  static formatDateTime(date) {
    return this.format(date, 'YYYY-MM-DD HH:mm:ss');
  }
  
  static formatTime(date) {
    return this.format(date, 'HH:mm:ss');
  }
  
  static relative(date) {
    if (!date) return '-';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '-';
    
    const now = new Date();
    const diff = now - d;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}天前`;
    if (hours > 0) return `${hours}小时前`;
    if (minutes > 0) return `${minutes}分钟前`;
    if (seconds > 0) return `${seconds}秒前`;
    return '刚刚';
  }
}

// 防抖函数
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 节流函数
function throttle(func, limit = 300) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// 加载状态管理
class Loading {
  static show(element) {
    if (typeof element === 'string') {
      element = document.querySelector(element);
    }
    if (element) {
      element.disabled = true;
      const originalText = element.textContent;
      element.dataset.originalText = originalText;
      element.innerHTML = '<span class="spinner"></span> 加载中...';
    }
  }
  
  static hide(element) {
    if (typeof element === 'string') {
      element = document.querySelector(element);
    }
    if (element) {
      element.disabled = false;
      element.textContent = element.dataset.originalText || '提交';
      delete element.dataset.originalText;
    }
  }
}