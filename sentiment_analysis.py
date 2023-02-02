import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F


class FinBert():
    def __init__(self) -> None:
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert").to(self.device)

    def SentimentAnalyzer(self, doc):
        with torch.no_grad():
            pt_batch = self.tokenizer(doc, padding=True, truncation=True,
                                      max_length=512, return_tensors="pt")
            pt_batch.to(self.device)
            outputs = self.model(**pt_batch)
            pt_predictions = F.softmax(outputs.logits, dim=-1)
            pt_predictions.to(self.device)
            return pt_predictions.detach().cpu().numpy()

    def findPercentageBySentence(self, text):
        posAvg, negAvg, neuAvg = 0, 0, 0
        sentimentArr = self.SentimentAnalyzer(text).tolist()
        posAvg = sentimentArr[0][0]
        negAvg = sentimentArr[0][1]
        neuAvg = sentimentArr[0][2]
        return {'pos': posAvg, 'neg': negAvg, 'neu': neuAvg}
