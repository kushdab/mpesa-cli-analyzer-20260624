import csv
import argparse
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

class MpesaAnalyzer:
    def __init__(self):
        self.categories = {
            'Airtime': ['safcom', 'airtime'],
            'Utilities': ['kplc', 'nairobi water', 'dstv', 'zuku'],
            'Food': ['kfc', 'java', 'glovo', 'supermarket', 'naivas', 'carrefour'],
            'Transport': ['uber', 'bolt', 'little cab'],
            'P2P': ['to -', 'from -']
        }

    def parse_csv(self, file_path: str) -> List[Dict[str, Any]]:
        transactions = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Normalize keys to handle different M-Pesa export formats
                    clean_row = {k.strip(): v.strip() for k, v in row.items()}
                    if not clean_row.get('Details'):
                        continue
                    
                    transactions.append({
                        'date': self._parse_date(clean_row.get('Completion Time', '')),
                        'details': clean_row.get('Details', '').lower(),
                        'withdrawn': self._to_float(clean_row.get('Withdrawn', '0')),
                        'paid_in': self._to_float(clean_row.get('Paid In', '0'))
                    })
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
            sys.exit(1)
        return transactions

    def _parse_date(self, date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now()

    def _to_float(self, val: str) -> float:
        try:
            return float(val.replace(',', ''))
        except:
            return 0.0

    def categorize(self, details: str) -> str:
        for category, keywords in self.categories.items():
            if any(kw in details for kw in keywords):
                return category
        return 'Other'

    def generate_report(self, transactions: List[Dict[str, Any]]):
        monthly_stats = defaultdict(lambda: {'spent': 0.0, 'received': 0.0, 'cats': defaultdict(float)})
        
        for tx in transactions:
            month_key = tx['date'].strftime('%Y-%B')
            cat = self.categorize(tx['details'])
            
            monthly_stats[month_key]['spent'] += tx['withdrawn']
            monthly_stats[month_key]['received'] += tx['paid_in']
            if tx['withdrawn'] > 0:
                monthly_stats[month_key]['cats'][cat] += tx['withdrawn']

        print("\n=== M-Pesa Monthly Spending Analysis ===")
        for month, data in sorted(monthly_stats.items()):
            print(f"\nMonth: {month}")
            print(f"  Total Received: KES {data['received']:,.2f}")
            print(f"  Total Spent:    KES {data['spent']:,.2f}")
            print("  Spending Breakdown by Category:")
            for cat, amt in sorted(data['cats'].items(), key=lambda x: x[1], reverse=True):
                perc = (amt / data['spent'] * 100) if data['spent'] > 0 else 0
                print(f"    - {cat:12}: KES {amt:10,.2f} ({perc:5.1f}%)")
        print("\nReport generated successfully.")

def main():
    parser = argparse.ArgumentParser(description='Analyze M-Pesa CSV Statements')
    parser.add_argument('file', help='Path to the M-Pesa CSV file')
    args = parser.parse_args()

    analyzer = MpesaAnalyzer()
    data = analyzer.parse_csv(args.file)
    if not data:
        print("No transaction data found.")
        return
    
    analyzer.generate_report(data)

if __name__ == '__main__':
    main()
