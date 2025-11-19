document.addEventListener("DOMContentLoaded", () => {
    const guessButton = document.getElementById("guess-button");
    const nicknameInput = document.getElementById("nickname-input");
    const setNicknameButton = document.getElementById("set-nickname-button");
    const nicknameModal = document.getElementById("nickname-modal");
    const wordInput = document.getElementById("word-input");
    const rankingTable = document.getElementById("ranking-table");
    const rankingSection = document.getElementById("ranking-section");
    const giveUpButton = document.getElementById("give-up-button");
    const top10Button = document.getElementById("top10-button");
    const backButton = document.getElementById("back-button");
    const top10RankingTable = document.getElementById("top10-ranking-table");
    const top10RankingSection = document.getElementById("top10-ranking-section");
    const mainHeader = document.getElementById("main-header");
    const gameInfo = document.getElementById("game-info");
    const wordcloudSection = document.querySelector(".wordcloud-section");
    const qaSections = document.querySelectorAll(".qa");
    const footerBasic = document.querySelector(".footer-basic");
    const customHr = document.querySelector(".custom-hr");

    let attempts = 0;
    let rankings = [];

    function containsEnglish(input) {
        const englishRegex = /[a-zA-Z]/;
        return englishRegex.test(input);
    }

    function updateRankingTable(rankings, lastword) {
        rankingTable.innerHTML = "";

        const sortedRankings = [...rankings].sort((a, b) => b.similarity - a.similarity);

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
        if (!localStorage.getItem("nickname")) {
            gameInfo.textContent = "닉네임을 설정한 후 게임을 시작해주세요.";
            return;
        }

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

    // 닉네임 설정 처리
    setNicknameButton.addEventListener("click", () => {
        const nickname = nicknameInput.value.trim();
        if (!nickname) {
            gameInfo.textContent = "닉네임을 입력해주세요.";
            return;
        }

        fetch('/set-nickname', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nickname })
            })
            .then(async(res) => {
                const data = await res.json();
                if (!res.ok) {
                    gameInfo.textContent = data.error || '닉네임 설정 실패';
                    return;
                }
                // 성공
                localStorage.setItem('nickname', data.nickname);
                gameInfo.textContent = `닉네임이 설정되었습니다: ${data.nickname}`;
                // 모달 숨김
                if (nicknameModal) nicknameModal.style.display = 'none';
                // 단어 입력창과 추측 버튼을 복구/활성화
                wordInput.style.display = '';
                guessButton.style.display = '';
                wordInput.disabled = false;
                guessButton.disabled = false;
                giveUpButton.disabled = false;
                // 게임을 시작하도록 호출
                startGame();
            })
            .catch((err) => {
                console.error('닉네임 설정 중 오류:', err);
                gameInfo.textContent = '닉네임 설정 중 오류가 발생했습니다.';
            });
    });

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
            let colorClass = "";
            let fontWeight = "";
            if (rankIndex === 0) {
                colorClass = "gold";
                fontWeight = "bold";
            } else if (rankIndex === 1) {
                colorClass = "silver";
                fontWeight = "bold";
            } else if (rankIndex === 2) {
                colorClass = "bronze";
                fontWeight = "bold";
            }
            const displayName = item.nickname || item.uuid || '(unknown)';
            row.innerHTML = `
                <td class="${colorClass}" style="font-weight: ${fontWeight};">#${rankIndex + 1}</td>
                <td class="${colorClass}" style="font-weight: ${fontWeight};">${displayName}</td>
                <td class="${colorClass}" style="font-weight: ${fontWeight};">${item.attempts}</td>
                <td class="${colorClass}" style="font-weight: ${fontWeight};">${item.time}</td>
            `;
            top10RankingTable.appendChild(row);
        });
    }

    function saveGameState() {
        const gameState = {
            attempts,
            rankings,
            gameInfo: gameInfo.textContent,
            wordInput: wordInput.value,
            wordInputDisabled: wordInput.disabled,
            guessButtonDisabled: guessButton.disabled,
            giveUpButtonDisabled: giveUpButton.disabled,
        };
        localStorage.setItem("gameState", JSON.stringify(gameState));
    }

    function loadGameState() {
        const gameState = JSON.parse(localStorage.getItem("gameState"));
        if (gameState) {
            attempts = gameState.attempts;
            rankings = gameState.rankings;
            gameInfo.textContent = gameState.gameInfo;
            wordInput.value = gameState.wordInput;
            wordInput.disabled = gameState.wordInputDisabled;
            guessButton.disabled = gameState.guessButtonDisabled;
            giveUpButton.disabled = gameState.giveUpButtonDisabled;
            updateRankingTable(rankings);
        }
    }

    top10Button.addEventListener("click", () => {
        saveGameState();
        mainHeader.style.display = "none";
        gameInfo.style.display = "none";
        rankingSection.style.display = "none";
        wordcloudSection.style.display = "none";
        guessButton.style.display = "none";
        giveUpButton.style.display = "none";
        top10Button.style.display = "none";
        wordInput.style.display = "none";
        top10RankingSection.style.display = "block";
        qaSections.forEach(section => section.style.display = "none");
        footerBasic.style.display = "none";
        customHr.style.display = "none";
        fetchTop10Rankings();
    });

    backButton.addEventListener("click", () => {
        top10RankingSection.style.display = "none";
        mainHeader.style.display = "block";
        gameInfo.style.display = "block";
        rankingSection.style.display = "block";
        wordcloudSection.style.display = "block";
        guessButton.style.display = "block";
        giveUpButton.style.display = "block";
        top10Button.style.display = "block";
        wordInput.style.display = "block";
        qaSections.forEach(section => section.style.display = "block");
        footerBasic.style.display = "block";
        customHr.style.display = "block";
        loadGameState();
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
                saveGameState();
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
                    saveGameState();
                }
            })
            .catch((error) => console.error("포기 처리 중 오류 발생:", error));
    });

    loadGameState();
    // 닉네임이 이미 로컬에 있으면 모달 숨기기, 없으면 모달 표시
    if (localStorage.getItem('nickname')) {
        const existing = localStorage.getItem('nickname');
        if (nicknameModal) nicknameModal.style.display = 'none';
        gameInfo.textContent = `닉네임이 설정되었습니다: ${existing}`;
    } else {
        if (nicknameModal) {
            nicknameModal.style.display = 'flex';
            // 비활성화: 모달에서 닉네임 입력 전까지 게임 입력 금지
            wordInput.disabled = true;
            guessButton.disabled = true;
            giveUpButton.disabled = true;
            // focus
            nicknameInput && nicknameInput.focus();
        }
    }

    startGame();
});