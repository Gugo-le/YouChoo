document.addEventListener("DOMContentLoaded", () => {
    const guessButton = document.getElementById("guess-button");
    const wordInput = document.getElementById("word-input");
    const rankingTable = document.getElementById("ranking-table");
    const rankingSection = document.getElementById("ranking-section");
    const startButton = document.getElementById("start-button");
    const giveUpButton = document.getElementById("give-up-button");
    const wordcloud = document.getElementById("wordcloud");
    const gameInfo = document.getElementById("game-info");
    const top10Button = document.getElementById("top10-button");
    const backButton = document.getElementById("back-button");
    const top10RankingTable = document.getElementById("top10-ranking-table");
    const top10Container = document.getElementById("top10-container");
    const mainContainer = document.querySelector(".container");
    const mainHeader = document.getElementById("main-header");

    let attempts = 0;
    let rankings = [];

    function containsEnglish(input) {
        const englishRegex = /[a-zA-Z]/;
        return englishRegex.test(input);
    }

    function updateRankingTable(rankings, lastword) {
        rankingTable.innerHTML = "";

        const sortedRankings = [...rankings].sort((a, b) => b.similarity - a.similarity);

        // 방금 입력한 단어를 제일 상단에 추가 ==> 시도횟수가 많아지면 사용자가 불편함.
        const lastWordRanking = sortedRankings.find(item => item.word === lastword);
        if (lastWordRanking) {
            const row = document.createElement("tr");
            row.classList.add("last-guessed-word");
            row.innerHTML = `
                <td>#${rankings.findIndex((originalItem) => originalItem.word === lastword) + 1}</td>
                <td style="color: red;">${lastWordRanking.word}</td>
                <td>${(lastWordRanking.similarity * 100).toFixed(2)}%</td>
                <td>${sortedRankings.indexOf(lastWordRanking) + 1}</td>
            `;
            rankingTable.appendChild(row);
        }

        sortedRankings.forEach((item, rankIndex) => {
            if (item.word !== lastword) {
                const inputOrder = rankings.findIndex((originalItem) => originalItem.word === item.word) + 1;

                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>#${inputOrder}</td>
                    <td style="color: white;">${item.word}</td>
                    <td>${(item.similarity * 100).toFixed(2)}%</td>
                    <td>${rankIndex + 1}</td>
                `;
                rankingTable.appendChild(row);
            }
        });
    }

    function fetchRankings(lastword) {
        fetch("/rankings")
            .then((response) => response.json())
            .then((data) => {
                if (data.rankings) {
                    updateRankingTable(data.rankings, lastword);
                }
            })
            .catch((error) => console.error("랭킹 조회 중 오류 발생:", error));
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
    setInterval(fetchWordcloud, 10000);

    function startGame() {
        if (localStorage.getItem("gameStatus") === "finished") {
            gameInfo.textContent = "‼️게임은 하루에 한 번만 가능합니다.‼️";
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
                updateRankingTable(rankings);
                fetchRankings();
                fetchWordcloud();

                gameInfo.textContent = "인공지능은 어떤 단어를 생각하고 있을까요?";
                wordInput.disabled = false;
                guessButton.disabled = false;
                giveUpButton.disabled = false;
            })
            .catch((error) => console.error("게임 시작 중 오류 발생:", error));
    }

    function fetchTop10Rankings() {
        fetch("/top10")
            .then((response) => response.json())
            .then((data) => {
                if (data.rankings) {
                    updateTop10RankingTable(data.rankings);
                }
            })
            .catch((error) => console.error("TOP 10 랭킹 조회 중 오류 발생:", error));
    }

    function updateTop10RankingTable(rankings) {
        top10RankingTable.innerHTML = "";

        rankings.sort((a, b) => a.attempts - b.attempts).forEach((item, rankIndex) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>#${rankIndex + 1}</td>
                <td>${item.uuid}</td>
                <td>${item.attempts}</td>
                <td>${item.time}</td>
            `;
            top10RankingTable.appendChild(row);
        });
    }

    top10Button.addEventListener("click", () => {
        guessButton.style.display = "none";
        wordInput.style.display = "none";
        mainHeader.style.display = "none";
        gameInfo.style.display = "none";
        rankingSection.style.display = "none";
        top10Container.style.display = "block";
        fetchTop10Rankings();
    });

    backButton.addEventListener("click", () => {
        top10Container.style.display = "none";
        mainHeader.style.display = "block";
        gameInfo.style.display = "block";
        rankingSection.style.display = "block";
        guessButton.style.display = "block";
        wordInput.style.display = "block";
    });

    guessButton.addEventListener("click", () => {
        const userInput = wordInput.value.trim();

        if (containsEnglish(userInput)) {
            gameInfo.textContent = "‼️영어는 입력할 수 없습니다. 한글 단어를 입력해주세요.‼️";
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
                    gameInfo.textContent = `🎉 축하합니다. ${data.attempts}번째만에 정답을 맞췄습니다! 랭킹은 ${data.rank}위 입니다.`;
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

                updateRankingTable(rankings, userInput);
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