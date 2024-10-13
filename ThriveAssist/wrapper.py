from openai import OpenAI

client = OpenAI(api_key=OPEN_API_KEY)

def chat(prompt: str):
    primer = "Your role is to give people physical and mental health advice based on what they write in a journal entry and three questions. In the following prompt, the journal entry will be provided as a long paragraph. Afterwards, there will be three question answer pairs, with the question on the top and the answer following. Your goal is to read the journal entry and answers and generate holistic and practical advice to mitigate or resolve their issues. Prioritize readily available solutions and avoid going straight to mental health specialists, but it is OK to reccomend them. Provide a solution with short-term and long-term plans that will improve their health. The structure of the response should be as follows: 1. Reassure the user of their stresses and worries. 2. Provide a basic diagnosis of their issues. 3. Provide short-term and long-term plans. 4. Provide any extra information such as reccomendations."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{primer}\n{prompt}"}]
    )
    return response.choices[0].message.content.strip()

def generate_questions(prompt: str):
    primer = "After reading the journal and the three questions and answers, generate three more questions that would clarify missing information in previous answers, gain further insight into the user's problems, or a question asking the user if they are open to a certain idea. This is very important: format the questions such that only the questions alone are provided in the response. Separate each question with a vertical bar (\"|\") such that no white space is in between each question. After this primer prompt, you will receive a journal entry provided as a long paragraph, and three question and answer pairs. The journal entry will come first, then in each pair the question will be above the answer."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{primer}\n{prompt}"}]
    )
    return response.choices[0].message.content.strip().split(" | ")
