// ユーザー名取得用のurl
const getuserUrl = 'http://localhost:8000/memos/myuser';

// DOM要素を取得
const loginButton = document.getElementById('login-button');

// ログイン状態取得
let isLoggedIn = checkLoginStatus();

// 状態に応じて内容を変更
if (isLoggedIn == true) {
    loginButton.innerHTML = `<button onclick="logout()" class="auth-link">ログアウト</button>`;
} else {
    loginButton.innerHTML = `<a href="../auth/index.html" class="auth-link">ログイン・新規登録</a>`;
}

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

// ログイン/ログアウト用の関数（例）
function login() {
    console.log('ログイン処理を実行');
}

function logout() {
    console.log('ログアウト処理を実行');
}
