import unittest
from unittest.mock import patch, MagicMock
import requests
from file_for_test import CatFactProcessor, APIError


class TestCatFactProcessor(unittest.TestCase):
    # положительный тест (метод возвращает верный факт и добавляет его в список фактов)
    @patch('file_for_test.requests.get')
    def test_get_fact_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"fact": "Cats sleep 16 hours a day."}
        mock_get.return_value = mock_response

        processor = CatFactProcessor()
        fact = processor.get_fact()

        self.assertEqual(fact, "Cats sleep 16 hours a day.")
        self.assertIn(fact, processor.facts)

    # отрицательный тест (в случае ошибки метод выбрасывает исключение APIError
    # и текст ошибки содержит ожидаемое сообщение)
    @patch('file_for_test.requests.get')
    def test_get_fact_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        processor = CatFactProcessor()

        with self.assertRaises(APIError) as context:
            processor.get_fact()

        self.assertIn("Error request for API", str(context.exception))

    # отрицательный тест (метод возвращает 0, если список фактов пуст)
    def test_get_fact_length_no_facts(self):
        processor = CatFactProcessor()
        self.assertEqual(processor.get_fact_length(), 0)

    # положительный тест (добавляется один факт, и проверяется, что длина этого факта правильная)
    def test_get_fact_length_with_fact(self):
        processor = CatFactProcessor()
        processor.facts.append("Cats are cute.")
        self.assertEqual(processor.get_fact_length(), len("Cats are cute."))

    # отрицательный тест (метод возвращает статистику с нулевыми значениями, если список фактов пуст)
    def test_get_stats_no_facts(self):
        processor = CatFactProcessor()
        expected = {"average": 0, "min": 0, "max": 0}
        self.assertEqual(processor.get_stats(), expected)

    # положительный тест (добавляется несколько фактов, и затем проверяется,
    # что средняя, минимальная и максимальная длина вычисляются правильно)
    def test_get_stats_with_facts(self):
        processor = CatFactProcessor(num_facts=3)
        processor.facts = [
            "Cats are great.",
            "They love to sleep.",
            "Purring is cute.",
            "Jumping high.",
        ]
        stats = processor.get_stats()
        lengths = [len(f) for f in processor.facts[-3:]]
        self.assertEqual(stats["average"], sum(lengths)/3)
        self.assertEqual(stats["min"], min(lengths))
        self.assertEqual(stats["max"], max(lengths))


if __name__ == '__main__':
    unittest.main()
