import { displayMessage } from '../util/util.js'; //メッセージ表示関数

// ユーザー名取得用のurl
const getuserUrl = 'http://localhost:8000/memos/myuser';
// mainページのurl
// TODO: 定数をどこかに固める。
const mainUrl = '../memo/index.html';

// ログインユーザー名
let loginUser = '';

async function init() {
    // ボタンの存在を待つ
    await waitForElement('#login-button');

    const loginButton = document.getElementById('login-button');
    const isLoggedIn = await checkLoginStatus();

    if (isLoggedIn) {
        loginButton.innerHTML = `
        <span class="user-name">${loginUser}</span>
        <button id="logout-button" class="auth-link">ログアウト</button>
        <a href="../auth/index.html" class="auth-link">ログイン・新規登録</a>
      `;
        // イベント定義
        document
            .getElementById('logout-button')
            .addEventListener('click', logout);
    } else {
        loginButton.innerHTML = `<a href="../auth/index.html" class="auth-link">ログイン・新規登録</a>`;
    }
}

// 指定要素の登場を待つユーティリティ関数
function waitForElement(selector) {
    return new Promise((resolve) => {
        const element = document.querySelector(selector);
        if (element) {
            return resolve(element);
        }

        const observer = new MutationObserver(() => {
            const el = document.querySelector(selector);
            if (el) {
                observer.disconnect();
                resolve(el);
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });
    });
}

init(); // 初期化実行

/**
 * 関数定義
 */
// ログイン状態取得
async function checkLoginStatus() {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
        const res = await fetch(getuserUrl, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        if (res.status === 200) {
            const user = await res.json();
            loginUser = user.username;
            console.log('ログインユーザー:', user.username);
            return true;
        } else {
            console.warn('ログインしていません');
            return false;
        }
    } catch (err) {
        console.error('通信エラー:', err);
        return false;
    }
}

// ログアウト処理
function logout() {
    // ローカルストレージのトークン削除
    localStorage.removeItem('access_token');
    displayMessage('ログアウトします。');
    window.location.reload(); // ← これで確実に再読み込み
}
