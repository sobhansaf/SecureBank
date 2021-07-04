from datetime import datetime

log_file_name = 'data.log'
log_file = open(log_file_name, 'a')
format_ = '%d-%m-%Y %H:%M:%S'    # datetime format

def log(string):
    
    now = datetime.now().strftime(format_)
    print(f'[{now}] : {string}', file=log_file)


# now = datetime.now().strftime('%d-%m-%Y %H:%M:%S')




