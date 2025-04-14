// document.addEventListener('DOMContentLoaded', function () {
//     // 仮のログイン状態をチェックする例
//     const isLoggedIn = true; // 実際にはサーバーや認証システムを使います
//     const username = 'hoge'; // ユーザー名 (ログイン中のユーザーの名前)

//     // ログイン状態に応じてユーザー名を表示
//     if (isLoggedIn) {
//         const usernameElement = document.getElementById('username');
//         usernameElement.textContent = `ユーザー名： ${username} `;
//     }
// });

// script.js

// ユーザーのログイン状態を模擬
let isLoggedIn = true;
let username = 'hoge';

// DOM要素を取得
const loginButton = document.getElementById('login-button');

// 状態に応じて内容を変更
if (isLoggedIn) {
    loginButton.innerHTML = `<button onclick="logout()" class="auth-link">ログアウト</button>`;
} else {
    loginButton.innerHTML = `<a href="../auth/index.html" class="auth-link">ログイン・新規登録</a>`;
}

// ログイン/ログアウト用の関数（例）
function login() {
    console.log('ログイン処理を実行');
}

function logout() {
    console.log('ログアウト処理を実行');
}
