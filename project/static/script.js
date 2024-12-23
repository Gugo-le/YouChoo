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

    function containsEnglish(input) {
        const englishRegex = /[a-zA-Z]/;
        return englishRegex.test(input);
    }

    function updateRankingTable(lastword) {
        rankingTable.innerHTML = "";

        const sortedRankings = [...rankings].sort((a, b) => b.similarity - a.similarity);

        sortedRankings.forEach((item, rankIndex) => {
            const inputOrder = rankings.findIndex((originalItem) => originalItem.word === item.word) + 1;

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>#${inputOrder}</td>
                <td style="color: ${item.word === lastword ? 'red' : 'white'};">${item.word}</td>
                <td>${(item.similarity * 100).toFixed(2)}%</td>
                <td>${rankIndex + 1}</td>
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
        if (localStorage.getItem("gameStatus") === "finished") {
            gameInfo.textContent = "게임은 하루에 한 번만 가능합니다.";
            fetchWordcloud();
            wordInput.disabled = true;
            guessButton.disabled = true;
            giveUpButton.disabled = true;
            return;
        }

        fetch("/start")
            .then((response) => response.json())
            .then((data) => {
                attempts = 0;
                rankings = [];
                updateRankingTable();
                fetchWordcloud();

                gameInfo.textContent = "인공지능은 어떤 단어를 생각하고 있을까요?";
                wordInput.disabled = false;
                guessButton.disabled = false;
                giveUpButton.disabled = false;
            })
            .catch((error) => console.error("게임 시작 중 오류 발생:", error));
    }

    guessButton.addEventListener("click", () => {
        const userInput = wordInput.value.trim();

        if (containsEnglish(userInput)) {
            gameInfo.textContent = "영어는 입력할 수 없습니다. 한글 단어를 입력해주세요.";
            wordInput.value = "";
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

                if (data.message) {
                    gameInfo.textContent = `🎉 축하합니다. ${attempts + 1}번째만에 정답을 맞췄습니다!`;
                    localStorage.setItem("gameStatus", "finished");
                    wordInput.disabled = true;
                    guessButton.disabled = true;
                    giveUpButton.disabled = true;
                    return;
                }

                attempts = data.attempts;

                const existingIndex = rankings.findIndex((item) => item.word === data.user_input);
                if (existingIndex !== -1) {
                    rankings[existingIndex].similarity = Math.max(
                        rankings[existingIndex].similarity,
                        data.similarity_score
                    );
                } else {
                    rankings.push({ word: data.user_input, similarity: data.similarity_score });
                }

                updateRankingTable(userInput);
                wordInput.value = "";
            })
            .catch((error) => console.error("추측 처리 중 오류 발생:", error));
    });

    giveUpButton.addEventListener("click", () => {
        fetch("/giveup")
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    gameInfo.textContent = `게임을 포기하셨습니다. 정답은 "${data.message}"입니다.`;
                    localStorage.setItem("gameStatus", "finished");
                    wordInput.disabled = true;
                    guessButton.disabled = true;
                    giveUpButton.disabled = true;
                }
            })
            .catch((error) => console.error("포기 처리 중 오류 발생:", error));
    });

    startGame();
});