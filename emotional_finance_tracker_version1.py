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
        self.budgets = self.data.get('budgets', {})
        self.categories = ['Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities', 
                          'Entertainment', 'Healthcare', 'Groceries', 'Investment', 'Other']
        self.income_sources = ['Salary', 'Freelance', 'Investment', 'Gift', 'Bonus', 'Other']
        # Money + Mind: Emotional trigger tracking
        self.emotions = ['Happy', 'Stressed', 'Sad', 'Bored', 'Anxious', 'Excited', 
                        'Tired', 'Lonely', 'Angry', 'Celebratory', 'Neutral']
        self.spending_types = ['Planned', 'Impulse', 'Necessary', 'Regretful']
    
    def load_data(self):
        """Load financial data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠ Warning: Data file corrupted. Starting fresh.")
                return {'expenses': [], 'income': [], 'budgets': {}}
        return {'expenses': [], 'income': [], 'budgets': {}}
    
    def save_data(self):
        """Save financial data to JSON file"""
        self.data['expenses'] = self.expenses
        self.data['income'] = self.income
        self.data['budgets'] = self.budgets
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def validate_date(self, date_str):
        """Validate date format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def add_income(self, amount, source, description, date=None):
        """Add income entry"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        elif not self.validate_date(date):
            print("✗ Invalid date format. Use YYYY-MM-DD")
            return False
        
        if amount <= 0:
            print("✗ Amount must be positive")
            return False
        
        income_entry = {
            'date': date,
            'amount': float(amount),
            'source': source,
            'description': description
        }
        self.income.append(income_entry)
        self.save_data()
        print(f"✓ Income added: €{amount} from {source}")
        return True
    
    def add_expense(self, amount, category, description, date=None, emotion=None, spending_type=None):
        """Add a new expense with optional emotional tracking"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        elif not self.validate_date(date):
            print("✗ Invalid date format. Use YYYY-MM-DD")
            return False
        
        if amount <= 0:
            print("✗ Amount must be positive")
            return False
        
        expense = {
            'date': date,
            'amount': float(amount),
            'category': category,
            'description': description
        }
        
        # Money + Mind: Add emotional context if provided
        if emotion:
            expense['emotion'] = emotion
        if spending_type:
            expense['spending_type'] = spending_type
        
        self.expenses.append(expense)
        self.save_data()
        print(f"✓ Expense added: €{amount} for {category}")
        
        # Check budget warning
        self.check_budget_alert(category, date)
        return True
    
    def set_budget(self, category, amount, month=None, year=None):
        """Set monthly budget for a category"""
        if month is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        budget_key = f"{year}-{month:02d}"
        if budget_key not in self.budgets:
            self.budgets[budget_key] = {}
        
        self.budgets[budget_key][category] = float(amount)
        self.save_data()
        print(f"✓ Budget set: €{amount} for {category} ({month}/{year})")
    
    def check_budget_alert(self, category, date):
        """Check if expense exceeds budget and alert user"""
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        budget_key = f"{date_obj.year}-{date_obj.month:02d}"
        
        if budget_key in self.budgets and category in self.budgets[budget_key]:
            budget = self.budgets[budget_key][category]
            
            # Calculate total spent in category this month
            month_expenses = [e for e in self.expenses 
                            if datetime.strptime(e['date'], '%Y-%m-%d').month == date_obj.month 
                            and datetime.strptime(e['date'], '%Y-%m-%d').year == date_obj.year
                            and e['category'] == category]
            
            total_spent = sum(e['amount'] for e in month_expenses)
            
            if total_spent > budget:
                print(f"⚠ BUDGET ALERT: {category} spending (€{total_spent:.2f}) exceeds budget (€{budget:.2f})!")
            elif total_spent > budget * 0.8:
                remaining = budget - total_spent
                print(f"⚠ Budget warning: Only €{remaining:.2f} remaining for {category}")
    
    def view_budgets(self, month=None, year=None):
        """View budgets and spending comparison"""
        if month is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        budget_key = f"{year}-{month:02d}"
        
        if budget_key not in self.budgets or not self.budgets[budget_key]:
            print(f"No budgets set for {month}/{year}")
            return
        
        print(f"\n{'='*85}")
        print(f"BUDGET TRACKER - {month}/{year}")
        print(f"{'='*85}")
        print(f"{'Category':<25} {'Budget':<12} {'Spent':<12} {'Remaining':<12} {'Status':<10}")
        print(f"{'-'*85}")
        
        for category, budget in self.budgets[budget_key].items():
            month_expenses = [e for e in self.expenses 
                            if datetime.strptime(e['date'], '%Y-%m-%d').month == month 
                            and datetime.strptime(e['date'], '%Y-%m-%d').year == year
                            and e['category'] == category]
            
            spent = sum(e['amount'] for e in month_expenses)
            remaining = budget - spent
            
            if spent > budget:
                status = "⚠ OVER"
            elif spent > budget * 0.8:
                status = "⚡ Warning"
            else:
                status = "✓ OK"
            
            print(f"{category:<25} €{budget:<11.2f} €{spent:<11.2f} €{remaining:<11.2f} {status:<10}")
        
        print(f"{'='*85}\n")
    
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
        for i, inc in enumerate(self.income):
            if inc in filtered:
                desc = inc['description'][:32] + '...' if len(inc['description']) > 35 else inc['description']
                if show_index:
                    print(f"{i:<4} {inc['date']:<12} {inc['source']:<20} €{inc['amount']:<9.2f} {desc:<35}")
                else:
                    print(f"{inc['date']:<12} {inc['source']:<20} €{inc['amount']:<9.2f} {desc:<35}")
                total += inc['amount']
        
        print("="*85)
        print(f"Total Income: €{total:.2f}\n")
    
    def view_expenses(self, month=None, year=None, show_index=False, category=None):
        """View expenses for a specific month or all expenses"""
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        filtered = self.expenses
        
        # Filter by month/year
        if month and year:
            filtered = [e for e in filtered 
                       if datetime.strptime(e['date'], '%Y-%m-%d').month == month 
                       and datetime.strptime(e['date'], '%Y-%m-%d').year == year]
        
        # Filter by category
        if category:
            filtered = [e for e in filtered if e['category'] == category]
        
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
        for i, exp in enumerate(self.expenses):
            if exp in filtered:
                desc = exp['description'][:32] + '...' if len(exp['description']) > 35 else exp['description']
                if show_index:
                    print(f"{i:<4} {exp['date']:<12} {exp['category']:<20} €{exp['amount']:<9.2f} {desc:<35}")
                else:
                    print(f"{exp['date']:<12} {exp['category']:<20} €{exp['amount']:<9.2f} {desc:<35}")
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
        
        category_totals = defaultdict(float)
        for exp in monthly_expenses:
            category_totals[exp['category']] += exp['amount']
        
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
        
        expense_values = [monthly_expenses.get(m, 0) for m in all_months]
        income_values = [monthly_income.get(m, 0) for m in all_months]
        savings_values = [income_values[i] - expense_values[i] for i in range(len(all_months))]
        
        avg_income = statistics.mean(income_values) if income_values else 0
        avg_expenses = statistics.mean(expense_values) if expense_values else 0
        avg_savings = statistics.mean(savings_values) if savings_values else 0
        
        recent_income = income_values[-1] if income_values else 0
        recent_expenses = expense_values[-1] if expense_values else 0
        recent_savings = recent_income - recent_expenses
        
        n = len(expense_values)
        if n >= 3:
            x_values = list(range(n))
            x_mean = statistics.mean(x_values)
            
            y_mean_exp = statistics.mean(expense_values)
            numerator_exp = sum((x - x_mean) * (y - y_mean_exp) for x, y in zip(x_values, expense_values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            slope_exp = numerator_exp / denominator if denominator != 0 else 0
            predicted_expenses = expense_values[-1] + slope_exp
            
            y_mean_inc = statistics.mean(income_values)
            numerator_inc = sum((x - x_mean) * (y - y_mean_inc) for x, y in zip(x_values, income_values))
            slope_inc = numerator_inc / denominator if denominator != 0 else 0
            predicted_income = income_values[-1] + slope_inc
        else:
            predicted_expenses = avg_expenses
            predicted_income = avg_income
        
        predicted_savings = predicted_income - predicted_expenses
        
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
        
        print(f"\n💡 PERSONALIZED RECOMMENDATIONS:")
        
        if recent_savings < 0:
            print(f"  ⚠ ALERT: You're spending more than you earn!")
            print(f"  • Reduce expenses by at least €{abs(recent_savings):.2f}")
        elif recent_savings < avg_income * 0.2:
            print(f"  ⚠ WARNING: Low savings rate!")
            print(f"  • Target: Save at least 20% of income (€{avg_income * 0.2:.2f})")
        else:
            print(f"  ✓ Good job! You're saving money.")
        
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
        
        optimal_savings = predicted_income * 0.3
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
    
    def export_to_csv(self, filename='financial_report.csv'):
        """Export all financial data to CSV"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Type', 'Date', 'Category/Source', 'Amount', 'Description'])
            
            for exp in self.expenses:
                writer.writerow(['Expense', exp['date'], exp['category'], exp['amount'], exp['description']])
            
            for inc in self.income:
                writer.writerow(['Income', inc['date'], inc['source'], inc['amount'], inc['description']])
        
        print(f"✓ Data exported to {filename}")
    
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
                return True
            else:
                print("✗ Deletion cancelled.")
                return False
        else:
            print("Invalid index")
            return False
    
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
                return True
            else:
                print("✗ Deletion cancelled.")
                return False
        else:
            print("Invalid index")
            return False
    
    def analyze_emotional_spending(self, month=None, year=None):
        """Money + Mind: Analyze spending patterns by emotion"""
        filtered = self.expenses
        
        if month and year:
            filtered = [e for e in self.expenses 
                       if datetime.strptime(e['date'], '%Y-%m-%d').month == month 
                       and datetime.strptime(e['date'], '%Y-%m-%d').year == year]
        
        # Filter only expenses with emotional data
        emotional_expenses = [e for e in filtered if 'emotion' in e]
        
        if not emotional_expenses:
            print("\n⚠ No emotional data tracked yet.")
            print("Start tracking emotions with your expenses to see patterns!")
            return
        
        # Group by emotion
        emotion_spending = defaultdict(lambda: {'count': 0, 'total': 0, 'expenses': []})
        spending_type_data = defaultdict(lambda: {'count': 0, 'total': 0})
        category_emotion = defaultdict(lambda: defaultdict(float))
        
        for exp in emotional_expenses:
            emotion = exp.get('emotion', 'Unknown')
            amount = exp['amount']
            category = exp['category']
            
            emotion_spending[emotion]['count'] += 1
            emotion_spending[emotion]['total'] += amount
            emotion_spending[emotion]['expenses'].append(exp)
            
            category_emotion[emotion][category] += amount
            
            if 'spending_type' in exp:
                spending_type = exp['spending_type']
                spending_type_data[spending_type]['count'] += 1
                spending_type_data[spending_type]['total'] += amount
        
        total_emotional_spending = sum(data['total'] for data in emotion_spending.values())
        
        period = f"{month}/{year}" if month and year else "All Time"
        
        print("\n" + "="*80)
        print(f"💭 MONEY + MIND ANALYSIS - {period}")
        print("="*80)
        
        # Emotional spending breakdown
        print(f"\n{'Emotion':<15} {'Count':<8} {'Total Spent':<15} {'Avg/Purchase':<15} {'% of Total'}")
        print("-"*80)
        
        sorted_emotions = sorted(emotion_spending.items(), key=lambda x: x[1]['total'], reverse=True)
        
        for emotion, data in sorted_emotions:
            avg_spend = data['total'] / data['count']
            percentage = (data['total'] / total_emotional_spending * 100)
            print(f"{emotion:<15} {data['count']:<8} €{data['total']:<14.2f} €{avg_spend:<14.2f} {percentage:.1f}%")
        
        print("-"*80)
        print(f"{'TOTAL':<15} {sum(d['count'] for d in emotion_spending.values()):<8} €{total_emotional_spending:<14.2f}")
        
        # Spending type analysis
        if spending_type_data:
            print(f"\n{'Spending Type':<15} {'Count':<8} {'Total':<15} {'% of Total'}")
            print("-"*80)
            
            sorted_types = sorted(spending_type_data.items(), key=lambda x: x[1]['total'], reverse=True)
            for stype, data in sorted_types:
                percentage = (data['total'] / total_emotional_spending * 100)
                print(f"{stype:<15} {data['count']:<8} €{data['total']:<14.2f} {percentage:.1f}%")
        
        # Insights and recommendations
        print(f"\n{'='*80}")
        print("🧠 PSYCHOLOGICAL INSIGHTS & RECOMMENDATIONS")
        print("="*80)
        
        # Find highest spending emotion
        if sorted_emotions:
            top_emotion, top_data = sorted_emotions[0]
            top_avg = top_data['total'] / top_data['count']
            
            print(f"\n🎯 Trigger Alert:")
            print(f"   Your highest spending emotion is '{top_emotion}'")
            print(f"   Total: €{top_data['total']:.2f} across {top_data['count']} purchases")
            print(f"   Average per purchase: €{top_avg:.2f}")
            
            # Category breakdown for top emotion
            if category_emotion[top_emotion]:
                print(f"\n   Most spent categories when {top_emotion.lower()}:")
                sorted_cats = sorted(category_emotion[top_emotion].items(), 
                                   key=lambda x: x[1], reverse=True)[:3]
                for cat, amt in sorted_cats:
                    print(f"     • {cat}: €{amt:.2f}")
        
        # Impulse spending analysis
        if 'Impulse' in spending_type_data:
            impulse_total = spending_type_data['Impulse']['total']
            impulse_pct = (impulse_total / total_emotional_spending * 100)
            
            if impulse_pct > 30:
                print(f"\n⚠ Warning: {impulse_pct:.1f}% of your spending is impulsive (€{impulse_total:.2f})")
                print(f"   Tip: Try the 24-hour rule for non-essential purchases")
            elif impulse_pct > 15:
                print(f"\n⚡ Notice: {impulse_pct:.1f}% impulse spending detected (€{impulse_total:.2f})")
        
        # Regretful spending
        if 'Regretful' in spending_type_data:
            regret_total = spending_type_data['Regretful']['total']
            print(f"\n💡 You marked €{regret_total:.2f} as regretful purchases")
            print(f"   Consider: What emotions preceded these purchases?")
            
            regretful_expenses = [e for e in emotional_expenses if e.get('spending_type') == 'Regretful']
            regret_emotions = defaultdict(int)
            for exp in regretful_expenses:
                regret_emotions[exp.get('emotion', 'Unknown')] += 1
            
            if regret_emotions:
                top_regret_emotion = max(regret_emotions.items(), key=lambda x: x[1])
                print(f"   Pattern: Most regrets happen when feeling '{top_regret_emotion[0]}'")
        
        # Emotional spending vs necessary spending
        necessary_total = spending_type_data.get('Necessary', {}).get('total', 0)
        discretionary = total_emotional_spending - necessary_total
        
        print(f"\n📊 Spending Breakdown:")
        print(f"   Necessary: €{necessary_total:.2f} ({necessary_total/total_emotional_spending*100:.1f}%)")
        print(f"   Discretionary: €{discretionary:.2f} ({discretionary/total_emotional_spending*100:.1f}%)")
        
        # Healthy spending emotions
        healthy_emotions = ['Happy', 'Celebratory', 'Excited', 'Neutral']
        healthy_total = sum(emotion_spending[e]['total'] for e in healthy_emotions if e in emotion_spending)
        healthy_pct = (healthy_total / total_emotional_spending * 100)
        
        print(f"\n✅ Positive emotional spending: {healthy_pct:.1f}%")
        
        stress_emotions = ['Stressed', 'Anxious', 'Sad', 'Angry', 'Lonely']
        stress_total = sum(emotion_spending[e]['total'] for e in stress_emotions if e in emotion_spending)
        stress_pct = (stress_total / total_emotional_spending * 100)
        
        if stress_pct > 25:
            print(f"⚠ Stress-related spending: {stress_pct:.1f}% (€{stress_total:.2f})")
            print(f"   Suggestion: Find healthier coping mechanisms (exercise, meditation, etc.)")
        
        print("="*80 + "\n")
        
        return {
            'emotion_spending': dict(emotion_spending),
            'spending_type_data': dict(spending_type_data),
            'total': total_emotional_spending
        }
    
    def get_emotional_journal(self, month=None, year=None):
        """Money + Mind: View chronological emotional spending journal"""
        filtered = self.expenses
        
        if month and year:
            filtered = [e for e in self.expenses 
                       if datetime.strptime(e['date'], '%Y-%m-%d').month == month 
                       and datetime.strptime(e['date'], '%Y-%m-%d').year == year]
        
        emotional_expenses = [e for e in filtered if 'emotion' in e]
        
        if not emotional_expenses:
            print("\n⚠ No emotional data tracked yet.")
            return
        
        # Sort by date
        emotional_expenses.sort(key=lambda x: x['date'], reverse=True)
        
        period = f"{month}/{year}" if month and year else "All Time"
        
        print("\n" + "="*90)
        print(f"📖 EMOTIONAL SPENDING JOURNAL - {period}")
        print("="*90)
        print(f"{'Date':<12} {'Emotion':<12} {'Type':<12} {'Category':<18} {'Amount':<10} {'Description'}")
        print("-"*90)
        
        for exp in emotional_expenses:
            emotion = exp.get('emotion', '-')
            stype = exp.get('spending_type', '-')
            desc = exp['description'][:25] + '...' if len(exp['description']) > 28 else exp['description']
            
            print(f"{exp['date']:<12} {emotion:<12} {stype:<12} {exp['category']:<18} €{exp['amount']:<9.2f} {desc}")
        
        print("="*90 + "\n")


def main():
    tracker = ExpenseTracker()
    
    while True:
        print("\n" + "="*60)
        print("PERSONAL FINANCE TRACKER 💰")
        print("="*60)
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Income")
        print("4. View Expenses")
        print("5. Monthly Balance & Summary")
        print("6. Analyze Financial Trends")
        print("7. AI Prediction: Savings Forecast")
        print("8. Set Budget")
        print("9. View Budgets")
        print("10. Export to CSV")
        print("11. Delete Entry")
        print("12. 💭 Money + Mind: Emotional Analysis")
        print("13. 📖 Money + Mind: Emotional Journal")
        print("14. Exit")
        print("="*60)
        
        choice = input("\nSelect option (1-14): ").strip()
        
        if choice == '1':
            print("\n--- ADD INCOME ---")
            print("\nSelect Income Source:")
            for i, source in enumerate(tracker.income_sources, 1):
                print(f"  {i}. {source}")
            
            source_choice = input(f"\nEnter number (1-{len(tracker.income_sources)}): ").strip()
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
            
            category_choice = input(f"\nEnter number (1-{len(tracker.categories)}): ").strip()
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
            
            # Money + Mind: Optional emotional tracking
            track_emotion = input("\n💭 Track emotion for this purchase? (y/n, default: n): ").strip().lower()
            
            emotion = None
            spending_type = None
            
            if track_emotion in ['y', 'yes']:
                print("\nHow were you feeling?")
                for i, emo in enumerate(tracker.emotions, 1):
                    print(f"  {i}. {emo}")
                
                emotion_choice = input(f"\nSelect emotion (1-{len(tracker.emotions)}): ").strip()
                try:
                    emotion_idx = int(emotion_choice) - 1
                    if 0 <= emotion_idx < len(tracker.emotions):
                        emotion = tracker.emotions[emotion_idx]
                except ValueError:
                    print("Invalid emotion, skipping...")
                
                print("\nWhat type of spending was this?")
                for i, stype in enumerate(tracker.spending_types, 1):
                    print(f"  {i}. {stype}")
                
                type_choice = input(f"\nSelect type (1-{len(tracker.spending_types)}): ").strip()
                try:
                    type_idx = int(type_choice) - 1
                    if 0 <= type_idx < len(tracker.spending_types):
                        spending_type = tracker.spending_types[type_idx]
                except ValueError:
                    print("Invalid type, skipping...")
            
            try:
                tracker.add_expense(
                    float(amount), 
                    category, 
                    description,
                    date_input if date_input else None,
                    emotion,
                    spending_type
                )
            except ValueError:
                print("Invalid amount!")
        
        elif choice == '3':
            month = input("Month (1-12, press Enter for all): ").strip()
            year = input("Year (YYYY, press Enter for all): ").strip()
            
            try:
                if month and year:
                    tracker.view_income(int(month), int(year))
                else:
                    tracker.view_income()
            except ValueError:
                print("Invalid month or year!")
        
        elif choice == '4':
            month = input("Month (1-12, press Enter for all): ").strip()
            year = input("Year (YYYY, press Enter for all): ").strip()
            
            try:
                if month and year:
                    tracker.view_expenses(int(month), int(year))
                else:
                    tracker.view_expenses()
            except ValueError:
                print("Invalid month or year!")
        
        elif choice == '5':
            month = input("Month (1-12, press Enter for current): ").strip()
            year = input("Year (YYYY, press Enter for current): ").strip()
            
            try:
                if month and year:
                    tracker.get_monthly_balance(int(month), int(year))
                else:
                    tracker.get_monthly_balance()
            except ValueError:
                print("Invalid month or year!")
        
        elif choice == '6':
            tracker.analyze_spending_trends()
        
        elif choice == '7':
            tracker.predict_next_month_savings()
        
        elif choice == '8':
            print("\n--- SET BUDGET ---")
            print("\nSelect Category:")
            for i, category in enumerate(tracker.categories, 1):
                print(f"  {i}. {category}")
            
            category_choice = input(f"\nEnter number (1-{len(tracker.categories)}): ").strip()
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
            
            amount = input("Budget amount: €").strip()
            month = input("Month (1-12, press Enter for current): ").strip()
            year = input("Year (YYYY, press Enter for current): ").strip()
            
            try:
                if month and year:
                    tracker.set_budget(category, float(amount), int(month), int(year))
                else:
                    tracker.set_budget(category, float(amount))
            except ValueError:
                print("Invalid input!")
        
        elif choice == '9':
            month = input("Month (1-12, press Enter for current): ").strip()
            year = input("Year (YYYY, press Enter for current): ").strip()
            
            try:
                if month and year:
                    tracker.view_budgets(int(month), int(year))
                else:
                    tracker.view_budgets()
            except ValueError:
                print("Invalid month or year!")
        
        elif choice == '10':
            filename = input("Filename (press Enter for 'financial_report.csv'): ").strip()
            if not filename:
                filename = 'financial_report.csv'
            tracker.export_to_csv(filename)
        
        elif choice == '11':
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
        
        elif choice == '12':
            print("\n--- 💭 MONEY + MIND: EMOTIONAL SPENDING ANALYSIS ---")
            month = input("Month (1-12, press Enter for all time): ").strip()
            year = input("Year (YYYY, press Enter for all time): ").strip()
            
            try:
                if month and year:
                    tracker.analyze_emotional_spending(int(month), int(year))
                else:
                    tracker.analyze_emotional_spending()
            except ValueError:
                print("Invalid month or year!")
        
        elif choice == '13':
            print("\n--- 📖 MONEY + MIND: EMOTIONAL SPENDING JOURNAL ---")
            month = input("Month (1-12, press Enter for all time): ").strip()
            year = input("Year (YYYY, press Enter for all time): ").strip()
            
            try:
                if month and year:
                    tracker.get_emotional_journal(int(month), int(year))
                else:
                    tracker.get_emotional_journal()
            except ValueError:
                print("Invalid month or year!")
        
        elif choice == '14':
            print("\nGoodbye! Track wisely, save smartly! 💰")
            break
        
        else:
            print("Invalid option! Please select 1-14.")


if __name__ == "__main__":
    main()