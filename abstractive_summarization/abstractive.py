from transformers import MBartForConditionalGeneration,  MBartTokenizer

path1=r"C:\Users\user\Desktop\mbart_sum\tokenizer"
path=r"C:\Users\user\Desktop\mbart_sum"

#обработка весов модели
tokenizer = MBartTokenizer.from_pretrained(path1)
model = MBartForConditionalGeneration.from_pretrained(path)


def abstractive(article_text, tokenizer=tokenizer, model=model):
    input_ids = tokenizer(
        [article_text],
        max_length=600,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )["input_ids"]

    output_ids = model.generate(
        input_ids=input_ids,
        no_repeat_ngram_size=4
    )[0]

    summary = tokenizer.decode(output_ids, skip_special_tokens=True)
    return summary
