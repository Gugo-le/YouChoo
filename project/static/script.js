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
                attempts = 0;
                rankings = [];
                updateRankingTable();
                fetchWordcloud();

                // 게임 정보 업데이트
                gameInfo.textContent = "게임이 시작되었습니다! 단어를 추측해보세요.";
                alert(data.message); // 시작 메시지 표시
            })
            .catch((error) => console.error("게임 시작 중 오류 발생:", error));
    }

    guessButton.addEventListener("click", () => {
        const userInput = wordInput.value.trim();
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
                    gameInfo.textContent = `정답을 맞췄습니다! 정답: ${data.message}`;
                    alert(`정답입니다! 🎉 정답은 '${data.message}'입니다.`);
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

    giveUpButton.addEventListener("click", () => {
        alert("게임을 포기했습니다. 정답은 페이지에서 확인하세요.");
    });

    // 페이지 로드 시 게임 자동 시작
    startGame();
});