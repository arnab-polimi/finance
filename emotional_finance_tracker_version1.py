import json
import os
from datetime import datetime
from collections import defaultdict
import statistics

class MoneyMindTracker:
    def __init__(self, data_file='money_mind.json'):
        self.data_file = data_file
        self.data = self.load_data()
        self.expenses = self.data.get('expenses', [])
        self.income = self.data.get('income', [])
        self.budgets = self.data.get('budgets', {})
        self.emotional_insights = self.data.get('emotional_insights', [])
        
        self.categories = ['Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities', 
                          'Entertainment', 'Healthcare', 'Groceries', 'Investment', 'Other']
        self.income_sources = ['Salary', 'Freelance', 'Investment', 'Gift', 'Bonus', 'Other']
        
        # Emotional states
        self.emotions = ['Happy', 'Stressed', 'Sad', 'Anxious', 'Excited', 'Bored', 
                        'Angry', 'Tired', 'Celebrating', 'Neutral']
        
        # Spending triggers
        self.triggers = ['Impulse', 'Planned', 'Social Pressure', 'Comfort/Stress Relief', 
                        'Reward', 'Necessity', 'FOMO', 'Boredom', 'Advertisement']
    
    def load_data(self):
        """Load financial and emotional data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠ Warning: Data file corrupted. Starting fresh.")
                return {'expenses': [], 'income': [], 'budgets': {}, 'emotional_insights': []}
        return {'expenses': [], 'income': [], 'budgets': {}, 'emotional_insights': []}
    
    def save_data(self):
        """Save all data to JSON file"""
        self.data['expenses'] = self.expenses
        self.data['income'] = self.income
        self.data['budgets'] = self.budgets
        self.data['emotional_insights'] = self.emotional_insights
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def validate_date(self, date_str):
        """Validate date format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def add_expense(self, amount, category, description, date=None, emotion=None, trigger=None, notes=None):
        """Add expense with emotional context"""
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
            'description': description,
            'emotion': emotion,
            'trigger': trigger,
            'notes': notes
        }
        self.expenses.append(expense)
        self.save_data()
        print(f"✓ Expense added: ${amount} for {category}")
        
        # Provide immediate emotional insight
        if emotion and trigger:
            self.provide_instant_insight(category, amount, emotion, trigger)
        
        self.check_budget_alert(category, date)
        return True
    
    def provide_instant_insight(self, category, amount, emotion, trigger):
        """Provide immediate feedback based on emotional state and trigger"""
        print(f"\n💭 MINDFUL MOMENT:")
        
        # Emotional spending patterns
        if emotion in ['Stressed', 'Anxious', 'Sad'] and trigger == 'Comfort/Stress Relief':
            print(f"  ⚠ Emotional spending detected!")
            print(f"  → You spent ${amount:.2f} while feeling {emotion.lower()}")
            print(f"  💡 TIP: Try a 10-minute walk or call a friend next time")
            print(f"     Alternative coping strategies can save money and boost mood!")
        
        elif trigger == 'Impulse' and amount > 50:
            print(f"  ⚠ Large impulse purchase spotted!")
            print(f"  💡 TIP: Try the 24-hour rule for purchases over $50")
            print(f"     Wait a day - if you still want it, then buy it!")
        
        elif trigger == 'Social Pressure' or trigger == 'FOMO':
            print(f"  ⚠ Social influence detected!")
            print(f"  💡 TIP: Your worth isn't measured by keeping up with others")
            print(f"     True friends respect your financial boundaries!")
        
        elif emotion == 'Celebrating' and trigger == 'Reward':
            print(f"  ✓ Celebration spending - enjoy the moment!")
            print(f"  💡 TIP: Balance treats with free celebrations too")
            print(f"     A picnic can be just as memorable as a fancy dinner!")
        
        elif trigger == 'Boredom' and category in ['Shopping', 'Entertainment']:
            print(f"  ⚠ Boredom spending detected!")
            print(f"  💡 TIP: Find free activities - library, hiking, creative hobbies")
            print(f"     Boredom spending often leads to buyer's remorse!")
        
        print()
    
    def add_income(self, amount, source, description, date=None, emotion=None):
        """Add income with emotional context"""
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
            'description': description,
            'emotion': emotion
        }
        self.income.append(income_entry)
        self.save_data()
        print(f"✓ Income added: ${amount} from {source}")
        return True
    
    def log_emotional_insight(self, insight_type, emotion, amount, category, reflection):
        """Log an emotional insight for future analysis"""
        insight = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': insight_type,
            'emotion': emotion,
            'amount': amount,
            'category': category,
            'reflection': reflection
        }
        self.emotional_insights.append(insight)
        self.save_data()
    
    def analyze_emotional_spending(self):
        """Analyze spending patterns based on emotions and triggers"""
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        # Filter expenses with emotional data
        emotional_expenses = [e for e in self.expenses if e.get('emotion')]
        
        if not emotional_expenses:
            print("No emotional data recorded yet. Start tracking emotions with your expenses!")
            return
        
        print("\n" + "="*80)
        print("🧠 EMOTIONAL SPENDING ANALYSIS")
        print("="*80)
        
        # Group by emotion
        emotion_spending = defaultdict(lambda: {'count': 0, 'total': 0, 'categories': defaultdict(float)})
        trigger_spending = defaultdict(lambda: {'count': 0, 'total': 0})
        
        for exp in emotional_expenses:
            emotion = exp.get('emotion')
            trigger = exp.get('trigger')
            amount = exp['amount']
            category = exp['category']
            
            if emotion:
                emotion_spending[emotion]['count'] += 1
                emotion_spending[emotion]['total'] += amount
                emotion_spending[emotion]['categories'][category] += amount
            
            if trigger:
                trigger_spending[trigger]['count'] += 1
                trigger_spending[trigger]['total'] += amount
        
        # Emotion breakdown
        print(f"\n📊 SPENDING BY EMOTIONAL STATE:")
        print(f"{'-'*80}")
        print(f"{'Emotion':<15} {'Transactions':<15} {'Total Spent':<15} {'Avg/Transaction':<15}")
        print(f"{'-'*80}")
        
        for emotion in sorted(emotion_spending.keys(), key=lambda x: emotion_spending[x]['total'], reverse=True):
            data = emotion_spending[emotion]
            avg = data['total'] / data['count']
            print(f"{emotion:<15} {data['count']:<15} ${data['total']:<14.2f} ${avg:<14.2f}")
        
        # Trigger breakdown
        print(f"\n🎯 SPENDING BY TRIGGER:")
        print(f"{'-'*80}")
        print(f"{'Trigger':<25} {'Transactions':<15} {'Total Spent':<15} {'Avg/Transaction':<15}")
        print(f"{'-'*80}")
        
        for trigger in sorted(trigger_spending.keys(), key=lambda x: trigger_spending[x]['total'], reverse=True):
            data = trigger_spending[trigger]
            avg = data['total'] / data['count']
            print(f"{trigger:<25} {data['count']:<15} ${data['total']:<14.2f} ${avg:<14.2f}")
        
        # High-risk patterns
        print(f"\n⚠️  HIGH-RISK EMOTIONAL PATTERNS:")
        print(f"{'-'*80}")
        
        risk_emotions = ['Stressed', 'Anxious', 'Sad', 'Bored']
        risk_triggers = ['Impulse', 'Comfort/Stress Relief', 'FOMO', 'Boredom']
        
        total_risk_spending = 0
        risk_count = 0
        
        for exp in emotional_expenses:
            if exp.get('emotion') in risk_emotions or exp.get('trigger') in risk_triggers:
                total_risk_spending += exp['amount']
                risk_count += 1
        
        if risk_count > 0:
            total_spending = sum(e['amount'] for e in emotional_expenses)
            risk_percentage = (total_risk_spending / total_spending * 100) if total_spending > 0 else 0
            
            print(f"  • Risk-driven transactions: {risk_count}")
            print(f"  • Total risk-driven spending: ${total_risk_spending:.2f}")
            print(f"  • Percentage of total spending: {risk_percentage:.1f}%")
            
            if risk_percentage > 30:
                print(f"\n  ⚠️  ALERT: Over 30% of your spending is emotionally driven!")
                print(f"  💡 RECOMMENDATION: Consider these strategies:")
                print(f"     → Practice the 24-hour rule for non-essential purchases")
                print(f"     → Build a list of free stress-relief activities")
                print(f"     → Set up automatic savings to reduce available spending money")
                print(f"     → Talk to someone when feeling strong urges to spend")
        else:
            print(f"  ✓ Great job! No high-risk emotional spending detected!")
        
        # Category-emotion connections
        print(f"\n🔗 EMOTION-CATEGORY CONNECTIONS:")
        print(f"{'-'*80}")
        
        for emotion, data in sorted(emotion_spending.items(), key=lambda x: x[1]['total'], reverse=True)[:5]:
            top_category = max(data['categories'].items(), key=lambda x: x[1])
            print(f"  When {emotion}: You spend most on {top_category[0]} (${top_category[1]:.2f})")
        
        print("="*80 + "\n")
    
    def get_emotional_triggers_report(self, days=30):
        """Get a report of emotional triggers over the last N days"""
        cutoff_date = datetime.now()
        recent_expenses = []
        
        for exp in self.expenses:
            exp_date = datetime.strptime(exp['date'], '%Y-%m-%d')
            days_diff = (cutoff_date - exp_date).days
            if days_diff <= days and exp.get('emotion'):
                recent_expenses.append(exp)
        
        if not recent_expenses:
            print(f"No emotional data for the last {days} days.")
            return
        
        print("\n" + "="*80)
        print(f"🎯 EMOTIONAL TRIGGERS REPORT (Last {days} Days)")
        print("="*80)
        
        # Pattern detection
        patterns = defaultdict(list)
        for exp in recent_expenses:
            key = (exp.get('emotion'), exp.get('trigger'))
            patterns[key].append(exp)
        
        print(f"\n🔍 DETECTED PATTERNS:")
        print(f"{'-'*80}")
        
        for (emotion, trigger), exps in sorted(patterns.items(), key=lambda x: len(x[1]), reverse=True):
            if len(exps) >= 2:  # Pattern = 2+ occurrences
                total = sum(e['amount'] for e in exps)
                categories = [e['category'] for e in exps]
                most_common_cat = max(set(categories), key=categories.count)
                
                print(f"\n  Pattern: {emotion} + {trigger}")
                print(f"  • Frequency: {len(exps)} times")
                print(f"  • Total spent: ${total:.2f}")
                print(f"  • Most common category: {most_common_cat}")
                
                # Personalized advice
                if emotion in ['Stressed', 'Anxious'] and len(exps) >= 3:
                    print(f"  ⚠️  ALERT: Recurring stress spending!")
                    print(f"  💡 ACTION PLAN:")
                    print(f"     → Track what's causing stress (work, relationships, health?)")
                    print(f"     → Create a 'stress SOS' list of free activities")
                    print(f"     → Set a weekly stress-spending limit: ${total/len(exps)*0.5:.2f}")
        
        print("="*80 + "\n")
    
    def mood_money_journal(self):
        """Interactive journaling about money and emotions"""
        print("\n" + "="*80)
        print("📔 MOOD + MONEY JOURNAL")
        print("="*80)
        print("\nTake a moment to reflect on your financial emotions...")
        print()
        
        # Prompts
        print("How are you feeling about money today?")
        for i, emotion in enumerate(self.emotions, 1):
            print(f"  {i}. {emotion}")
        
        emotion_choice = input("\nSelect emotion (1-{}): ".format(len(self.emotions))).strip()
        try:
            emotion = self.emotions[int(emotion_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid selection!")
            return
        
        print(f"\nYou're feeling {emotion} about money.")
        print("\nWhat's on your mind? (Write freely)")
        reflection = input("→ ").strip()
        
        print("\nAny recent purchase you're thinking about?")
        purchase = input("→ ").strip()
        
        # Save journal entry
        journal_entry = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'emotion': emotion,
            'reflection': reflection,
            'purchase_thought': purchase
        }
        
        if 'journal_entries' not in self.data:
            self.data['journal_entries'] = []
        
        self.data['journal_entries'].append(journal_entry)
        self.save_data()
        
        # Provide supportive response
        print(f"\n💚 Thank you for sharing.")
        
        if emotion in ['Stressed', 'Anxious', 'Sad']:
            print(f"\nIt's okay to feel {emotion.lower()} about money. You're not alone.")
            print("Remember: Your worth isn't your net worth. 💙")
            print("\n💡 Helpful actions:")
            print("  • Review your budget - knowledge reduces anxiety")
            print("  • Celebrate small wins - paid a bill? That's progress!")
            print("  • Take a break from money stress - do something you love")
        
        elif emotion in ['Happy', 'Excited', 'Celebrating']:
            print(f"\nWonderful! It's great to feel {emotion.lower()} about money! 🎉")
            print("\n💡 Maintain this positive momentum:")
            print("  • Lock in some savings while you're feeling good")
            print("  • Celebrate without overspending")
            print("  • Share your wins with supportive people")
        
        print("\n✓ Journal entry saved!")
        print("="*80 + "\n")
    
    def view_journal_entries(self):
        """View past journal entries"""
        if 'journal_entries' not in self.data or not self.data['journal_entries']:
            print("No journal entries yet. Start journaling to track your emotional money journey!")
            return
        
        print("\n" + "="*80)
        print("📖 YOUR MONEY + MIND JOURNAL")
        print("="*80 + "\n")
        
        entries = self.data['journal_entries'][-10:]  # Last 10 entries
        
        for entry in entries:
            print(f"📅 {entry['date']}")
            print(f"😊 Feeling: {entry['emotion']}")
            print(f"💭 Reflection: {entry['reflection']}")
            if entry.get('purchase_thought'):
                print(f"🛍️  Purchase thought: {entry['purchase_thought']}")
            print("-" * 80)
        
        print()
    
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
        print(f"✓ Budget set: ${amount} for {category} ({month}/{year})")
    
    def check_budget_alert(self, category, date):
        """Check if expense exceeds budget"""
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        budget_key = f"{date_obj.year}-{date_obj.month:02d}"
        
        if budget_key in self.budgets and category in self.budgets[budget_key]:
            budget = self.budgets[budget_key][category]
            
            month_expenses = [e for e in self.expenses 
                            if datetime.strptime(e['date'], '%Y-%m-%d').month == date_obj.month 
                            and datetime.strptime(e['date'], '%Y-%m-%d').year == date_obj.year
                            and e['category'] == category]
            
            total_spent = sum(e['amount'] for e in month_expenses)
            
            if total_spent > budget:
                print(f"⚠ BUDGET ALERT: {category} spending (${total_spent:.2f}) exceeds budget (${budget:.2f})!")
            elif total_spent > budget * 0.8:
                remaining = budget - total_spent
                print(f"⚠ Budget warning: Only ${remaining:.2f} remaining for {category}")
    
    def view_expenses(self, month=None, year=None, show_index=False, show_emotions=False):
        """View expenses with optional emotional data"""
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        filtered = self.expenses
        
        if month and year:
            filtered = [e for e in filtered 
                       if datetime.strptime(e['date'], '%Y-%m-%d').month == month 
                       and datetime.strptime(e['date'], '%Y-%m-%d').year == year]
        
        if not filtered:
            print("No expenses found for this period.")
            return
        
        print("\n" + "="*100)
        if show_emotions:
            if show_index:
                print(f"{'#':<4} {'Date':<12} {'Category':<18} {'Amount':<10} {'Emotion':<12} {'Trigger':<20}")
            else:
                print(f"{'Date':<12} {'Category':<18} {'Amount':<10} {'Emotion':<12} {'Trigger':<20}")
        else:
            if show_index:
                print(f"{'#':<4} {'Date':<12} {'Category':<20} {'Amount':<10} {'Description':<35}")
            else:
                print(f"{'Date':<12} {'Category':<20} {'Amount':<10} {'Description':<35}")
        print("="*100)
        
        total = 0
        for i, exp in enumerate(self.expenses):
            if exp in filtered:
                if show_emotions:
                    emotion = exp.get('emotion', 'N/A')
                    trigger = exp.get('trigger', 'N/A')
                    if show_index:
                        print(f"{i:<4} {exp['date']:<12} {exp['category']:<18} ${exp['amount']:<9.2f} {emotion:<12} {trigger:<20}")
                    else:
                        print(f"{exp['date']:<12} {exp['category']:<18} ${exp['amount']:<9.2f} {emotion:<12} {trigger:<20}")
                else:
                    desc = exp['description'][:32] + '...' if len(exp['description']) > 35 else exp['description']
                    if show_index:
                        print(f"{i:<4} {exp['date']:<12} {exp['category']:<20} ${exp['amount']:<9.2f} {desc:<35}")
                    else:
                        print(f"{exp['date']:<12} {exp['category']:<20} ${exp['amount']:<9.2f} {desc:<35}")
                total += exp['amount']
        
        print("="*100)
        print(f"Total Expenses: ${total:.2f}\n")
    
    def get_monthly_balance(self, month=None, year=None):
        """Get monthly financial summary"""
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
        
        print(f"\n{'='*70}")
        print(f"💰 FINANCIAL SUMMARY FOR {month}/{year}")
        print(f"{'='*70}")
        
        print(f"\nINCOME: ${total_income:.2f}")
        print(f"EXPENSES: ${total_expenses:.2f}")
        
        print(f"\nEXPENSE BREAKDOWN:")
        print(f"{'-'*70}")
        if category_totals:
            for cat, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                print(f"  {cat:<25} ${amount:>10.2f}  ({percentage:.1f}%)")
        
        print(f"\n{'='*70}")
        savings_rate = (net_balance / total_income * 100) if total_income > 0 else 0
        
        if net_balance > 0:
            print(f"  NET SAVINGS: ${net_balance:.2f} ✓")
            print(f"  Savings Rate: {savings_rate:.1f}%")
        elif net_balance < 0:
            print(f"  NET DEFICIT: ${abs(net_balance):.2f} ⚠")
        else:
            print(f"  NET BALANCE: $0.00")
        
        print(f"{'='*70}\n")
    
    def delete_expense(self, index):
        """Delete an expense"""
        if 0 <= index < len(self.expenses):
            deleted = self.expenses[index]
            print(f"\nDeleting: ${deleted['amount']:.2f} - {deleted['category']}")
            
            confirm = input("Confirm? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                self.expenses.pop(index)
                self.save_data()
                print(f"✓ Deleted!")
                return True
        print("Invalid index or cancelled")
        return False


def main():
    tracker = MoneyMindTracker()
    
    print("\n" + "="*80)
    print("💰 MONEY + MIND 🧠")
    print("Your Personal Finance Tracker with Emotional Intelligence")
    print("="*80)
    
    while True:
        print("\n" + "="*80)
        print("MAIN MENU")
        print("="*80)
        print("\n💰 FINANCIAL TRACKING:")
        print("  1. Add Income")
        print("  2. Add Expense (with emotional context)")
        print("  3. View Expenses")
        print("  4. Monthly Balance & Summary")
        print("  5. Set Budget")
        
        print("\n🧠 EMOTIONAL INTELLIGENCE:")
        print("  6. Analyze Emotional Spending Patterns")
        print("  7. Emotional Triggers Report (Last 30 Days)")
        print("  8. Mood + Money Journal")
        print("  9. View Journal Entries")
        
        print("\n⚙️  OTHER:")
        print("  10. Delete Expense")
        print("  11. Exit")
        print("="*80)
        
        choice = input("\nSelect option (1-11): ").strip()
        
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
            
            amount = input("Amount: $").strip()
            description = input("Description: ").strip()
            date_input = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
            
            print("\nHow did receiving this income make you feel? (optional)")
            for i, emotion in enumerate(tracker.emotions, 1):
                print(f"  {i}. {emotion}")
            emotion_choice = input("Select (or press Enter to skip): ").strip()
            
            emotion = None
            if emotion_choice:
                try:
                    emotion = tracker.emotions[int(emotion_choice) - 1]
                except (ValueError, IndexError):
                    pass
            
            try:
                tracker.add_income(
                    float(amount), 
                    source, 
                    description,
                    date_input if date_input else None,
                    emotion
                )
            except ValueError:
                print("Invalid amount!")
        
        elif choice == '2':
            print("\n--- ADD EXPENSE WITH EMOTIONAL CONTEXT ---")
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
            
            amount = input("Amount: $").strip()
            description = input("Description: ").strip()
            date_input = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
            
            # Emotional context
            print("\n🧠 Let's add emotional context (helps you understand your spending patterns):")
            print("\nHow were you feeling when you made this purchase?")
            for i, emotion in enumerate(tracker.emotions, 1):
                print(f"  {i}. {emotion}")
            emotion_choice = input("Select emotion: ").strip()
            
            try:
                emotion = tracker.emotions[int(emotion_choice) - 1]
            except (ValueError, IndexError):
                emotion = 'Neutral'
            
            print("\nWhat triggered this purchase?")
            for i, trigger in enumerate(tracker.triggers, 1):
                print(f"  {i}. {trigger}")
            trigger_choice = input("Select trigger: ").strip()
            
            try:
                trigger = tracker.triggers[int(trigger_choice) - 1]
            except (ValueError, IndexError):
                trigger = 'Other'
            
            notes = input("\nAny additional notes? (optional): ").strip()
            
            try:
                tracker.add_expense(
                    float(amount), 
                    category, 
                    description,
                    date_input if date_input else None,
                    emotion,
                    trigger,
                    notes if notes else None
                )
            except ValueError:
                print("Invalid amount!")
        
        elif choice == '3':
            month = input("Month (1-12, press Enter for all): ").strip()
            year = input("Year (YYYY, press Enter for all): ").strip()
            show_emotions = input("Show emotional data? (yes/no): ").strip().lower() == 'yes'
            
            try:
                if month and year:
                    tracker.view_expenses(int(month), int(year), show_emotions=show_emotions)
                else:
                    tracker.view_expenses(show_emotions=show_emotions)
            except ValueError:
                print("Invalid month or year!")
        
        elif choice == '4':
            month = input("Month (1-12, press Enter for current): ").strip()
            year = input("Year (YYYY, press Enter for current): ").strip()
            
            try:
                if month and year:
                    tracker.get_monthly_balance(int(month), int(year))
                else:
                    tracker.get_monthly_balance()
            except ValueError:
                print("Invalid month or year!")
        
        elif choice == '5':
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
            
            amount = input("Budget amount: $").strip()
            month = input("Month (1-12, press Enter for current): ").strip()
            year = input("Year (YYYY, press Enter for current): ").strip()
            
            try:
                if month and year:
                    tracker.set_budget(category, float(amount), int(month), int(year))
                else:
                    tracker.set_budget(category, float(amount))
            except ValueError:
                print("Invalid input!")
        
        elif choice == '6':
            tracker.analyze_emotional_spending()
        
        elif choice == '7':
            tracker.get_emotional_triggers_report()
        
        elif choice == '8':
            tracker.mood_money_journal()
        
        elif choice == '9':
            tracker.view_journal_entries()
        
        elif choice == '10':
            if not tracker.expenses:
                print("No expenses to delete.")
                continue
            
            tracker.view_expenses(show_index=True)
            index = input("\nEnter expense # to delete (or 'cancel'): ").strip()
            
            if index.lower() == 'cancel':
                continue
            
            try:
                tracker.delete_expense(int(index))
            except ValueError:
                print("Invalid index!")
        
        elif choice == '11':
            print("\n" + "="*80)
            print("💙 Thank you for using Money + Mind!")
            print("Remember: Financial wellness is about progress, not perfection.")
            print("You're doing great by being mindful of your money! 🌟")
            print("="*80 + "\n")
            break
        
        else:
            print("Invalid option! Please select 1-11.")


if __name__ == "__main__":
    main()