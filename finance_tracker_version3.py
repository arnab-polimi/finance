import json
import os
from datetime import datetime
from collections import defaultdict
import statistics

class ExpenseTracker:
    def __init__(self, data_file='finances.json'):
        self.data_file = data_file
        self.data = self.load_data()
        self.expenses = self.data.get('expenses', [])
        self.income = self.data.get('income', [])
        self.categories = ['Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities', 
                          'Entertainment', 'Healthcare', 'Groceries', 'Investment', 'Other']
        self.income_sources = ['Salary', 'Freelance', 'Investment', 'Gift', 'Bonus', 'Other']
    
    def load_data(self):
        """Load financial data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {'expenses': [], 'income': []}
    
    def save_data(self):
        """Save financial data to JSON file"""
        self.data['expenses'] = self.expenses
        self.data['income'] = self.income
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def add_income(self, amount, source, description, date=None):
        """Add income entry"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        income_entry = {
            'date': date,
            'amount': float(amount),
            'source': source,
            'description': description
        }
        self.income.append(income_entry)
        self.save_data()
        print(f"✓ Income added: €{amount} from {source}")
    
    def add_expense(self, amount, category, description, date=None):
        """Add a new expense"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        expense = {
            'date': date,
            'amount': float(amount),
            'category': category,
            'description': description
        }
        self.expenses.append(expense)
        self.save_data()
        print(f"✓ Expense added: €{amount} for {category}")
    
    def view_income(self, month=None, year=None, show_index=False):
        """View income for a specific month or all income"""
        if not self.income:
            print("No income recorded yet.")
            return
        
        filtered = self.income
        if month and year:
            filtered = [i for i in self.income 
                       if datetime.strptime(i['date'], '%Y-%m-%d').month == month 
                       and datetime.strptime(i['date'], '%Y-%m-%d').year == year]
        
        if not filtered:
            print("No income found for this period.")
            return
        
        print("\n" + "="*85)
        if show_index:
            print(f"{'#':<4} {'Date':<12} {'Source':<20} {'Amount':<10} {'Description':<35}")
        else:
            print(f"{'Date':<12} {'Source':<20} {'Amount':<10} {'Description':<35}")
        print("="*85)
        
        total = 0
        # Create index mapping for original list
        for i, inc in enumerate(self.income):
            if inc in filtered:
                if show_index:
                    print(f"{i:<4} {inc['date']:<12} {inc['source']:<20} €{inc['amount']:<9.2f} {inc['description']:<35}")
                else:
                    print(f"{inc['date']:<12} {inc['source']:<20} €{inc['amount']:<9.2f} {inc['description']:<35}")
                total += inc['amount']
        
        print("="*85)
        print(f"Total Income: €{total:.2f}\n")
    
    def view_expenses(self, month=None, year=None, show_index=False):
        """View expenses for a specific month or all expenses"""
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        filtered = self.expenses
        if month and year:
            filtered = [e for e in self.expenses 
                       if datetime.strptime(e['date'], '%Y-%m-%d').month == month 
                       and datetime.strptime(e['date'], '%Y-%m-%d').year == year]
        
        if not filtered:
            print("No expenses found for this period.")
            return
        
        print("\n" + "="*85)
        if show_index:
            print(f"{'#':<4} {'Date':<12} {'Category':<20} {'Amount':<10} {'Description':<35}")
        else:
            print(f"{'Date':<12} {'Category':<20} {'Amount':<10} {'Description':<35}")
        print("="*85)
        
        total = 0
        # Create index mapping for original list
        for i, exp in enumerate(self.expenses):
            if exp in filtered:
                if show_index:
                    print(f"{i:<4} {exp['date']:<12} {exp['category']:<20} €{exp['amount']:<9.2f} {exp['description']:<35}")
                else:
                    print(f"{exp['date']:<12} {exp['category']:<20} €{exp['amount']:<9.2f} {exp['description']:<35}")
                total += exp['amount']
        
        print("="*85)
        print(f"Total Expenses: €{total:.2f}\n")
    
    def get_monthly_balance(self, month=None, year=None):
        """Get income vs expenses balance for a month"""
        if month is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        monthly_expenses = [e for e in self.expenses 
                           if datetime.strptime(e['date'], '%Y-%m-%d').month == month 
                           and datetime.strptime(e['date'], '%Y-%m-%d').year == year]
        
        monthly_income = [i for i in self.income 
                         if datetime.strptime(i['date'], '%Y-%m-%d').month == month 
                         and datetime.strptime(i['date'], '%Y-%m-%d').year == year]
        
        total_income = sum(i['amount'] for i in monthly_income)
        total_expenses = sum(e['amount'] for e in monthly_expenses)
        net_balance = total_income - total_expenses
        
        # Category breakdown
        category_totals = defaultdict(float)
        for exp in monthly_expenses:
            category_totals[exp['category']] += exp['amount']
        
        # Income source breakdown
        income_sources = defaultdict(float)
        for inc in monthly_income:
            income_sources[inc['source']] += inc['amount']
        
        print(f"\n{'='*70}")
        print(f"FINANCIAL SUMMARY FOR {month}/{year}")
        print(f"{'='*70}")
        
        print(f"\nINCOME BREAKDOWN:")
        print(f"{'-'*70}")
        for source, amount in sorted(income_sources.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source:<25} €{amount:>10.2f}")
        print(f"{'-'*70}")
        print(f"  {'TOTAL INCOME':<25} €{total_income:>10.2f}")
        
        print(f"\nEXPENSE BREAKDOWN:")
        print(f"{'-'*70}")
        if category_totals:
            for cat, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                print(f"  {cat:<25} €{amount:>10.2f}  ({percentage:.1f}%)")
        print(f"{'-'*70}")
        print(f"  {'TOTAL EXPENSES':<25} €{total_expenses:>10.2f}")
        
        print(f"\n{'='*70}")
        savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0
        
        if net_balance > 0:
            print(f"  NET SAVINGS: €{net_balance:.2f} ✓")
            print(f"  Savings Rate: {savings_rate:.1f}%")
        elif net_balance < 0:
            print(f"  NET DEFICIT: €{abs(net_balance):.2f} ⚠")
            print(f"  Overspending by: {abs(savings_rate):.1f}%")
        else:
            print(f"  NET BALANCE: €0.00 (Breaking Even)")
        
        print(f"{'='*70}\n")
        
        return {
            'income': total_income,
            'expenses': total_expenses,
            'balance': net_balance,
            'savings_rate': savings_rate
        }
    
    def analyze_spending_trends(self):
        """Analyze spending and income patterns over months"""
        if not self.expenses and not self.income:
            print("Not enough data for analysis.")
            return
        
        monthly_expenses = defaultdict(float)
        monthly_income = defaultdict(float)
        
        for exp in self.expenses:
            date_obj = datetime.strptime(exp['date'], '%Y-%m-%d')
            month_key = f"{date_obj.year}-{date_obj.month:02d}"
            monthly_expenses[month_key] += exp['amount']
        
        for inc in self.income:
            date_obj = datetime.strptime(inc['date'], '%Y-%m-%d')
            month_key = f"{date_obj.year}-{date_obj.month:02d}"
            monthly_income[month_key] += inc['amount']
        
        all_months = sorted(set(list(monthly_expenses.keys()) + list(monthly_income.keys())))
        
        if len(all_months) < 2:
            print("Need at least 2 months of data for trend analysis.")
            return
        
        print("\n" + "="*70)
        print("MONTHLY FINANCIAL TREND")
        print("="*70)
        print(f"{'Month':<12} {'Income':<15} {'Expenses':<15} {'Savings':<15}")
        print("-"*70)
        
        for month in all_months:
            inc = monthly_income.get(month, 0)
            exp = monthly_expenses.get(month, 0)
            sav = inc - exp
            status = "✓" if sav > 0 else "⚠"
            print(f"{month:<12} €{inc:<14.2f} €{exp:<14.2f} €{sav:<14.2f} {status}")
        
        print("="*70 + "\n")
        
        return monthly_expenses, monthly_income
    
    def predict_next_month_savings(self):
        """AI prediction: Predict savings and provide recommendations"""
        if not self.expenses and not self.income:
            print("No data available for prediction.")
            return
        
        # Group data by month
        monthly_expenses = defaultdict(float)
        monthly_income = defaultdict(float)
        
        for exp in self.expenses:
            date_obj = datetime.strptime(exp['date'], '%Y-%m-%d')
            month_key = f"{date_obj.year}-{date_obj.month:02d}"
            monthly_expenses[month_key] += exp['amount']
        
        for inc in self.income:
            date_obj = datetime.strptime(inc['date'], '%Y-%m-%d')
            month_key = f"{date_obj.year}-{date_obj.month:02d}"
            monthly_income[month_key] += inc['amount']
        
        all_months = sorted(set(list(monthly_expenses.keys()) + list(monthly_income.keys())))
        
        if len(all_months) < 2:
            print("Need at least 2 months of data for predictions.")
            return
        
        # Calculate statistics
        expense_values = [monthly_expenses.get(m, 0) for m in all_months]
        income_values = [monthly_income.get(m, 0) for m in all_months]
        savings_values = [income_values[i] - expense_values[i] for i in range(len(all_months))]
        
        avg_income = statistics.mean(income_values) if income_values else 0
        avg_expenses = statistics.mean(expense_values) if expense_values else 0
        avg_savings = statistics.mean(savings_values) if savings_values else 0
        
        recent_income = income_values[-1] if income_values else 0
        recent_expenses = expense_values[-1] if expense_values else 0
        recent_savings = recent_income - recent_expenses
        
        # Predict using linear regression
        n = len(expense_values)
        if n >= 3:
            x_values = list(range(n))
            x_mean = statistics.mean(x_values)
            
            # Predict expenses
            y_mean_exp = statistics.mean(expense_values)
            numerator_exp = sum((x - x_mean) * (y - y_mean_exp) for x, y in zip(x_values, expense_values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            slope_exp = numerator_exp / denominator if denominator != 0 else 0
            predicted_expenses = expense_values[-1] + slope_exp
            
            # Predict income
            y_mean_inc = statistics.mean(income_values)
            numerator_inc = sum((x - x_mean) * (y - y_mean_inc) for x, y in zip(x_values, income_values))
            slope_inc = numerator_inc / denominator if denominator != 0 else 0
            predicted_income = income_values[-1] + slope_inc
        else:
            predicted_expenses = avg_expenses
            predicted_income = avg_income
        
        predicted_savings = predicted_income - predicted_expenses
        
        # Category analysis
        category_monthly = defaultdict(lambda: defaultdict(float))
        for exp in self.expenses:
            date_obj = datetime.strptime(exp['date'], '%Y-%m-%d')
            month_key = f"{date_obj.year}-{date_obj.month:02d}"
            category_monthly[exp['category']][month_key] += exp['amount']
        
        print("\n" + "="*70)
        print("AI SAVINGS PREDICTION & FINANCIAL ANALYSIS")
        print("="*70)
        
        print(f"\nHISTORICAL OVERVIEW:")
        print(f"  • Months tracked: {n}")
        print(f"  • Average monthly income: €{avg_income:.2f}")
        print(f"  • Average monthly expenses: €{avg_expenses:.2f}")
        print(f"  • Average monthly savings: €{avg_savings:.2f}")
        print(f"  • Average savings rate: {(avg_savings/avg_income*100) if avg_income > 0 else 0:.1f}%")
        
        print(f"\nCURRENT MONTH:")
        print(f"  • Income: €{recent_income:.2f}")
        print(f"  • Expenses: €{recent_expenses:.2f}")
        print(f"  • Savings: €{recent_savings:.2f}")
        print(f"  • Savings rate: {(recent_savings/recent_income*100) if recent_income > 0 else 0:.1f}%")
        
        print(f"\nNEXT MONTH PREDICTION:")
        print(f"  • Expected income: €{predicted_income:.2f}")
        print(f"  • Expected expenses: €{predicted_expenses:.2f}")
        print(f"  • Predicted savings: €{predicted_savings:.2f}")
        
        # Recommendations
        print(f"\n💡 PERSONALIZED RECOMMENDATIONS:")
        
        if recent_savings < 0:
            print(f"  ⚠ ALERT: You're spending more than you earn!")
            print(f"  • Reduce expenses by at least €{abs(recent_savings):.2f}")
        elif recent_savings < avg_income * 0.2:
            print(f"  ⚠ WARNING: Low savings rate!")
            print(f"  • Target: Save at least 20% of income (€{avg_income * 0.2:.2f})")
        else:
            print(f"  ✓ Good job! You're saving money.")
        
        # Category recommendations
        print(f"\n  Top spending categories to watch:")
        for category in ['Food & Dining', 'Shopping', 'Entertainment']:
            if category in category_monthly:
                cat_data = category_monthly[category]
                if len(cat_data) >= 2:
                    cat_values = [cat_data[month] for month in sorted(cat_data.keys())]
                    cat_avg = statistics.mean(cat_values)
                    cat_recent = cat_values[-1]
                    
                    if cat_recent > cat_avg * 1.15:
                        diff = cat_recent - cat_avg
                        print(f"    • {category}: Reduce by €{diff:.2f} (Current: €{cat_recent:.2f})")
        
        # Optimal savings goal
        optimal_savings = predicted_income * 0.3  # 30% savings goal
        needed_reduction = predicted_expenses - (predicted_income - optimal_savings)
        
        print(f"\n🎯 OPTIMAL SAVINGS GOAL:")
        print(f"  • Target savings: €{optimal_savings:.2f} (30% of income)")
        if needed_reduction > 0:
            print(f"  • Reduce spending by: €{needed_reduction:.2f}")
            print(f"  • New expense target: €{predicted_income - optimal_savings:.2f}")
        else:
            print(f"  • You're on track! Keep it up!")
        
        print("="*70 + "\n")
        
        return {
            'predicted_income': predicted_income,
            'predicted_expenses': predicted_expenses,
            'predicted_savings': predicted_savings,
            'optimal_savings': optimal_savings
        }
    
    def delete_expense(self, index):
        """Delete an expense by index"""
        if 0 <= index < len(self.expenses):
            deleted = self.expenses[index]
            print(f"\nYou are about to delete:")
            print(f"  Date: {deleted['date']}")
            print(f"  Category: {deleted['category']}")
            print(f"  Amount: €{deleted['amount']:.2f}")
            print(f"  Description: {deleted['description']}")
            
            confirm = input("\nAre you sure? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                self.expenses.pop(index)
                self.save_data()
                print(f"✓ Expense deleted successfully!")
            else:
                print("✗ Deletion cancelled.")
        else:
            print("Invalid index")
    
    def delete_income(self, index):
        """Delete an income entry by index"""
        if 0 <= index < len(self.income):
            deleted = self.income[index]
            print(f"\nYou are about to delete:")
            print(f"  Date: {deleted['date']}")
            print(f"  Source: {deleted['source']}")
            print(f"  Amount: €{deleted['amount']:.2f}")
            print(f"  Description: {deleted['description']}")
            
            confirm = input("\nAre you sure? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                self.income.pop(index)
                self.save_data()
                print(f"✓ Income deleted successfully!")
            else:
                print("✗ Deletion cancelled.")
        else:
            print("Invalid index")


def main():
    tracker = ExpenseTracker()
    
    while True:
        print("\n" + "="*60)
        print("PERSONAL FINANCE TRACKER")
        print("="*60)
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Income")
        print("4. View Expenses")
        print("5. Monthly Balance & Summary")
        print("6. Analyze Financial Trends")
        print("7. AI Prediction: Savings Forecast")
        print("8. Delete Entry")
        print("9. Exit")
        print("="*60)
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == '1':
            print("\n--- ADD INCOME ---")
            print("\nSelect Income Source:")
            for i, source in enumerate(tracker.income_sources, 1):
                print(f"  {i}. {source}")
            
            source_choice = input("\nEnter number (1-{}): ".format(len(tracker.income_sources))).strip()
            try:
                source_idx = int(source_choice) - 1
                if 0 <= source_idx < len(tracker.income_sources):
                    source = tracker.income_sources[source_idx]
                else:
                    print("Invalid selection!")
                    continue
            except ValueError:
                print("Invalid input!")
                continue
            
            amount = input("Amount: €").strip()
            description = input("Description: ").strip()
            date_input = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
            
            try:
                tracker.add_income(
                    float(amount), 
                    source, 
                    description,
                    date_input if date_input else None
                )
            except ValueError:
                print("Invalid amount!")
        
        elif choice == '2':
            print("\n--- ADD EXPENSE ---")
            print("\nSelect Category:")
            for i, category in enumerate(tracker.categories, 1):
                print(f"  {i}. {category}")
            
            category_choice = input("\nEnter number (1-{}): ".format(len(tracker.categories))).strip()
            try:
                category_idx = int(category_choice) - 1
                if 0 <= category_idx < len(tracker.categories):
                    category = tracker.categories[category_idx]
                else:
                    print("Invalid selection!")
                    continue
            except ValueError:
                print("Invalid input!")
                continue
            
            amount = input("Amount: €").strip()
            description = input("Description: ").strip()
            date_input = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
            
            try:
                tracker.add_expense(
                    float(amount), 
                    category, 
                    description,
                    date_input if date_input else None
                )
            except ValueError:
                print("Invalid amount!")
        
        elif choice == '3':
            month = input("Month (1-12, press Enter for all): ").strip()
            year = input("Year (YYYY, press Enter for all): ").strip()
            
            if month and year:
                tracker.view_income(int(month), int(year))
            else:
                tracker.view_income()
        
        elif choice == '4':
            month = input("Month (1-12, press Enter for all): ").strip()
            year = input("Year (YYYY, press Enter for all): ").strip()
            
            if month and year:
                tracker.view_expenses(int(month), int(year))
            else:
                tracker.view_expenses()
        
        elif choice == '5':
            month = input("Month (1-12, press Enter for current): ").strip()
            year = input("Year (YYYY, press Enter for current): ").strip()
            
            if month and year:
                tracker.get_monthly_balance(int(month), int(year))
            else:
                tracker.get_monthly_balance()
        
        elif choice == '6':
            tracker.analyze_spending_trends()
        
        elif choice == '7':
            tracker.predict_next_month_savings()
        
        elif choice == '8':
            print("\n--- DELETE ENTRY ---")
            print("1. Delete Expense")
            print("2. Delete Income")
            del_choice = input("Select (1-2): ").strip()
            
            if del_choice == '1':
                if not tracker.expenses:
                    print("No expenses to delete.")
                    continue
                    
                tracker.view_expenses(show_index=True)
                index = input("\nEnter expense # to delete (or 'cancel' to go back): ").strip()
                
                if index.lower() == 'cancel':
                    print("Cancelled.")
                    continue
                    
                try:
                    tracker.delete_expense(int(index))
                except ValueError:
                    print("Invalid index!")
                    
            elif del_choice == '2':
                if not tracker.income:
                    print("No income to delete.")
                    continue
                    
                tracker.view_income(show_index=True)
                index = input("\nEnter income # to delete (or 'cancel' to go back): ").strip()
                
                if index.lower() == 'cancel':
                    print("Cancelled.")
                    continue
                    
                try:
                    tracker.delete_income(int(index))
                except ValueError:
                    print("Invalid index!")
            else:
                print("Invalid option!")
        
        elif choice == '9':
            print("\nGoodbye! Track wisely, save smartly! 💰")
            break
        
        else:
            print("Invalid option!")


if __name__ == "__main__":
    main()
