import { displayMessage } from '../util.js'; //メッセー表示関数

// グローバルスコープでFastAPIのURLを定義
// TODO:URLは要検討
const loginUrl = 'http://localhost:8000/auth/login'; //ログイン画面
const sigunupUrl = 'http://localhost:8000/auth/signup'; //登録用URL

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
            displayMessage(data.message);
            // TODO:メインページへの遷移？
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
 *　ログイン：非同期関数
 */
async function login(user) {
    try {
        // APIにPOSTリクエスト送信
        // JSON形式
        const response = await fetch(loginUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user),
        });
        // レスポンスのボディをJSONとして解析
        const data = await response.json();
        // レスポンスが成功した場合(HTTPステータスコード：200)
        if (response.ok) {
            // 成功メッセージをアラートで表示
            displayMessage(data.message);
            // TODO:メインページへの遷移？
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
