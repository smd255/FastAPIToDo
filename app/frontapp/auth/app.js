import { displayMessage } from '../util/util.js'; //メッセー表示関数

// グローバルスコープでFastAPIのURLを定義
// TODO:URLは要検討
const loginUrl = 'http://localhost:8000/auth/login'; //ログインAPI用URL
const sigunupUrl = 'http://localhost:8000/auth/signup'; //登録API用URL
const mainUrl = '../memo/index.html'; //メインページ

document.addEventListener('DOMContentLoaded', function () {
    const formTitle = document.getElementById('form-title'); // フォームタイトル
    const submitBtn = document.getElementById('submit-btn'); // 送信ボタン
    const toggleText = document.getElementById('toggle-text'); // メッセージ用

    let isRegister = false; // 初期状態はログイン要求ページ

    function updateForm() {
        if (isRegister) {
            formTitle.innerText = '新規登録';
            submitBtn.innerText = '新規登録';
            toggleText.innerHTML =
                'アカウントをお持ちですか？ <a href="#" id="toggle-link">ログイン</a>';
        } else {
            formTitle.innerText = 'ログイン';
            submitBtn.innerText = 'ログイン';
            toggleText.innerHTML =
                'アカウントをお持ちでないですか？ <a href="#" id="toggle-link">新規登録</a>';
        }

        // クリックイベントを再設定（リンクが書き換えられるため）
        document
            .getElementById('toggle-link')
            .addEventListener('click', function (event) {
                event.preventDefault(); // ページ遷移を防ぐ
                isRegister = !isRegister; // 切り替え
                updateForm(); // フォームを更新
            });
    }
    updateForm(); // 初期状態を反映

    //送信ボタンクリック時処理
    submitBtn.onclick = async () => {
        //ユーザー名とパスワード取得
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const user = { username, password };
        // 送信関数実行
        if (isRegister) {
            //新規登録関数実行
            signUp(user);
        } else {
            // ログイン関数実行
            login(user);
        }
    };
});

/**
 * フォームをリセットし新規登録モードに戻す関数
 */

function resetForm() {
    // ユーザー名のリセット
    document.getElementById('username').value = '';
    // パスワードのリセット
    document.getElementById('password').value = '';
}

/**
 * 新規登録：非同期関数
 */
async function signUp(user) {
    try {
        // APIにPOSTリクエスト送信
        // JSON形式
        const response = await fetch(sigunupUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user),
        });
        // レスポンスのボディをJSONとして解析
        const data = await response.json();
        // レスポンスが成功した場合(HTTPステータスコード：200)
        if (response.ok) {
            // 成功メッセージをアラートで表示
            displayMessage('登録成功');
            isRegister = false; //ログイン側に表示切替
            window.location.reload(); // 再読み込み
        } else {
            // エラーメッセージ表示
            // TODO:場合分けでエラーメッセージ切り替え
            displayMessage(data.detail);
            // フォームをリセットして新規入力状態に戻す
            // TODO: ユーザー名, パスワードのどちらの間違いかによってリセットする対象を変える
            resetForm();
        }
    } catch (error) {
        // ネットワークエラーやその他の理由でリクエスト自体が失敗した場合
        console.error('ユーザー登録中にエラーが発生しました：', error);
    }
}

/**
 * ログイン処理
 */
async function login(user) {
    const { username, password } = user;

    // リクエスト送信
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    // デバッグ用_すべてのキーと値をコンソールに出力
    for (const [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }

    const response = await fetch(loginUrl, {
        method: 'POST',
        body: formData,
        headers: {
            // 'Content-Type' を設定しないこと！Fetch APIが自動的に設定する
        },
    });

    // レスポンスデータ(JSON)取得
    if (response.ok) {
        const data = await response.json();
        const token = data.access_token;

        // Authorizationヘッダーに保存する仕組み(ローカルストレージ)
        localStorage.setItem('access_token', token);
        displayMessage('ログイン成功');
        window.location.href = mainUrl; // メインページに遷移
    } else {
        console.error('Login failed!');
    }
}

/**
 * トークン認証
 * 認証必要ページ用に提供
 */
export async function fetchProtectedData(url) {
    const token = localStorage.getItem('access_token');

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (response.ok) {
        const data = await response.json();
        console.log(data);
    } else {
        console.error('Failed to fetch protected data.');
    }
}
