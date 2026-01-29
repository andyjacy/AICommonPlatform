/**
 * 国际化 (i18n) 管理模块
 * 支持中文 (zh) 和英文 (en)
 */

class I18nManager {
    constructor() {
        this.language = 'zh'; // 默认语言
        this.translations = {};
        this.initialized = false;
    }

    /**
     * 初始化 i18n 管理器
     * @param {string} defaultLang - 默认语言
     */
    async init(defaultLang = 'zh') {
        this.language = defaultLang;
        
        // 从 localStorage 获取用户偏好
        const savedLang = localStorage.getItem('user_language');
        if (savedLang && ['zh', 'en'].includes(savedLang)) {
            this.language = savedLang;
        }
        
        // 加载翻译文件
        await this.loadLanguage(this.language);
        this.initialized = true;
    }

    /**
     * 加载指定语言的翻译文件
     * @param {string} lang - 语言代码
     */
    async loadLanguage(lang) {
        try {
            const response = await fetch(`/static/i18n/${lang}.json`);
            if (response.ok) {
                this.translations = await response.json();
                this.language = lang;
                localStorage.setItem('user_language', lang);
                console.log(`[i18n] Loaded language: ${lang}`);
            } else {
                console.error(`[i18n] Failed to load language: ${lang}`);
            }
        } catch (error) {
            console.error(`[i18n] Error loading language file:`, error);
        }
    }

    /**
     * 获取翻译文本
     * @param {string} key - 翻译键（使用点号分隔的路径）
     * @param {object} params - 参数对象（用于替换占位符）
     * @returns {string} 翻译后的文本
     */
    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations;

        for (const k of keys) {
            value = value?.[k];
            if (!value) {
                console.warn(`[i18n] Missing translation key: ${key}`);
                return key; // 返回 key 作为备用
            }
        }

        // 替换参数
        let result = value;
        for (const [param, paramValue] of Object.entries(params)) {
            result = result.replace(`{{${param}}}`, paramValue);
        }

        return result;
    }

    /**
     * 切换语言
     * @param {string} lang - 语言代码
     */
    async switchLanguage(lang) {
        if (!['zh', 'en'].includes(lang)) {
            console.warn(`[i18n] Invalid language: ${lang}`);
            return false;
        }

        await this.loadLanguage(lang);
        
        // 发送事件
        window.dispatchEvent(new CustomEvent('languageChanged', { 
            detail: { language: lang } 
        }));

        return true;
    }

    /**
     * 获取当前语言
     * @returns {string} 当前语言代码
     */
    getCurrentLanguage() {
        return this.language;
    }

    /**
     * 获取所有支持的语言
     * @returns {array} 语言列表
     */
    getSupportedLanguages() {
        return ['zh', 'en'];
    }
}

// 创建全局实例
const i18n = new I18nManager();

/**
 * 页面加载完毕后初始化 i18n
 */
document.addEventListener('DOMContentLoaded', async () => {
    // 尝试从用户令牌获取语言偏好
    const token = localStorage.getItem('auth_token');
    if (token) {
        try {
            const response = await fetch(`/api/user/verify-token?token=${token}`);
            const data = await response.json();
            
            if (data.status === 'valid' && data.language) {
                await i18n.init(data.language);
            } else {
                await i18n.init();
            }
        } catch (error) {
            console.warn('[i18n] Failed to get user language:', error);
            await i18n.init();
        }
    } else {
        await i18n.init();
    }
    
    // 更新页面翻译
    updatePageTranslations();
});

/**
 * 更新页面上的所有翻译文本
 */
function updatePageTranslations() {
    // 更新所有包含 data-i18n 属性的元素
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const text = i18n.t(key);
        
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = text;
        } else if (element.getAttribute('data-i18n-title')) {
            element.title = text;
        } else {
            element.textContent = text;
        }
    });
}

/**
 * 监听语言变化事件
 */
window.addEventListener('languageChanged', (event) => {
    console.log(`[i18n] Language changed to: ${event.detail.language}`);
    updatePageTranslations();
});

/**
 * 辅助函数：切换语言并保存到服务器
 */
async function switchUserLanguage(lang, token) {
    if (!['zh', 'en'].includes(lang)) {
        console.warn(`[i18n] Invalid language: ${lang}`);
        return false;
    }

    // 切换前端语言
    await i18n.switchLanguage(lang);

    // 保存到服务器
    if (token) {
        try {
            const response = await fetch(`/api/user/language?token=${token}&language=${lang}`, {
                method: 'PUT'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                console.log(`[i18n] Language preference saved: ${lang}`);
                return true;
            }
        } catch (error) {
            console.error('[i18n] Failed to save language preference:', error);
        }
    }

    return true;
}
