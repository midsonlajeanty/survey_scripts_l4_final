import re
import json
import uuid

from services import s3


class Survey:
    def __init__(self, questions_file):
        with open(questions_file, 'r', encoding='utf-8') as file:
            self.questions = json.load(file)

    def validate_input(self, user_input):
        pattern = re.compile(r'^\d+(,\d+)*$')
        return bool(pattern.match(user_input))

    def ask_question(self, question_data):
        print('\n')
        print(question_data['question'])
        for i, answer in enumerate(question_data['answers'], 1):
            print(f"{i}. {answer}")

        if question_data['can_specify']:
            print(f"{len(question_data['answers']) + 1}. Autre")

        while True:
            if question_data['allow_multiple']:
                print("Entrez les numéros des réponses qui vous correspondent, séparés par des virgules (ex: 1,2,3)")

            user_input = input("Votre réponse : ")

            if self.validate_input(user_input):
                user_input = [int(num.strip()) for num in user_input.split(',')]

                if not question_data['allow_multiple'] and len(user_input) > 1:
                    print("Veuillez entrer un seul numéro.")
                    continue

                max = len(question_data['answers']) + 1 if question_data['can_specify'] else len(question_data['answers'])
                valid_numbers = list(range(1, max + 1))

                if all(num in valid_numbers for num in user_input):
                    if len(user_input) == 1:
                        if question_data['can_specify'] and user_input == len(question_data['answers']) + 1:
                            return input("Précisez votre réponse : ")
                        else:
                            return question_data['answers'][user_input[0] - 1]
                    else:
                        response = [question_data['answers'][num - 1] for num in user_input]

                        if question_data['can_specify'] and len(user_input) == len(question_data['answers']) + 1:
                            while True:
                                response.append(
                                    input("Précisez votre réponse : "))

                                want_to_add = input("Voulez-vous ajouter une réponse ? (o/n) : ")
                                if want_to_add.lower() != 'o':
                                    break

                        return response
                else:
                    print(
                        "Veuillez entrer des numéros valides séparés par des virgules.")
            else:
                print("Veuillez entrer des numéros valides séparés par des virgules.")

    def save_data(self, result: dict):
        print('\nSaving data ...')
        data: list = json.loads(s3.read())
        data.append(result)
        s3.write(json.dumps(data, indent=2, ensure_ascii=False))
        print("Data Save successfully !!!")

    def run(self):
        results: list[dict] = []

        for question_data in self.questions:
            answer = self.ask_question(question_data)
            results.append({"question": question_data['question'], "answer": answer})

        self.save_data({
            'reference': str(uuid.uuid4()),
            'answers': results
        })


if __name__ == "__main__":
    question_file = 'data/questions.json'
    survey = Survey(question_file)
    survey.run()
