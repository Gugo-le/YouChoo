document.addEventListener("DOMContentLoaded", () => {
    const guessButton = document.getElementById("guess-button");
    const wordInput = document.getElementById("word-input");
    const rankingTable = document.getElementById("ranking-table");
    const startButton = document.getElementById("start-button");
    const giveUpButton = document.getElementById("give-up-button");
    const wordcloud = document.getElementById("wordcloud");
    const gameInfo = document.getElementById("game-info");

    let attempts = 0;
    let rankings = [];

    // 영어 입력 감지 함수
    function containsEnglish(input) {
        const englishRegex = /[a-zA-Z]/;
        return englishRegex.test(input);
    }

    function updateRankingTable(lastword) {
        rankingTable.innerHTML = "";

        // 유사도 순위 계산
        const sortedRankings = [...rankings].sort((a, b) => b.similarity - a.similarity);

        sortedRankings.forEach((item, rankIndex) => {
            const inputOrder = rankings.findIndex((originalItem) => originalItem.word === item.word) + 1; // 입력 순서 찾기

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>#${inputOrder}</td> <!-- 입력 순서 -->
                <td style="color: ${item.word === lastword ? 'red' : 'white'};">${item.word}</td> <!-- 단어 -->
                <td>${(item.similarity * 100).toFixed(2)}%</td> <!-- 유사도 -->
                <td>${rankIndex + 1}</td> <!-- 랭킹 -->
            `;
            rankingTable.appendChild(row);
        });
    }

    function fetchWordcloud() {
        fetch("/wordcloud")
            .then((response) => response.json())
            .then((data) => {
                if (data.wordcloud) {
                    wordcloud.src = `data:image/png;base64,${data.wordcloud}`;
                }
            })
            .catch((error) => console.error("워드클라우드 업데이트 중 오류 발생:", error));
    }

    function startGame() {
        fetch("/start")
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    gameInfo.textContent = "게임이 시작되었습니다! 단어를 추측해보세요.";
                    wordInput.disabled = false;
                    guessButton.disabled = false;
                    giveUpButton.disabled = false;
                }
            })
            .catch((error) => console.error("게임 시작 중 오류 발생:", error));
    }


    function checkGameStatus() {
        fetch("/check-status")
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "finished") {
                    gameInfo.textContent = "이미 게임을 하셨습니다.";
                    wordInput.disabled = true;
                    guessButton.disabled = true;
                    giveUpButton.disabled = true;
                }
            })
            .catch((error) => console.error("게임 상태 확인 중 오류 발생:", error));
    }

    checkGameStatus();


    // 포기하면 정답 나오고 게임 참여 못하게
    giveUpButton.addEventListener("click", () => {
        fetch("/giveup")
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    gameInfo.textContent = `게임을 포기하셨습니다. 정답은 "${data.message}"입니다.`;
                    setTimeout(() => {
                        updateRankingTable();
                        wordInput.disabled = true;
                        guessButton.disabled = true;
                        giveUpButton.disabled = true;
                    }, 1000);
                }
            })
            .catch((error) => console.error("포기 처리 중 오류 발생:", error));
    });

    const cookies = document.cookie.split("; ").reduce((acc, cookie) => {
        const [key, value] = cookie.split("=");
        acc[key] = value;
        return acc;
    }, {});

    if (cookies.game_status === "finished") {
        gameInfo.textContent = "이미 게임에 참여하셨습니다. 새로고침 후 새로운 게임에 도전하세요.";
        wordInput.disabled = true;
        guessButton.disabled = true;
        giveUpButton.disabled = true;
    }

    guessButton.addEventListener("click", () => {
        const userInput = wordInput.value.trim();

        // 영어 입력 감지
        if (containsEnglish(userInput)) {
            gameInfo.textContent = "영어는 입력할 수 없습니다. 한글 단어를 입력해주세요."
            wordInput.value = ""; // 입력 초기화
            return;
        }

        if (!userInput) return;

        fetch("/guess", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ user_input: userInput }),
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // 정답 처리
                if (data.message) { // JSON 응답에서 정답 메시지
                    gameInfo.textContent = `🎉 축하합니다. ${attempts + 1}번째만에 정답을 맞췄습니다!`;
                    return;
                }

                attempts = data.attempts;

                // 유사도 저장
                const existingIndex = rankings.findIndex((item) => item.word === data.user_input);
                if (existingIndex !== -1) {
                    rankings[existingIndex].similarity = Math.max(
                        rankings[existingIndex].similarity,
                        data.similarity_score
                    );
                } else {
                    rankings.push({ word: data.user_input, similarity: data.similarity_score });
                }

                updateRankingTable(userInput); // 방금 입력한 단어 전달
                wordInput.value = ""; // 입력 초기화
            })
            .catch((error) => console.error("추측 처리 중 오류 발생:", error));
    });

    // 페이지 로드 시 게임 자동 시작
    startGame();
});