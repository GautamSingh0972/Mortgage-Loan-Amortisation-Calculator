from project import amortisation_schedule, monthly_payment, total_interest
import pytest 

def test_monthly_payment():
    assert round(monthly_payment(200000, 5, 25), 2) == 1169.18
    assert round(monthly_payment(12000, 0 , 1), 2) == 1000.00
    assert round(monthly_payment(100000, 6, 30), 2) == 599.55
    
    with pytest.raises(ValueError):
        monthly_payment(-5000, 5, 25) 
    with pytest.raises(ValueError):
        monthly_payment(200000, 5, 0)
    with pytest.raises(ValueError):
        monthly_payment(200000, -3, 25)
    

def test_total_interest():
    assert round(total_interest(1000, 12, 0.16666666666), 2) == 15.02
    assert round(total_interest(200000, 5, 25), 2) == 150754.02
    assert round(total_interest(200000, 5, 25, 200), 2) == 108911.43
    
    with pytest.raises(ValueError):
        total_interest(-60000, 10, 12) 
    with pytest.raises(ValueError):
        total_interest(123000, 12, 0)
    with pytest.raises(ValueError):
        total_interest(124000, -59, 36)
    with pytest.raises(ValueError):
        total_interest(10000, 4, 12, -160)

def test_amortisation_schedule():
    schedule = amortisation_schedule(1000, 12, 0.16666666666)
    assert len(schedule) == 2
    assert round(schedule[0]["Interest"], 2) == 10.00
    assert round(schedule[0]["Closing Balance"], 2) == 502.49
    assert round(schedule[1]["Interest"], 2) == 5.02
    assert round(schedule[1]["Closing Balance"], 2) == 0.00
    assert len(amortisation_schedule(200000, 5, 25)) == 300
    assert len(amortisation_schedule(200000, 5, 25, 200)) == 226
    
    with pytest.raises(ValueError):
        amortisation_schedule(-92000, 23, 43) 
    with pytest.raises(ValueError):
        amortisation_schedule(12300, 10, 0)
    with pytest.raises(ValueError):
        amortisation_schedule(37200, -12, 45)
    with pytest.raises(ValueError):
        amortisation_schedule(23000, 6, 23, -200)
    
    
    
    
        