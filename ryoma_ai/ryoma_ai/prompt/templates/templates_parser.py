import json

dataset1 = json.load(open("./dataset1.json"))
dataset2 = json.load(open("./dataset2.json"))

formatted_data = {
    "question": "What are the average and minimum price (in Euro) of all products?",
    "templates": [],
}


def convert(data):
    d = {
        "args": data["args"],
        "costs": data["costs"],
    }

    for question in data["questions"]:
        if (
            question["response"]
            == "avg(age) , min(age) , max(age) FROM singer WHERE country = 'France'"
        ):
            d["formatted_question"] = question

    return d


for data in [dataset1, dataset2]:
    formatted_data["templates"].append(convert(data))
json.dump(formatted_data, open("./formatted_data.json", "w"), indent=4)
