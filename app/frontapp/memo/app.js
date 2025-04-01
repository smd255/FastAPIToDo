import { displayMessage } from '../util.js'; //メッセージ表示関数

// グローバルスコープでFastAPIのURLを定義
const apiUrl = 'http://localhost:8000/memos/';

// ユーザーid取得用のurl
const getuserUrl = 'http://localhost:8000/auth/me';

// 編集中のメモIDを保持する変数
let editingMemoId = null;

/**
 * フォームをリセットし新規登録モードに戻す関数
 */
function resetForm() {
    // フォームのタイトルをリセット
    document.getElementById('formTitle').textContent = 'メモの作成';
    // 項目：タイトルをリセット
    document.getElementById('title').value = '';
    // 項目：詳細をリセット
    document.getElementById('description').value = '';
    // 更新実行ボタンを非表示にする
    document.getElementById('updateButton').style.display = 'none';
    // 新規登録ボタンを再表示
    document.querySelector(
        '#createMemoForm button[type="submit"]'
    ).style.display = 'block';
    // 編集中のメモIDをリセット
    editingMemoId = null;
}

// トークン取得
function getToken() {
    // ローカルストレージからトークンを取得
    const token = localStorage.getItem('access_token');

    // トークンが存在しない場合のエラー処理
    if (!token) {
        throw new Error('認証トークンがありません。ログインしてください。');
    }
    return token;
}

/**
 * 新規登録：非同期関数
 */
async function createMemo(memo) {
    try {
        // トークン取得
        const token = getToken();

        // APIに「POSTリクエスト」を送信してメモを作成。
        // headersに'Content-Type'を'application/json'に設定。
        // JSON形式のデータを送信
        const response = await fetch(`${apiUrl}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`, // Authorizationヘッダーを追加
            },

            // メモオブジェクトをJSON文字列に変換して送信
            body: JSON.stringify(memo),
        });
        // レスポンスのボディをJSONとして解析
        const data = await response.json();
        // レスポンスが成功した場合(HTTPステータスコード：200)
        if (response.ok) {
            // 成功メッセージをアラートで表示
            displayMessage(data.message);
            // フォームをリセットして新規入力状態に戻す
            resetForm();
            // メモ一覧を最新の状態に更新
            await fetchAndDisplayMemos();
        } else {
            // レスポンスが失敗した場合、エラーメッセージを表示
            if (response.status === 422) {
                // バリデーションエラーの場合
                displayMessage('入力内容に誤りがあります。');
            } else {
                displayMessage(data.detail);
            }
        }
    } catch (error) {
        // ネットワークエラーやその他の理由でリクエスト自体が失敗した場合
        console.error('メモ作成中にエラーが発生しました：', error);
    }
}

/**
 * 更新：非同期関数
 */
