import gspread
import datetime as dt

def next_available_row(sh):
    str_list = list(filter(None, sh.col_values(1)))
    return str(len(str_list)+1)

gc = gspread.service_account('client_secret.json')

sh = gc.open_by_key('1sfcjAUXq75S_8OoXXG2Ebi_iJegUz49UUfEkLqLNJ50').sheet1

def add_data(accounts, wallet, desc, nominal_amount) -> None:
    
    next_row = next_available_row(sh)
    
    sh.update("A{}:E{}".format(next_row, next_row), [[dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), accounts, wallet, desc, nominal_amount,]], raw=False)
    print(next_row)
    if (next_row == '2'):
        sh.update("F{}".format(next_row), sh.acell("E{}".format(next_row), value_render_option='FORMULA').value)
    else:
        sh.update("F{}".format(next_row), "=F{}+E{}".format(int(next_row)-1, next_row), raw=False)