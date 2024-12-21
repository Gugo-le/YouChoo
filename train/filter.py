import re

# 불필요한 정보를 제거하고 단어만 필터링하는 함수
def clean_words(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        # 읽은 내용들을 리스트로 저장
        lines = infile.readlines()
    
    cleaned_words = []
    
    for line in lines:
        # 정규 표현식을 사용하여 단어만 추출 (여기서는 한글 단어만 추출)
        words = re.findall(r'[가-힣]+', line)  # 한글 단어만 추출
        
        # 한 줄에 여러 단어가 있을 경우, 그 단어들을 모두 리스트에 추가
        cleaned_words.extend(words)
    
    # 결과를 새로운 파일에 저장
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for word in cleaned_words:
            outfile.write(f"{word}\n")
    
    print(f"불필요한 정보가 제거된 단어들이 {output_file}에 저장되었습니다.")

# 사용 예시
clean_words('wordlist.txt', 'word.txt')