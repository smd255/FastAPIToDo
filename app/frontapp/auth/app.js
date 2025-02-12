document.addEventListener("DOMContentLoaded", function () {
    const formTitle = document.getElementById("form-title");
    const submitBtn = document.getElementById("submit-btn");
    const toggleLink = document.getElementById("toggle-link");
    const toggleText = document.getElementById("toggle-text"); // メッセージ用

    let isRegister = false; // 初期状態はログイン

    function updateForm() {
        if (isRegister) {
            formTitle.innerText = "新規登録";
            submitBtn.innerText = "新規登録";
            toggleText.innerHTML = 'アカウントをお持ちですか？ <a href="#" id="toggle-link">ログイン</a>';
        } else {
            formTitle.innerText = "ログイン";
            submitBtn.innerText = "ログイン";
            toggleText.innerHTML = 'アカウントをお持ちでないですか？ <a href="#" id="toggle-link">新規登録</a>';
        }

        // クリックイベントを再設定（リンクが書き換えられるため）
        document.getElementById("toggle-link").addEventListener("click", function (event) {
            event.preventDefault(); // ページ遷移を防ぐ
            isRegister = !isRegister; // 切り替え
            updateForm(); // フォームを更新
        });
    }

    updateForm(); // 初期状態を反映
});