async function updateMemo(memo) {
    try {
        // トークン取得
        const token = getToken();

        // APIに「POSTリクエスト」を送信してメモを更新。
        // headersに'Content-Type'を'application/json'に設定。
        // JSON形式のデータを送信
        const response = await fetch(`${apiUrl}${editingMemoId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(memo),
        });
        // レスポンスのボディをJSONとして解析
        const data = await response.json();
        // レスポンスが成功した場合(HTTPステータスコード：200)
        if (response.ok) {
            // 成功メッセージをアラートで表示
            displayMessage(data.message);
            // フォームをリセットして新規入力状態に戻す
            resetForm();
            // メモ一覧を最新の状態に更新
            await fetchAndDisplayMemos();
        } else {
            // レスポンスが失敗した場合エラーメッセージを表示
            if (response.status === 422) {
                // バリデーションエラーの場合
                displayMessage('入力内容に誤りがあります。');
            } else {
                displayMessage(data.detail);
            }
        }
    } catch (error) {
        // ネットワークエラーやその他の理由でリクエスト自体が失敗した場合
        console.error('メモ更新中にエラーが発生しました：', error);
    }
}

/**
 * 削除：非同期関数
 */
async function deleteMemo(memoId) {
    try {
        // トークン取得
        const token = getToken();

        // APIに「DELETEリクエスト」を送信してメモを削除します。
        const response = await fetch(`${apiUrl}${memoId}`, {
            method: 'DELETE',
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        // レスポンスのボディをJSONとして解析
        const data = await response.json();
        // レスポンスが成功した場合(HTTPステータスコード：200)
        if (response.ok) {
            // 成功メッセージをアラートで表示
            displayMessage(data.message);

            // メモ一覧を最新の状態に更新
            await fetchAndDisplayMemos();
        } else {
            // レスポンスが失敗した場合、エラーメッセージを表示
            displayMessage(data.detail);
        }
    } catch (error) {
        // ネットワークエラーやその他の理由でリクエスト自体が失敗した場合
        console.error(`メモ削除中にエラーが発生しました：`, error);
    }
}

/**
 * メモ一覧をサーバーから取得して表示する非同期関数
 */
async function fetchAndDisplayMemos() {
    try {
        // トークン取得
        const token = getToken();

        // APIに「GETリクエスト」を送信してメモ一覧を取得。
        const response = await fetch(`${apiUrl}`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        // レスポンスが失敗した場合、エラーを投げる。
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // レスポンスのボディをJSONとして解析
        const memos = await response.json();
        // HTML内のメモ一覧を表示する部分を取得
        const memosTableBody = document.querySelector('#memos tbody');
        // 一覧をクリア
        memosTableBody.innerHTML = '';
        // 取得したメモのデータを1つずつ設定
        memos.forEach((memo) => {
            // 行を作成
            const row = document.createElement('tr');
            // 行の中身：タイトル、説明、編集と削除ボタン
            row.innerHTML = `
                <td><input type="checkbox" data-id="${memo.memo_id}" ${memo.is_check ? 'checked' : ''}></td>
                <td>${memo.title}</td>
                <td>${memo.description}</td>
                <td>
                    <button class="edit" data-id="${memo.memo_id}">編集</button>
                    <button class="delete" data-id="${memo.memo_id}">削除</button>
                </td>
            `;
            // 作成した行をテーブルのbodyに追加
            memosTableBody.appendChild(row);
        });
    } catch (error) {
        // ネットワークエラーやその他の理由でリクエスト自体が失敗した場合
        console.error('メモ一覧の取得中にエラーが発生しました：', error);
    }
}

/**
 *  特定のメモを編集するための非同期関数
 */
async function editMemo(memoId) {
    // 編集するメモのIDをグローバル変数に設定
    editingMemoId = memoId;
    // トークン取得
    const token = getToken();
    // サーバーから特定のIDのメモのデータを取得するリクエストを送信
    const response = await fetch(`${apiUrl}${memoId}`, {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    // レスポンスのJSONを解析し、メモデータを取得
    const memo = await response.json();
    // レスポンスが正常でなければ、エラーメッセージを表示し、処理を終了
    if (!response.ok) {
        await displayMessage(memo.detail);
        return;
    }
    // 取得したメモのタイトルと説明をフォームに設定
    document.getElementById('title').value = memo.title;
    document.getElementById('description').value = memo.description;
    // ===フォーム===
    // フォームの見出しを「メモの編集」に更新
    document.getElementById('formTitle').textContent = 'メモの編集';
    // 更新実行ボタンを表示する
    document.getElementById('updateButton').style.display = 'block';
    // 新規登録ボタンを非表示にする
    document.querySelector(
        '#createMemoForm button[type="submit"]'
    ).style.display = 'none';
}

/**
 * チェックボックス状態取得
 */
function getCheckboxState(memoId) {
    const checkbox = document.querySelector(
        `input[type="checkbox"][data-id="${memoId}"]`
    );
    return checkbox ? checkbox.checked : null;
}

/**
 * 特定のメモのチェックボックスの状態更新用非同期関数
 */
async function updateCheckBox(memoId, isChecked) {
    // トークン取得
    const token = getToken();
    // サーバーから特定のIDのメモのデータを取得するリクエストを送信
    const response = await fetch(`${apiUrl}${memoId}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    // レスポンスのJSONを解析し、メモデータを取得
    const memo = await response.json();
    // レスポンスが正常でなければ、エラーメッセージを表示し、処理を終了
    if (!response.ok) {
        await displayMessage(memo.detail);
        return;
    }
    memo.is_check = isChecked; //チェックボックス状態を反映
    //更新
    try {
        // APIに「POSTリクエスト」を送信してメモを更新。
        // headersに'Content-Type'を'application/json'に設定。
        // JSON形式のデータを送信
        const response = await fetch(`${apiUrl}${memoId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(memo),
        });
    } catch (error) {
        // ネットワークエラーやその他の理由でリクエスト自体が失敗した場合
        console.error('チェックボックス更新中にエラーが発生しました：', error);
    }
}

// ログイン中のユーザー情報の取得
// function initializeUserId() {
//     // トークン取得
//     const token = getToken();
//     fetch(getuserUrl, {
//         headers: {
//             Authorization: `Bearer ${token}`,
//         },
//         method: 'GET',
//         credentials: 'include', // クッキーを含める
//     })
//         .then((response) => {
//             if (!response.ok) {
//                 throw new Error('ユーザー情報の取得に失敗しました');
//             }
//             // return response.json(); // ユーザー情報をJSON形式で取得
//             currentUserId = response.json().user_id;
//         })
//         .then((user) => {
//             console.log('ログイン中のユーザー:', user);
//             const userIdElement = document.getElementById('user-id');
//             userIdElement.textContent = `User ID: ${user.user_id}`; // 画面に表示
//         })
//         .catch((error) => {
//             console.error('エラー:', error);
//         });
// }

// フォームのイベント設定関数
function initializeFormEvents() {
    const form = document.getElementById('createMemoForm');
    form.onsubmit = async (event) => {
        event.preventDefault();
        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;

        if (editingMemoId) {
            const is_check = getCheckboxState(editingMemoId);
            const memo = { title, description, is_check };
            await updateMemo(memo);
        } else {
            const memo = { title, description };
            await createMemo(memo);
        }
    };
}

// 更新ボタンのイベント設定関数
function initializeUpdateButtonEvent() {
    document.getElementById('updateButton').onclick = async () => {
        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
        const is_check = getCheckboxState(editingMemoId);
        await updateMemo({ title, description, is_check });
    };
}

// メモ一覧テーブル内のクリックイベント設定関数
function initializeTableClickEvents() {
    document
        .querySelector('#memos tbody')
        .addEventListener('click', async (event) => {
            if (event.target.className === 'edit') {
                const memoId = event.target.dataset.id;
                await editMemo(memoId);
            } else if (event.target.className === 'delete') {
                const memoId = event.target.dataset.id;
                await deleteMemo(memoId);
            } else if (event.target.type === 'checkbox') {
                const memoId = event.target.dataset.id;
                const isChecked = event.target.checked;
                await updateCheckBox(memoId, isChecked);
            }
        });
}

/**
 * ドキュメントの読み込みが完了時の処理
 */
document.addEventListener('DOMContentLoaded', () => {
    // initializeUserId();
    initializeFormEvents();
    initializeUpdateButtonEvent();
    initializeTableClickEvents();
    fetchAndDisplayMemos();
});
