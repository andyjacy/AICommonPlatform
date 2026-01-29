/**
 * 用户会话管理模块
 * 处理登录、登出、会话验证和用户数据隔离
 */

class SessionManager {
    constructor() {
        this.token = null;
        this.user = null;
        this.isAuthenticated = false;
        this.sessionCheckInterval = null;
    }

    /**
     * 初始化会话管理器
     */
    async init() {
        // 从 localStorage 获取保存的令牌
        const savedToken = localStorage.getItem('auth_token');
        
        if (savedToken) {
            // 验证令牌是否仍然有效
            if (await this.verifyToken(savedToken)) {
                this.token = savedToken;
                return true;
            } else {
                // 令牌已过期，清除
                localStorage.removeItem('auth_token');
                return false;
            }
        }
        
        return false;
    }

    /**
     * 处理登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {boolean} 登录是否成功
     */
    async login(username, password) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.status === 'success' && data.token) {
                this.token = data.token;
                this.user = data.user;
                this.isAuthenticated = true;

                // 保存令牌到 localStorage
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('user_info', JSON.stringify(this.user));

                // 启动会话检查
                this.startSessionCheck();

                console.log('[Session] User logged in:', this.user.username);
                return true;
            } else {
                console.error('[Session] Login failed:', data.message);
                return false;
            }
        } catch (error) {
            console.error('[Session] Login error:', error);
            return false;
        }
    }

    /**
     * 处理登出
     * @returns {boolean} 登出是否成功
     */
    async logout() {
        try {
            if (this.token) {
                await fetch(`/api/user/logout?token=${this.token}`, {
                    method: 'POST'
                });
            }

            // 清除本地数据
            this.token = null;
            this.user = null;
            this.isAuthenticated = false;
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_info');

            // 停止会话检查
            this.stopSessionCheck();

            console.log('[Session] User logged out');
            return true;
        } catch (error) {
            console.error('[Session] Logout error:', error);
            return false;
        }
    }

    /**
     * 验证令牌有效性
     * @param {string} token - 令牌
     * @returns {boolean} 令牌是否有效
     */
    async verifyToken(token) {
        try {
            const response = await fetch(`/api/user/verify-token?token=${token}`);
            const data = await response.json();

            if (data.status === 'valid') {
                this.user = {
                    id: data.user_id,
                    username: data.username,
                    role: data.role,
                    language: data.language
                };
                this.isAuthenticated = true;
                return true;
            } else {
                this.isAuthenticated = false;
                return false;
            }
        } catch (error) {
            console.error('[Session] Token verification error:', error);
            this.isAuthenticated = false;
            return false;
        }
    }

    /**
     * 获取用户信息
     * @returns {object|null} 用户对象或 null
     */
    getUser() {
        return this.user;
    }

    /**
     * 获取令牌
     * @returns {string|null} 令牌或 null
     */
    getToken() {
        return this.token;
    }

    /**
     * 检查用户是否已认证
     * @returns {boolean} 是否已认证
     */
    isLoggedIn() {
        return this.isAuthenticated;
    }

    /**
     * 启动会话检查（定期验证令牌）
     */
    startSessionCheck() {
        // 每 5 分钟检查一次会话有效性
        this.sessionCheckInterval = setInterval(async () => {
            if (this.token && !await this.verifyToken(this.token)) {
                console.log('[Session] Session expired, logging out');
                await this.logout();
                
                // 触发会话过期事件
                window.dispatchEvent(new CustomEvent('sessionExpired', { 
                    detail: { message: '会话已过期，请重新登录' } 
                }));
            }
        }, 5 * 60 * 1000); // 5 分钟
    }

    /**
     * 停止会话检查
     */
    stopSessionCheck() {
        if (this.sessionCheckInterval) {
            clearInterval(this.sessionCheckInterval);
            this.sessionCheckInterval = null;
        }
    }
}

/**
 * 获取用户 QA 历史
 * @param {string} token - 用户令牌
 * @param {number} limit - 限制数量
 * @returns {array} 历史记录数组
 */
async function getUserQAHistory(token, limit = 20) {
    try {
        const response = await fetch(`/api/qa/history?token=${token}&limit=${limit}`);
        const data = await response.json();

        if (data.status === 'success') {
            return data.history || [];
        } else {
            console.error('[QA] Failed to get history:', data.message);
            return [];
        }
    } catch (error) {
        console.error('[QA] Error fetching history:', error);
        return [];
    }
}

/**
 * 获取特定 QA 的详细信息
 * @param {number} qaId - QA ID
 * @param {string} token - 用户令牌
 * @returns {object|null} QA 详情或 null
 */
async function getQADetail(qaId, token) {
    try {
        const response = await fetch(`/api/qa/history/${qaId}?token=${token}`);
        const data = await response.json();

        if (data.status === 'success') {
            return data.qa;
        } else {
            console.error('[QA] Failed to get detail:', data.message);
            return null;
        }
    } catch (error) {
        console.error('[QA] Error fetching detail:', error);
        return null;
    }
}

/**
 * 提交问题（带用户令牌）
 * @param {string} question - 问题文本
 * @param {string} token - 用户令牌
 * @returns {object|null} QA 响应或 null
 */
async function askQuestion(question, token) {
    try {
        const response = await fetch('/api/trace/qa/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                token: token
            })
        });

        const data = await response.json();

        if (!data.error) {
            return data;
        } else {
            console.error('[QA] Failed to ask question:', data.error);
            return null;
        }
    } catch (error) {
        console.error('[QA] Error asking question:', error);
        return null;
    }
}

// 创建全局会话管理器实例
const session = new SessionManager();

/**
 * 页面加载时初始化会话
 */
document.addEventListener('DOMContentLoaded', async () => {
    if (await session.init()) {
        console.log('[Session] Existing session restored');
        
        // 触发登录事件
        window.dispatchEvent(new CustomEvent('userLoggedIn', { 
            detail: { user: session.getUser() } 
        }));
    }
});

/**
 * 监听会话过期事件
 */
window.addEventListener('sessionExpired', (event) => {
    console.warn('[Session] Session expired:', event.detail.message);
    // 这里可以显示一个警告消息或重定向到登录页面
    alert(event.detail.message);
});

/**
 * 监听登出事件
 */
window.addEventListener('userLoggedOut', (event) => {
    console.log('[Session] User logged out event');
    // 清除页面中的用户特定数据
    location.reload();
});
