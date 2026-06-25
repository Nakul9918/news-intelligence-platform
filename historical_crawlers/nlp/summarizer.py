from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


summarizer = LsaSummarizer()


def generate_summary(content, sentences_count=3):

    if not content:
        return ""

    try:

        parser = PlaintextParser.from_string(
            content,
            Tokenizer("english")
        )

        summary = summarizer(
            parser.document,
            sentences_count
        )

        final_summary = " ".join(
            str(sentence)
            for sentence in summary
        )

        return final_summary

    except Exception as e:

        print("Summary Error :", e)

        return ""