from currency_converter import CurrencyConverter
from tabulate import tabulate 


currencies = {'AUD',
 'BGN',
 'BRL',
 'CAD',
 'CHF',
 'CNY',
 'CYP',
 'CZK',
 'DKK',
 'EEK',
 'EUR',
 'GBP',
 'HKD',
 'HRK',
 'HUF',
 'IDR',
 'ILS',
 'INR',
 'ISK',
 'JPY',
 'KRW',
 'LTL',
 'LVL',
 'MTL',
 'MXN',
 'MYR',
 'NOK',
 'NZD',
 'PHP',
 'PLN',
 'ROL',
 'RON',
 'RUB',
 'SEK',
 'SGD',
 'SIT',
 'SKK',
 'THB',
 'TRL',
 'TRY',
 'USD',
 'ZAR'}

def main():
   print("Loan calculator\n") 
   #Getting the principal amount, and converting if needed
   c = CurrencyConverter() 
   while True: 
       try:
      
           entry = input("Enter your principal loan amount (If your currency is anything other than GBP please enter the currency code but not the amount (e.g.: USD, CNY, INR): \n").strip().upper()
           if entry.isalpha() and entry in currencies: 
               break
           elif float(entry) <= 0:
               raise ValueError("Loan amount is negative")
           break    
       except ValueError as e:
           print(f"Something went wrong: {e}")
   if entry.isalpha():
      while True:
          try:
            amount = float(input("Enter the principal loan in your currency (no currency code): \n"))
            if amount <= 0: 
                raise ValueError("The number is not positive")
            break
          except ValueError:
                print("The value is negative or not a number")
              
      principal_loan = c.convert(amount,entry, "GBP")
   else:
       principal_loan = float(entry)
       
   while True:
        try:
           annual_rate = float(input("Enter your annual interest rate as a float (omit the '%'): \n")) #===> getting the annual interest rate
           if annual_rate >= 0:
               
               break
           else:
               print("Please enter a number greater than zero")
            
        except ValueError:
             print("The value is not a number")

   while True:
       try:
           years = float(input("Enter the amount the years you're paying the loan over: \n"))
           if years > 0:
            break  # Stops looping only if it's a positive number (decimal or whole)
           else:
               print("Please enter a number greater than zero.")
       
       except ValueError:
                print("The value is not a number")
    
   answer = input(f"Is this the correct amount of years: {years} (Please enter Y/N):\n").upper().strip()
   if answer == "Y":
       years = years 
   elif answer == "N":
       years = float(input("Please enter the correct amount of years:\n"))
            
          
   payment = monthly_payment(principal_loan,annual_rate, years)
   print(f"Your monthly payments are £{payment:.2f}\n")
   
   while True:
       try:
           overpayment =input("How much extra do you want to pay each month?:\n£")
           
           if  str(overpayment) == " " or str(overpayment) == "":
               overpayment = 0
               break
           elif float(overpayment) >= 0:
               float(overpayment)
               break
           elif float(overpayment) < 0:
               raise ValueError("overpayments cannot be below £0")
           break 
       except ValueError as e: 
           print(f"Something went wrong: {e}")
           
           
   
   print("\n", tabulate(amortisation_schedule(principal_loan, annual_rate, years, overpayment), headers = "keys", floatfmt= ",.2f"))
       
   print(f"Your total interest is £{total_interest(principal_loan, annual_rate, years, overpayment):,.2f}")

def monthly_payment(principal_loan,annual_rate, years):
   if principal_loan <= 0:
       raise ValueError("The principal loan must be greater than 0")
   if years <= 0: 
       raise ValueError("Please enter a vlaid timeframe")
   if annual_rate < 0:
       raise ValueError("Please ensure the interest rate is greater than not less than 0")

   monthly_payments = years * 12 

   if annual_rate == 0:

        m = principal_loan/monthly_payments
        return float(m)
   else:
#Calculating the interest rate per month
       monthly_rate = annual_rate/12/100 
       m = ((principal_loan * monthly_rate) / (1-((1+ monthly_rate)**- monthly_payments))) #====> calculate the standard loan amortisation formula  
   
       return float(m)
   
def amortisation_schedule(principal_loan, annual_rate, years, overpayment=0):
    
    
    overpayment = float(overpayment)
    
    if principal_loan <= 0:
        raise ValueError("The principal loan must be greater than 0")
    if years <= 0: 
        raise ValueError("Please enter a vlaid timeframe")
    if annual_rate < 0:
        raise ValueError("Please ensure the interest rate is greater than not less than 0")
    if overpayment < 0: 
        raise ValueError("Please ensure overpayments are not negative")
    
    rows = []
    monthly_rate = float(annual_rate/12/100)
    balance = float(principal_loan)
    month = 0
    payment = monthly_payment(principal_loan,annual_rate, years)
    while balance > 0:
            old_balance = balance
            interest = old_balance * monthly_rate
            payment_this_month = min(payment + overpayment, balance + interest)
            principal_repaid = payment_this_month - interest
            new_balance = old_balance - principal_repaid
            balance = new_balance
            month += 1
          
            b = { "Month": month, "Opening Balance": float(old_balance), "Interest": float(interest), "Payment": float(payment_this_month), "Principal Repaid":float(principal_repaid), "Closing Balance":new_balance}
      
            rows.append(b)
           
    return rows 



def total_interest(principal_loan, annual_rate, years, overpayment=0):
    overpayment = float(overpayment)
    
    
    if principal_loan <= 0:
        raise ValueError("The principal loan must be greater than 0")
    if years <= 0: 
        raise ValueError("Please enter a vlaid timeframe")
    if annual_rate < 0:
        raise ValueError("Please ensure the interest rate is greater than not less than 0")
    if overpayment < 0: 
        raise ValueError("Please ensure overpayments are not negative")
      
 
    monthly_rate = float(annual_rate/12/100)
    balance = float(principal_loan)
    total_interest = 0
    payment = monthly_payment(principal_loan,annual_rate, years)
    while balance > 0 :
        old_balance = balance 
        interest = old_balance * monthly_rate
        payment_this_month = min(payment + overpayment, balance + interest)
        principal_repaid = payment_this_month - interest
        new_balance = balance - principal_repaid
        balance = new_balance
        
        total_interest = total_interest + interest
    return(total_interest)
if __name__ == "__main__":  
    main()