import csv
import math
import unittest
import warnings
from io import StringIO

import pandas as pd

from src.core.data_pipeline import (
    build_forecast_table,
    forecast_metrics_from_plan_rows,
    validate_forecast_plan_rows,
)
from src.utils.document_examples import build_document_examples

warnings.filterwarnings("ignore", category=FutureWarning)


def _build_forecast_table_without_future_warnings(application):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        return build_forecast_table(pd.DataFrame([application]))


def _build_document_examples_without_future_warnings(application):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        return build_document_examples(application)


FORECAST_ROWS = [
    {
        "forecast_year": 1,
        "projected_revenue": 120000.0,
        "projected_employees": 11,
        "projected_free_cash_flow": -5000.0,
        "projected_debt": 90000.0,
    },
    {
        "forecast_year": 2,
        "projected_revenue": 118000.0,
        "projected_employees": 12,
        "projected_free_cash_flow": 3000.0,
        "projected_debt": 87000.0,
    },
    {
        "forecast_year": 3,
        "projected_revenue": 145000.0,
        "projected_employees": 13,
        "projected_free_cash_flow": 13000.0,
        "projected_debt": 78000.0,
    },
    {
        "forecast_year": 4,
        "projected_revenue": 151000.0,
        "projected_employees": 14,
        "projected_free_cash_flow": 18000.0,
        "projected_debt": 69000.0,
    },
    {
        "forecast_year": 5,
        "projected_revenue": 200000.0,
        "projected_employees": 16,
        "projected_free_cash_flow": 34000.0,
        "projected_debt": 50000.0,
    },
]


BASE_APPLICATION = {
    "application_id": "TEST-APP",
    "company_id": "TEST-CO",
    "company_name": "Example SME",
    "annual_revenue": 100000.0,
    "employees": 10,
    "existing_debt": 100000.0,
    "requested_amount": 25000.0,
    "term_months": 60,
    "interest_rate": 0.10,
    "free_cash_flow": 10000.0,
    "monthly_burn_rate": 5000.0,
    "cash_flow_to_revenue_ratio": 0.10,
    "forecast_revenue_cagr": 0.10,
    "forecast_employee_cagr": 0.05,
    "forecast_fcf_margin_year5": 0.15,
    "planned_debt_reduction_pct": 0.25,
}


class ForecastPlanTests(unittest.TestCase):
    def test_submitted_rows_are_preserved_by_forecast_rendering(self):
        # New SME submissions should show the exact annual rows the applicant
        # saved, not a re-interpolated forecast generated from year-5 metrics.
        application = {**BASE_APPLICATION, "forecast_plan_rows": FORECAST_ROWS}

        rendered = _build_forecast_table_without_future_warnings(application)

        self.assertEqual(
            rendered[
                [
                    "forecast_year",
                    "projected_revenue",
                    "projected_employees",
                    "projected_free_cash_flow",
                    "projected_debt",
                ]
            ].to_dict("records"),
            FORECAST_ROWS,
        )

    def test_legacy_application_without_rows_still_generates_five_years(self):
        # Existing demo sessions and seed records do not all have
        # forecast_plan_rows, so the historical generated forecast remains as a
        # compatibility fallback.
        rendered = _build_forecast_table_without_future_warnings(BASE_APPLICATION)

        self.assertEqual(rendered["forecast_year"].tolist(), [1, 2, 3, 4, 5])
        self.assertEqual(len(rendered), 5)

    def test_year_five_and_cagr_metrics_are_derived_from_submitted_rows(self):
        metrics, errors = forecast_metrics_from_plan_rows(
            FORECAST_ROWS, annual_revenue=100000.0, employees=10, existing_debt=100000.0
        )

        self.assertFalse(errors)
        self.assertEqual(metrics["forecast_revenue_year5"], 200000.0)
        self.assertEqual(metrics["forecast_employees_year5"], 16)
        self.assertEqual(metrics["forecast_fcf_year5"], 34000.0)
        self.assertEqual(metrics["planned_debt_reduction_amount"], 50000.0)
        self.assertAlmostEqual(
            metrics["forecast_revenue_cagr"], math.pow(2.0, 1 / 5) - 1
        )
        self.assertAlmostEqual(metrics["forecast_fcf_margin_year5"], 0.17)
        self.assertAlmostEqual(metrics["planned_debt_reduction_pct"], 0.50)

    def test_invalid_or_incomplete_rows_are_rejected(self):
        invalid_rows = [
            {
                "forecast_year": year,
                "projected_revenue": None,
                "projected_employees": None,
                "projected_free_cash_flow": None,
                "projected_debt": None,
            }
            for year in range(1, 6)
        ]

        rows, errors = validate_forecast_plan_rows(invalid_rows)

        self.assertEqual(rows, [])
        self.assertTrue(errors)

    def test_sample_forecast_support_file_uses_annual_plan_rows(self):
        application = {**BASE_APPLICATION, "forecast_plan_rows": FORECAST_ROWS}

        examples = _build_document_examples_without_future_warnings(application)
        decoded = examples["forecast_support"]["content"].decode("utf-8")
        reader = csv.DictReader(StringIO(decoded))
        rows = list(reader)

        self.assertEqual(
            reader.fieldnames,
            [
                "forecast_year",
                "projected_revenue_eur",
                "projected_employees",
                "projected_free_cash_flow_eur",
                "projected_debt_eur",
                "assumptions_evidence_note",
            ],
        )
        self.assertEqual(len(rows), 5)

    def test_fraudulent_forecast_support_contains_year_level_red_flags(self):
        application = {
            **BASE_APPLICATION,
            "forecast_plan_rows": FORECAST_ROWS,
            "sample_document_profile": "fraudulent",
        }

        examples = _build_document_examples_without_future_warnings(application)
        decoded = examples["forecast_support"]["content"].decode("utf-8").lower()

        self.assertIn("unsupported growth assumption", decoded)
        self.assertIn("unsigned loi", decoded)


if __name__ == "__main__":
    unittest.main()
