import requests


class APIError(Exception):
    pass


class CatFactProcessor:
    def __init__(self, num_facts=5):
        self.num_facts = num_facts
        self.facts = []

    def get_fact(self):
        try:
            response = requests.get("https://catfact.ninja/fact")
            data = response.json()
            fact = data["fact"]
            self.facts.append(fact)
            return fact
        except requests.exceptions.RequestException as e:
            raise APIError(f"Error request for API: {e}")

    def get_fact_length(self):
        if not self.facts:
            return 0
        return len(self.facts[-1])

    def get_stats(self):
        if not self.facts:
            return {"average": 0, "min": 0, "max": 0}
        lengths = [len(fact) for fact in self.facts[-self.num_facts:]]
        return {
            "average": sum(lengths) / len(lengths) if lengths else 0,
            "min": min(lengths) if lengths else 0,
            "max": max(lengths) if lengths else 0,
        }
